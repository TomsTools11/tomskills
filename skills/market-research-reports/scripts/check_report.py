#!/usr/bin/env python3
"""Check a compiled market report before delivery.

Run after compiling. Reports every problem at once and exits 1 if any ERROR.

Usage:
    python check_report.py drafts/report.tex            # expects report.log/.pdf beside it
    python check_report.py drafts/report.tex --min-pages 30

Checks:
  ERROR  \\baseyear still 0, template placeholders left in the text
  ERROR  figure with no image, \\includegraphics pointing at a missing file
  ERROR  figure caption without a "Source:" line
  ERROR  LaTeX errors, undefined references or citations in the .log
  ERROR  page count below --min-pages
  WARN   base year more than 2 years before today (stale data)
"""

import argparse
import datetime
import re
import subprocess
import sys
from pathlib import Path

# Template placeholder patterns. Each is something a finished report never contains.
PLACEHOLDERS = [
    (r"\$?X+\.X+", "numeric placeholder like X.XX"),
    (r"\bCompany [A-J]\b", "placeholder competitor name"),
    (r"\bTODO\b|\bTBD\b", "TODO/TBD"),
    # [Instruction text] at line start or after a space; skips \begin{box}[Title] and \\[1cm]
    (r"(?:^|(?<=\s))\[[A-Z][^\]\n]{3,}\]", "bracketed template instruction"),
]


def strip_comments(tex):
    return re.sub(r"(?<!\\)%.*", "", tex)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tex")
    ap.add_argument("--min-pages", type=int, default=50, help="minimum PDF pages (default 50)")
    args = ap.parse_args()

    tex_path = Path(args.tex)
    if not tex_path.exists():
        sys.exit(f"Not found: {tex_path}")
    raw = tex_path.read_text(errors="replace")
    body = strip_comments(raw)
    errors, warns = [], []

    # Base year
    m = re.search(r"\\newcommand\{\\baseyear\}\{(\d+)\}", raw)
    if m:
        year = int(m.group(1))
        today = datetime.date.today().year
        if year == 0:
            errors.append("\\baseyear is 0. Set it to the latest year with actual data")
        elif year < today - 2:
            warns.append(f"\\baseyear is {year}; data older than 2 years. Look for newer figures")

    # Placeholders, reported with line numbers
    lines = body.splitlines()
    for pat, what in PLACEHOLDERS:
        hits = [i + 1 for i, ln in enumerate(lines) if re.search(pat, ln)]
        if hits:
            shown = ", ".join(map(str, hits[:10])) + (" ..." if len(hits) > 10 else "")
            errors.append(f"{what} on {len(hits)} line(s): {shown}")

    # Figures: image present, file exists, caption cites a source
    for fig in re.finditer(r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}", body, re.S):
        block = fig.group(1)
        line = body[: fig.start()].count("\n") + 1
        cap = re.search(r"\\caption\{((?:[^{}]|\{[^{}]*\})*)\}", block)
        name = cap.group(1)[:50].replace("\n", " ") if cap else f"line {line}"
        imgs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", block)
        if not imgs and "tikzpicture" not in block:
            errors.append(f"figure '{name}' (line {line}) has no image. Render it or delete the figure")
        for img in imgs:
            p = (tex_path.parent / img)
            if not any(p.with_suffix(s).exists() for s in ("", ".png", ".pdf", ".jpg")) and not p.exists():
                errors.append(f"figure '{name}' points at missing file {img}")
        if cap and not re.search(r"source|\\cite", cap.group(1), re.I) and "\\figuresource" not in block:
            errors.append(f"figure '{name}' (line {line}) caption has no Source")

    # Compile log
    log = tex_path.with_suffix(".log")
    if not log.exists():
        errors.append(f"{log.name} missing. Compile the report first")
    else:
        lt = log.read_text(errors="replace")
        n_err = len(re.findall(r"^! ", lt, re.M))
        if n_err:
            first = re.search(r"^! .*", lt, re.M).group(0)
            errors.append(f"{n_err} LaTeX error(s) in log; first: {first}")
        refs = sorted(set(re.findall(r"Reference `([^']+)' on page \d+ undefined", lt)))
        cites = sorted(set(re.findall(r"Citation `([^']+)' on page \d+ undefined", lt)))
        if refs:
            errors.append(f"undefined \\ref labels: {', '.join(refs[:10])}")
        if cites:
            errors.append(f"undefined citations (add to references.bib, rerun bibtex): {', '.join(cites[:10])}")
        if "Rerun to get cross-references right" in lt:
            warns.append("LaTeX asks for another xelatex pass")

    # Page count
    pdf = tex_path.with_suffix(".pdf")
    if pdf.exists():
        pages = None
        try:
            from pypdf import PdfReader
            pages = len(PdfReader(str(pdf)).pages)
        except Exception:
            try:
                info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
                pages = int(re.search(r"Pages:\s+(\d+)", info).group(1))
            except Exception:
                warns.append("could not count pages (install pypdf or poppler-utils)")
        if pages is not None:
            if pages < args.min_pages:
                errors.append(f"{pages} pages, below the {args.min_pages}-page minimum. "
                              "Deepen thin chapters with sourced analysis; do not pad")
            else:
                print(f"pages: {pages}")
    else:
        errors.append(f"{pdf.name} missing. Compile the report first")

    for w in warns:
        print("WARN ", w)
    for e in errors:
        print("ERROR", e)
    print("PASS" if not errors else f"FAIL: {len(errors)} error(s)")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
