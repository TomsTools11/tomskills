# Diagnostics, Formulas & Pitfalls Reference

Complete diagnostic matrices, formula reference, analysis checklist, and common pitfalls for GOAL Platform campaign analysis.

---

## Key Formulas Reference

| Formula | Calculation | Notes |
|---------|-------------|-------|
| Effective Bid | Base Bid (Avg Bid from campaign CSV) × (Source Multiplier / 100) | What the client actually pays per click on each source |
| Target Multiplier | (Target RPC / Base Bid) × 100% | Use when recommendation is to raise multiplier |
| Target Base Bid | Target RPC / (Source Multiplier / 100) | Use when recommendation is to raise base bid |
| Projected Monthly Leads | (Leads to Date / Days Elapsed) × Total Days in Month | Reliable after 10+ days of data |
| Impression Share | Impressions / Searches (from campaign CSV) | Drop >5pp indicates competitive pressure |
| Bid Rate | Bids / Opportunities (from source settings) | % of available opportunities the source enters |
| Win Rate | Wins (Impressions) / Bids (from source settings) | THE most diagnostic metric for competitive positioning |
| Volume Impact Potential | Opportunities × (Target Bid Rate − Current Bid Rate) × Expected Win Rate | Prioritization metric for recommendations |
| Contact Rate | Contacted / Leads (from the exports after dispositions are imported) | Leading indicator for accounts under 90 days. Typical 20 to 40%; over 50% usually means a mapping error; under 5% is a red flag |
| Quote Rate | Quotes / Leads | Leading indicator for accounts under 90 days. Typical 8 to 20%; under 5% is a red flag |
| Hourly Contact Rate | Contacted / Leads for the hour (by-hour export, converted to agent local time) | Never use the export's `Contacted CVR`: it is click-based. Act only on hours or blocks with 30+ leads |
| Hourly Effective Bid | Ad Group Base Bid × (Source Multiplier / 100) × (Campaign Modifier / 100) × (Hour % / 100) | AM rule, 10/16/26: 100% is the ad group's flat base bid and the hour % stacks on every other modifier. Check the highest combination against 1st RPC |
| Placement Rate (campaign export) | Impressions / Searches | The export's "Win Rate" column is Clicks / Searches, not a placement rate |

---

## Root Cause Classification Matrix (Layer 2)

Use this to determine the primary root cause at the campaign level:

| Searches | Win Rate | Impression Share | Diagnosis |
|----------|----------|------------------|-----------|
| Stable/Up | Down | Down | **Competitive Positioning** — Being outbid by competitors |
| Down | Stable | Stable | **Market Demand Decline** — Fewer searches in the market |
| Stable/Up | Stable | Down | **Budget Constraint** — Running out of daily budget |
| Down | Down | Down | **Market + Competitive** — Both demand and competitive factors |

---

## Account Maturity Diagnostic (Layer 2 — Under 90 Days)

Contact Rate = Contacted / Leads. Quote Rate = Quotes / Leads.

| Contact Rate | Quote Rate | Interpretation |
|-------------|------------|----------------|
| 20 to 40% | 8 to 20% | Typical. The agency is working and quoting leads. Hold current settings; CPA will mature. |
| Over 50% | Any | Almost always a disposition mapping error ("Transferred" or "Contact Attempted" mapped to contacted). Check the import before reading anything else. |
| 40 to 50% | Any | Above typical. Confirm the mapping before treating it as a strength. |
| 20 to 40% | Under 5% | Contacted but not quoting. Possible targeting mismatch or lead quality. Investigate filters and ad group settings. |
| 5 to 20% | Any | Low contact. Work the Contact Rate Problem matrix below: hours, then geo, then source, then agency-side checks. |
| Under 5% | Any | Red flag. Usually the wrong status column, an overly strict mapping, or dispositions not yet imported. Confirm the import before diagnosing the agency. |

---

## Contact Rate Problem Matrix

Work in this order. GOAL can optimize by hour, geo, and source; most vendors can only change activation times, consumer-profile settings, and geos, so optimize where they can't first. Full playbook: `schedule-optimization.md`.

| Step | Look at | Lever | What to request from the user |
|------|---------|-------|-------------------------------|
| 1. Hours | Contact rate and inbound calls by hour, converted from Pacific to agent local time, hours under 30 leads merged | Raise hours with above-average contact rate and real volume; lower hours carrying spend at below-average contact rate | By-hour export (and day-of-week); the current schedule (every day's tab plus its time zone) |
| 2. Geo | Contact rate by county (by-county export) or ZIP (prospects export, leads only) | Split the state into non-overlapping ad groups (top target ZIPs vs. the rest) at different base bids | By-county export; prospects export for ZIP |
| 3. Source | Contact rate by source type | Multiplier changes per the Layer 3/4 rules | By-source-type export; source settings; RightPricing |
| 4. Agency side | Do Not Call statuses (or renamed equivalents); CRM rules that remove not-interested leads; recycle-bin or archive reports; follow-up cadence; whether call logs back up "we work every lead" | Investigation Items and client questions, not bid changes | Count of leads in a DNC-type status; the recycle-bin report (Lead Manager); call, text, and email logs (Ricochet exports them) |

On DNC: GOAL's guidance is that GOAL leads carry consumer consent, which takes them off a prior DNC registration, so agents can work them. Present it as GOAL's guidance and send legal questions to your compliance contact.

---

## The Three-Metric Funnel (Layer 3)

Source diagnosis follows a strict sequential evaluation. Each metric is a gate — diagnose and fix upstream before looking downstream:

**Gate 1: Target Rate (Opportunities)** → **Gate 2: Bid Rate** → **Gate 3: Win Rate**

### Gate 1: Target Rate / Opportunity Volume

| Target Rate | Diagnosis | Action |
|-------------|-----------|--------|
| Low / Few Opportunities | **"Kiss of Death" — Over-filtering.** Upstream targeting filters are too restrictive, killing the prospect pool before any auction. | Do NOT adjust bids. Relax filters. Keep targeting "lean and mean" — use bid modifiers for preferences instead of hard exclusions. |
| High / Many Opportunities | Healthy prospect pool. Proceed to Gate 2. | Continue to Bid Rate evaluation. |

### Gate 2: Bid Rate

| Bid Rate | Diagnosis | Action |
|----------|-----------|--------|
| Low (<15%) | **Structural problem — almost always Ad Group Cannibalization.** Multiple ad groups with overlapping geographic targeting bid against each other. | DO NOT raise bid (base or multiplier). Fix geographic overlap or other structural issues upstream. |
| Normal/High | Healthy auction entry. Proceed to Gate 3. | Continue to Win Rate evaluation. |

### Gate 3: Win Rate (Bid Strength)

| Win Rate | Diagnosis | Action |
|----------|-----------|--------|
| Low (<10%) | **Bid Strength problem.** Entering auctions but losing. | **This is the ONLY scenario where raising the source multiplier is appropriate.** Cross-reference with RightPricing data in Layer 4 before acting. |
| Normal | Competitive. | Monitor and maintain. |
| High (>30%) | Performing well, possibly overpaying. | Check if bid can be reduced. |

### Source Problem Classification Summary

| Bid Rate | Win Rate | Leads | Problem Type |
|----------|----------|-------|-------------|
| Low (<15%) | Any | Low | **Bid Rate Problem** — Not entering enough auctions. Almost always Ad Group Cannibalization. DO NOT raise bid. Fix structural issues upstream. |
| Normal | Low (<10%) | Low | **Win Rate Problem** — Entering auctions but losing. **The ONLY time to consider raising the multiplier.** Validate with RightPricing data first. |
| Normal | High (>30%) | Good | **Performing Well** — May be overpaying. Check if bid can be reduced. |
| Zero | N/A | Zero | **Not Bidding** — May have filter/targeting issues or newly enabled source. Investigate before adjusting any bid lever. |

---

## Market Position × Source Problem Recommendation Matrix (Layer 4)

This is the diagnostic crossover that generates the actual recommendation. **"Target band" is the 2nd-to-1st band for both Home and Auto (AM rule, 8/25/26).** The point inside the band is chosen per account and stated; clearing 1st needs a stated reason and the account manager's go-ahead.

| Source Problem | Market Position | Recommendation |
|---------------|----------------|----------------|
| Win Rate Problem | Below the target band (under 2nd RPC) | **RAISE BID**: Clear underbid. Evaluate base bid vs. multiplier per decision framework in analysis-framework.md, then calculate the target to reach the point in the band chosen for the account (near 2nd for tight budgets or launches, toward 1st with headroom). |
| Win Rate Problem | Within or above the target band | **INVESTIGATE**: Bid is already in or above the band. Problem is NOT the bid amount. Check targeting, filters, ad group settings, and the schedule (business hours below 100% suppress wins). Contact GOAL product team. |
| Bid Rate Problem | Any | **DO NOT RAISE BID**: Source barely enters auctions regardless of bid level. Problem is upstream: targeting, filters, ad group settings, or technical issue. |
| Performing Well | Above the target band (over 1st RPC) | **CONSIDER REDUCING**: Client is likely overpaying unless the account manager approved clearing 1st. Test lowering the effective bid into the band (via base bid or multiplier) and monitor win rate. |
| Performing Well | Within the target band | **MONITOR**: On target. A source near 1st on a tight budget may be reducible 5 to 10% toward 2nd without losing significant volume. |
| Not Bidding | Any | **INVESTIGATE FIRST**: Determine why zero bids are being placed before adjusting any bid lever. |

---

## Recommendation Presentation Rules

### Stepping Up vs. Stepping Down

It is generally much easier to bid aggressively upfront to capture volume and then slow-step the bid backward to find the efficiency sweet spot, rather than slow-stepping the bid upward and continually missing out on volume in the process.

### Proportional Changes

When stepping up bids (whether base bid or multipliers), apply proportional incremental changes (e.g., +10% from current) rather than arbitrary flat increases. Example: if current multiplier is 110%, recommend 120% (not "add 10 points"). If current base bid is $8.00, recommend $8.80 (not "add $1").

### Presenting with Context

Every recommendation should include:
- What to change (specific base bid or multiplier adjustment, with brief rationale for why that lever was chosen)
- Why (linking back to the data — which metric, which layer)
- Expected impact (directional, not exact — "should improve win rate and capture more auction volume")
- For base bid changes: impact on all active sources (show which sources benefit and verify none are pushed into overpaying)
- Caveats or things to monitor after the change

---

## Complete Analysis Checklist

### Layer 1: Client Context
- [ ] Extracted the stated problem from client message
- [ ] Identified willingness to adjust (bid, budget, targeting)
- [ ] Noted implicit constraints and scope of ask

### Layer 2: Campaign Trends
- [ ] Built monthly trend table with all key metrics
- [ ] Checked the Change History to verify agent actions
- [ ] Projected partial month data (if applicable)
- [ ] Calculated baselines (averages across complete months)
- [ ] Quantified the gap (leads, win rate, impression share)
- [ ] Classified root cause (competitive, demand, budget, mixed)
- [ ] Assessed account maturity (≤90 days: use leading indicators instead of CPA)
- [ ] Contact rate read against 20 to 40% typical (over 50% = check the mapping first; under 5% = check the import)

### Data Preparation (if disposition data provided)
- [ ] Obtained client disposition data (or requested export)
- [ ] Applied Three-Column Rule (contacted, quoted, bound)
- [ ] Disposition columns hold `1` or blank only (never `0`)
- [ ] Verified phone number is unique key for match-back
- [ ] Applied CRM-specific mapping rules (e.g., Ricochet Lead Status)
- [ ] Stripped phone number formatting (no dashes, parentheses, or country codes)

### Layer 3: Source Diagnosis (Three-Metric Funnel)
- [ ] Filtered to active sources with opportunities
- [ ] **Gate 1 — Target Rate:** Evaluated opportunity volume per source; flagged any sources with low target rate as potential over-filtering ("Kiss of Death")
- [ ] Assessed whether filters are "lean and mean" — bid modifiers preferred over hard exclusions
- [ ] **Gate 2 — Bid Rate:** Checked for Ad Group geographic overlap (cannibalization) as primary cause of low bid rate
- [ ] Confirmed no bid adjustments recommended for low-bid-rate sources (fix is structural/upstream)
- [ ] Calculated effective bids (Base Bid × Multiplier)
- [ ] Verified multiplier math (no accidental bid-downs)
- [ ] Ranked sources by opportunity volume
- [ ] **Gate 3 — Win Rate:** Identified sources with low win rate as the ONLY candidates for multiplier increases
- [ ] By-hour file converted from Pacific to the agent's local time, zone labeled, all four time zone checks run (`schedule-optimization.md`)
- [ ] Schedule (supplied by the user, every day plus its time zone) audited for business hours below 100%, blocked hours, inactive days, and wide swings
- [ ] Hours under 30 leads merged into blocks or excluded; contact-rate gaps under 10 points treated as noise unless both sides have 100+ leads
- [ ] Checked whether any hour shows Contacted or Quote above Leads (outcomes stamped when logged; hourly rates are directional)

### Layer 4: Market Calibration
- [ ] Received the user-provided Trailing 7-Day RightPricing report from Periscope
- [ ] Filtered for correct state and vertical
- [ ] Sanitized export (removed Inventory column before client presentation)
- [ ] Mapped effective bids to RightPricing positions
- [ ] Cross-referenced position with source problem type
- [ ] Evaluated base bid vs. multiplier per decision framework
- [ ] Calculated target values for the chosen bid lever
- [ ] For base bid changes: verified impact on all active sources
- [ ] Applied 20–30% Geo-Buffer if targeting is severely restricted
- [ ] Identified investigation items (anomalies bid changes cannot fix)

### Final Recommendations
- [ ] Prioritized by impact (highest opportunity volume first)
- [ ] Categorized into bid adjustments (base bid and/or multiplier), investigations, and hold-steady
- [ ] Respected client constraints from Layer 1
- [ ] Included context and rationale for each recommendation

---

## Common Pitfalls to Avoid

### 1. Recommending Bid Increases Without Market Pricing Data

The single biggest lesson from analysis experience. Initial recommendations based only on source performance data may suggest raising a source from 104% to 115–120%. But RightPricing data might show the effective bid is already 52% ABOVE first position pricing. The real problem was bid rate (2.09%), not bid amount. Raising the bid (whether base or multiplier) would have wasted money.

### 2. Treating All Sources Equally

A 10% multiplier increase on a source with 2,176 opportunities has vastly more potential impact than a 50% increase on a source with 40 opportunities. Always weight recommendations by opportunity volume.

### 3. Ignoring the Bid Rate Metric (and Its Root Cause)

Bid rate tells what percentage of available opportunities the source actually enters auctions for. A low bid rate means the system is filtering out most opportunities BEFORE the bid amount even matters. Raising the bid (base or multiplier) for a low-bid-rate source only increases what is paid on the tiny fraction of auctions entered — it is one of the most common and costly mistakes. Low bid rates are **almost always caused by Ad Group Cannibalization** — multiple ad groups with overlapping geographic targeting competing against each other. The fix is structural: ensure strict geographic separation between ad groups. If no cannibalization exists, investigate filter conflicts or platform routing issues.

### 4. Confusing Campaign-Level Metrics with Source-Level Metrics

Campaign-level Win Rate, Avg Bid, and Impression Share are aggregates across ALL sources. They are useful for trend analysis but misleading for bid optimization. A campaign with 12% win rate may have one source at 85% and another at 2%. Source-level data is required for actionable recommendations.

### 5. Over-Rotating on the Client's Framing

The client said "raise the bid." But the data may show that the bid is not the problem. The job of the account manager is to use data to identify the real lever, not just execute what the client assumes is the fix. Present the data-driven recommendation alongside the client's suggestion and explain why the data points a different direction when it does.

### 6. Judging Account Health by Blended CPA Alone

A high blended CPA often masks strong performance on individual sources. This is especially common with "Premium Referral" sources, which tend to carry higher CPAs that skew the overall account metrics. Meanwhile, "Paid Search" sources may be performing well within target. Before recommending budget cuts or major bid reductions based on a high blended CPA:
- Isolate Paid Search performance to show where the client is winning
- Identify which specific sources (usually 1–2 Premium Referral) are driving the CPA up
- Recommend targeted optimization on the underperforming source rather than across-the-board changes

**CPA Benchmark: the "Sideways Benchmark" = $675.** At the source level, a CPA **under $675 is neutral or profitable** (hold or scale); a CPA **consistently over $675 is a loss** and warrants an immediate pivot (bid the source down toward ~65%, recheck targeting, or reallocate budget). Note the maturity caveat: for accounts under 90 days CPA is unreliable. Judge with leading indicators (Contact Rate, typical 20 to 40%; Quote Rate, typical 8 to 20%) before applying the $675 benchmark.

### 7. The "Format Trap" in Disposition Data

If lead matching fails during disposition upload, 90% of the time the root cause is phone number formatting. Client CRM exports frequently contain parentheses, dashes, spaces, or country code prefixes (e.g., "(555) 123-4567" or "+1-555-123-4567") that do not match the raw 10-digit format stored in GOAL (e.g., "5551234567"). Before uploading any disposition file, ensure the Phone Number column strips all special characters to produce a clean 10-digit string. A single formatting mismatch can cause an entire lead's disposition to be silently dropped, making CPA data appear worse than reality.

### 8. Removing Publisher Sources Instead of Filtering

Clients frequently request removal of a high-volume publisher source because they received a single bad lead. Think of volume like a fire hose — use targeting filters (geography, property types) to clean the water, not removing the entire hose. Never completely turn off a strong source just because an agent complains.

### 9. The "Doesn't Equal" Filtering Trap

When setting up targeting, use inclusive filtering ("Equals") for parameters like property type to ensure data accuracy. "Doesn't Equal" should generally be reserved for strict disqualifiers like bad credit or prior specific insurance carriers. Overuse of "Doesn't Equal" often leads to unintended over-filtering and volume death.

### 10. Misunderstanding Multiplier Math

Agents intending to increase a bid by 20% sometimes mistakenly set the multiplier to 20%. This tells the system to bid at 20% *of* the base bid, effectively tanking the bid amount. An intended 20% increase requires setting the multiplier to 120%. Always verify the math if performance suddenly drops after an update.

### 11. Ad Group Cannibalization

Creating multiple ad groups with overlapping geographical targeting (e.g., one ad group targeting an entire state and another targeting specific cities within that state) causes the campaigns to compete against each other in the auction. This suppresses the bid rate and ruins performance. Always ensure strict geographic separation when utilizing multiple ad groups.

### 12. The "Kiss of Death" — Over-Filtering

Over-filtering is the single most common cause of low opportunity volume (low Target Rate). Agents or account managers who stack restrictive filters — continuous prior coverage required, specific credit tiers, narrow property types, etc. — silently kill the prospect pool before any auction mechanics take effect. The fix is to keep targeting **"lean and mean"**: use hard filters only for absolute disqualifiers (e.g., state residency) and express all other preferences through **percentage-based bid modifiers**. For example, bid DOWN on non-homeowners instead of excluding them entirely. This preserves volume while still prioritizing the best prospects.

### 13. Raising Multipliers on Low-Bid-Rate Sources

This is the most expensive mistake in source optimization. When a source has a low bid rate (<15%), the system barely enters any auctions — so raising the multiplier just overpays on the tiny fraction of auctions entered. The bid amount is not the problem. The problem is structural (almost always Ad Group Cannibalization). Always diagnose and fix the bid rate problem before even looking at the multiplier. The **only** valid reason to raise a source multiplier is a Win Rate problem (low win rate with normal bid rate).

### 14. Reading the Schedule as an On/Off Window

The campaign schedule is a bid adjustment for each hour, not just an activation window. 100% bids the base and 0% turns the hour off, but 50% does not mean half the volume: in competitive business hours, competitors bid at or above 100%, so a 50% hour usually wins little or nothing. On a volume complaint, check the schedule the user supplies for business hours below 100%, blocked hours, inactive days, and wide swings (10% one hour, 150% the next) before touching bids or budget.

### 15. Hourly Time Zone Mismatch

The Analytics by-hour export is in Pacific time and ignores the agent's time zone. Reading "07 AM" as 7 AM for an Eastern agent puts every recommendation three hours early. Convert with real dates from the export window (Arizona's offset to Pacific changes with daylight saving time), check split-zone states by county, confirm activity starts at or after the first scheduled hour, and write recommendations in the schedule's own zone, which can differ from the agent's.

### 16. Blocking the Lunch Hour

Blocking noon is usually a mistake: many shoppers search on their lunch break. Keep it blocked only when the account's history shows no activity that hour and the agency wants the break.
