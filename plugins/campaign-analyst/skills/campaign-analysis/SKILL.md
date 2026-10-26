---
name: campaign-analysis
description: This skill should be used when the user invokes "campaign-analysis" directly, asks to "analyze a GOAL client campaign", "diagnose campaign performance", "generate bid recommendations", "review campaign data", "what's wrong with this campaign", or provides GOAL Platform CSV data and asks for optimization recommendations. Also triggers when the user mentions bid multipliers, source-level diagnosis, win rate analysis, RightPricing calibration, or GOAL Platform performance troubleshooting for any client account.
---

# GOAL Platform Campaign Analysis

Diagnose GOAL Platform client campaign performance and generate calibrated bid optimization recommendations using a systematic four-layer analytical framework. The final output is a polished, shareable HTML report.

## Copy guidelines (mandatory)

Reports deliver information and present it visually. Any objective or narrative is accomplished through the visuals and through the account manager's live conversation — never through report copy.

**Core principle:** accurate metrics plus a clean visual. No narrative, no opinion, no filler. If the data cannot visually make the point, stop and flag it to the account manager with alternative visual options.

### Voice and framing
- Never address the client by name in body copy. Identity belongs in the header/sidebar metadata only ("Prepared for [Name]").
- Frame account actions as "we" — the account manager operates the campaign ("We increased the daily budget from $50 to $95").
- Never reference the client's emotions, expectations, or shortfalls ("you expected more volume", "the first day did not deliver", "that is a fair frustration" — all banned).
- Concise, professional, straightforward. No flowery, creative, or descriptive language. No metaphors. No rhetorical constructions ("every update is aimed at that number").

### Section headers and sub-copy
- Sub-headers carry scope and dates only ("June 1–9"). Never interpretive claims ("every stage after the impression is strong" — unclear jargon, implies an unstated problem, raises questions instead of answering them).

### Chart and figure notes
- State the metrics, nothing else: "Shoppers click the ad about half the time it is shown (48.8%); about three quarters of clicks become a lead or a call (72.5%)."
- No commentary on what metrics mean ("the ad is doing its job", "the constraint is visibility"). Strong metrics are weakened by added praise; conclusions are delivered in conversation.
- Plain-language labels for non-expert readers ("Your ad shown" with a small "impressions" sublabel).

### Every report accomplishes two things
1. **Current status over a reasonable time window.** Choose a window and visual that make single-day judgments visibly premature (e.g., daily lead events and daily spend across 3+ weeks, with non-delivery days hatched). The data makes this point — never state it in copy.
2. **The updates being made and the data behind them.** Present updates as opportunities toward the stated objective (e.g., more volume), not as a list of what was broken. Each update pairs with the specific metric that motivated it.

### Hard bans recap
Client name in body copy · client emotions/expectations · narrative or opinion sentences · metaphor · interpretive sub-headers · chart commentary beyond the metrics · unexplained jargon · projections or estimated results in client-facing update reports.

## Framework Overview

The analysis operates across four layers, each building on the previous:

| Layer | Name | Purpose |
|-------|------|---------|
| 1 | Client Context | Parse the stated problem, willingness to adjust, and implicit constraints |
| 2 | Campaign Trends | Build monthly trend tables, calculate baselines, classify root cause |
| 3 | Source Diagnosis | Drill into source settings to classify each source's problem type |
| 4 | Market Calibration | Cross-reference effective bids against RightPricing market data |

**Critical rule:** Source-level performance data alone is insufficient for bid recommendations. Without market pricing context (RightPricing report), it is impossible to determine whether the issue is bid amount, bid rate, targeting, or filter settings. Always request RightPricing data before finalizing bid recommendations.

**Bid lever neutrality:** When analysis indicates a bid increase is needed, always evaluate both raising the base bid and adjusting source multipliers. Choose the lever that best fits the data — do not default to either. See the Base Bid vs. Multiplier Decision Framework in `references/analysis-framework.md`.

**Target Position Philosophy (AM rule, 8/25/26):** Home and Auto both target the **band between 2nd and 1st position**. Where a source sits inside the band is a per-account call, stated with its reason:

- **Sit near 2nd** for split or tight budgets, new launches, unproven or low-intent sources, or caps that fill early in the day.
- **Move toward 1st** when volume is the priority and the budget has headroom, the source has proven CPA, the geo is restricted, or the auction is volatile.
- **Clearing 1st** on Home or Auto needs a stated reason and the account manager's go-ahead. A 1st-heavy market (position share) is a diagnostic, not by itself a reason to price to 1st.

The underlying discipline still holds: don't overpay for a higher position than the account needs. A source below 2nd RPC is below target on both verticals.

## Workflow

### Step 1: Gather Inputs

**The user supplies all data. Claude has no access to the GOAL dashboard, Periscope/Sisense, or the client's CRM** — it cannot pull or export anything itself. The user exports these and pastes/uploads them; Claude analyzes what is provided. If something is missing, ask the user to export and provide it.

Before beginning analysis, collect the following from the user:

**Required:**
- Monthly Campaign CSVs (minimum 3 months, 6 ideal) — exported from the GOAL dashboard containing Searches, Impressions, Clicks, Leads, Calls, CTR, Cost, Avg CPC, Avg Bid, Avg Pos, Win Rate, Sold, Sold CVR, Sold CPA, Sold Rev
- Client message or context — the stated problem, questions, or goals

**Strongly Recommended:**
- Source Settings Export — CSV showing all traffic sources with Status, Source Name, Bid Multiplier, Opportunities, Bids, Bid Rate, Impressions, Clicks, Leads, Calls, Win Rate, Sold, CPC, Profit, CM
- RightPricing Report — market-level pricing showing RPC at each ad wall position (1st, 2nd, 3rd+) broken down by source type. **This is the single most important input for calibrating bid recommendations.**
- By-Hour Analytics export (Group By `Hour`, one campaign): when the concern is contact rate, volume, the daily cap filling early, or CPA by time of day. It is in Pacific time; see `references/schedule-optimization.md` before reading it.
- Current campaign schedule: **supplied by the user**, usually screenshots of each weekday's tab: every day's Active state, the % for each hour, and the schedule's time zone. Needed for any schedule recommendation or volume complaint. If it is missing, ask for it, including the time zone and any day not shown; never assume an unseen day matches a seen one, and never look for it in the dashboard (Claude never opens a campaign's settings page).

**Optional:**
- By-Day-of-Week Analytics export (Group By `Day of Week`): pulled with the by-hour file, because the schedule is set per weekday
- Ad Group Settings (targeting filters, age ranges, coverage types)
- Change History (platform changes made by the agent)
- Competitive Context (competitor activity, new market entrants)
- Client disposition data (contacted, quoted, bound from their CRM)

If data is missing, note which layers will be limited and proceed with what is available. Flag missing RightPricing data as a critical gap.

### Step 2: Execute the Four-Layer Analysis

Work through each layer sequentially. Consult `references/analysis-framework.md` for detailed procedures, diagnostic matrices, and decision trees at each layer.

**Layer 1 — Client Context Parsing:**
- Extract the stated problem (low volume, high CPA, declining ROAS, etc.)
- Identify willingness to adjust (bid, budget, targeting, sources)
- Note implicit constraints — respect the scope of the client's ask
- Route a contact-rate complaint to the contact-rate playbook in `references/schedule-optimization.md` (hours, then geo, then source, then agency-side checks), because GOAL can optimize by hour where other vendors cannot

**Layer 2 — Campaign Trend Analysis:**
- Build monthly trend table from CSVs
- Handle partial months using projection formula
- Calculate baselines (averages across complete months)
- Quantify performance gaps (lead volume, win rate, impression share, spend)
- Classify root cause using the diagnostic matrix (see `references/diagnostics-and-formulas.md`)
- For accounts under 90 days, use leading indicators (Contact Rate, Quote Rate) instead of Sold CPA
- **Hourly check** (when the by-hour export is provided; run the four time zone checks in `references/schedule-optimization.md` first): Budget Constraint → cap-timing playbook (is spend front-loaded into the morning?); contact-rate concern → contact rate by hour; volume complaint → audit the schedule the user supplied

**Layer 3 — Source-Level Diagnosis (Three-Metric Funnel: Target Rate → Bid Rate → Win Rate):**
- Filter to active sources with Opportunities > 0
- **Gate 1 — Target Rate:** Evaluate opportunity volume per source. Low opportunities = "Kiss of Death" (over-filtering). Do NOT adjust bids; relax upstream filters. Keep targeting "lean and mean" — use bid modifiers for preferences instead of hard exclusions.
- **Gate 2 — Bid Rate:** Check for ad group cannibalization (geographic overlap) — the primary cause of low bid rate. DO NOT raise multipliers on low-bid-rate sources.
- Calculate effective bids: Base Bid × (Multiplier / 100)
- Rank sources by opportunity volume (focus impact on high-volume sources)
- **Gate 3 — Win Rate:** Identify low-win-rate sources as the ONLY candidates for multiplier increases. Cross-reference with RightPricing data before acting.
- **Schedule audit and hourly analysis** (`references/schedule-optimization.md`): flag business hours set below 100%, blocked hours (including noon), inactive days, and wide swings; rank hours by the client's KPI (contact rate, inbound calls, or item CPA) with thin hours merged to clear the 30-lead floor; find hours that carry spend at below-average results and hours that pair strong results with real volume

**Layer 4 — Market Pricing Calibration:**
- Map each source's effective bid to RightPricing market positions
- Cross-reference position with source problem type to generate the recommendation
- **Determine the optimal bid lever** — base bid raise vs. source multiplier adjustment. Evaluate both options using the decision framework in `references/analysis-framework.md` and choose based on the data pattern.
- Calculate target values for the chosen lever: Target Multiplier = (Target RPC / Base Bid) × 100%, OR Target Base Bid = Target RPC / (Source Multiplier / 100)
- Apply 20–30% geo-buffer if targeting is severely restricted
- Round up 5–10% for bid volatility

### Step 3: Generate Recommendations

Categorize all recommendations into three groups:

1. **Bid Adjustments** — Either base bid changes or source multiplier changes (or both), chosen based on the data pattern. For each recommendation, include the current value, recommended value, resulting effective bid, target market position, and a brief rationale for why this lever was chosen over the alternative. Apply proportional incremental changes rather than arbitrary flat increases.
   - **Schedule Adjustments** (sub-group): hour-of-day changes in the table format from `references/schedule-optimization.md` (day, hour in the schedule's zone and in agent local time, current %, recommended %, leads, contact rate, spend, why), ranked by leads affected; Volume Impact Potential does not apply to hours. Ask before an hour moves more than 25%, an hour with leads goes to 0%, a raised hour pushes a Home or Auto source past 1st RPC, or the account is paused, cancelled, or under 90 days. Never change the live schedule.

2. **Investigation Items** — Anomalies that cannot be resolved by bid changes alone. Flag for follow-up with the client or GOAL product team.

3. **Hold Steady** — Sources performing well that should not be changed. Explain why leaving them alone is deliberate, not an oversight.

**Prioritize by impact:** Rank recommendations by Volume Impact Potential = Opportunities × (Target Bid Rate − Current Bid Rate) × Expected Win Rate.

**Respect client constraints:** Map recommendations back to Layer 1 willingness. Do not recommend 3× increases if the client said "a little."

### Step 4: Build the Output Report

Generate a polished, standalone HTML file following the template in `references/output-template.html`. The report should be professional enough for client-facing delivery.

**Report structure:**
1. Executive Summary: one-paragraph diagnosis with root cause classification
2. Campaign Trend Dashboard: monthly metrics table with baseline comparisons and gap indicators
3. Source Performance Matrix: source-by-source breakdown with problem classification and current vs. recommended bids
4. Market Position Map: effective bids plotted against RightPricing positions (when data available)
5. Hourly Performance: leads, contact rate, and spend by hour in agent local time, zone named, with the current schedule % beside each hour (when the by-hour export is provided)
6. Recommendations Table: prioritized by impact, categorized into bid adjustments (base bid and/or multiplier changes, plus schedule adjustments), investigations, and hold-steady
7. Methodology Notes: brief explanation of the analysis framework for client transparency

**Styling:**
- Client-facing reports are built with the `goal-client-report` skill in this plugin; this skill's diagnostic report keeps its own template.
- GOAL primary blue (#057BE5) as the accent, navy (#00172D) masthead, Inter throughout.
- Color-coded status indicators: green = performing (#2BBF7A), amber = investigate (#F0A93B), red = action needed (#E5484D).
- Responsive design that works on screen and prints cleanly (`@media print`).
- Self-contained delivery: the GOAL wordmark lives in `../assets/` — keep that folder beside the HTML or inline the logo as a base64 data URI before sending. Inter loads from Google Fonts with a system-sans fallback.

### Step 5: Present and Iterate

Share the HTML report. Offer to:
- Adjust specific recommendations based on feedback
- Generate a PDF version for formal delivery
- Deep-dive into any individual source or metric
- Re-run the analysis with updated data

## Key Formulas

| Formula | Calculation |
|---------|-------------|
| Effective Bid | Base Bid (Avg Bid from CSV) × (Source Multiplier / 100) |
| Target Multiplier | (Target RPC / Base Bid) × 100% |
| Target Base Bid | Target RPC / (Source Multiplier / 100) |
| Projected Monthly Value | (Actual Value / Days Elapsed) × Total Days in Month |
| Impression Share | Impressions / Searches (from campaign CSV) |
| Bid Rate | Bids / Opportunities (from source settings) |
| Win Rate | Wins (Impressions) / Bids (from source settings) |
| Volume Impact Potential | Opportunities × (Target Bid Rate − Current Bid Rate) × Expected Win Rate |
| Hourly Contact Rate | Contacted / Leads for the hour (never the export's click-based `Contacted CVR`) |
| Hourly Effective Bid | Ad Group Base Bid × (Source Multiplier / 100) × (Campaign Modifier / 100) × (Hour % / 100) (AM rule, 10/16/26: the hour % stacks on every other modifier) |

## Critical Guardrails

- **Follow the Three-Metric Funnel in order.** Target Rate → Bid Rate → Win Rate. Each is a gate. Diagnose and fix upstream issues before looking downstream.
- **Never recommend bid increases without RightPricing context.** A source appearing to need a higher bid may already be above first position — the problem is elsewhere. If already bidding above 1st position RPC but win rate is still low, raising the bid further will not help.
- **Do not treat all sources equally.** A 10% change on a 2,000-opportunity source is vastly more impactful than a 50% change on a 40-opportunity source.
- **Watch for the "Kiss of Death" — over-filtering.** Low opportunity volume almost always means overly restrictive targeting. Keep filters "lean and mean" — use bid modifiers for preferences, hard filters only for absolute disqualifiers.
- **NEVER raise multipliers on low-bid-rate sources.** Low bid rate means the source barely enters auctions — almost always caused by Ad Group Cannibalization. Raising the bid just overpays on the tiny fraction of auctions entered. Fix is structural/upstream.
- **Win Rate is the ONLY valid trigger for raising a multiplier.** Normal bid rate + low win rate = the one and only scenario where increasing a source multiplier is appropriate.
- **Never judge account health by blended CPA alone.** A high blended CPA is often caused by one un-optimized Premium Referral source. Always isolate Paid Search performance first.
- **Multiplier math matters.** Setting multiplier to 20% means bidding at 20% of the base bid, not a 20% increase. A 20% increase requires setting to 120%.
- **The schedule is a bid adjustment, and 0% is off.** Each hour's % scales the ad group's base bid for that hour and stacks on source multipliers and campaign modifiers; it is not just an activation window.
- **Business hours well below 100% win little.** Competitors bid at or above 100% then, so a 50% business hour usually wins close to nothing, not half. Check the schedule first on any volume complaint.
- **Hourly data is Pacific: convert before analyzing.** Run the four time zone checks in `references/schedule-optimization.md` every time; this is where hourly analysis most often goes wrong.
- **Never open or export anything from a campaign's settings page.** The user supplies the current schedule; ask for it when it's needed and missing.

## Reference Files

- **`references/analysis-framework.md`**: Detailed Layer 1–4 procedures, diagnostic decision trees, maturity phase analysis for accounts under 90 days, and the schedule (hour-of-day) optimization step
- **`references/schedule-optimization.md`**: How the campaign schedule works, the Pacific-time checks for the by-hour export, the sample floor, the contact-rate / cap-timing / volume / CPA playbooks, the Schedule Adjustments format and ask-first triggers, and client-facing rules
- **`references/diagnostics-and-formulas.md`**: Root cause classification matrix, source problem diagnostic matrix, market position mapping table, recommendation crossover matrix, common pitfalls with explanations, and complete analysis checklist
- **`references/output-template.html`**: Base HTML template for the final report artifact with GOAL branding, responsive layout, and print styles
