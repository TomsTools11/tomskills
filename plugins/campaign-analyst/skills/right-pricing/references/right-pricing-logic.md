# Right Pricing Decision Logic & Examples

Detailed decision trees, edge-case handling, special-source rules, and worked examples for the right-pricing process. This is the backup detail for the 8-step workflow in `SKILL.md`.

---

## Anchor Source Selection Logic

The anchor source determines the base bid. Choosing the wrong anchor creates cascading problems across all modifiers.

### Decision Tree

```
1. Filter the RightPricing report to Opportunities > 0 (kills UI-bug ghost duplicates).
2. Delete/ignore the Inventory column. Use `clicks` as the volume signal.
3. Sort by `clicks` (descending).
4. For the top ~5 sources by clicks:
   a. Read second_rpc (2nd-position cost) for each.
   b. Calculate the median second_rpc across those sources (exclude obvious
      Premium Search outliers — they distort the median).
   c. The anchor is the source whose second_rpc is closest to that median.
5. Tie → choose the source with higher volume.
6. Median falls between two sources → choose the cheaper one
   (it's easier to bid UP with modifiers than to bid DOWN).
7. Never anchor on a thin-data source (< 50 clicks) or a Premium Search channel.
```

### Why Anchor on the 2nd-Position RPC?

`Base Bid = anchor's second_rpc`. The 2nd position is the structural sweet spot for the *anchor*, even though the campaign's actual target position varies by vertical:

- **1st position** is often inflated by aggressive bidders / carrier budgets and yields diminishing returns relative to cost.
- **3rd+ position** is too low — anchoring there forces most modifiers above 100% and skews the whole distribution.
- **2nd position** sits in the middle of the competitive range and produces a balanced set of modifiers (some above, some below 100%).

Note the distinction: the **anchor** is always read at 2nd position to set the base bid, but each source's **Target Bid** (Step 4) is built from the point in the 2nd-to-1st band chosen for that source.

### Common Anchor Source Profiles

| Vertical | Typical Anchor | Why |
|----------|---------------|-----|
| Home Insurance | Mid-tier referral @ 2nd position | High volume, mid-range RPC, stable pricing |
| Auto Insurance | Mid-tier referral @ 2nd position | Large referral networks drive volume |
| Commercial | Tier 2 referral @ 2nd position | Commercial has fewer mid-tier sources; Tier 2 is the volume leader |

---

## Target Bid Logic (Step 4 Detail)

The modifier is built from each source's **Target Bid**, the bid needed to win the *desired* position for the vertical.

```
Base case:           Target Bid = desired-position RPC + placement cushion   (cushion set per account, see below)
Restricted geo:      Target Bid = (desired-position RPC) × (1.20 to 1.30)   [SITUATIONAL 20–30%, applied BEFORE the multiplier]
No 2nd-pos data:     Target Bid = ~90% of 1st-position RPC
Thin 2nd-pos data:   Target Bid = ~85% of 1st-position RPC
Ceiling:             Target Bid < 1st-position RPC when 2nd is the target (clearing 1st needs a stated reason and AM go-ahead)
```

**Placement cushion: decide it from the account, not a fixed number.** There is no default percentage above the position RPC and no fixed percentage-of-1st cap. For each source or source group, pick a point between the desired position's RPC and the next position up, and say why:

| Account / source situation | Where to sit |
|----------------------------|--------------|
| Budget split across campaigns or tight for the market | At or just above the position RPC |
| New account or launch week | At or just above the position RPC |
| Unproven or low-intent source | At or just above the position RPC |
| Daily cap already filling early in the day | At or just above the position RPC (or lower; the cap is doing the throttling). Alternative: keep band prices and lower the morning hours in the schedule so the budget reaches later hours |
| Volume is the stated priority and the budget has headroom | Further up, toward the next position |
| Source has proven CPA from disposition data | Further up, toward the next position |
| Volatile auction, need to hold the slot rather than touch it | Further up, toward the next position |
| Market is 1st-heavy and day 4–7 win rate is still lagging | Further up, toward 1st (without clearing it unless approved) |

When signals point both ways (for example, volume priority on a split budget), say which one you weighted and why so the account manager can flip it. The 20–30% geo premium is applied only for tightly filtered territories.

**Desired position (Home and Auto, AM rule 8/25/26):** the band between 2nd and 1st position. The placement table above picks the point inside it. Clearing 1st needs a stated reason and the account manager's go-ahead; a 1st-heavy position share is a diagnostic, not by itself a reason.

---

## Schedule Interaction

Band prices assume a **100% hour**. The campaign schedule adjusts each hour's bid from 0% to 300%, set per weekday (0% = off). The hour's % stacks on every other modifier (AM rule, 10/16/26): `Hourly Effective Bid = Ad Group Base Bid × (Source Multiplier / 100) × (Campaign Modifier / 100) × (Hour % / 100)`. 100% is the ad group's flat base bid; 150% bids 50% over it before the other modifiers apply.

| Schedule state | What to do |
|---|---|
| Flat at 100% (or unknown on a new setup) | Price as normal. |
| Hours above 100% | Show the effective bid at the highest scheduled %. A Home or Auto source that clears its 1st RPC at that hour needs the account manager's go-ahead. |
| Business hours below 100% | Show the effective bid at the lowest scheduled business-hour %. A source that falls under its 2nd RPC there is below target in those hours; flag it. Business hours well below 100% usually win little, because competitors bid at or above 100% then. |
| Cap fills early | Consider lowering the morning hours instead of pricing every source down to 2nd (`../../campaign-analysis/references/schedule-optimization.md`). |

The schedule comes from the user (screenshots of each weekday's tab plus its time zone). Never open the campaign settings page to read it.

---

## Special-Source Rules

| Source type | Rule |
|-------------|------|
| **Premium / Home Search** | Hyper-expensive, high-intent. Requires hyper-aggressive elevation — modifiers commonly **200–400%** (see the CA Home example: Home Search → 400%). If budget can't sustain it, **cap and accept lower positioning** rather than starve the campaign. |
| **Premium Referral (both verticals)** | High-volume, low-intent; damages delivery on **both Home and Auto** by draining cash on low-intent clicks. On new setups, bid down out of the gate: **70% on Home**, **65–70% on Auto**. Ignore its high RPC. |
| **Tier 1 (all verticals)** | The best source; never bid it down (team rule, 10/8/26). Modifier is **100% or 110%**, never below 100%. Math under 100% → set 100% and note the override. Math over 110% → set 110% and flag the band price (modifier and effective bid) for AM approval. Exempt from defensive down-bids, tiered-build floors, budget-fit trims, and money-pit down-bids; if it underperforms, check targeting, bid rate, and speed-to-lead. Can still be the anchor (100%). |
| **Restricted geo footprint** | A 50-mile office radius or ~15 zips (vs. a clean full state) means standard RPC underdelivers. **Inject a 20–30% premium onto the Target Bids _before_ the multiplier calc.** |
| **Thin / no data (UI ghosts)** | Filter strictly to **Opportunities > 0**; the system duplicates zero-volume sources. Don't optimize ghost channels. |
| **Zero wins despite aggressive RPC** | Almost always a **targeting conflict or timeout**, not a bid issue. **Do not raise bids further** — investigate internal campaign competition: conflicting demographic restrictions, or overlapping geographic ad groups cannibalizing the same auction. |

---

## Edge Cases

### Edge Case 1: Thin-Data Sources (< 50 clicks in 7 days)

Sources with fewer than 50 clicks in the trailing window have unreliable RPC averages — a handful of expensive clicks skews the mean.

**Handling:**
- Calculate the modifier as normal but flag: "⚠️ Low volume — modifier based on limited data. Monitor 2 weeks and re-calibrate."
- Round to the nearest 5%.
- Never use a thin-data source as the anchor.

### Edge Case 2: No Data for a Source

A source is in the campaign settings but has zero data in the report.

**Handling:**
- Set modifier to **100%** as a neutral start.
- Flag: "No market data — starting at 100%, monitor 14 days, adjust on actual RPC and win rate."
- Do NOT set to 0% or disable — the source may become active.

### Edge Case 3: Premium Search with Extreme RPC

Search channels often run 3–5× referral RPC. Expected.

**Handling:**
- Calculate the modifier normally (200–400%+), rounding to the nearest 10% above 200%.
- Validate against budget: "At a 280% modifier, the effective bid on Home Search is $X.XX; at ~Y clicks/week that's ~$Z/month on this source alone."
- Budget-constrained → recommend a lower modifier and accept reduced search position, **or** recommend a budget increase if the channel is high-quality (Step 7).

### Edge Case 4: Target CPL Below Market Floor

If the implied CPC (`Target CPL × Click-to-Lead Rate`) falls below the cheapest available positions:

**Handling — surface the tension immediately and present three options:**
1. **Raise the target CPL** to something achievable.
2. **Improve the click-to-lead rate** via landing-page / QuoteFunnel optimization.
3. **Restrict sources** to the cheapest channels and accept lower volume.

### Edge Case 5: Re-Pricing an Existing Campaign

**Handling:**
- Pull current modifiers alongside the new data.
- Show Current → Recommended → Change.
- Flag any change > 30% — significant shifts that could spike or crash volume.
- For large changes, phase it: move 50% of the way, monitor 7 days, then complete.

---

## Worked Examples

### Example 1 (Canonical): Home Insurance — California (live training math)

This is the canonical reference example. It calibrates modifiers **directly off the 2nd-position RPC with no placement cushion**, the standard training-transcript math and the placement you'd pick for a tight budget or a launch.

**Anchor selection.** Among the top click drivers in the state, **Tier 3** is the ideal anchor: it commands the highest absolute volume footprint (**3,765 clicks**) while holding a balanced, mid-cost structure (**$3.49 at position 2**) versus the hyper-expensive search environment. → **Base Bid = $3.49** (Tier 3's `second_rpc`).

**Modifier calibration** — `Source Multiplier = (Source Target Bid / Base Bid) × 100%`, using each source's 2nd-position RPC as its Target Bid:

| Source | 2nd-pos RPC | Math | Raw | Modifier (rounded) | Notes |
|--------|-------------|------|-----|--------------------|-------|
| **Tier 3 (anchor)** | $3.49 | — | 100% | **100%** | Hardcoded to lock the baseline entry price |
| **Tier 1** | $4.07 | $4.07 / $3.49 × 100 | 116.6% | **110%** | Tier 1 range is 100–110%; flag that holding 2nd needs 120% |
| **Tier 2** | $2.61 | $2.61 / $3.49 × 100 | 74.8% | **75%** | Cheaper, lower-tier discount |
| **Home Search** | $14.05 | $14.05 / $3.49 × 100 | 402.6% | **400%** | Hyper-aggressive elevation for high-intent search; round to nearest 10% above 200% |

Per the rounding rules: 74.8% → **75%**; 402.6% → nearest 10% = **400%**. Tier 1's 116.6% is above its 100–110% range, so it sets at **110%** (effective $3.84, under its $4.07 2nd-position RPC) and the output flags that holding 2nd would take 120% (effective $4.19) for the account manager to approve.

---

### Example 2: Home Insurance — Colorado (illustrating a +10% placement cushion)

> Note: this example places each source 10% above its position RPC (×1.10). That is the call you'd make when holding the slot matters more than the last dollar, such as a volatile auction or a volume-first client with budget headroom. Example 1 sits at the position RPC. Neither is a default.

**Input (RightPricing, trailing 7 days, CO Home; Inventory column already removed, Opportunities > 0):**

| Source | 1st RPC | 2nd RPC (`second_rpc`) | 3rd RPC | `clicks` |
|--------|---------|------------------------|---------|----------|
| MediaAlpha | $12.50 | $9.80 | $7.20 | 850 |
| QuoteWizard | $11.00 | $8.50 | $6.00 | 620 |
| EverQuote | $10.80 | $8.20 | $5.80 | 580 |
| SmartFinancial | $9.50 | $7.40 | $5.20 | 340 |
| Home Search | $28.00 | $22.00 | $16.00 | 210 |

**Target CPL:** $35 **Click-to-Lead:** 55%

**Step 3 — Base bid + CPL sanity check:**
```
Implied CPC = $35 × 0.55 = $19.25
```
Well above 2nd-position RPC for all referral sources → target is realistic.
Anchor selection — among the top sources by `clicks`, QuoteWizard is high-volume (2nd-most clicks) and mid-cost (its `second_rpc` of $8.50 sits squarely in the referral range of $7.40–$9.80, excluding the Home Search outlier). → **Anchor: QuoteWizard @ 2nd = $8.50 → Base Bid $8.50.**

**Step 4–5 — Target Bids (Home → target 2nd position, +10% placement cushion) and Modifiers:**

| Source | 2nd RPC | Target Bid (×1.10) | Modifier `(TB/8.50)×100` | Rounded | Effective Bid |
|--------|---------|--------------------|--------------------------|---------|---------------|
| QuoteWizard (anchor) | $8.50 | — | 100% | **100%** | $8.50 |
| MediaAlpha | $9.80 | $10.78 | 126.8% | **125%** | $10.63 |
| EverQuote | $8.20 | $9.02 | 106.1% | **105%** | $8.93 |
| SmartFinancial | $7.40 | $8.14 | 95.8% | **95%** | $8.08 |
| Home Search | $22.00 | $24.20 | 284.7% | **280%** | $23.80 |

All referral Target Bids stay below their own 1st-position RPC (e.g., MediaAlpha $10.78 vs. $12.50 at 1st). ✔

**Aggressive option (Home, budget headroom):** to push MediaAlpha to **1st** position, Target Bid = $12.50 × 1.05 = $13.13 → modifier 154% → 155%. Only do this with budget headroom or an explicit growth mandate, and the account manager's go-ahead (it clears 1st).

**Step 7 — Budget reconciliation (Home Search):**
At 280% (effective $23.80) and ~210 clicks/week, Home Search ≈ $5,000/week ≈ **$20K/month on one source.** If total budget is $5K/month, either cap Home Search to ~150% (effective $12.75, accept lower position) **or** recommend a budget increase if search traffic is converting — do not starve the referral sources to feed it.

---

### Example 3: Auto Insurance, Texas (target band 2nd to 1st; budget-constrained; illustrates cushion math + premium referral)

**Input (RightPricing, trailing 7 days, TX Auto; cleaned):**

| Source | 1st RPC | 2nd RPC (`second_rpc`) | 3rd RPC | `clicks` | Type |
|--------|---------|------------------------|---------|----------|------|
| MediaAlpha | $18.00 | $14.50 | $10.00 | 1,200 | Premium Referral (low-intent) |
| EverQuote | $16.50 | $13.00 | $9.00 | 900 | Mid-tier referral |
| QuoteWizard | $15.80 | $12.50 | $8.50 | 750 | Mid-tier referral |
| SmartFinancial | $13.00 | $10.00 | $7.00 | 400 | Mid-tier referral |
| Auto Search | $35.00 | $28.00 | $20.00 | 180 | Premium Search |

**Target CPL:** $25 **Click-to-Lead:** 50% **Monthly Budget:** $8,000

**Step 3 — Base bid + CPL sanity check:**
```
Implied CPC = $25 × 0.50 = $12.50
```
Sits between 2nd and 3rd for most sources — achievable, but the client won't hold top positions on the priciest sources. Median referral `second_rpc` (excluding the low-intent Premium Referral, MediaAlpha): $12.50 → **Anchor: QuoteWizard @ 2nd = $12.50 → Base Bid $12.50.**

**Step 4–6 — Target Bids (Auto → target 2nd, +10% placement cushion) and Modifiers:**

> Note: on a budget this tight, the placement table would usually put sources at or just above their position RPC. The +10% here shows the cushion math; in a live build, state which placement you chose and why.

| Source | Basis | Target Bid | Modifier | Rounded | Effective Bid | Note |
|--------|-------|-----------|----------|---------|---------------|------|
| QuoteWizard (anchor) | 2nd $12.50 | — | 100% | **100%** | $12.50 | Anchor |
| MediaAlpha | Premium Referral | — | — | **65%** | $8.13 | Bid down out of the gate; ignore its high RPC (low-intent volume) |
| EverQuote | 2nd $13.00 ×1.10 = $14.30 | $14.30 | 114.4% | **115%** | $14.38 | Solid volume, slight premium |
| SmartFinancial | 2nd $10.00 ×1.10 = $11.00 | $11.00 | 88.0% | **90%** | $11.25 | Lower-tier discount |
| Auto Search | 2nd $28.00 ×1.10 = $30.80 | $30.80 | 246.4% | **250%** | $31.25 | ⚠️ Premium Search — budget impact |

**Step 7 — Budget reconciliation:**
- **MediaAlpha** is the highest-volume source but low-intent — the proactive 65% bid-down protects against burning the $8K budget on weak leads.
- **Auto Search** at 250% (effective $31.25) × ~180 clicks/week ≈ $5,600/week — far beyond an $8K/month budget. Cap Auto Search to ~130% (effective $16.25, ~3rd–4th position) **or** disable it and concentrate budget on referral sources where the client can hold 2nd. If search converts well, recommend a budget increase instead of starving it.

---

## Modifier Rounding Guidelines

| Calculated Modifier | Round To | Rationale |
|--------------------:|----------|-----------|
| 97–103% | 100% | Within noise — keep it simple |
| Any other value ≤ 200% | Nearest 5% | Clean numbers are easier to manage |
| Over 200% (Premium Search) | Nearest 10% | Large modifiers have bigger absolute impact per rounding unit |

---

## Disposition-Based Optimization (Step 8 Detail)

**Guiding principle: start aggressive to capture volume, then peel back. CPA > CPL.**

### Maturity Phase Rule — Accounts < 90 Days

CPA is unreliable early (policies take time to close). Optimize on leading indicators:

| Indicator | Target | If missed |
|-----------|--------|-----------|
| **Contact Rate** (Contacted / Leads) | **20 to 40%** typical | Over 50% = almost always a disposition mapping error; check the import first. Under 5% = red flag (wrong status column or dispositions not imported). Below typical = work the contact-rate playbook (`../../campaign-analysis/references/schedule-optimization.md`: hours, then geo, then source, then agency-side checks) before touching source bids. |
| **Quote Rate** (Quotes / Leads) | **8 to 20%** typical | Under 5% = red flag. Low quote rate with typical contact = filtering/targeting or fit problem. |

### Mature Accounts — True CPA by Source

Overlay imported quote/bind statuses by matching phone numbers to dispositions to compute true CPA per source.

- **Honey Holes** — low CPA, strong bind rate → **bid up.**
- **Money Pits:** high spend, zero sales → **bid down toward ~65%.** Turn the channel off **only as a last resort**, after multiple reductions fail. Tier 1 is exempt: it stays at 100% minimum, and an underperforming Tier 1 points to targeting, bid rate, or speed-to-lead.

### CPA Benchmark — the "Sideways Benchmark" = $675

- **Under $675** → neutral or profitable. Hold or scale.
- **Consistently over $675** → a loss. **Pivot immediately** (bid down the offending sources, recheck targeting, reallocate budget).

---

## Pacing Check

Use during the Week-2 / Week-3 reviews:

```
Projected Monthly Leads = (Leads to Date / Days Elapsed) × Total Days in Month
```

Compare against the client's monthly lead goal. If projection trails the goal and budget isn't capping, there's room to bid up; if it's pacing over while CPA holds under $675, the campaign is healthy.

---

## Monitoring Cadence After Right-Pricing

| Timeframe | Action |
|-----------|--------|
| Days 1–3 | Confirm impressions and clicks are flowing; any sources with 0 activity? |
| Days 4–7 | Review win rate by source. **< ~5% on a bid-up source = bid still too low OR targeting conflict.** |
| Week 2 | Pull a fresh RightPricing report; compare market shifts. Run the pacing check. |
| Weeks 3–4 | Evaluate CPL vs. target and CPA vs. target. |
| Monthly | Full re-price on disposition data. |
| Quarterly | Deep-dive client review (budget, targets, market reality). |

### Red Flags

- **Budget caps before midday** → lower the morning hours in the schedule so the budget reaches later hours (needs the user's schedule), or sit sources nearer 2nd. Confirm against daily pacing first.
- **0% win rate after a bid increase** → stop raising; investigate targeting/timeout, not price.
- **CPA consistently over $675** → loss; pivot immediately.
