# Detailed Analysis Framework

Complete procedures for each analytical layer, including decision trees, advanced tactics, and edge case handling.

## Layer 1: Client Context Parsing

Every analysis begins with the client's message. This step establishes the problem frame and determines which levers the client is willing to pull.

### Step 1: Extract the Stated Problem

Read the client message and identify the specific complaint. Common categories:

- **Low lead volume** — not receiving enough leads
- **High CPA** — cost per acquisition is too high
- **Low conversion rates** — leads are not converting to quotes or sales
- **Declining ROAS** — return on ad spend is dropping
- **General performance decline** — a vague sense that things are off

### Step 2: Identify Willingness to Adjust

Determine what the client has explicitly said they are open to changing. This directly constrains recommendations. Common levers:

- Raising bids
- Increasing budget
- Expanding targeting (geography, demographics)
- Adding new sources
- Adjusting schedules (hour-of-day bid adjustments)

### Step 3: Note Implicit Constraints

What the client did NOT say is equally important. If they only mention bids, do not recommend budget changes without flagging it as an additional option. If they said "a little," do not recommend 3× increases. Respect the scope of their ask.

**Example:** Client says "We're still getting really low volume of leads. How do we fix that? I don't mind raising the bid or budget a little." This means:
- Problem: Low lead volume
- Willingness: Raise bid or budget "a little" (moderate, not aggressive)
- Implicit constraint: "A little" suggests incremental changes, not 2× increases

---

## Layer 2: Campaign Trend Analysis

This layer uses monthly campaign CSVs to establish baselines, identify the performance gap, and classify the root cause.

### Step 1: Build the Monthly Trend Table

Extract these metrics from each monthly CSV and compile into a single table:

| Metric | What It Reveals |
|--------|-----------------|
| Searches | Total market demand — is the market shrinking or stable? |
| Impressions (& %) | How often the client's ad is shown. Impression Share = Impressions / Searches. A drop means competitors are outbidding. |
| Clicks | Traffic received. CTR = Clicks / Impressions. Drop in CTR may indicate ad quality or position issues. |
| Leads | Primary volume metric — usually the core client complaint. |
| Cost | Total spend. Rising cost with falling leads = efficiency problem. |
| Avg CPC | Actual cost per click. Compare to Avg Bid to see auction efficiency. |
| Avg Bid | Client's bid level. Has it changed? Is it keeping pace with market? |
| Win Rate | % of bids that win the auction (Impressions / Bids). THE most diagnostic metric for competitive positioning. |
| Sold / Sold CPA | Downstream conversion and cost-per-acquisition. Tells if leads actually convert. |

### Step 2: Handle Partial Months

If the current month is incomplete, project the full month:

```
Projected Monthly Value = (Actual Value / Days Elapsed) × Total Days in Month
```

Apply this to Leads, Searches, Cost, and other volume metrics. Clearly label projected values as estimates. The projection becomes more reliable after 10+ days of data.

### Step 3: Calculate Baselines and Identify the Gap

Compute the average of each metric across all complete months. Then compare the current/projected month to the baseline:

- **Lead Volume Gap:** How many fewer leads vs. average? What % below baseline?
- **Win Rate Gap:** Current win rate vs. historical average. A drop >3 percentage points is significant.
- **Impression Share Gap:** Current vs. average. Drops >5pp indicate competitive pressure.
- **Spend Gap:** Is spending lower because of fewer wins, or has budget been reduced?

### Step 4: Root Cause Classification

Use this diagnostic matrix to determine the primary root cause category:

| Searches | Win Rate | Impression Share | Diagnosis |
|----------|----------|------------------|-----------|
| Stable/Up | Down | Down | **Competitive Positioning** — being outbid |
| Down | Stable | Stable | **Market Demand Decline** — fewer searches in market |
| Stable/Up | Stable | Down | **Budget Constraint** — running out of daily budget |
| Down | Down | Down | **Market + Competitive** — both factors at play |

### Step 5: Maturity Phase Analysis (Accounts Under 90 Days)

For accounts active less than 90 days, standard CPA-driven analysis produces unreliable results. Disposition data takes time to mature — leads must move through the quoting and binding process before Sold CPA becomes meaningful.

**Use leading indicators instead of CPA for new accounts:**

- **Contact Rate** = Contacted / Leads. Typical 20 to 40%.
- **Quote Rate** = Quotes / Leads. Typical 8 to 20%.

| Contact Rate | Quote Rate | Interpretation |
|-------------|------------|----------------|
| 20 to 40% | 8 to 20% | Typical. The agency is working and quoting leads. Hold current settings; CPA will mature. |
| Over 50% | Any | Almost always a disposition mapping error ("Transferred" or "Contact Attempted" mapped to contacted). Check the import before reading anything else. |
| 40 to 50% | Any | Above typical. Confirm the mapping before treating it as a strength. |
| 20 to 40% | Under 5% | Contacted but not quoting. Possible targeting mismatch or lead quality issue. Investigate filters and ad group settings. |
| 5 to 20% | Any | Low contact. Work the contact-rate playbook in `schedule-optimization.md`: hours, then geo, then source, then agency-side checks (speed-to-lead, Do Not Call statuses, removed or archived leads, call logs). |
| Under 5% | Any | Red flag. Usually the wrong status column, an overly strict mapping, or dispositions not yet imported. Confirm the import before diagnosing the agency. |

---

## Layer 3: Source-Level Diagnosis

Once the campaign-level root cause is established, drill into source-level data to identify exactly where volume is concentrated, where opportunities are being missed, and which sources have the most room for improvement.

**The Three-Metric Funnel:** Source diagnosis follows a strict sequential evaluation: Target Rate (Opportunities) → Bid Rate → Win Rate. Each metric acts as a gate — diagnose and fix issues at each stage before moving to the next, because upstream problems render downstream metrics meaningless.

### Step 1: Filter to Active Sources with Activity

From the Source Settings export, filter to sources that are both Active AND have Opportunities > 0. Inactive sources and sources with zero opportunities can be ignored for bid optimization. Note: There is a known UI bug that sometimes duplicates sources and shows them as having zero volume. Rely strictly on the Opportunities > 0 filter to identify real, active channels.

### Step 2: Evaluate Target Rate (Opportunity Volume) — The First Gate

Before looking at Bid Rate or Win Rate, evaluate the **Target Rate** (Opportunities column) for each active source. This metric represents how many consumer profiles in a given source actually matched the campaign's core filtering criteria and geographic settings.

- **Low Target Rate / Low Opportunities:** There are not enough contacts in that source matching the campaign's criteria. This is typically caused by the **"Kiss of Death": over-filtering**. The campaign's upstream targeting filters are too restrictive, killing the available prospect pool before a single bid is placed.
    - **What to do:** Do NOT adjust bids. Instead, relax the upstream filters. Keep core targeting **"lean and mean"** — remove strict requirements like continuous prior coverage, specific credit tiers, or narrow property types. Rely on **percentage-based bid modifiers** to express preferences instead of hard exclusions. For example, instead of filtering OUT non-homeowners, keep them in the pool and bid DOWN on them with a modifier. This preserves volume while still prioritizing the best prospects.
- **High Target Rate / High Opportunities:** The prospect pool is healthy. The campaign is successfully capturing a large volume of potential consumers to evaluate. Proceed to Step 3.

**Lean and Mean Targeting Principle:** As a general rule, campaigns should use inclusive "Equals" filters only for absolute disqualifiers (e.g., state residency) and express all other targeting preferences through bid modifiers. Over-filtering is one of the most common and damaging mistakes on the platform — it silently destroys volume before any auction mechanics come into play.

### Step 3: Check for Ad Group Cannibalization

If the client has multiple ad groups, check the targeting criteria for geographic overlap. For example, if Ad Group A targets all of Colorado and Ad Group B targets specific Colorado zip codes, the ad groups will bid against each other, creating internal conflict and suppressing the overall bid rate. Ensure there is no geographic overlap — strict separation is required.

### Step 4: Evaluate Bid Rate — The Second Gate

**Bid Rate** is calculated as **Bids divided by Opportunities**. It tells you what percentage of the available, targeted opportunities the system actually decided to enter an auction for.

- **Low Bid Rate (Typically < 15%):** The system is filtering out most opportunities *before* the bid amount even matters. **DO NOT raise the multiplier.** Raising the bid on a low-bid-rate source is one of the most common and costly pitfalls — it simply wastes the client's budget by overpaying on the tiny fraction of auctions they actually enter. Low bid rates are **almost always caused by Ad Group Cannibalization** — multiple ad groups with overlapping geographical zip codes bidding against each other and canceling each other out. Check Step 3 findings first. If no cannibalization exists, investigate other structural issues: targeting filter conflicts, platform routing bugs, or source configuration errors.
    - **What to do:** Fix the structural/upstream issue. Never touch the bid lever for a low-bid-rate source.
- **Normal/High Bid Rate:** The campaign is successfully entering auctions. The structural setup is healthy. Proceed to Step 5.

### Step 5: Calculate Effective Bids

For each active source, compute the effective bid:

```
Effective Bid = Base Bid (Avg Bid from campaign CSV) × (Source Multiplier / 100)
```

This is what the client actually pays per click on each source.

### Step 6: Rank Sources by Opportunity Volume

Sort active sources by Opportunities descending. This identifies where the most auction inventory exists. Focus recommendations on top sources by opportunity volume — a 10% multiplier adjustment on a source with 2,000 opportunities will have a vastly larger impact on campaign volume than a 50% adjustment on a source with only 40 opportunities.

### Step 7: Evaluate Win Rate (Bid Strength) — The Third Gate

**Win Rate** is calculated as **Wins (Impressions) divided by Bids**. You cannot accurately analyze a source without this metric.

- **Low Win Rate (Typically < 10%):** If Bid Rate is normal but Win Rate is low, this is a **Bid Strength problem**. The campaign is successfully entering auctions but losing them to competitors because the bid is simply too low. **This is the ONLY scenario where you should increase the source multiplier** (or base bid, per the decision framework in Layer 4).
- **High Win Rate (> 30%):** The source is performing well and may be overpaying. Check if the bid can be reduced.
- **Normal Win Rate:** The source is competitive. Monitor and maintain.

**Source Problem Classification Summary:**

| Bid Rate | Win Rate | Leads | Problem Type |
|----------|----------|-------|-------------|
| Low (<15%) | Any | Low | **Bid Rate Problem** — not entering enough auctions. Almost always Ad Group Cannibalization. DO NOT raise bid. Fix structural issues upstream. |
| Normal | Low (<10%) | Low | **Win Rate Problem (Bid Strength)** — entering auctions but losing (e.g., 400 bids but 40 impressions). **This is the ONLY time to consider raising the multiplier.** |
| Normal | High (>30%) | Good | **Performing Well** — may be overpaying. Check if bid can be reduced. |
| Zero | N/A | Zero | **Not Bidding** — may have filter/targeting issues or may be newly enabled. Investigate before adjusting any bid lever. |

### Step 8: Schedule (Hour-of-Day) Optimization

The campaign schedule is a **bid adjustment per hour**, set per weekday from 0% to 300%. 100% bids the base; **0% turns the hour off**. Full procedure, checks, and examples: `schedule-optimization.md`. In short:

1. **Get the current schedule from the user**: each weekday's Active state and hourly %, plus the schedule's time zone. Never open the campaign's settings page; ask when the schedule is missing, and don't assume an unseen day matches a seen one.
2. **Convert the by-hour export from Pacific to the agent's local time** and run the four time zone checks. Hourly analysis most often goes wrong here.
3. **Clear the sample floor.** Merge hours under 30 leads into blocks. Treat contact-rate gaps under 10 points as noise unless both sides have 100+ leads.
4. **Match the playbook to the concern.** Contact rate: hours, then geo, then source, then agency-side checks. Cap filling early: lower the morning hours so budget reaches later hours. Volume complaint: audit for business hours below 100%, blocked hours, inactive days, and wide swings. CPA: rank hours by item CPA beside spend.
5. **Write Schedule Adjustments in the schedule's zone**, with agent local time beside it when the zones differ. Ask before any hour moves more than 25%, an hour with leads goes to 0%, or a raised hour pushes a Home or Auto source past 1st RPC.

**Off-hours discounting is one option, not the default.** Evening or weekend hours at a discount buy leftover inventory cheaply, which suits an agency that covers those hours and contacts those leads. It does not replace business-hour volume: a business hour set well below 100% wins little, because competitors bid at or above 100% then. Multiplier math applies: 150% raises the hour's bid, 50% halves it.

---

## Layer 4: Market Pricing Calibration

This is the most critical layer. Without RightPricing data, recommendations are guesses. The RightPricing report provides the market context needed to understand WHY a source is underperforming and what specifically to recommend.

### The RightPricing Report (Provided by the User)

Claude has no access to Periscope/Sisense — the **user pulls and supplies** this report. Claude validates the copy provided. When the user pulls it, confirm it was configured this way (if not, ask them to re-pull):

1. From the Periscope/Sisense RightPricing dashboard
2. Filtered for the **specific state and vertical** being analyzed (e.g., Auto — TX, Home — CO). Not aggregated across states or verticals.
3. Date range set to exactly **Last 7 Days.** This trailing 7-day window avoids historical noise from seasonal swings or past competitive shifts.
4. Exported or screenshotted showing RPC at positions 1 through 3+ for each source type, then provided to Claude.

### Sanitize the Export

Before presenting to a client, delete the 'Inventory' column. Clients often conflate 'Inventory' (available auctions) with 'Traffic' (actual clicks), leading to unrealistic volume expectations. Only share the RPC columns for each position.

### Map Effective Bids to Market Positions

For each active source, compare the client's Effective Bid to the RightPricing data for that source. Determine which ad wall position the client's bid corresponds to:

| Position | What It Means | Typical Click Share |
|----------|---------------|-------------------|
| Above 1st RPC | Bidding above the highest-paying advertiser; likely overpaying unless the account manager approved clearing 1st | 78 to 84% of available clicks |
| Between 1st and 2nd RPC | Strong volume; the Home and Auto target band | 40 to 60% of clicks |
| Just above 2nd RPC | Bottom of the band: efficient balance of volume and cost | 50 to 65% of clicks |
| Between 2nd and 3rd RPC | Mid-wall: below target | 15 to 30% of clicks |
| Below 3rd RPC | Lower wall: below target | Under 10% of clicks per slot |

**Target band (AM rule, 8/25/26): the band between 2nd and 1st position, for both Home and Auto.** "On target" = at or above 2nd RPC and below 1st RPC; "below target" = below 2nd RPC. Where a source sits inside the band is chosen per account and stated with its reason: near 2nd for split or tight budgets, new launches, unproven or low-intent sources, or caps that fill early in the day; toward 1st when volume is the priority with budget headroom, proven CPA, a restricted geo, or a volatile auction. Clearing 1st needs a stated reason and the account manager's go-ahead.

### Cross-Reference Position with Source Problem Type

This is the diagnostic crossover that generates the actual recommendation. "Target band" below is the 2nd-to-1st band for both Home and Auto.

| Source Problem | Market Position | Recommendation |
|---------------|----------------|----------------|
| Win Rate | Below the target band (under 2nd RPC) | **RAISE BID**: Clear underbid. Use the Base Bid vs. Multiplier Decision Framework (below) to determine whether to raise the base bid or the source multiplier. Target the point in the band chosen for the account (near 2nd for tight budgets or launches, toward 1st with headroom). |
| Win Rate | Within or above the target band | **INVESTIGATE**: Bid is already in or above the band. Problem is NOT the bid amount. Check targeting, filters, ad group settings, and the schedule (business hours below 100% suppress wins). Consider contacting GOAL product team. |
| Bid Rate | Any | **DO NOT RAISE BID**: Source barely enters auctions regardless of bid level. Fix is upstream: targeting filters, ad group settings, or technical issue. |
| Performing Well | Above the target band (over 1st RPC) | **CONSIDER REDUCING**: Client is likely overpaying unless the account manager approved clearing 1st. Test lowering the effective bid into the band via base bid or multiplier, and monitor win rate. |
| Performing Well | Within the target band | **MONITOR**: On target. A source near 1st on a tight budget may be reducible 5 to 10% toward 2nd without losing significant volume. |
| Not Bidding | Any | **INVESTIGATE FIRST**: Determine why zero bids are being placed before adjusting any bid lever. |

### Base Bid vs. Multiplier Decision Framework

When the data indicates a bid increase is needed, evaluate BOTH levers and choose based on the pattern in the data. Do not default to either.

**Raise the BASE BID when:**
- Multiple sources simultaneously show win rate problems with similar shortfalls — this indicates systemic underbidding across the board, not a source-specific issue
- Most active sources would need multiplier increases of similar magnitude (e.g., all need +15–25%) — a single base bid raise is simpler and achieves the same result
- The current base bid is significantly below the market floor (e.g., below 3rd position RPC for most sources) — multiplier adjustments alone would require extreme values (200%+) that are fragile and hard to manage
- The client has few active sources — when there are only 2–3 sources, per-source multipliers add complexity without benefit

**Raise SOURCE MULTIPLIERS when:**
- Only specific sources have win rate problems while others perform well — this is the classic case for surgical multiplier adjustment
- Sources need different amounts of adjustment (e.g., Source A needs +10% but Source B needs +40%) — a base bid raise would over-bid on A while under-bidding on B
- The base bid is already well-calibrated for the majority of sources — changing it would disrupt sources that are performing
- The client wants granular, per-source control or has a mix of source types (Paid Search vs. Premium Referral) with very different market pricing

**Use BOTH when:**
- The base bid is below market floor AND specific sources need additional lift beyond what a base bid raise provides
- Present this as a two-step recommendation: first raise base bid to get the floor right, then fine-tune individual multipliers

### Calculate Target Values (When Raising)

When the recommendation is to raise the **multiplier**:

```
Target Multiplier = (Target RPC / Base Bid) × 100%
```

When the recommendation is to raise the **base bid**:

```
Target Base Bid = Target RPC / (Source Multiplier / 100)
```

When recommending a base bid change, show the impact on ALL active sources — not just the ones that triggered the recommendation. Verify no currently-performing source would be pushed into overpaying territory.

### The Geography Buffer Rule

If the client is heavily filtering their geography (e.g., a 50-mile office radius, a strict list of ~15 zip codes, or only ~30% of a state's zips), the baseline target-position RPC won't win enough traffic in that restricted pool. **Inject a 20%–30% premium onto the target-position RPC *before* running the multiplier calculation.** In severe cases this may push the effective bid into a higher position band, which is acceptable for geo-restricted campaigns.

### Rounding Rule

Round modifiers to the **nearest 5%** (if the result is 97–103%, keep it at 100%); for modifiers **over 200%, round to the nearest 10%**. A small **5–10% volatility uplift is discretionary** — apply it when you need to hold a position firmly rather than just touch it (or in volatile auctions). It is not a mandatory default; the canonical calibration math runs off the raw target-position RPC.
