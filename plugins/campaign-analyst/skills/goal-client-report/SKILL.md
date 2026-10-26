---
name: goal-client-report
description: Builds client-facing GOAL account review reports for insurance agency clients as a single self-contained HTML file in the Structured Dashboard design (opens in the viewer's system light or dark mode, with a light/dark toggle button), filled from the GOAL campaign export CSVs and printable to PDF. Use whenever the user asks to make, build, or create a client report, account review, performance review, campaign report, campaign overview, dashboard, or visuals from GOAL campaign data, or names an agency and asks for its report, even if they only say "build the Lakeside report" or "turn these exports into visuals". Replaces goal-visuals-builder, build-client-visual, and the Refined Light, Navy Editorial, and internal dashboard templates. Not for internal source-level diagnosis or bid recommendations; use campaign-analysis for those.
---

# GOAL Client Report

Turns GOAL campaign exports into a client-facing account review: a sidebar-nav dashboard with a period strip, key metrics, performance by line, a conversion funnel, and recommendations. It opens in light or dark to match the viewer's system, has a round light/dark toggle in the top-right corner that overrides it (the choice is remembered across every GOAL report on the same site), and always prints light. The reader is an agency owner, usually non-technical.

## Workflow

Copy this checklist and track progress:

```
Report progress:
- [ ] 1. Confirm account, campaign(s), and period
- [ ] 2. Locate the export CSVs
- [ ] 3. Compute metrics (scripts/compute_metrics.py)
- [ ] 4. Fill the template
- [ ] 5. Finalize and check (scripts/finalize_report.py) until ok
- [ ] 6. Review the rendered page, then save and deliver
```

**1. Confirm scope.** Ask once, only for what the user has not said: which account, which campaign(s), what period. Default: one report per campaign, plus a "Campaign Overview" report when the account runs more than one campaign.

**2. Locate the exports.** Use only the GOAL export CSVs (see `reference/content-model.md` for the file set). Account folders sit under `~/GOAL/My Accounts/Account Mgmt/{Account}/`; list the account folder and use the newest folder with "review" in its name (older accounts use `Account Reviews/`, newer ones `account-reviews/account-review-{m-d-yy}/`). In Claude Code, read the path directly; in Cowork, reach it through the connected folder (mounted under `$HOME/mnt/<folder name>` in the computer's shell). Never ask for CRM or disposition files; dispositions are already imported into GOAL. If the exports are missing or stale, run the `goal-campaign-exports` skill or ask the user to export them. An optional by-hour export (`campaign-performance-by-hour-...csv`) feeds the optional Performance by Hour section.

**3. Compute metrics.** Run the script; do not compute by hand. `<skill-dir>` below is this skill's folder: the base directory shown when the skill loads, or `${CLAUDE_SKILL_DIR}` in Claude Code. Commands run in the session's working directory, not the skill folder, so a bare `scripts/...` path will not resolve; pass the export files by their full path or run from the review folder.

```bash
python3 <skill-dir>/scripts/compute_metrics.py campaign-performance-home-ca-last30days.csv \
  campaign-performance-by-source-type-home-ca-last30days.csv --out metrics.json
```

It returns totals, per-row metrics, CPA, contact and quote rates, ready-made donut `dash`/`offset` values, and funnel counts, rates, and bar widths. Read `missing` and `warnings` first: a missing column means that card or stage is omitted, never estimated.

For the optional by-hour file, pass the agent's time zone and the export window. GOAL exports hours in Pacific time; the script converts them with the real dates (so daylight saving time is handled), re-sorts by clock time, and merges thin hours into `blocks[]`:

```bash
python3 <skill-dir>/scripts/compute_metrics.py campaign-performance-by-hour-home-ca-last30days.csv \
  --to-tz America/Chicago --period-start 2026-09-01 --period-end 2026-09-30 --out hourly.json
```

Its warnings (DST change in the window, hours crossing midnight, hours under 30 leads, no outcome columns, outcomes above leads) go to the user before the section is built.

**4. Fill the template.** Copy `templates/structured-dashboard.html` to the output name (see Delivery). Then:
- Replace every `[Bracketed]` field (identity lives in the sidebar, `<title>`, and footer only).
- Replace every worked-example number (the "Northwind" account) with JSON values. Section-by-section mapping: `reference/content-model.md`.
- Write all copy to `reference/copy-guidelines.md`. Read it before writing; the template's example copy shows the target tone.
- Remove cards, rows, stages, or sections that have no data, and remove their nav links.
- Keep the template's CSS, sizes, and layout. Do not add sections, chart types, or fonts. The one optional section is 04 Performance by Hour: keep it only when the by-hour export has outcome columns (see `reference/content-model.md`); otherwise delete it and its nav link and renumber Recommendations to 04. Every color in the body is a CSS variable (`var(--s1)` to `var(--s5)`, `var(--brand)`); a hex value would not switch in dark mode.
- Leave the light/dark mode wiring exactly as the template has it. Every report ships with all four parts:
  1. the theme `<script>` as the first element in `<head>` (sets `data-theme` on `<html>` before the page paints, so there is no flash of the wrong theme);
  2. `data-theme="system"` on the root `.g` div;
  3. the `/* Theme toggle */` CSS block at the end of `<style>`;
  4. the `<button class="theme-toggle" ... onclick="goalToggleTheme()">` with its moon and sun icons, just before `</body>`.

  Default is the viewer's system setting. Clicking the toggle flips light/dark and saves the choice under the `goal-theme` key, which every report on the same site shares; flipping back to the system's own theme clears the saved override. The toggle is hidden in print. Do not remove, restyle, or move it, and do not add a second toggle.

**5. Finalize and check.**

```bash
python3 <skill-dir>/scripts/finalize_report.py "Acme Insurance - Home Campaign.html"
```

This inlines both logos as base64 and checks for unfilled placeholders, leftover example numbers, CPL, sales framing, client name in body copy, hard-coded colors, the theme setting and light/dark toggle, donut math, bar widths, nav links, and the footnote. Fix every error and rerun until `"ok": true`. Read each warning and fix it unless it is a false positive.

**6. Review and deliver.** Look at the rendered page in light mode, dark mode, and print preview (Cmd/Ctrl-P). In a headless browser, emulate `prefers-color-scheme` (light and dark) and confirm the page opens in that theme, click the toggle and confirm it flips, then emulate print media and confirm the page is light and the toggle is gone. Confirm every number on the page matches `metrics.json`.

## Delivery

- File name: `{Agency display name} - {Campaign} Campaign.html` (for example `The Lakeside Agency - Home Campaign.html`); the overview is `{Agency display name} - Campaign Overview.html`. Use a hyphen, never an em dash.
- Save into the same account review folder as the exports. The `deploy-reporting-site` skill picks reports up from the account folder when the user wants them online.
- In the reply, give one line per file and offer print-to-PDF. Do not restate the report's contents.

## Templates

| Template | File | Use |
|---|---|---|
| Structured Dashboard (v2) | `templates/structured-dashboard.html` | The only report design. One file covers light and dark mode, with the toggle built in. |

## Rules that never bend

- **CPA is the headline efficiency metric. Never show cost per lead.**
- **Conversion rates use Leads as the denominator, never Clicks.** Every report carries: "All conversion metrics calculated based on Leads, not Clicks."
- **Never invent or estimate a number.** No projections or close-rate promises.
- **No selling to active accounts:** no "Why GOAL", no "% exclusive" card, no "they chose you". Add persuasion only when the user explicitly asks.
- **Nothing internal reaches the client:** no bid multipliers, bids, bid rate, win rate, RightPricing, or source-settings data.
- **Brand:** Sora for headings and numbers, Outfit for text, both already loaded. Colors only from the template's tokens (brand blue `#057BE5`, ink `#001020`, amber for Refining). No emoji, no new gradients, no Inter. The magenta `#E83A89` is for marketing pages, never reports.
- **Logo:** black wordmark in light mode, white in dark mode; both are wired in the sidebar and switch automatically. Never recolor or stretch them.
- **Light/dark toggle on every report:** opens in the viewer's system theme, the toggle overrides it, print is always light. A report without the toggle is not finished.

## Retired

These were removed on consolidation and should not be rebuilt unless the user asks: the Refined Light and Navy Editorial client templates; the navy-sidebar v1 Structured Dashboard with Inter and the executive-summary box; the internal data-dense dashboard; the "Why GOAL leads are different" section; the "% exclusive" KPI card; the "Our current objective" close-rate finale; CPL anywhere; the old CSV-to-HTML generator script and its pre-refresh color palette.
