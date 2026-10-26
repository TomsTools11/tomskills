#!/usr/bin/env python3
r"""Compute client-report metrics from GOAL Analytics export CSVs.

Usage:
    python3 compute_metrics.py FILE.csv [FILE.csv ...] [--out metrics.json]
    python3 compute_metrics.py campaign-performance-by-hour-home-ga-last30days.csv \
        --to-tz America/New_York --period-start 2026-09-01 --period-end 2026-09-30

Each file is read independently. The first column is treated as the grouping
dimension (Campaign, Source Type, Property Type, ...). Prints JSON with, per file:
  - rows: raw counts plus derived metrics per row
  - totals: summed counts plus derived metrics (a "Total" row in the export is
    ignored and the rows are summed instead, then compared against it)
  - donut: dash/offset values for the lead-mix donut (sum to exactly 100)
  - funnel: counts, stage-to-stage rates and bar widths for the funnel
  - missing: metrics that cannot be computed because the export lacks a column

By-hour exports (first column "Hour") also get:
  - hourly: one entry per hour, converted from the export's time zone (Pacific unless
    the header or labels say otherwise, e.g. "Hour (Eastern)" / "10 AM ET") to --to-tz,
    sorted by clock time, with lead-based rates and a bar width
  - blocks: adjacent hours merged in clock order until each holds --min-leads leads
    (default 30); a trailing block under the floor is kept and flagged
  - time_zone: the zones, the offset used, and whether the file was converted
  - warnings for a DST change inside the window, hours pushed across midnight, hours
    under the floor, missing outcome columns, and outcomes above leads in any hour
  The offset is computed from real dates (--period-start/--period-end) with zoneinfo,
  so daylight saving time is handled (Arizona vs Pacific differs by season).

Every conversion rate uses Leads (or the stage above it in the funnel), never Clicks.
Cost per lead is deliberately not computed: client reports never show it.
"""
import argparse
import csv
import datetime as dt
import json
import math
import re
import sys
from collections import Counter

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:  # Python < 3.9
    ZoneInfo = None
    ZoneInfoNotFoundError = Exception

# Header aliases seen in GOAL exports. Matching is case-insensitive on the full header.
ALIASES = {
    "searches": ["searches", "opportunities"],
    "impressions": ["impressions", "impr", "impr."],
    "clicks": ["clicks"],
    "leads": ["leads"],
    "calls": ["calls", "inbound calls"],
    "cost": ["cost", "spend", "total cost"],
    "contacted": ["contacted", "contact", "contacts", "contacted leads"],
    "quotes": ["quote", "quotes", "quoted"],
    "policies": ["policy", "policies", "sold", "bound", "binds"],
    "avg_pos": ["avg pos", "avg. pos", "average position", "avg position"],
}

TOTAL_LABELS = {"total", "totals", "grand total", "", "--"}

# Funnel bar floor: the smallest stage still shows a readable bar with its count.
FUNNEL_MIN_WIDTH = 12

# ---------- By-hour exports ----------
DEFAULT_FROM_TZ = "America/Los_Angeles"  # GOAL Analytics reports hours in Pacific time
HOUR_MIN_WIDTH = 2                       # hourly bars are linear and empty (the count sits beside the bar)
ZONE_NAMES = {  # header word or label suffix -> IANA zone
    "eastern": "America/New_York", "et": "America/New_York", "est": "America/New_York", "edt": "America/New_York",
    "central": "America/Chicago", "ct": "America/Chicago", "cst": "America/Chicago", "cdt": "America/Chicago",
    "mountain": "America/Denver", "mt": "America/Denver", "mst": "America/Denver", "mdt": "America/Denver",
    "pacific": "America/Los_Angeles", "pt": "America/Los_Angeles", "pst": "America/Los_Angeles", "pdt": "America/Los_Angeles",
    "arizona": "America/Phoenix", "az": "America/Phoenix",
    "alaska": "America/Anchorage", "akt": "America/Anchorage", "akst": "America/Anchorage", "akdt": "America/Anchorage",
    "hawaii": "Pacific/Honolulu", "ht": "Pacific/Honolulu", "hst": "Pacific/Honolulu",
}
ZONE_LABELS = {  # IANA zone -> (label for report sub-headers, short form)
    "America/New_York": ("Eastern Time", "ET"), "America/Detroit": ("Eastern Time", "ET"),
    "America/Indiana/Indianapolis": ("Eastern Time", "ET"), "America/Kentucky/Louisville": ("Eastern Time", "ET"),
    "America/Chicago": ("Central Time", "CT"), "America/Indiana/Knox": ("Central Time", "CT"),
    "America/Menominee": ("Central Time", "CT"),
    "America/Denver": ("Mountain Time", "MT"), "America/Boise": ("Mountain Time", "MT"),
    "America/Phoenix": ("Arizona Time", "MST"),
    "America/Los_Angeles": ("Pacific Time", "PT"),
    "America/Anchorage": ("Alaska Time", "AKT"), "Pacific/Honolulu": ("Hawaii Time", "HT"),
}
HOUR_LABEL_RE = re.compile(r"^\s*(\d{1,2})(?::00)?\s*([AaPp]\.?[Mm]\.?)?\s*([A-Za-z]{1,4})?\s*$")


def parse_number(value):
    """'$1,234.50' -> 1234.5, '2,448 (23.24%)' -> 2448, '-' or '' -> None."""
    if value is None:
        return None
    text = str(value).strip()
    if text in ("", "-", "--", "N/A", "n/a"):
        return None
    text = text.split("(")[0]
    text = re.sub(r"[$,%\s]", "", text)
    try:
        return float(text)
    except ValueError:
        return None


def map_headers(headers):
    mapping = {}
    lowered = {h.strip().lower(): h for h in headers}
    for key, names in ALIASES.items():
        for name in names:
            if name in lowered:
                mapping[key] = lowered[name]
                break
    return mapping


def ratio(num, den):
    if num is None or den in (None, 0):
        return None
    return round(num / den, 4)


def derive(c):
    """Derived metrics from a dict of counts. Rates are fractions (0.31 = 31%)."""
    cpa = None
    if c.get("cost") is not None and c.get("policies"):
        cpa = round(c["cost"] / c["policies"], 2)
    return {
        "ctr": ratio(c.get("clicks"), c.get("impressions")),
        "click_to_lead": ratio(c.get("leads"), c.get("clicks")),
        "contact_rate": ratio(c.get("contacted"), c.get("leads")),
        "quote_rate": ratio(c.get("quotes"), c.get("leads")),
        "lead_to_sale": ratio(c.get("policies"), c.get("leads")),
        "quote_to_policy": ratio(c.get("policies"), c.get("quotes")),
        "contacted_to_quote": ratio(c.get("quotes"), c.get("contacted")),
        "cpa": cpa,
    }


def donut(rows, label_key):
    """Lead-mix segments. Largest remainder rounding so dashes sum to exactly 100.0."""
    items = [(r[label_key], r["counts"].get("leads") or 0) for r in rows]
    items = [(name, n) for name, n in items if n > 0]
    total = sum(n for _, n in items)
    if not total:
        return []
    items.sort(key=lambda x: -x[1])
    raw = [n * 1000 / total for _, n in items]  # tenths of a percent
    floors = [math.floor(x) for x in raw]
    short = 1000 - sum(floors)
    for i in sorted(range(len(raw)), key=lambda i: -(raw[i] - floors[i]))[:short]:
        floors[i] += 1
    out, offset = [], 0
    for (name, n), tenths in zip(items, floors):
        out.append({"label": name, "leads": int(n), "dash": tenths / 10, "offset": offset / 10})
        offset += tenths
    return out


def funnel(t):
    """Funnel stages present in the export, their rates, and log-scaled bar widths.

    Rate basis matches the template: Clicks are a share of impressions, Leads a share
    of clicks, and every stage after Leads is a share of Leads (never Clicks).
    Real proportions make the lower stages invisible (82 clicks on 1,782 impressions
    is 4.6%), so widths are log-scaled: order is preserved and every bar is readable.
    `bar_class` is "pre" above the Leads divider and "cv" from Leads down; the last
    stage also gets "end".
    """
    order = [("impressions", "Your ad shown", None), ("clicks", "Clicks", "impressions"),
             ("leads", "Leads", "clicks"), ("contacted", "Contacted", "leads"),
             ("quotes", "Quotes", "leads"), ("policies", "Policies", "leads")]
    stages = [(k, label, base, t[k]) for k, label, base in order if t.get(k)]
    if not stages:
        return []
    top = stages[0][3]
    out = []
    for i, (k, label, base, n) in enumerate(stages):
        if top <= 1:
            width = 100
        else:
            width = FUNNEL_MIN_WIDTH + (100 - FUNNEL_MIN_WIDTH) * math.log(max(n, 1)) / math.log(top)
        cls = "pre" if k in ("impressions", "clicks") else "cv"
        if cls == "cv" and i == len(stages) - 1:
            cls += " end"
        out.append({
            "stage": k, "label": label, "count": int(n),
            "rate": ratio(n, t.get(base)) if base else None,
            "rate_label": f"of {base}" if base else None,
            "bar_class": cls,
            "width": int(round(width)),
        })
    return out


def parse_hour(label):
    """'07 AM' -> 7, '12 PM' -> 12, '12 AM' -> 0, '10 AM ET' -> 10, '19' -> 19. Returns (hour, zone suffix)."""
    m = HOUR_LABEL_RE.match(label or "")
    if not m:
        return None, None
    h = int(m.group(1))
    ampm = (m.group(2) or "").replace(".", "").lower()
    if ampm:
        if not 1 <= h <= 12:
            return None, None
        h = h % 12 + (12 if ampm == "pm" else 0)
    elif not 0 <= h <= 23:
        return None, None
    return h, (m.group(3) or "").lower() or None


def hour_label(h):
    h %= 24
    return f"{h % 12 or 12} {'AM' if h < 12 else 'PM'}"


def zone_info(name):
    if ZoneInfo is None:
        raise SystemExit("Python 3.9+ is required for time zone conversion (zoneinfo).")
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        raise SystemExit(f"Unknown time zone '{name}'. Use an IANA name such as America/Chicago.")


def zone_display(name):
    return ZONE_LABELS.get(name, (name, name))


def detect_source_zone(header, labels):
    """Zone named by the header ('Hour (Eastern)') or a label suffix ('10 AM ET'), else None."""
    hm = re.search(r"\(([^)]+)\)", header or "")
    if hm:
        word = hm.group(1).strip().lower().replace(" time", "")
        if word in ZONE_NAMES:
            return ZONE_NAMES[word]
    suffixes = {parse_hour(l)[1] for l in labels} - {None}
    if len(suffixes) == 1:
        suffix = suffixes.pop()
        if suffix in ZONE_NAMES:
            return ZONE_NAMES[suffix]
    return None


def offsets_for_window(from_name, to_name, start, end):
    """Hour offset (to minus from) on each day of the window, read at noon in the source zone."""
    fz, tz = zone_info(from_name), zone_info(to_name)
    counts, day = Counter(), start
    while day <= end:
        noon = dt.datetime(day.year, day.month, day.day, 12, tzinfo=fz)
        diff = noon.astimezone(tz).utcoffset() - noon.utcoffset()
        counts[int(round(diff.total_seconds() / 3600))] += 1
        day += dt.timedelta(days=1)
    return counts


def bucket(rows, keys):
    out = {}
    for k in keys:
        vals = [r[k] for r in rows if r.get(k) is not None]
        out[k] = round(sum(vals), 2) if vals else None
    return out


def hourly_view(rows, dim, cols, args):
    """Convert, sort, and summarize a by-hour export. Returns (extra keys, warnings) or raises ValueError."""
    warnings = []
    labels = [r[dim] for r in rows]
    parsed = [parse_hour(l)[0] for l in labels]
    bad = [l for l, h in zip(labels, parsed) if h is None]
    if bad:
        raise ValueError(f"unreadable hour labels: {', '.join(bad[:5])}")
    if not args.to_tz:
        raise ValueError("by-hour export: pass --to-tz with the agent's time zone (e.g. America/Chicago); "
                         "GOAL reports hours in Pacific time")
    zone_info(args.to_tz)
    detected = detect_source_zone(dim, labels)
    from_name = detected or args.from_tz
    if detected and args.from_tz_given and detected != args.from_tz:
        warnings.append(f"--from-tz {args.from_tz} ignored: the file is labeled {detected}.")

    today = dt.date.today()
    start = args.period_start or args.period_end or today
    end = args.period_end or args.period_start or today
    if not (args.period_start and args.period_end):
        warnings.append("No --period-start/--period-end: the offset was computed for "
                        f"{start.isoformat()}. Pass the export window so daylight saving time is handled.")
    if end < start:
        raise ValueError("--period-end is before --period-start")
    counts = offsets_for_window(from_name, args.to_tz, start, end)
    offset = counts.most_common(1)[0][0]
    if len(counts) > 1:
        detail = ", ".join(f"{n} days at {o:+d}h" for o, n in sorted(counts.items()))
        warnings.append(f"The offset from {from_name} to {args.to_tz} changes inside the window ({detail}). "
                        f"Converted with {offset:+d}h; hours on the other side of the change are off by one. "
                        "Split the window at the DST change for exact hours.")
    converted = offset != 0 or from_name != args.to_tz
    if detected and offset == 0:
        converted = False  # already in the target zone: never convert twice

    keys = ["searches", "impressions", "clicks", "leads", "calls", "contacted", "quotes", "policies", "cost"]
    items, crossed = [], []
    for r, h in zip(rows, parsed):
        c = r["counts"]
        local = h + offset
        if (local >= 24 or local < 0) and (c.get("leads") or 0) > 0:
            crossed.append(f"{r[dim]} -> {hour_label(local)} ({int(c.get('leads') or 0)} leads, "
                           f"{'next' if local >= 24 else 'previous'} day)")
        items.append({"hour": local % 24, "source_label": r[dim], **{k: c.get(k) for k in keys if k in cols}})
    if crossed:
        warnings.append("Conversion moves hours across midnight: " + "; ".join(crossed) +
                        ". The day-of-week export is on Pacific calendar days; say so wherever days are shown.")
    items.sort(key=lambda x: x["hour"])

    floor = args.min_leads
    max_leads = max((x.get("leads") or 0) for x in items) or 0
    total_leads = sum((x.get("leads") or 0) for x in items)
    thin = []
    for x in items:
        n = x.get("leads") or 0
        x["label"] = hour_label(x["hour"])
        x["contact_rate"] = ratio(x.get("contacted"), x.get("leads"))
        x["quote_rate"] = ratio(x.get("quotes"), x.get("leads"))
        x["share_of_leads"] = ratio(n, total_leads)
        x["width"] = 0 if not n or not max_leads else max(HOUR_MIN_WIDTH, int(round(100 * n / max_leads)))
        x["below_floor"] = n < floor
        if n < floor:
            thin.append(f"{x['label']} ({int(n)})")
    if thin:
        warnings.append(f"Hours under {floor} leads: {', '.join(thin)}. Do not act on a single thin hour; "
                        "use blocks[] or a longer window.")

    if "contacted" not in cols:
        warnings.append("No Contacted/Quote/Bound columns: contact rate by hour is not available. "
                        "Use leads, calls, and spend by hour. Never show a 0% contact rate for this file.")
    over = [x["label"] for x in items
            if (x.get("contacted") or 0) > (x.get("leads") or 0) or (x.get("quotes") or 0) > (x.get("leads") or 0)]
    if over:
        warnings.append(f"Contacted or quotes exceed leads in {', '.join(over)}: some outcomes are timestamped when "
                        "logged, not when the lead arrived. Treat hourly contact and quote rates as directional.")

    blocks, cur = [], []
    for x in items:
        cur.append(x)
        if sum((y.get("leads") or 0) for y in cur) >= floor:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    block_out = []
    for b in blocks:
        agg = bucket(b, [k for k in keys if k in cols])
        first, last = b[0]["hour"], b[-1]["hour"]
        block_out.append({
            "label": hour_label(first) if first == last else f"{hour_label(first)} to {hour_label(last + 1)}",
            "hours": [y["label"] for y in b],
            **agg,
            "contact_rate": ratio(agg.get("contacted"), agg.get("leads")),
            "quote_rate": ratio(agg.get("quotes"), agg.get("leads")),
            "below_floor": (agg.get("leads") or 0) < floor,
        })

    name, abbr = zone_display(args.to_tz)
    extra = {
        "time_zone": {"source": from_name, "target": args.to_tz, "offset_hours": offset,
                      "converted": converted, "label": name, "abbr": abbr,
                      "window": [start.isoformat(), end.isoformat()]},
        "min_leads": floor,
        "hourly": items,
        "blocks": block_out,
    }
    return extra, warnings


def process(path, args=None):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows_raw = list(reader)
    if not headers:
        return {"file": path, "error": "no header row"}
    dim = headers[0]
    cols = map_headers(headers)
    rows, export_total = [], None
    for r in rows_raw:
        label = (r.get(dim) or "").strip()
        counts = {k: parse_number(r.get(h)) for k, h in cols.items()}
        if label.lower() in TOTAL_LABELS:
            export_total = counts
            continue
        rows.append({dim: label, "counts": counts, "metrics": derive(counts)})

    totals = {}
    for k in cols:
        if k == "avg_pos":
            continue
        vals = [r["counts"].get(k) for r in rows if r["counts"].get(k) is not None]
        totals[k] = round(sum(vals), 2) if vals else None

    warnings = []
    if export_total:
        for k, v in totals.items():
            ev = export_total.get(k)
            if v is not None and ev is not None and abs(v - ev) > max(1, 0.01 * ev):
                warnings.append(f"Summed {k} ({v}) differs from the export's Total row ({ev}).")

    needed = {
        "contacted": "Contact rate (no Contacted column; omit the card and funnel stage)",
        "quotes": "Quote rate",
        "policies": "CPA and policies bound",
        "cost": "CPA",
        "calls": "Inbound calls",
        "impressions": "Funnel top stage",
    }
    missing = [msg for k, msg in needed.items() if k not in cols]
    if "policies" in cols and not totals.get("policies"):
        warnings.append("Zero policies recorded: CPA cannot be shown. Do not estimate it.")

    result = {
        "file": path,
        "dimension": dim,
        "columns_found": cols,
        "rows": rows,
        "totals": {"counts": totals, "metrics": derive(totals)},
        "donut": donut(rows, dim) if len(rows) > 1 else [],
        "funnel": funnel(totals),
        "missing": missing,
        "warnings": warnings,
    }
    if dim.strip().lower().startswith("hour"):
        try:
            extra, hour_warnings = hourly_view(rows, dim, cols, args)
        except ValueError as e:
            return {"file": path, "error": str(e)}
        result["donut"] = []  # a lead-mix donut by hour is not a report visual
        result.update(extra)
        result["warnings"] = warnings + hour_warnings
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--out", help="write JSON here instead of stdout")
    ap.add_argument("--to-tz", help="by-hour files: the agent's IANA time zone (required), e.g. America/Chicago")
    ap.add_argument("--from-tz", default=None,
                    help=f"by-hour files: the export's zone when the file is not labeled (default {DEFAULT_FROM_TZ})")
    ap.add_argument("--period-start", type=dt.date.fromisoformat, help="first day of the export window, YYYY-MM-DD")
    ap.add_argument("--period-end", type=dt.date.fromisoformat, help="last day of the export window, YYYY-MM-DD")
    ap.add_argument("--min-leads", type=int, default=30, help="by-hour files: sample floor per hour or block (default 30)")
    args = ap.parse_args()
    args.from_tz_given = args.from_tz is not None
    args.from_tz = args.from_tz or DEFAULT_FROM_TZ
    results = []
    for p in args.files:
        try:
            results.append(process(p, args))
        except FileNotFoundError:
            results.append({"file": p, "error": "file not found"})
        except UnicodeDecodeError:
            results.append({"file": p, "error": "not a UTF-8 CSV; re-export from GOAL"})
    text = json.dumps(results, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)
        print(f"wrote {args.out}")
    else:
        print(text)
    if any("error" in r for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
