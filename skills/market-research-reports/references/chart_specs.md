# Chart Specs for make_charts.py

## Contents
- Spec file layout and required fields
- Template figure → chart type map
- One example per chart type (growth, tam_sam_som, pie, bar, matrix, heatmap, five_forces, lines, gantt, timeline, grid, flow)
- Rules for numbers

## Spec file layout

`data/charts.json` holds one object with a `charts` list. Every chart needs:

| Field | Meaning |
|---|---|
| `file` | PNG name. Use the template's name (map below) so `\includegraphics` resolves |
| `type` | One of the 12 types below |
| `title` | Chart title drawn on the image |
| `source` | Where the numbers came from, e.g. `"Grand View Research (2025); IBISWorld"`. For framework diagrams built from your own synthesis: `"Team analysis of sources in Appendix A"` |

Validate, then render:

```bash
python scripts/make_charts.py data/charts.json --validate-only
python scripts/make_charts.py data/charts.json --out figures/
```

The script writes `figures/figure_sources.tsv`; paste each source into that figure's `\caption{... Source: ...}`.

## Template figure → chart type

| Template file | Type | Notes |
|---|---|---|
| market_growth_trajectory.png | growth | actual + projected bars |
| tam_sam_som.png | tam_sam_som | |
| regional_breakdown.png | pie | |
| segment_growth.png | bar | CAGR by segment |
| market_share.png | pie | add an "Other" slice so shares reach 100 |
| customer_segments.png | pie | |
| competitive_positioning.png, strategic_groups.png | matrix | |
| driver_impact_matrix.png, segment_attractiveness.png | matrix | |
| opportunity_matrix.png, recommendation_priority.png | matrix | |
| innovation_curve.png | matrix or timeline | matrix: maturity vs. impact |
| risk_heatmap.png | heatmap | |
| porters_five_forces.png | five_forces | |
| financial_projections.png, scenario_analysis.png | lines | |
| implementation_timeline.png, technology_roadmap.png, milestone_tracker.png | gantt | |
| regulatory_timeline.png, trends_timeline.png | timeline | |
| pestle_analysis.png, risk_mitigation.png, market_structure.png | grid | |
| industry_ecosystem.png, customer_journey.png | flow | |

A chart left out of the spec means its figure environment must be deleted from the .tex, not left empty.

## Examples

Values below are illustrative only. Never copy them into a report.

### growth
```json
{"file": "market_growth_trajectory.png", "type": "growth", "title": "US Pet Insurance Market, USD B",
 "years": [2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028],
 "values": [2.6, 3.2, 3.9, 4.7, 5.6, 6.6, 7.8, 9.1],
 "first_projected_year": 2026, "unit": "USD billions", "cagr_note": "17.5% CAGR 2025-2028",
 "source": "NAPHIA State of the Industry; team projection (Appendix A)"}
```

### tam_sam_som
```json
{"file": "tam_sam_som.png", "type": "tam_sam_som", "title": "Market Opportunity",
 "tam": 48.0, "sam": 12.5, "som": 1.1, "unit": "USD B", "source": "Bottom-up model, Ch. 2"}
```

### pie
Set `"percent": true` when values are shares; the validator then requires a ~100 total.
```json
{"file": "market_share.png", "type": "pie", "title": "Market Share by Company",
 "labels": ["Trupanion", "Nationwide", "Healthy Paws", "Other"], "values": [22, 18, 14, 46],
 "percent": true, "source": "Company filings; NAPHIA"}
```

### bar
```json
{"file": "segment_growth.png", "type": "bar", "title": "Segment CAGR",
 "labels": ["Accident & illness", "Accident only", "Wellness add-on"], "values": [18.2, 6.1, 12.4],
 "axis_label": "CAGR (%)", "value_format": "%.1f%%", "source": "NAPHIA"}
```

### matrix
`x`/`y` on a 0-10 scale; `size` 0-1 (optional, e.g. relative revenue). `quadrants` order: top-left, top-right, bottom-left, bottom-right.
```json
{"file": "competitive_positioning.png", "type": "matrix", "title": "Competitive Positioning",
 "x_label": "Market focus (niche to broad)", "y_label": "Offering (product to platform)",
 "quadrants": ["Niche platforms", "Platform leaders", "Specialists", "Product leaders"],
 "points": [{"label": "Trupanion", "x": 4, "y": 7, "size": 0.8}, {"label": "Lemonade", "x": 7, "y": 6, "size": 0.3}],
 "source": "Team analysis of company materials"}
```

### heatmap
Probability and impact are integers 1-5.
```json
{"file": "risk_heatmap.png", "type": "heatmap", "title": "Risk Heatmap",
 "risks": [{"label": "R1 Vet cost inflation", "probability": 4, "impact": 4},
           {"label": "R2 New state regulation", "probability": 2, "impact": 3}],
 "source": "Risk register, Ch. 8"}
```

### five_forces
Keys: `new_entrants`, `supplier_power`, `buyer_power`, `substitutes`, `rivalry`. Rating: Low, Medium, High. Up to 3 factors each.
```json
{"file": "porters_five_forces.png", "type": "five_forces", "title": "Porter's Five Forces",
 "forces": {"new_entrants": {"rating": "Medium", "factors": ["Low capital need for MGAs", "Licensing per state"]},
            "supplier_power": {"rating": "Low", "factors": ["Fragmented reinsurers"]},
            "buyer_power": {"rating": "High", "factors": ["Easy online comparison"]},
            "substitutes": {"rating": "Medium", "factors": ["Pet savings accounts"]},
            "rivalry": {"rating": "High", "factors": ["20+ active carriers", "Price-led ads"]}},
 "source": "Team analysis, Ch. 4"}
```

### lines
```json
{"file": "scenario_analysis.png", "type": "lines", "title": "Revenue Scenarios, USD M",
 "x": [2026, 2027, 2028], "series": {"Conservative": [10, 13, 16], "Base": [12, 17, 23], "Optimistic": [14, 21, 31]},
 "axis_label": "USD millions", "source": "Financial model, Ch. 11"}
```

### gantt
`start`/`end` in any consistent unit; name it in `time_label`. `group` colors bars by phase.
```json
{"file": "implementation_timeline.png", "type": "gantt", "title": "Implementation Roadmap", "time_label": "Month",
 "tasks": [{"label": "Licensing", "start": 0, "end": 4, "group": "Phase 1"},
           {"label": "Pilot launch", "start": 4, "end": 9, "group": "Phase 2"}],
 "source": "Recommendations, Ch. 10"}
```

### timeline
```json
{"file": "regulatory_timeline.png", "type": "timeline", "title": "Regulatory Timeline",
 "events": [{"when": "2024", "label": "NAIC Pet Insurance Model Act adopted"}, {"when": "2026", "label": "State adoptions"}],
 "source": "NAIC; state insurance departments"}
```

### grid
`columns` defaults to 3. PESTLE uses 6 cells.
```json
{"file": "pestle_analysis.png", "type": "grid", "title": "PESTLE Analysis",
 "cells": [{"title": "Political", "items": ["State model act adoption"]}, {"title": "Economic", "items": ["Vet CPI above core CPI"]}],
 "source": "Team analysis, Ch. 3"}
```

### flow
```json
{"file": "industry_ecosystem.png", "type": "flow", "title": "Value Chain",
 "steps": [{"title": "Carriers", "items": ["Underwrite risk"]}, {"title": "MGAs", "items": ["Product, pricing"]},
           {"title": "Distribution", "items": ["Direct, employer, vet"]}, {"title": "Pet owners", "items": []}],
 "source": "Team analysis"}
```

## Rules for numbers

- Every value comes from `sources/research_log.md`. If a number is missing, research it or drop the chart; never estimate silently.
- Projections you compute yourself: say so in `source` ("team projection") and state the method in Appendix A.
- Use one unit per chart and name it in `unit`, `axis_label`, or the title.
