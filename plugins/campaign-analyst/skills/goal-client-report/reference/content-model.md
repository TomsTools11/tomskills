# Content model: Structured Dashboard

Each section, the data it needs, and where that data comes from. Field names in `code` are keys in the JSON that `scripts/compute_metrics.py` prints.

## Contents
- Source files
- Identity fields
- Period strip
- 01 Key metrics
- 02 Performance by line
- 03 Conversion funnel
- 04 Performance by hour (optional)
- 05 Recommendations (04 when the hourly section is left out)
- Footer
- Light and dark mode
- Fill checklist

## Source files
The standard GOAL export set per campaign (produced by the `goal-campaign-exports` skill), in the account's review folder. Account folders sit under `~/GOAL/My Accounts/Account Mgmt/{Account}/`. To find the exports, list the account folder and use the newest folder with "review" in its name (older accounts use `Account Reviews/`, newer ones `account-reviews/`). New review folders are `account-reviews/account-review-{m-d-yy}/`.

| File | Feeds |
|---|---|
| `campaign-performance-{campaign}-{state}-{timeframe}.csv` | Exec summary, Key metrics, Funnel |
| `campaign-performance-by-source-type-...csv` | Section 02 rows for a single-campaign report |
| `campaign-performance-by-property-type-...csv` (Home only) | Section 02 rows, alternative to source type |
| `campaign-performance-by-hour-...csv` (optional) | Section 04 Performance by Hour, only when it has Contacted, Quote, and Bound columns. Hours are Pacific in the export; `compute_metrics.py --to-tz` converts them |
| `campaign-performance-by-day-of-week-...csv` (optional) | Not shown in the client report by default; context for the account manager |
| `source-settings-...csv` | Not used. Bid multipliers, bid rate, win rate, and RightPricing never appear in a client report. |

Dispositions are already imported into GOAL before export, so contacted, quote, and policy counts come from the exports. Do not ask for CRM or disposition files.

## Identity fields
| Placeholder | Example | Notes |
|---|---|---|
| `[Agency Name]` | Northwind Insurance Agency | Sidebar H1, `<title>`, footer. Never in body copy. |
| `[Contact Name]` | Jordan Avery | "Prepared for" line only. |
| `[City, ST]` | Flossmoor, IL | |
| `[Campaign]` | Home (CA), or "All campaigns" for an overview | Sidebar, `<title>`, strip badge. |
| `[Reporting Period]` | June 1–30, 2026 / Last 30 days | Matches the export timeframe. |

## Period strip
The bar above section 01. Fields: Reporting period, Lines (the lines or source types covered), Lead source ("GOAL branded campaigns"). The badge on the right holds `[Campaign]`. Never put "100% Exclusive" or any other sales claim in the badge. Add a field only for a fact from the exports.

## 01 Key metrics
Six cards (or three). Default set and source:

| Card | Value | Sub-line |
|---|---|---|
| Leads | `totals.counts.leads` | Lines or campaign covered |
| Contact rate | `totals.metrics.contact_rate` | "18 of 59 leads" |
| Quote rate | `totals.metrics.quote_rate` | "7 of 59 leads" |
| CPA | `totals.metrics.cpa` | "Cost per policy · N bound". Keep this card's `hl` class (the highlighted card). |
| Policies bound | `totals.counts.policies` | Scope |
| Inbound calls | `totals.counts.calls` | "Direct from prospects" |

Missing column (see `missing` in the JSON): drop that card and keep an even grid (6 or 3). Substitutes when a card drops: Quotes, Clicks, Average ad position. Never CPL.

## 02 Performance by line
- **Overview report (several lines):** one row per campaign/line from each campaign's totals.
- **Single-campaign report:** one row per source type (or property type for Home) from the by-dimension export.
- Donut: use `donut[]` straight from the JSON (`dash`, `offset`, `leads`). Segment, legend swatch, and table dot use the same variable, in order: `var(--s1)` through `var(--s5)`. Never a hex value: the variables switch for dark mode. More than five segments: merge the smallest into "Other" on `var(--s5)`. Center number = total leads; update the SVG `aria-label` to match.
- One row per segment: lead count, calls, and a one-line note (the row's metrics plus any update made).
- Tags (optional, factual only): `tag blue` "Primary" (largest share of leads) · `tag neutral` "Active" · `tag amber` "Refining" (an update is in progress). Never "Strongest Line" or "High Quality". Delete a tag rather than invent a status.
- Empty cell: "0", never a dash.
- One segment only: delete the donut panel and keep the table.

## 03 Conversion funnel
Use `funnel[]` from the JSON, one `.fstep` per stage:
- `count` inside the bar, `width` as `data-w`, `bar_class` as the `<i>` class (`pre` above the divider, `cv` from Leads down, `cv end` on the last stage).
- `rate` as the bold percentage and `rate_label` as the small line under it ("of impressions", "of clicks", "of leads"). The first stage shows 100% with no label.
- Keep the divider line ("Conversion funnel · rates based on Leads") between Clicks and Leads.
- Drop stages the export lacks. Inbound calls are a KPI, not a funnel stage.
- The note lists the lead-based rates with counts, e.g. "Contact rate **31%** (18 of 59 leads). Quote rate **12%** (7 of 59). Lead to sale **5.1%** (3 of 59). CPA **$334**." Nothing else.

## 04 Performance by hour (optional)
Use only when a by-hour export with Contacted, Quote, and Bound columns is in the folder, and the period has at least one block of 30 or more leads. Otherwise delete the section and its nav link and renumber Recommendations to 04 in the sidebar and the section header.

Run `compute_metrics.py` with `--to-tz` (the agent's time zone, from the office address; check the county in split-zone states) and `--period-start`/`--period-end` (the export window). Read its `warnings` first: a DST change inside the window, hours crossing midnight, or outcomes above leads in an hour each need a note to the account manager before the section is used.

- **Sub-header:** the period and the zone: "Sept 1–30 · Central Time" (`time_zone.label`). Hours are always agent local time with the zone named. `finalize_report.py` fails a section with no zone or with hours out of clock order.
- **Bars:** one `.fstep` per `hourly[]` entry, in clock order (the export sorts by volume; the script re-sorts). Label = `label`, `data-w` = `width` (linear, the bar is empty), bold figure = `leads`, small line = `share_of_leads` as "N% of leads" ("<1% of leads" when it rounds to 0, written `&lt;1%` in the HTML).
- **Time-block table:** one row per `blocks[]` entry: block label, leads, calls, contacted, and "N% of leads" for contact rate. A block with `below_floor: true` shows "Under 30 leads" in place of the rate and a `var(--s5)` dot.
- **Note:** metrics only, e.g. "8 AM to 11 AM: **41 of 120 leads**, contact rate **34%**."
- **Never** show schedule percentages, bids, hourly effective bids, win rate, or the export's CVR columns.

## 05 Recommendations
Three to five items. Each: Title Case heading, `GOAL` tag (`tag blue`) or `Agency` tag (`tag neutral`), one or two factual sentences, and a "Metric behind it:" line citing a number shown elsewhere in the report. Common items: budget or schedule change (GOAL), 5-minute response, 30-day cadence with the Week 1 / Week 2 / Weeks 3–4 grid (Agency), updating dispositions in GOAL weekly (Agency). Delete the cadence grid if that item is not used.

Schedule change example (invented numbers): heading "Shift Bids Toward 8 AM to 11 AM", `GOAL` tag, body "We increased bids from 8 AM to 11 AM.", then "Metric behind it: contact rate 34% (41 of 120 leads) from 8 AM to 11 AM." Hours in agent local time; direction and hours only, never the percentage.

## Footer
The `.mfoot` line: "All conversion metrics calculated based on Leads, not Clicks." and "GOAL · [Reporting Period]". Keep both. The sidebar footer repeats the footnote on screen; the `.mfoot` line is what prints.

## Light and dark mode
The report opens in the viewer's system setting and carries a round light/dark toggle fixed to the top-right corner; print is always light and hides the toggle. Four pieces make it work, and all four stay exactly as the template has them:

| Piece | Where | Job |
|---|---|---|
| Theme `<script>` | First element in `<head>` | Reads a saved choice (`localStorage` key `goal-theme`) or the system setting and sets `data-theme` on `<html>` before paint; follows live system changes when nothing is saved; defines `goalToggleTheme()` |
| `data-theme="system"` | Root `<div class="g">` | No-JS fallback: the page still follows the system via the media query |
| `/* Theme toggle */` CSS | End of `<style>` | Button look in both themes, icon swap, hidden in print |
| `<button class="theme-toggle">` | Just before `</body>` | Moon icon in light mode, sun icon in dark mode; click flips the theme |

The saved choice is shared by every GOAL report on the same site, so a client who picks dark mode on one report sees dark on the others. Choosing the theme that matches their system clears the saved choice. Both logos stay in the sidebar (black shows in light mode, white in dark). Every color in the body comes from a CSS variable.

## Fill checklist
- [ ] Every `[Bracketed]` field replaced, including `<title>`
- [ ] Every worked-example number replaced with a value from the JSON
- [ ] Cards, rows, and stages without data removed cleanly; nav links match remaining sections; section numbers run 01 to N
- [ ] Performance by Hour: kept only with outcome columns and a 30+ lead block; zone in the sub-header; hours in clock order and agent local time; no schedule percentages
- [ ] Copy passes reference/copy-guidelines.md
- [ ] Checked in light mode, dark mode, and print preview; the toggle flips the theme and is hidden in print
- [ ] `finalize_report.py` returns `"ok": true`
