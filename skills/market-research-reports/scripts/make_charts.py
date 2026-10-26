#!/usr/bin/env python3
"""Render market-report figures from a JSON spec of researched numbers.

Every chart is drawn from data in the spec, never invented. The script
validates the whole spec first and renders nothing if any chart has an error.

Usage:
    python make_charts.py data/charts.json --out figures/
    python make_charts.py data/charts.json --validate-only

Spec format and one example per chart type: references/chart_specs.md
Requires: matplotlib (pip install matplotlib --break-system-packages)
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import matplotlib
    matplotlib.use("Agg")  # headless rendering, no display in the sandbox
    import matplotlib.pyplot as plt
    from matplotlib.patches import Circle, FancyBboxPatch
except ImportError:
    sys.exit("matplotlib is missing. Run: pip install matplotlib --break-system-packages")

# Colors mirror assets/market_research.sty so figures match the document.
NAVY = "#003366"      # primaryblue
MIDBLUE = "#336699"   # secondaryblue
LIGHTBLUE = "#ADD8E6" # lightblue
GRAY = "#757575"      # mediumgray
# Okabe-Ito palette (chart1-chart7 in the .sty): readable with color-vision deficiency.
SERIES = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#56B4E9", "#D55E00", "#F0E442"]
RATING = {"low": "#009E73", "medium": "#E69F00", "high": "#D55E00"}

DPI = 300            # print resolution required by the report quality bar
WIDE = (10, 5.5)     # fits \textwidth at 0.9 scale on letter paper
SQUARE = (7.5, 7.5)  # for matrices and concentric diagrams

FORCES = ["new_entrants", "supplier_power", "buyer_power", "substitutes", "rivalry"]
FORCE_TITLES = {
    "new_entrants": "Threat of New Entrants",
    "supplier_power": "Supplier Power",
    "buyer_power": "Buyer Power",
    "substitutes": "Threat of Substitutes",
    "rivalry": "Competitive Rivalry",
}


# ---------------------------------------------------------------- validation

def _num_list(c, key, errs, where):
    v = c.get(key)
    if not isinstance(v, list) or not v or not all(isinstance(x, (int, float)) for x in v):
        errs.append(f"{where}: '{key}' must be a non-empty list of numbers")
        return None
    return v


def validate(spec):
    errs = []
    charts = spec.get("charts")
    if not isinstance(charts, list) or not charts:
        return ["spec: top-level 'charts' must be a non-empty list"]
    seen = set()
    for i, c in enumerate(charts):
        where = f"charts[{i}] ({c.get('file', 'no file')})"
        t = c.get("type")
        if t not in RENDERERS:
            errs.append(f"{where}: unknown type '{t}'. Valid types: {', '.join(sorted(RENDERERS))}")
            continue
        f = c.get("file", "")
        if not f.endswith(".png"):
            errs.append(f"{where}: 'file' must be a .png name, e.g. market_growth_trajectory.png")
        if f in seen:
            errs.append(f"{where}: duplicate file name")
        seen.add(f)
        if not str(c.get("source", "")).strip():
            errs.append(f"{where}: 'source' is required (cite the research note or say 'Team analysis')")
        if not str(c.get("title", "")).strip():
            errs.append(f"{where}: 'title' is required")

        if t == "growth":
            years = _num_list(c, "years", errs, where)
            vals = _num_list(c, "values", errs, where)
            if years and vals and len(years) != len(vals):
                errs.append(f"{where}: 'years' has {len(years)} items but 'values' has {len(vals)}")
            fp = c.get("first_projected_year")
            if years and fp is not None and fp not in years:
                errs.append(f"{where}: first_projected_year {fp} is not in 'years'")
        elif t == "tam_sam_som":
            try:
                tam, sam, som = float(c["tam"]), float(c["sam"]), float(c["som"])
                if not tam >= sam >= som > 0:
                    errs.append(f"{where}: need tam >= sam >= som > 0, got {tam}, {sam}, {som}")
            except (KeyError, TypeError, ValueError):
                errs.append(f"{where}: 'tam', 'sam', 'som' must all be numbers")
        elif t in ("pie", "bar"):
            labels = c.get("labels")
            vals = _num_list(c, "values", errs, where)
            if not isinstance(labels, list) or (vals and len(labels) != len(vals)):
                errs.append(f"{where}: 'labels' must be a list the same length as 'values'")
            if t == "pie" and vals:
                if any(v < 0 for v in vals):
                    errs.append(f"{where}: pie values cannot be negative")
                if c.get("percent") and abs(sum(vals) - 100) > 1.5:
                    errs.append(f"{where}: percent shares sum to {sum(vals):.1f}, expected ~100. "
                                "Add an 'Other' slice or fix the figures")
        elif t == "matrix":
            pts = c.get("points")
            if not isinstance(pts, list) or not pts:
                errs.append(f"{where}: 'points' must be a non-empty list")
            else:
                for j, p in enumerate(pts):
                    if not all(isinstance(p.get(k), (int, float)) for k in ("x", "y")) or "label" not in p:
                        errs.append(f"{where}: points[{j}] needs 'label', numeric 'x' and 'y'")
                    elif not (0 <= p["x"] <= 10 and 0 <= p["y"] <= 10):
                        errs.append(f"{where}: points[{j}] '{p['label']}' x/y must be on the 0-10 scale")
            for k in ("x_label", "y_label"):
                if not c.get(k):
                    errs.append(f"{where}: '{k}' is required")
        elif t == "heatmap":
            risks = c.get("risks")
            if not isinstance(risks, list) or not risks:
                errs.append(f"{where}: 'risks' must be a non-empty list")
            else:
                for j, r in enumerate(risks):
                    if r.get("probability") not in range(1, 6) or r.get("impact") not in range(1, 6):
                        errs.append(f"{where}: risks[{j}] probability and impact must be integers 1-5")
        elif t == "five_forces":
            forces = c.get("forces", {})
            for k in FORCES:
                rating = str(forces.get(k, {}).get("rating", "")).lower()
                if rating not in RATING:
                    errs.append(f"{where}: forces.{k}.rating must be Low, Medium or High")
        elif t == "lines":
            x = _num_list(c, "x", errs, where)
            series = c.get("series")
            if not isinstance(series, dict) or not series:
                errs.append(f"{where}: 'series' must be an object of name -> list of numbers")
            elif x:
                for name, vals in series.items():
                    if len(vals) != len(x):
                        errs.append(f"{where}: series '{name}' has {len(vals)} points, x has {len(x)}")
        elif t == "gantt":
            tasks = c.get("tasks")
            if not isinstance(tasks, list) or not tasks:
                errs.append(f"{where}: 'tasks' must be a non-empty list")
            else:
                for j, tk in enumerate(tasks):
                    s, e = tk.get("start"), tk.get("end")
                    if not isinstance(s, (int, float)) or not isinstance(e, (int, float)) or e <= s:
                        errs.append(f"{where}: tasks[{j}] needs numeric start < end")
        elif t == "timeline":
            ev = c.get("events")
            if not isinstance(ev, list) or not ev or not all("label" in e and "when" in e for e in ev):
                errs.append(f"{where}: 'events' must be a list of {{'when', 'label'}}")
        elif t in ("grid", "flow"):
            key = "cells" if t == "grid" else "steps"
            items = c.get(key)
            if not isinstance(items, list) or not items or not all("title" in x for x in items):
                errs.append(f"{where}: '{key}' must be a list of {{'title', 'items'}}")
    return errs


# ---------------------------------------------------------------- renderers

def _finish(fig, ax, c, out):
    if ax is not None:
        ax.set_title(c["title"], fontsize=13, fontweight="bold", color=NAVY, loc="left")
    fig.tight_layout()
    fig.savefig(out, dpi=DPI, facecolor="white")
    plt.close(fig)


def _clean(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", alpha=0.25)


def r_growth(c, out):
    fig, ax = plt.subplots(figsize=WIDE)
    fp = c.get("first_projected_year")
    colors = [LIGHTBLUE if fp is not None and y >= fp else NAVY for y in c["years"]]
    bars = ax.bar([str(y) for y in c["years"]], c["values"], color=colors)
    ax.bar_label(bars, fmt=c.get("value_format", "%.1f"), fontsize=8)
    ax.set_ylabel(c.get("unit", ""))
    if c.get("cagr_note"):
        ax.text(0.01, 0.95, c["cagr_note"], transform=ax.transAxes, fontsize=10, color=NAVY,
                fontweight="bold", va="top")
    if fp is not None:
        ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=NAVY),
                           plt.Rectangle((0, 0), 1, 1, color=LIGHTBLUE)],
                  labels=["Actual", "Projected"], frameon=False, loc="upper center")
    _clean(ax)
    _finish(fig, ax, c, out)


def r_tam_sam_som(c, out):
    fig, ax = plt.subplots(figsize=SQUARE)
    unit = c.get("unit", "")
    tam, sam, som = float(c["tam"]), float(c["sam"]), float(c["som"])
    # Radii scale with sqrt(value) so circle area is proportional to market size,
    # floored so a tiny SOM stays legible.
    r = lambda v: max((v / tam) ** 0.5, 0.18)
    for v, col, name, y in ((tam, NAVY, "TAM", 0.82), (sam, MIDBLUE, "SAM", None), (som, "#56B4E9", "SOM", None)):
        rad = r(v)
        ax.add_patch(Circle((0, rad - 1), rad, color=col))
        ax.text(0, 2 * rad - 1 - 0.12, f"{name}\n{v:,.1f} {unit}", ha="center", va="top",
                color="white", fontsize=12, fontweight="bold")
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_aspect("equal")
    ax.axis("off")
    _finish(fig, ax, c, out)


def r_pie(c, out):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.pie(c["values"], labels=c["labels"], colors=SERIES * 3, startangle=90, counterclock=False,
           autopct="%1.1f%%", pctdistance=0.78, wedgeprops={"width": 0.45, "edgecolor": "white"},
           textprops={"fontsize": 9})
    if c.get("center_text"):
        ax.text(0, 0, c["center_text"], ha="center", va="center", fontsize=12, fontweight="bold", color=NAVY)
    ax.axis("equal")
    _finish(fig, ax, c, out)


def r_bar(c, out):
    fig, ax = plt.subplots(figsize=WIDE)
    pairs = sorted(zip(c["values"], c["labels"])) if c.get("sort", True) else list(zip(c["values"], c["labels"]))
    vals, labels = [p[0] for p in pairs], [p[1] for p in pairs]
    bars = ax.barh(labels, vals, color=SERIES[0])
    ax.bar_label(bars, fmt=c.get("value_format", "%.1f"), padding=3, fontsize=9)
    ax.set_xlabel(c.get("axis_label", ""))
    ax.spines[["top", "right"]].set_visible(False)
    _finish(fig, ax, c, out)


def r_matrix(c, out):
    fig, ax = plt.subplots(figsize=SQUARE)
    ax.axhline(5, color=GRAY, lw=0.8)
    ax.axvline(5, color=GRAY, lw=0.8)
    q = c.get("quadrants")  # [top-left, top-right, bottom-left, bottom-right]
    if q and len(q) == 4:
        for (x, y), txt in zip(((0.3, 9.7), (9.7, 9.7), (0.3, 0.3), (9.7, 0.3)), q):
            ax.text(x, y, txt, ha="left" if x < 5 else "right", va="top" if y > 5 else "bottom",
                    fontsize=10, color=GRAY, fontweight="bold")
    for i, p in enumerate(c["points"]):
        size = 200 + 1800 * float(p.get("size", 0.3))  # size is 0-1 relative weight
        ax.scatter(p["x"], p["y"], s=size, color=SERIES[i % len(SERIES)], alpha=0.75, edgecolor="white")
        ax.annotate(p["label"], (p["x"], p["y"]), xytext=(0, -14 - size ** 0.5 / 2),
                    textcoords="offset points", ha="center", fontsize=8)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_xlabel(c["x_label"])
    ax.set_ylabel(c["y_label"])
    ax.set_xticks([])
    ax.set_yticks([])
    _finish(fig, ax, c, out)


def r_heatmap(c, out):
    fig, ax = plt.subplots(figsize=SQUARE)
    for p in range(1, 6):
        for i in range(1, 6):
            score = p * i  # 1-25; thresholds below match the risk register bands
            col = "#C8E6C9" if score <= 4 else "#FFF3B0" if score <= 9 else "#FFD8A8" if score <= 15 else "#F8B4B4"
            ax.add_patch(plt.Rectangle((i - 0.5, p - 0.5), 1, 1, color=col, ec="white"))
    cells = {}
    for r in c["risks"]:
        cells.setdefault((r["impact"], r["probability"]), []).append(r["label"])
    for (i, p), labels in cells.items():
        ax.text(i, p, "\n".join(labels), ha="center", va="center", fontsize=7, wrap=True)
    ticks = ["Very low", "Low", "Moderate", "High", "Very high"]
    ax.set_xticks(range(1, 6), ticks, fontsize=8)
    ax.set_yticks(range(1, 6), ticks, fontsize=8)
    ax.set_xlabel("Impact")
    ax.set_ylabel("Probability")
    ax.set_xlim(0.5, 5.5)
    ax.set_ylim(0.5, 5.5)
    _finish(fig, ax, c, out)


def _box(ax, x, y, w, h, title, body, color):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.01",
                                fc="white", ec=color, lw=2))
    ax.text(x, y + h / 2 - 0.04, title, ha="center", va="top", fontsize=9, fontweight="bold", color=color)
    if body:
        ax.text(x, y + h / 2 - 0.14, body, ha="center", va="top", fontsize=7.5, color="#424242", wrap=True)


def r_five_forces(c, out):
    fig, ax = plt.subplots(figsize=(9, 8))
    pos = {"new_entrants": (0.5, 0.86), "supplier_power": (0.15, 0.5), "rivalry": (0.5, 0.5),
           "buyer_power": (0.85, 0.5), "substitutes": (0.5, 0.14)}
    for k, (x, y) in pos.items():
        f = c["forces"][k]
        rating = f["rating"].capitalize()
        body = "\n".join(f"- {s}" for s in f.get("factors", [])[:3])
        _box(ax, x, y, 0.28, 0.24, f"{FORCE_TITLES[k]}\n({rating})", body, RATING[rating.lower()])
        if k != "rivalry":
            ax.annotate("", xy=(0.5 + (x - 0.5) * 0.45, 0.5 + (y - 0.5) * 0.45),
                        xytext=(0.5 + (x - 0.5) * 0.62, 0.5 + (y - 0.5) * 0.62),
                        arrowprops={"arrowstyle": "->", "color": GRAY, "lw": 1.5})
    ax.set_xlim(-0.03, 1.03)  # room for the side boxes' borders
    ax.set_ylim(-0.03, 1.03)
    ax.axis("off")
    _finish(fig, ax, c, out)


def r_lines(c, out):
    fig, ax = plt.subplots(figsize=WIDE)
    for i, (name, vals) in enumerate(c["series"].items()):
        ax.plot([str(x) for x in c["x"]], vals, marker="o", lw=2, color=SERIES[i % len(SERIES)], label=name)
    ax.set_ylabel(c.get("axis_label", ""))
    ax.legend(frameon=False)
    _clean(ax)
    _finish(fig, ax, c, out)


def r_gantt(c, out):
    tasks = c["tasks"]
    fig, ax = plt.subplots(figsize=(10, 0.5 * len(tasks) + 1.5))
    groups = list(dict.fromkeys(t.get("group", "") for t in tasks))
    for i, t in enumerate(tasks):
        col = SERIES[groups.index(t.get("group", "")) % len(SERIES)]
        ax.barh(i, t["end"] - t["start"], left=t["start"], color=col, height=0.6)
    ax.set_yticks(range(len(tasks)), [t["label"] for t in tasks], fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel(c.get("time_label", "Month"))
    if len(groups) > 1:
        ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=SERIES[i % len(SERIES)]) for i in range(len(groups))],
                  labels=groups, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0),
                  ncol=len(groups), fontsize=8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="x", alpha=0.25)
    _finish(fig, ax, c, out)


def r_timeline(c, out):
    ev = c["events"]
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axhline(0, color=NAVY, lw=2)
    for i, e in enumerate(ev):
        up = 1 if i % 2 == 0 else -1  # alternate above/below so labels never collide
        ax.plot([i, i], [0, 0.55 * up], color=GRAY, lw=1)
        ax.scatter(i, 0, s=60, color=SERIES[i % len(SERIES)], zorder=3)
        ax.text(i, 0.6 * up, f"{e['when']}\n{e['label']}", ha="center", va="bottom" if up > 0 else "top",
                fontsize=8, wrap=True)
    ax.set_xlim(-0.7, len(ev) - 0.3)
    ax.set_ylim(-1.6, 1.6)
    ax.axis("off")
    _finish(fig, ax, c, out)


def r_grid(c, out):
    cells = c["cells"]
    cols = min(c.get("columns", 3), len(cells))
    rows = -(-len(cells) // cols)
    fig, ax = plt.subplots(figsize=(10, 3.2 * rows))
    for i, cell in enumerate(cells):
        x = (i % cols + 0.5) / cols
        y = 1 - (i // cols + 0.5) / rows
        body = "\n".join(f"- {s}" for s in cell.get("items", []))
        _box(ax, x, y, 0.9 / cols, 0.88 / rows, cell["title"], body, SERIES[i % len(SERIES)])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    _finish(fig, ax, c, out)


def r_flow(c, out):
    steps = c["steps"]
    n = len(steps)
    fig, ax = plt.subplots(figsize=(max(10, 2.2 * n), 4))
    w = 0.8 / n
    for i, s in enumerate(steps):
        x = (i + 0.5) / n
        body = "\n".join(f"- {v}" for v in s.get("items", []))
        _box(ax, x, 0.5, w, 0.7, s["title"], body, SERIES[i % len(SERIES)])
        if i < n - 1:
            ax.annotate("", xy=(x + 1 / n - w / 2 - 0.005, 0.5), xytext=(x + w / 2 + 0.005, 0.5),
                        arrowprops={"arrowstyle": "->", "color": GRAY, "lw": 2})
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    _finish(fig, ax, c, out)


RENDERERS = {
    "growth": r_growth, "tam_sam_som": r_tam_sam_som, "pie": r_pie, "bar": r_bar,
    "matrix": r_matrix, "heatmap": r_heatmap, "five_forces": r_five_forces, "lines": r_lines,
    "gantt": r_gantt, "timeline": r_timeline, "grid": r_grid, "flow": r_flow,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", help="path to charts.json")
    ap.add_argument("--out", default="figures", help="output directory (default: figures)")
    ap.add_argument("--validate-only", action="store_true", help="check the spec, render nothing")
    args = ap.parse_args()

    try:
        spec = json.loads(Path(args.spec).read_text())
    except FileNotFoundError:
        sys.exit(f"Spec not found: {args.spec}")
    except json.JSONDecodeError as e:
        sys.exit(f"{args.spec} is not valid JSON: line {e.lineno} col {e.colno}: {e.msg}")

    errs = validate(spec)
    if errs:
        print(f"FAILED: {len(errs)} problem(s) in {args.spec}. Nothing rendered.")
        for e in errs:
            print("  -", e)
        sys.exit(1)
    if args.validate_only:
        print(f"OK: {len(spec['charts'])} chart(s) valid")
        return

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    manifest = []
    for c in spec["charts"]:
        RENDERERS[c["type"]](c, out / c["file"])
        manifest.append(f"{c['file']}\t{c['title']}\tSource: {c['source']}")
        print(f"  wrote {out / c['file']}")
    # Manifest gives the exact source line to paste into each \caption.
    (out / "figure_sources.tsv").write_text("file\ttitle\tsource\n" + "\n".join(manifest) + "\n")
    print(f"OK: {len(manifest)} figure(s); captions/sources in {out / 'figure_sources.tsv'}")


if __name__ == "__main__":
    main()
