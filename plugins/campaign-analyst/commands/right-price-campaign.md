---
description: Right-price a GOAL client campaign — calculate the optimal base bid and per-source modifiers from RightPricing market data
---

Run the `right-pricing` skill to calculate calibrated source modifiers for a client campaign.

1. Ask the user which client this is for, if not already specified in $ARGUMENTS.

2. Confirm the **vertical** (Home vs. Auto). Both target the band between 2nd and 1st position; the point inside the band is chosen per account and stated, and clearing 1st needs the AM's go-ahead. If the campaign's schedule isn't flat at 100%, ask for it (each weekday's tab plus its time zone): band prices assume a 100% hour.

3. Gather the required inputs. Prompt the user for:
   - **RightPricing Data** — the trailing-7-day Periscope RightPricing Report filtered to **one state and one vertical**, showing RPC at each ad position by source. Remind the user to ignore the **Inventory** column and filter to **Opportunities > 0**.
   - **Target Cost Per Lead (CPL)** and **expected click-to-lead rate** — for the sanity check
   - **Campaign Base Bid** — the current base bid (re-price) or none (new setup; calculated in Step 3)

4. Once data is provided, invoke the `right-pricing` skill and execute the 8-step workflow:
   - Step 1: Pull and validate the report (one state/vertical, trailing 7 days, kill Inventory column, use `second_rpc`/`clicks`, filter Opportunities > 0)
   - Step 2: Read the landscape (sort by `clicks`, group cost tiers)
   - Step 3: Set the base bid (anchor's 2nd-position RPC) + CPL sanity check
   - Step 4: Set each source's Target Bid (= desired-position RPC plus a placement cushion chosen from the account's situation, with the reason stated; stay below 1st RPC unless the AM approves clearing it; 20–30% geo buffer BEFORE the multiplier if territory is heavily restricted)
   - Step 5: Calculate modifiers `(Target Bid / Base Bid) × 100`, verify effective bids, round
   - Step 6: Apply special-source rules (Tier 1 at 100% or 110%, never bid down, above 110% only with AM go-ahead; Premium Search 200–400%; Premium Referral bid-down on both verticals, 70% Home / 65–70% Auto; zero-wins = targeting/timeout issue, never raise the bid)
   - Step 7: Reconcile against budget (cap premium spenders or recommend a budget increase rather than starving quality sources)
   - Step 8: Note the ongoing disposition-optimization plan (CPA > CPL, maturity-phase leading indicators, $675 Sideways Benchmark)

5. Present the modifier table with Target Bids, effective bids, budget impact estimates, and the monitoring cadence / red flags.

6. Offer to:
   - Adjust the anchor source, the point in the band, or base bid and recalculate all modifiers
   - Show the budget impact of different modifier scenarios (e.g., capping Premium Search)
   - Generate a formatted summary for client delivery
   - Integrate the modifiers into a full campaign analysis using `/analyze-client-data`
