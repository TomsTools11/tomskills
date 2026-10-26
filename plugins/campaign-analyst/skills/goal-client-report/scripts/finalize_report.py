#!/usr/bin/env python3
"""Make a filled report self-contained and check it before delivery.

Usage:
    python3 finalize_report.py REPORT.html [--out FINAL.html] [--check-only]

1. Inlines every assets/goal-wordmark-*.png reference (black for light mode, white for
   dark mode) as a base64 data URI, so the single HTML file carries its own logos
   (unless --check-only).
2. Adds any missing piece of the light/dark toggle (theme script, theme-aware selectors,
   toggle CSS, toggle button), copied from templates/structured-dashboard.html, and lists
   what it added under "repaired" (unless --check-only).
3. Runs the delivery checks (including, when the optional Performance by Hour section is
   present, a time zone label in its sub-header and hours in clock order) and prints JSON:
   {"ok": bool, "errors": [...], "warnings": [...], "repaired": [...]}.
   Exit code 1 when there are errors. Fix every error and run again until ok is true.
"""
import argparse
import base64
import json
import re
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
ASSETS = SKILL / "assets"
TEMPLATE = SKILL / "templates" / "structured-dashboard.html"
FOOTNOTE = "All conversion metrics calculated based on Leads, not Clicks."

# Fingerprints of the template's worked example. Two or more present = numbers not swapped.
EXAMPLE_MARKERS = ["1,782", "$334", "22 of 30 days", "$50 to $95", "June 1–30", "41 of 59 leads", "38 of 59 leads"]

BANNED = [  # (regex, message) -> errors
    (r"\bCPL\b|cost[\s-]per[\s-]lead", "Cost per lead appears. Client reports use CPA, never CPL."),
    (r"why goal|never resold|they chose you|chose you", "Sales framing appears. Reports to active accounts do not sell."),
    (r"\byou expected\b|\bfrustrat|\bdisappoint", "Copy references the client's expectations or emotions."),
]
CAUTION = [  # (regex, message) -> warnings
    (r"\b(?:schedule|bids?)\b[^.%]{0,40}?\b\d{1,3}%",
     "Possible schedule or bid percentage. Describe schedule changes by direction and hours, never by percentage."),
    (r"\bexclusive\b", "'Exclusive' appears. Keep it only if the user asked for exclusivity framing."),
    (r"\bprojected\b|\bwe expect\b|\bshould result\b|\bestimated\b|\bwill (?:increase|improve|double)",
     "Possible projection or estimated result. Client reports state actuals only."),
    (r"\bexcellent\b|\bgreat\b|\bimpressive\b|\bstrong\b|\bdoing its job\b",
     "Possible praise or interpretation. Notes state metrics only."),
]


def inline_logos(html):
    def repl(m):
        name = m.group(2)
        f = ASSETS / name
        if not f.exists():
            return m.group(0)
        data = base64.b64encode(f.read_bytes()).decode()
        return f'{m.group(1)}data:image/png;base64,{data}"'
    return re.sub(r'(src=")(?:\.\./|\./)?(?:[^"]*/)?assets/(goal-wordmark-[a-z]+\.png)"', repl, html)


# ---------- Light/dark toggle ----------
# The template is the single source of truth for the toggle's script, CSS, and button.
THEME_SCRIPT_RE = re.compile(r"<script>\s*/\* Theme:.*?</script>", re.S)
TOGGLE_CSS_RE = re.compile(r"/\* -+ Theme toggle.*?@media print\{ \.theme-toggle\{display:none !important;\} \}", re.S)
TOGGLE_BUTTON_RE = re.compile(r'<button class="theme-toggle".*?</button>', re.S)
# Selector upgrades that let data-theme on <html> (set by the toggle) drive the tokens.
SELECTOR_FIXES = [
    ('.g[data-theme="dark"]{', '.g[data-theme="dark"],:root[data-theme="dark"] .g{', ':root[data-theme="dark"] .g'),
    ('  .g[data-theme="system"]{', '  :root:not([data-theme]) .g[data-theme="system"]{', ':root:not([data-theme]) .g[data-theme="system"]'),
    ('  .g,.g[data-theme]{', '  .g,.g[data-theme],:root[data-theme] .g{', ':root[data-theme] .g{'),
]


def template_parts():
    tpl = TEMPLATE.read_text(encoding="utf-8")
    parts = {}
    for key, rx in (("script", THEME_SCRIPT_RE), ("css", TOGGLE_CSS_RE), ("button", TOGGLE_BUTTON_RE)):
        m = rx.search(tpl)
        if not m:
            raise SystemExit(f"Template is missing the theme {key}; restore templates/structured-dashboard.html.")
        parts[key] = m.group(0)
    return parts


def ensure_theme_toggle(html):
    """Add any missing toggle piece from the template. Returns (html, repaired)."""
    repaired = []
    parts = template_parts()
    head = re.search(r"<head\b[^>]*>.*?</head>", html, re.S | re.I)
    if head and not THEME_SCRIPT_RE.search(head.group(0)):
        charset = re.search(r'<meta charset="[^"]*">\s*\n?', html, re.I)
        at = charset.end() if charset else html.lower().index("<head>") + len("<head>")
        html = html[:at] + parts["script"] + "\n" + html[at:]
        repaired.append("Added the theme script at the top of <head>.")
    for old, new, marker in SELECTOR_FIXES:
        if marker not in html and old in html:
            html = html.replace(old, new, 1)
            repaired.append(f"Made {old.strip()} follow the toggle.")
    if not TOGGLE_CSS_RE.search(html) and "</style>" in html:
        at = html.index("</style>")
        html = html[:at] + "\n" + parts["css"] + "\n" + html[at:]
        repaired.append("Added the theme toggle CSS.")
    if not TOGGLE_BUTTON_RE.search(html) and "</body>" in html:
        at = html.rindex("</body>")
        before = html[:at]
        script_tail = re.search(r"\n<script>(?:(?!</script>).)*</script>\s*$", before, re.S)
        if script_tail:  # keep the button above the page's closing script, as in the template
            at = script_tail.start() + 1
        html = html[:at] + parts["button"] + "\n" + html[at:]
        repaired.append("Added the light/dark toggle button.")
    return html, repaired


def check_theme(html):
    errors = []
    head = re.search(r"<head\b[^>]*>(.*?)</head>", html, re.S | re.I)
    head_html = head.group(1) if head else ""
    script = THEME_SCRIPT_RE.search(head_html)
    if not script:
        errors.append("Theme script missing from <head>. The report must open in the viewer's system theme and support the toggle.")
    else:
        if "goalToggleTheme" not in script.group(0) or "goal-theme" not in script.group(0):
            errors.append("Theme script is altered. Copy it unchanged from the template.")
        style_at = head_html.find("<style")
        link_at = head_html.find("<link")
        firsts = [i for i in (style_at, link_at) if i >= 0]
        if firsts and script.start() > min(firsts):
            errors.append("Theme script must come before the stylesheets in <head>, or the page flashes the wrong theme.")
    for _, _, marker in SELECTOR_FIXES:
        if marker not in html:
            errors.append(f"CSS selector {marker} is missing, so the toggle cannot switch the colors.")
    if not TOGGLE_CSS_RE.search(html):
        errors.append("Theme toggle CSS missing (including the rule that hides it in print).")
    buttons = TOGGLE_BUTTON_RE.findall(html)
    if not buttons:
        errors.append("Light/dark toggle button missing before </body>.")
    elif len(buttons) > 1:
        errors.append(f"{len(buttons)} toggle buttons found. Keep exactly one.")
    elif 'onclick="goalToggleTheme()"' not in buttons[0] or "i-moon" not in buttons[0] or "i-sun" not in buttons[0]:
        errors.append("Toggle button is altered. Copy it unchanged from the template.")
    return errors


# ---------- Optional Performance by Hour section ----------
ZONE_LABEL_RE = re.compile(r"\b(?:Eastern|Central|Mountain|Pacific|Arizona|Alaska|Hawaii)(?: Standard| Daylight)? Time\b"
                           r"|\b(?:ET|CT|MT|PT|EST|EDT|CST|CDT|MST|MDT|PST|PDT|AKT|HT|HST)\b")
HOUR_LAB_RE = re.compile(r"^(\d{1,2})(?::00)?\s*([AaPp])\.?[Mm]\.?$")


def clock_hour(label):
    m = HOUR_LAB_RE.match(label.strip())
    if not m:
        return None
    h = int(m.group(1))
    if not 1 <= h <= 12:
        return None
    return h % 12 + (12 if m.group(2).lower() == "p" else 0)


def check_hourly(html):
    """Errors for the optional hourly section: time zone named in its sub-header, hours in clock order."""
    errors = []
    sec = re.search(r'<section\b[^>]*data-section="hourly"[^>]*>.*?</section>', html, re.S)
    if not sec:
        return errors
    sub = re.search(r'<div class="bhead">.*?<p>(.*?)</p>', sec.group(0), re.S)
    if not sub or not ZONE_LABEL_RE.search(visible_text(sub.group(1))):
        errors.append('Performance by Hour has no time zone in its sub-header. Add the agent\'s zone '
                      '(e.g. "Sept 1-30 · Central Time"); hours must be agent local time.')
    labels = [visible_text(l).strip() for l in re.findall(r'<div class="lab">(.*?)</div>', sec.group(0), re.S)]
    hours = [clock_hour(l) for l in labels]
    bad = [l for l, h in zip(labels, hours) if h is None]
    if bad:
        errors.append(f"Performance by Hour has hour labels that are not clock hours: {', '.join(bad[:5])}.")
    elif any(b <= a for a, b in zip(hours, hours[1:])):
        errors.append("Performance by Hour rows are out of clock order. Sort by hour (the export sorts by volume).")
    return errors


def visible_text(fragment):
    fragment = re.sub(r"<!--.*?-->", " ", fragment, flags=re.S)
    fragment = re.sub(r"<(script|style)\b.*?</\1>", " ", fragment, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", fragment)
    for a, b in (("&nbsp;", " "), ("&amp;", "&"), ("&middot;", "·"), ("&ndash;", "–"), ("&mdash;", "—")):
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text)


def check(html):
    errors, warnings = [], []
    text = visible_text(html)
    body = re.sub(r"<head\b.*?</head>", " ", html, flags=re.S | re.I)

    leftover = sorted(set(re.findall(r"\[[A-Z][A-Za-z ,/&.-]{1,40}\]", visible_text(body))))
    if leftover:
        errors.append(f"Unfilled placeholders: {', '.join(leftover)}")
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    if title and "[" in title.group(1):
        errors.append(f"Unfilled placeholder in <title>: {title.group(1).strip()}")

    hits = [m for m in EXAMPLE_MARKERS if m in text]
    if len(hits) >= 2:
        errors.append(f"Worked-example figures still present: {', '.join(hits)}")

    if re.search(r'src="(?:\.\./|\./)?[^"]*assets/goal-wordmark', html):
        errors.append("Logo still points at ../assets/. Run without --check-only to inline it.")

    if FOOTNOTE not in text:
        errors.append(f'Footnote missing: "{FOOTNOTE}"')

    for pattern, msg in BANNED:
        if re.search(pattern, text, re.I):
            errors.append(msg)
    for pattern, msg in CAUTION:
        found = sorted(set(m.group(0) for m in re.finditer(pattern, text, re.I)))
        if found:
            warnings.append(f"{msg} Found: {', '.join(found)}")
    if "—" in text:
        warnings.append("Em dash in visible text. Rewrite with a comma, period, colon, or '|'.")

    # Client name must not appear in body copy (header, sidebar and footer are fine).
    agency = re.search(r'<aside class="side">.*?<h1>(.*?)</h1>', html, re.S)
    main = re.search(r"<main\b.*?</main>", html, re.S)
    if agency and main:
        name = visible_text(agency.group(1)).strip()
        main_body = re.sub(r'<div class="mfoot">.*?</div>', " ", main.group(0), flags=re.S)
        if name and not name.startswith("[") and name.lower() in visible_text(main_body).lower():
            errors.append(f'Agency name "{name}" appears in body copy. Keep it in the sidebar and footer only.')

    # Light/dark: the report must follow the viewer's system setting.
    if not re.search(r'<div class="g" data-theme="system"', html):
        errors.append('The root <div class="g"> must keep data-theme="system" so the report follows light/dark mode.')
    errors.extend(check_theme(html))
    # Hard-coded colors in the body do not switch with the theme.
    body_only = re.search(r"<body\b.*?</body>", html, re.S)
    if body_only:
        hexes = sorted(set(re.findall(r'style="[^"]*#[0-9a-fA-F]{3,6}', body_only.group(0))))
        if hexes or re.search(r'stroke="#[0-9a-fA-F]{3,6}"', body_only.group(0)):
            errors.append("Hard-coded hex color in the body. Use the theme variables (var(--s1), var(--s2), var(--s3)) so dark mode works.")

    # Donut segments: dashes sum to 100, offsets cumulative.
    segs = re.findall(r'<circle class="seg"[^>]*>', html)
    if segs:
        dashes, offsets = [], []
        for s in segs:
            d = re.search(r'data-dash="([\d.]+)"', s)
            o = re.search(r'data-offset="([\d.]+)"', s)
            dashes.append(float(d.group(1)) if d else None)
            offsets.append(float(o.group(1)) if o else 0.0)
        if None in dashes:
            errors.append("A donut segment has no data-dash value.")
        else:
            if abs(sum(dashes) - 100) > 0.2:
                errors.append(f"Donut data-dash values sum to {sum(dashes):.1f}, not 100.")
            running = 0.0
            for d, o in zip(dashes, offsets):
                if abs(o - running) > 0.2:
                    errors.append(f"Donut data-offset {o} should be {running:.1f} (running total of earlier segments).")
                    break
                running += d
        legend = re.findall(r'<span class="vl">([\d,]+)</span>', html)
        center = re.search(r'<div class="center"><div class="n">([\d,]+)</div>', html)
        if legend and center:
            if sum(int(v.replace(",", "")) for v in legend) != int(center.group(1).replace(",", "")):
                errors.append("Donut legend values do not add up to the center total.")

    for w in re.findall(r'data-w="([^"]*)"', html):
        try:
            if not 0 <= float(w) <= 100:
                raise ValueError
        except ValueError:
            errors.append(f'Bar width data-w="{w}" must be a number from 0 to 100.')

    ids = set(re.findall(r'<section[^>]*\bid="([^"]+)"', html))
    for href in re.findall(r'<nav\b.*?</nav>', html, re.S)[:1]:
        for target in re.findall(r'href="#([^"]+)"', href):
            if target not in ids:
                errors.append(f"Sidebar nav links to #{target}, but no section has that id.")

    errors.extend(check_hourly(html))
    nums = re.findall(r'<div class="bhead"><span class="ix">(\d+)</span>', html)
    if nums and [int(n) for n in nums] != list(range(1, len(nums) + 1)):
        warnings.append(f"Section numbers run {', '.join(nums)}. Renumber them 01 to {len(nums):02d} "
                        "(and the sidebar nav) after removing a section.")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report")
    ap.add_argument("--out", help="write the finalized file here (default: overwrite the input)")
    ap.add_argument("--check-only", action="store_true", help="run checks without inlining logos or adding the toggle")
    args = ap.parse_args()

    src = Path(args.report)
    html = src.read_text(encoding="utf-8")
    repaired = []
    if not args.check_only:
        html = inline_logos(html)
        html, repaired = ensure_theme_toggle(html)
        dest = Path(args.out) if args.out else src
        dest.write_text(html, encoding="utf-8")
    errors, warnings = check(html)
    print(json.dumps({"ok": not errors, "errors": errors, "warnings": warnings, "repaired": repaired}, indent=2))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
