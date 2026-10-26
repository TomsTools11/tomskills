---
description: Run a full GOAL Platform campaign analysis on a client's data — diagnoses performance issues and generates calibrated bid optimization recommendations
---

Run the `campaign-analysis` skill to execute a full four-layer campaign analysis.

1. Ask the user which client this analysis is for, if not already specified in $ARGUMENTS.

2. Gather the required inputs. Prompt the user for:
   - **Monthly Campaign CSVs** (minimum 3 months, 6 ideal) — exported from the GOAL dashboard
   - **Client context** — the stated problem, questions, or goals
   - **Source Settings Export** (strongly recommended) — CSV showing all traffic sources with multipliers and performance
   - **RightPricing Report** (strongly recommended) — market-level pricing data for bid calibration
   - **By-Hour Analytics export** (strongly recommended when the concern is contact rate, volume, the cap filling early, or CPA by time of day): Group By `Hour`, one campaign. It is in Pacific time; the skill converts it.
   - **By-Day-of-Week Analytics export** (optional, pulled with the by-hour file): the schedule is set per weekday.
   - **Current campaign schedule** (needed for any schedule recommendation or volume complaint): screenshots of each weekday's tab (Active state and hourly %) plus the schedule's time zone. Claude never opens the campaign settings page, so ask for any day or the time zone if missing.

3. Once data is provided, invoke the `campaign-analysis` skill and execute the full four-layer framework:
   - Layer 1: Client Context Parsing
   - Layer 2: Campaign Trend Analysis
   - Layer 3: Source-Level Diagnosis
   - Layer 4: Market Pricing Calibration

4. Generate prioritized recommendations categorized as Bid Adjustments (with a Schedule Adjustments table when hourly data and the schedule are provided), Investigation Items, and Hold Steady.

5. Produce a polished, standalone HTML report suitable for internal review or client delivery.

6. Present the report and offer to iterate on specific recommendations, generate a PDF version, or deep-dive into individual sources.
