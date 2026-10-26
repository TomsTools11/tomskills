---
name: market-research-reports
description: Produces consulting-style market research reports (default 50+ pages) as LaTeX-compiled PDFs, with sourced market sizing (TAM/SAM/SOM, CAGR), competitive landscape, Porter's Five Forces, PESTLE, SWOT, risk analysis, strategic recommendations, and data-driven charts. Use when the user asks for a market research report, industry analysis, market sizing, market entry or due diligence report, or a McKinsey/BCG/Gartner-style market study. Not for a profile of a single company or a short answer about a market.
---

# Market Research Reports

Builds a long-form market report: research log, then chart data, then LaTeX chapters, then a validated PDF. Every number in the report traces to a logged source.

Paths below are relative to this skill's folder (the folder holding this SKILL.md). Call it `$SKILL`.

## Requirements

- `xelatex` and `bibtex` (TeX Live). Check with `which xelatex bibtex`.
- Python: `pip install matplotlib pypdf --break-system-packages`
- Web search and fetch tools for research.

## Workflow

Copy this checklist into the task list and tick items off:

```
- [ ] 1. Scope agreed
- [ ] 2. Research log built (sources/research_log.md)
- [ ] 3. Frameworks applied
- [ ] 4. Chart spec validated and figures rendered
- [ ] 5. Report written from template
- [ ] 6. Compiled and check_report.py passes
- [ ] 7. Independent review done
```

### 1. Scope

Confirm market definition, geography, time horizon, audience (investor, operator, entrant), and the decisions the report should inform. If the user gave these, proceed; otherwise ask once. Page minimum defaults to 50; use the user's number if they give one.

Create the project:

```
<project>/
├── drafts/report.tex          # copy of $SKILL/assets/market_report_template.tex
├── drafts/market_research.sty # copy of $SKILL/assets/market_research.sty
├── references/references.bib
├── data/charts.json
├── figures/
└── sources/research_log.md
```

### 2. Research

Search per chapter, not per report: one query for "market size", another for "market share by company", another for regulation, and so on. Open the primary page rather than relying on snippets.

Log every figure you might use in `sources/research_log.md`:

```
| Figure | Value | Year of data | Publisher | URL | Notes |
| US market size | $4.7B | 2024 | NAPHIA | https://... | gross written premium |
```

Rules:
- Market size and CAGR need at least two sources. When they disagree, report the range and say which you anchor on and why.
- Prefer data from the last 2 years. Flag anything older in Notes.
- No source, no number. If a needed figure cannot be found, write it as a stated assumption in Appendix A or drop it.
- Add each source to `references/references.bib` as you go.

### 3. Analysis

Apply the frameworks using `$SKILL/references/data_analysis_patterns.md` (sizing methods, Five Forces scoring, PESTLE, SWOT, risk scoring, scenarios). Each rating (High/Medium/Low, 1-5) gets a one-line rationale tied to logged evidence.

### 4. Charts

Write `data/charts.json` from the research log, then validate and render:

```bash
python $SKILL/scripts/make_charts.py data/charts.json --validate-only
python $SKILL/scripts/make_charts.py data/charts.json --out figures/
```

If validation fails, fix the spec and rerun until it reports OK. Nothing renders while any chart has an error. Spec format, the 12 chart types, and which template figure uses which type: `$SKILL/references/chart_specs.md`.

Minimum figures: market growth, TAM/SAM/SOM, Five Forces, competitive positioning, risk heatmap. Add others where the chapter has data to show.

### 5. Write

Fill `drafts/report.tex` chapter by chapter, using `$SKILL/references/report_structure_guide.md` for each chapter's content. Before writing:

- Set `\reporttitle`, `\baseyear` (latest year with actual data), and the other metadata at the top of the template. Year macros (`\baseyear`, `\horizonyear`, `\yr{n}`) fill the table and caption years.
- Delete any figure environment whose chart you did not render. Uncomment `\includegraphics` for those you did.
- End every figure caption with `Source: ...` from `figures/figure_sources.tsv`.

| Part | Pages | Core content |
|---|---|---|
| Front matter + executive summary | 5 | snapshot stat boxes, thesis, top findings, top recommendations |
| 1 Market overview | 4-5 | definition, scope, ecosystem |
| 2 Size and growth | 6-8 | TAM/SAM/SOM, history, projections, regions, segments |
| 3 Drivers and trends | 5-6 | PESTLE, driver impact |
| 4 Competitive landscape | 6-8 | Five Forces, shares, positioning, barriers |
| 5 Customers | 4-5 | segments, needs, buying process |
| 6 Technology | 4-5 | roadmap, adoption |
| 7 Regulation | 3-4 | framework, upcoming changes |
| 8 Risk | 3-4 | register, heatmap, mitigation |
| 9-11 Strategy, roadmap, financials | 10-12 | prioritized recommendations, phased plan, scenarios |
| Appendices + bibliography | 5 | methodology, data tables, company profiles |

Lead each section with the insight, then the evidence. Recommendations are numbered, specific, and say who does what by when. Box environments and table styles: `$SKILL/references/latex_formatting.md`.

If a chapter has little real evidence (common for niche markets), keep it short and say so. Reach the page minimum through depth in data-rich chapters and appendix data tables, never through filler.

### 6. Compile and check

```bash
cd drafts
xelatex -interaction=nonstopmode report.tex
bibtex report
xelatex -interaction=nonstopmode report.tex
xelatex -interaction=nonstopmode report.tex
python $SKILL/scripts/check_report.py report.tex --min-pages 50
```

`check_report.py` fails on: `\baseyear` unset, leftover template placeholders (`X.XX`, `Company A`, `[bracketed instructions]`), empty or missing figures, captions without a source, LaTeX errors, undefined references or citations, and page count under the minimum. Fix every ERROR, recompile, and rerun until it prints PASS.

### 7. Independent review

When a subagent tool is available, give a fresh agent the PDF text and `sources/research_log.md` and ask it to spot-check 10 numbers against the log, flag claims with no source, and flag recommendations not supported by the analysis. Fix what it finds and rerun step 6. Without subagents, do this check yourself against the log, not from memory.

Deliver the PDF with a short note on scope, base year, and the biggest data gaps.

## Reference files

- `references/report_structure_guide.md`: section-by-section content for every chapter
- `references/data_analysis_patterns.md`: framework templates and scoring
- `references/chart_specs.md`: chart JSON format with an example of each type
- `references/latex_formatting.md`: style package boxes, tables, figures, troubleshooting

## Troubleshooting

- **Undefined control sequence**: the project's `market_research.sty` is out of date or missing; recopy it from `$SKILL/assets/`.
- **Citations show as `[?]`**: run `bibtex report`, then `xelatex` twice.
- **Figure or table overflows the margin**: lower `width=` in `\includegraphics` or wrap the tabular in `\resizebox{\textwidth}{!}{...}`.
- **Chart text too small**: shorten labels in `charts.json`; matrices and grids read best with 10 or fewer items.
