---
name: right-pricing
description: This skill should be used when the user asks to "right-price a campaign", "set source modifiers", "calibrate bids from RightPricing data", "price traffic sources", "set up source-level bidding", "calculate source multipliers from Periscope data", or provides RightPricing market data (RPC by source and position) and wants to determine the correct base bid and source modifier percentages for a GOAL client campaign. Also triggers when the user mentions right-pricing, source pricing, traffic source modifiers, RPC-to-multiplier conversion, or Periscope pricing data.
---

# Right Pricing a GOAL Campaign

Calculate the optimal base bid and per-source bid modifiers for a GOAL client campaign using RightPricing market data from Periscope. The goal is to set bids that accurately reflect the relative value of each traffic source so the client wins the right ad position at a fair, budget-sustainable price.

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

## Core Principles

1. **Anchor the Base Bid.** Base the campaign bid on one high-volume, mid-cost source.
2. **Price Proportionately.** Price every other source as a percentage multiplier of that anchor base bid.
3. **Target the 2nd-to-1st band (Home and Auto, AM rule 8/25/26).** Every Home and Auto source is priced into the band between its 2nd- and 1st-position RPC. Where it sits inside the band is a per-account call, stated with its reason (Step 4). A source below 2nd RPC is below target on both verticals.
4. **Clearing 1st needs a reason and the account manager's go-ahead.** Pricing above a source's 1st-position RPC is an aggressive call for explicit growth intent with budget headroom, a heavily restricted geo, or a premium search channel worth dominating. A 1st-heavy market (position share) is a diagnostic, not by itself a reason to clear 1st.
5. **Band prices assume a 100% hour.** The campaign schedule adjusts the bid for each hour (0% to 300%, set per weekday). The hour's % multiplies the ad group's base bid and stacks on the source multiplier and any campaign modifiers (AM rule, 10/16/26), so an hour above 100% can push a band-priced source past its 1st RPC and an hour below 100% drops it under 2nd. See Step 5.

## Required Inputs

**The user supplies all data. Claude has no access to Periscope/Sisense or the GOAL platform** — it cannot pull reports or exports itself. The user pulls them and pastes/uploads them; Claude validates and analyzes what is provided. If an input is missing, ask the user to pull and provide it.

Before beginning, collect these from the user:

1. **RightPricing Data** — the Periscope RightPricing Report filtered to **one state and one vertical** (e.g., Auto – TX), trailing **exactly 7 days**. Shows RPC at each ad position by source plus volume signals.
2. **Target Cost Per Lead (CPL)** — the client's target CPL aligned with their monthly budget and volume goals. Used to validate that the proposed bid is mathematically realistic.
3. **Campaign Base Bid** — the current base bid (for a re-price) or none (for a new setup, where the base bid is calculated in Step 3).
4. **Expected Click-to-Lead Rate** — needed for the CPL sanity check. If unknown, use a vertical default and flag the assumption.
5. **Current campaign schedule** (re-prices of live campaigns): screenshots of each weekday's tab plus the schedule's time zone, supplied by the user. Needed only to check whether the schedule is flat at 100%. Claude never opens a campaign's settings page; if the schedule is needed and missing, ask for it.

## Workflow

### Step 1 — Validate the Report the User Provides

The RightPricing report is pulled and supplied by the user; Claude validates the copy that is pasted/uploaded. When the user pulls it from **Periscope / Sisense → RightPricing Report**, confirm it was configured as follows (if not, ask them to re-pull):

- Filtered to **one state and one vertical** (e.g., Auto – TX). **Never use blended data across multiple states** — it produces meaningless averages.
- Set the date range to **exactly the trailing 7 days. Do not expand this window under any circumstance** — a longer window pulls in seasonal noise and outdated competitive shifts that distort the real-time auction landscape.
- **CRITICAL — Suppress the Inventory Matrix:** Totally **remove or hide the `Inventory` column** before any landscape analysis. It represents *all matching programmatic auctions*, not realized traffic, and creates wildly unrealistic volume expectations.
- **`clicks` is the EXCLUSIVE volume signal.** Evaluate true audience density only from the `clicks` column — never from Inventory.
- **Primary cost column:** Look primarily at **`second_rpc`** (the cost for 2nd position).
- **Filter out interface ghosts:** Actively remove every row where **Opportunities = 0**. This is a known interface behavior that populates the export with duplicate zero-volume ghost channels — optimizing them wastes resources.

### Step 2 — Read the Landscape

1. **Sort by `clicks` (descending).**
2. **Evaluate the position spread** and prioritize the top-volume sources — these drive campaign performance.
3. **Group the sources into cost tiers:**
   - **High-cost / high-intent:** Premium Search channels (Home Search, Auto Search).
   - **Mid-cost:** Large referral networks or mid-tier traffic — *your anchor usually lives here.*
   - **Low-cost:** Broad or lower-tier traffic.

### Step 3 — Set the Base Bid

1. **Choose the anchor source.** Pick a **high-volume, mid-cost channel among the top ~5 by `clicks`**. It should be representative of the market — neither the cheapest (would underbid everything) nor the most expensive (would overbid low-value sources). A mid-tier referral source at 2nd position is the most common pick. See the reference file for the precise median-selection logic.
2. **Set the base bid:** `Base Bid = Anchor's 2nd-position RPC` (`second_rpc`).
3. **Sanity check the client's target:**
   ```
   Implied CPC = Target CPL × Click-to-Lead Rate
   ```
   If the implied CPC is far below the cheapest market positions, the client's lead target is mathematically unrealistic. Surface this immediately — the fix is a higher CPL, a better click-to-lead rate, or restricting to the cheapest sources (see reference file, Edge Case 4).

### Step 4 — Set Each Source's Target Bid

For each source, determine the **Target Bid** — the bid required to win the *desired* ad position for that vertical. This is the value the modifier is built from, not the raw market CPC.

- **Base rule:** `Target Bid = the desired position's RPC`, plus whatever placement cushion the account calls for (next bullet). The proportional modifier math (Step 5) runs off that Target Bid.
- **Placement within the target range is a per-account call, not a fixed cushion.** Decide how far above the desired position's RPC each source should sit, based on the account's situation, and state the choice and the reason for each source or source group in the output.
  - **Sit at or just above the position RPC** when the budget is split or tight, the account is new or just launching, the source is unproven or low-intent, or the daily cap is already filling early in the day. For a cap that fills early, the alternative is to keep the band prices and lower the morning hours in the schedule so the budget reaches the rest of the day (`../campaign-analysis/references/schedule-optimization.md`, cap-timing playbook).
  - **Move further up, toward the next position's RPC,** when volume is the stated priority and the budget has headroom, the source has proven CPA from disposition data, the auction is volatile, or the market is 1st-heavy and day 4–7 win rate is still lagging.
  - The California example (no cushion) and the Colorado example (+10%) show two points on that range. Neither is the default; the account decides.
- **Geography buffer (situational, applied BEFORE the multiplier calc):** if the client heavily filters their territory (e.g., an isolated 50-mile office radius, or a strict list of ~15 zip codes rather than a clean full-state layout), the baseline market RPC will underdeliver. **Inject a 20%–30% premium onto the source Target Bids before running the multiplier calculation.**
- **Missing or thin data:**
  - **No 2nd-position data:** use **~90% of 1st-position RPC**.
  - **Thin 2nd-position data:** use **~85% of 1st-position RPC**.
- **Ceiling:** when 2nd is the target, stay below the source's 1st-position RPC. How close to 1st you go is part of the placement call above, not a fixed percentage. Clearing 1st is an aggressive strategy (Core Principle 4, Step 6) and needs a stated reason and the account manager's go-ahead.

### Step 5 — Calculate Modifiers

1. **The anchor source is fixed at 100%.**
2. **For every other source:**
   ```
   Source Multiplier = (Source Target Bid / Base Bid) × 100
   ```
3. **Verify each one:**
   ```
   Effective Bid = Base Bid × (Modifier / 100)
   ```
4. **Important math rule:** a **20% increase means setting the multiplier to 120%.** Setting it to 20% drops the bid to 20% of the base bid (a massive *decrease*). Always double-check direction.
5. **Rounding:**
   - Round to the **nearest 5%**. If the result is **97–103%, just keep it at 100%**.
   - For modifiers **over 200%, round to the nearest 10%**.
6. **Tier 1 is never under 100%.** Whatever the math says, Tier 1 sets at 100% or 110% (Step 6).

**Schedule check.** If the schedule the user supplied isn't flat at 100%, add two columns to the table: the effective bid at the **highest** and at the **lowest** scheduled % (Effective Bid × campaign modifiers × Hour % / 100, per ad group; use the highest campaign modifier for the 1st-RPC check). Flag any Home or Auto source whose highest-hour effective bid clears its 1st RPC (ask the account manager first) and any whose lowest business-hour effective bid falls under its 2nd RPC.

Present the complete table:

| Source | RPC (target position) | Target Bid | Modifier | Effective Bid | Notes |
|--------|----------------------|----------------------|----------|---------------|-------|
| [Anchor] | $X.XX | $X.XX | 100% | $X.XX | Base bid anchor |
| [Source B] | $X.XX | $X.XX | XXX% | $X.XX | [vs anchor] |
| [Premium Search] | $X.XX | $X.XX | XXX% | $X.XX | High-intent, elevated modifier |

### Step 6 — Special-Source Rules & Exceptions

- **Premium / Home Search:** hyper-expensive, high-intent channels. High-intent search clicks require **hyper-aggressive elevation** to maintain competitive traction — modifiers commonly land **between 200% and 400%** (see the California Home example, where Home Search calibrates to 400%). If the budget can't sustain it, **cap the modifier and accept lower positioning** rather than starving the rest of the campaign.
- **Premium Referral (both verticals):** notoriously high-volume but low-intent — it risks damaging campaign delivery across **both Home and Auto** by draining the client's cash balance on low-intent clicks. On brand-new setups, proactively apply a defensive down-bid right out of the gate: **70% on Home**, and **65%–70% on Auto**.
- **Tier 1 (team rule, 10/8/26): never bid it down.** Tier 1 is the best source, so its modifier is **100% (baseline) or 110%**, never below 100%. This applies in every vertical and every pricing mode, and to every Tier 1 row if the campaign has more than one.
  - If the Step 5 math puts Tier 1 under 100% (the anchor prices above it), set **100%** anyway and note that the rule overrode the math.
  - If the math puts it above 110%, set **110%** and flag what the band would need (modifier and effective bid) so the account manager can approve going higher.
  - Tier 1 is exempt from defensive down-bids, the ~65% floor in a tiered or split-budget build, budget-fit trims in Step 7, and the money-pit down-bid in Step 8. If Tier 1 underperforms, check targeting, bid rate, and the agency's speed-to-lead instead of the bid.
  - Tier 1 can still be the anchor, which fixes it at 100%.
- **Geography buffer:** if the client heavily restricts their territory (e.g., a 50-mile office radius or ~15 zip codes instead of a clean full-state layout), inject the **20%–30% premium onto the source Target Bids _before_ the multiplier calc** (Step 4). Standard market RPC will underdeliver in tightly filtered geos.
- **UI ghosts (thin/no data):** already filtered in Step 1 (Opportunities = 0) — don't optimize zero-volume ghost channels.
- **Zero wins despite aggressive RPC:** this signals a **targeting conflict or timeout, not a bid problem. Do NOT raise bids further.** Route to investigate internal campaign competition — conflicting demographic restrictions, or overlapping geographic ad groups cannibalizing the same auction.

### Step 7 — Reconcile Against Budget

1. **Estimate the blended CPC**, weighted by each source's projected volume share.
2. **Confirm fit:** does the implied CPL fit within the client's daily/monthly budget?
3. **Flag disproportionate spenders** (usually Premium Search).
4. **Decision rule:** if proper right-pricing exceeds the client's budget, **recommend a budget increase rather than starving high-quality sources.** Capping a premium channel is acceptable; gutting the whole strategy to fit an undersized budget is not. Tier 1 is never the source you trim to fit the budget.

### Step 8 — Optimize with Disposition Data (Ongoing)

**Guiding principle: start aggressive to capture volume, then peel back. CPA matters more than CPL.**

- **Maturity Phase Rule (accounts < 90 days):** CPA is unreliable early because policies take time to close. Optimize on **leading indicators** instead:
  - **Contact Rate** (Contacted / Leads): typical **20 to 40%**. Over 50% almost always means a disposition mapping error; under 5% is a red flag (wrong status column or dispositions not imported). Below typical, work the contact-rate playbook in `../campaign-analysis/references/schedule-optimization.md` (hours, then geo, then source, then agency-side checks) before touching source bids.
  - **Quote Rate** (Quotes / Leads): typical **8 to 20%**; under 5% is a red flag.
- **Overlay data:** match phone numbers to imported quote and bind statuses to calculate **true CPA by source.**
- **Honey Holes** (low CPA, strong bind rate) → **bid up.**
- **Money Pits** (high spend, zero sales) → **bid down toward ~65%.** Turn a channel completely off **only as a last resort**, after multiple bid reductions fail to make it profitable. **Except Tier 1:** it never goes below 100%. If Tier 1 looks like a money pit, check targeting, bid rate, and the agency's speed-to-lead instead.

## Monitoring Cadence & Red Flags

| Timeframe | Action |
|-----------|--------|
| Days 1–3 | Confirm impressions and clicks are flowing. |
| Days 4–7 | Review win rate by source. **Under ~5% on a bid-up source = bid still too low or targeting conflict.** |
| Week 2 | Pull a fresh Periscope report; compare market shifts. Run a pacing check (Projected Monthly Leads). |
| Weeks 3–4 | Evaluate CPL vs. target and CPA vs. target. |
| Monthly | Full campaign re-price based on disposition data. |
| Quarterly | Deep-dive client review. |

**Red Flags:**

- **Budget caps before midday** → lower the morning hours in the schedule so the budget reaches later hours (needs the user's schedule), or sit sources nearer 2nd. Confirm against daily pacing first.
- **0% win rate after a bid increase** → stop raising; investigate targeting/timeout.
- **CPA above $675 — the "Sideways Benchmark."** Anything **under $675 is neutral or profitable**; anything **consistently over $675 is a loss** and requires an immediate pivot.

## Master Formulas Reference

| Formula | Calculation |
|---------|-------------|
| Source Multiplier | `(Source Target Bid / Base Bid) × 100` |
| Effective Bid | `Base Bid × (Modifier / 100)` |
| Implied CPC | `Target CPL × Click-to-Lead Rate` |
| Projected Monthly Leads | `(Leads to Date / Days Elapsed) × Total Days in Month` |
| Blended CPC Estimate | `Σ(Source Effective Bid × Source Volume Share)` |

## Critical Guardrails

- **One state, one vertical, trailing 7 days.** Never blend states or pull stale data.
- **Kill the Inventory column.** Use `clicks` for volume and `second_rpc` as the primary cost reference.
- **Never skip the CPL sanity check.** If the math doesn't support the target, say so before setting modifiers that will inevitably miss.
- **Multiplier math matters.** 120% = a 20% increase. Setting 20% bids at 20% of base.
- **Band prices assume a 100% hour.** When the schedule isn't flat, show effective bids at the highest and lowest scheduled %, and never open the campaign settings page to find out: the user supplies the schedule.
- **Never bid down Tier 1.** It sits at 100% or 110%, never below 100%, whatever the modifier math or a budget squeeze says. Going above 110% needs the account manager's go-ahead (team rule, 10/8/26).
- **Don't over-optimize low-volume sources.** Precision on a 10-click source is wasted effort — use round numbers and monitor.
- **Don't raise bids to fix a 0% win rate after a bid-up.** That's a targeting/timeout signal, not a price signal.
- **Re-price regularly.** Monthly on disposition data; full re-pull each month; quarterly deep dives.

## Integration with Campaign Analysis

When used alongside the `campaign-analysis` skill:

- Right Pricing feeds **Layer 4 (Market Calibration)** of the campaign analysis framework — the modifiers calculated here are the same ones the recommendation engine references.
- Campaign analysis may **trigger** right-pricing when the diagnosis shows source modifiers are miscalibrated against market RPC.
- **Post-analysis right-pricing** is the most common workflow: the analysis finds misaligned bids, and right-pricing supplies the corrective modifier values.

## Reference Files

- **`references/right-pricing-logic.md`** — Anchor-selection decision tree, edge cases (thin data, no data, sub-floor CPL, re-pricing), special-source detail, worked examples with Target Bid + buffer, rounding tables, and the full monitoring/red-flag breakdown.
