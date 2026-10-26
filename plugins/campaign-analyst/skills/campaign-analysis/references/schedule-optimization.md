# Campaign Schedule (Hour-of-Day) Optimization

Source: GOAL Account Review Enablement, 10/15/26. Used by `campaign-analysis` (Layers 2 and 3), the `goal-campaign-analyst` agent, and `right-pricing`.

The schedule is one of the levers GOAL can pull that other vendors cannot. Most vendors can only change activation times, consumer-profile settings, and geos, so optimize by hour, geo, and source first.

---

## How the Schedule Works

- The schedule sits in each campaign's settings, in a Schedule section. It is set **per weekday** (Monday through Sunday tabs, each with its own Active toggle), with one slider per hour from 12am to 11pm. Each slider runs from **0% to 300%**.
- Each hour carries a **bid adjustment**, not just an on/off switch. 100% bids the base, 125% bids 25% above it, 50% bids half of it. **0% turns the hour off: no traffic.** The on-screen text reads: "Schedule allows you to adjust your bid for each hour of the day. If you do not want to receive any traffic, move the slider to 0%."
- A setting covers the whole hour: 5 PM covers 5:00 to 5:59.
- **The hour's % stacks on every other modifier (AM rule, 10/16/26).** 100% is the ad group's flat base bid; 150% bids 50% over it. The hour's % then multiplies with the campaign modifiers (e.g. property type, demographic) and the source multiplier: `Hourly Effective Bid = Ad Group Base Bid × (Source Multiplier / 100) × (Campaign Modifier / 100) × (Hour % / 100)`. Example (invented numbers): $8.00 base × 110% source × 130% property type × 115% hour = $13.16. Ad groups can carry different base bids, so the same hour % lands at different dollar bids in each ad group.
- **Below 100% in competitive business hours, volume does not fall in proportion. It usually falls to little or nothing**, because competitors bid at or above 100% then ("It's a business hour, then they're paying 50% when other people are paying probably over 100%"). Treat a business hour set well below 100% as close to off, and say so when a client asks for one.
- The schedule runs in the time zone chosen in that campaign's Schedule section (a Timezone dropdown, e.g. Eastern Time (ET)), which can differ from the agent's local zone. Write recommendations in the schedule's zone.

## The Current Schedule Comes From the Account Manager

**Never open, read, or export anything from a campaign's settings page, including its Schedule section.** The account manager provides the current schedule, usually as screenshots of each day's tab.

A schedule recommendation needs, for every day Monday through Sunday:
- the day's Active state
- the % for each of the 24 hours
- the schedule's time zone (from the Timezone dropdown)

If the task needs the schedule and any of that is missing, ask the account manager for it (with the question tool if one is available, otherwise in plain text). **Do not assume a day you have not seen matches one you have.** Never look for the schedule in the dashboard yourself.

---

## Data

### The export
- Analytics → Product Type `Quote Funnels` → one campaign → Group By `Hour`. At least 30 days; use 60 to 90 days or All Time when hours are thin (see the sample floor below). File: `campaign-performance-by-hour-{campaign}-{state}-{timeframe}.csv` (pulled by `goal-campaign-exports`).
- The schedule is set per weekday, so pull the day-of-week export (Group By `Day of Week`) with the by-hour file: `campaign-performance-by-day-of-week-{campaign}-{state}-{timeframe}.csv`.
- The first column is `Hour` with labels like `07 AM`. **Rows come sorted by volume, not clock time.** Re-sort by clock time before reading.
- Drop the total row (label `--` or blank). Reconcile leads, contacted, and cost against the rollup's row 1 and state the basis. If the by-hour totals run higher than the rollup, the export is carrying call dispositions; say so and do not mix bases.

### The time zone checks (run all four before any hourly analysis)

**The export is in Pacific time and ignores the agent's time zone.** AI analysis gets this wrong often, so run every check, every time:

1. **Source zone.** Pacific, unless the header names another. A header like `Hour (Eastern)` with labels like `10 AM ET` means the file was already converted; do not convert it twice.
2. **Agent zone.** From the office address. In split-zone states (AK, FL, ID, IN, KS, KY, MI, NE, ND, OR, SD, TN, TX), check the county.
3. **Offset.** Compute it from real dates in the export window with Python's `zoneinfo`, not a fixed table. Pacific to Eastern is +3, Central +2, Mountain +1. Arizona is +0 during daylight saving time and +1 outside it, so a window that crosses a DST change has two offsets for Arizona agents.
4. **Sanity check.** Converted activity should start at or after the campaign's first scheduled hour in the schedule's zone and peak in local business hours. Leads in the middle of the local night mean the offset is wrong. If activity starts before the first scheduled hour, either the offset is wrong or the schedule changed during the window: ask the account manager before building on it.

This plugin's `goal-client-report` skill runs the conversion and the DST, midnight, sample-floor, and outcome-timestamp warnings; use it rather than converting by hand. The script is `skills/goal-client-report/scripts/compute_metrics.py` in this plugin (from this skill's base directory: `../goal-client-report/scripts/compute_metrics.py`; in Claude Code, `${CLAUDE_PLUGIN_ROOT}/skills/goal-client-report/scripts/compute_metrics.py`). Commands run in the session's working directory, so give the script and the export by full path:

```bash
python3 <plugin-root>/skills/goal-client-report/scripts/compute_metrics.py campaign-performance-by-hour-home-ga-last30days.csv \
  --to-tz America/New_York --period-start 2026-09-01 --period-end 2026-09-30 --out hourly.json
```

### Reading the hours
- Read KPIs in the **agent's local time**, since that is when shoppers search and the agency answers the phone. Then convert each recommendation into the **schedule's zone**. When the two zones differ, show both.
- **Day of week.** A time zone shift can move late-evening Pacific hours across midnight. The day-of-week export cannot be re-sorted by hour, so when converted hours with leads cross midnight, state that the day split is on Pacific calendar days and how many leads sit in the crossing hours. When no hour with leads crosses midnight, say so and use the export as is.
- Recommend **one hourly profile for all active days** unless weekdays and weekends (or a single day) behave differently and each group clears the sample floor on its own.

### Metrics
- `Contact Rate = Contacted / Leads` for the hour. The export's CVR columns (`Contacted CVR` and the rest) are **click-based**: never print them as rates. Quote Rate = Quote / Leads.
- The export's `Win Rate` column is **Clicks / Searches**. Placement rate = Impressions / Searches.
- No `Contacted`, `Quote`, or `Bound` columns means no contact rate by hour. Say so and fall back to leads, calls, and spend by hour. Never print a 0% contact rate for a file that has no outcome columns.

### Outcome timestamps
Hourly contact rate means "share of the leads that arrived this hour that were contacted" only when outcomes are filed under the lead's arrival hour. That holds for bulk-imported dispositions, which have been seen landing in the hours their leads arrived. Some outcomes logged by integration or pixel are filed under the hour they were logged instead, which can produce an hour with more quotes than leads (example, invented numbers: 9 quotes on 4 leads).

**Check:** if any hour shows Contacted or Quote greater than Leads, treat hourly contact and quote rates as directional for that account and say so. Lead, spend, and placement figures by hour are unaffected.

### Sample floor
- Act on an hour only with **at least 30 leads** in the window. Otherwise merge adjacent hours into blocks (early morning, morning, midday, afternoon, evening) or lengthen the window.
- At 30 leads a 30% contact rate carries about ±16 points of sampling noise. **Treat a contact-rate gap under 10 points between hours (or between an hour and the campaign average) as noise unless both sides have 100+ leads.**
- Weight hours by leads the way sources are weighted by opportunities: a 10-point gap on a 300-lead hour outranks a 25-point gap on a 35-lead hour.

---

## Playbooks

### Contact-rate concern
Work in this order, because GOAL can optimize by hour where other vendors cannot:

1. **Hours.** Rank hours or blocks by contact rate and by inbound calls. Raise hours that pair above-average contact rate with real lead volume; lower hours that carry spend at below-average contact rate.
2. **Geo.** Contact rate by county or ZIP. Split the state into ad groups (top target ZIPs vs. the rest of the state) at different base bids, with **no geographic overlap** between them (overlap cannibalizes bid rate). Geo is the most-used lever, but it takes a lot of fine-tuning to move results.
3. **Source.** Contact rate by source type.
4. **Agency side.** These are Investigation Items and client questions, not bid changes:
   - Leads parked in a Do Not Call status, or a renamed equivalent. GOAL's guidance: GOAL leads carry consumer consent, which takes them off a prior DNC registration, so agents can work them. Present it as GOAL's guidance and send legal questions to your compliance contact.
   - CRM rules that remove leads marked "not interested" (seen on Ricochet). The first 3 to 5 days are the hardest; re-contact after 2 to 3 weeks.
   - Recycle-bin or archive reports, especially on Lead Manager, where sold or not-interested leads get archived out of the normal report. Ask for one when reports show no binds.
   - Call, text, and email logs when the agency says leads are worked but contact rate is low (Ricochet exports them). Don't take the agency's word for it.
   - Follow-up cadence, and whether a cold-lead refill automation exists (e.g. an AgencyZoom automation that moves cold leads back into producer queues after 30 days).

### Cap hits early
Signs: spend concentrated in the first hours of the window, and later hours with searches but few or no placements. Confirm against the dashboard's daily pacing (the account manager supplies it) before acting. **Lower the morning hours so the budget reaches the hours with better contact rate.** This is often a better fix than pricing every source down to 2nd.

### Volume complaint
**Audit the schedule the account manager provides first** (ask for it if you don't have it): business hours under 100%, blocked hours, days toggled inactive, and swings like 10% to 150% across the day. Return business hours to 100% before raising bids or budget. A blocked noon hour stays blocked only when the account's history shows no activity then and the agency wants the break; otherwise blocking noon gives up one of the busiest shopping hours.

### CPA-focused account with sales data
Rank hours by item or policy CPA next to spend. Lower heavy-spend hours with weak CPA; raise hours with strong CPA and volume. **Under 90 days, use contact and quote rate instead**, since CPA hasn't matured.

### Client asks to cut business-hour bids or run mostly off-hours
Explain that a business hour at 50% usually wins little, not half. It can work for an agency that wants low-cost off-hours volume, so set it up as a test with a review date and expect lower volume.

### Off-hours discount
Evening or weekend hours at a discount buy leftover inventory cheaply. Use it when the agency covers those hours and the hourly data shows those leads get contacted. It does not replace business-hour volume.

---

## Recommendation Format

Under **Bid Adjustments**, add a **Schedule Adjustments** table, one per campaign, ranked by leads affected (Volume Impact Potential does not apply to hours):

| Day(s) | Hour (schedule zone) | Hour (agent local, if different) | Current % | Recommended % | Leads | Contact rate | Spend | Why |
|---|---|---|---|---|---|---|---|---|

Example row (invented numbers): `Mon-Fri | 8 AM-10 AM ET | 7 AM-9 AM CT | 100% | 115% | 142 | 31% | $1,240 | Contact rate 9 points above the campaign's 22% on 142 leads`.

Under the table, state the date range, the conversion used (e.g. "Pacific +3 to Eastern, computed on the window's dates"), the schedule's zone, and the sample floor applied.

- Step changes proportionally, the same way as multipliers (100% to 115%, not "add 15"), and keep every setting between 0% and 300%.
- Show the hourly effective bid for the account's top sources at each recommended %, per ad group, including any campaign modifiers that apply. Check the highest combination (top source × highest campaign modifier × highest hour) against 1st RPC.

**Ask the account manager first** (state the change and wait for his go-ahead) when:
- an hour moves more than 25% from its current setting;
- an hour with leads in the window goes to 0%;
- a raised hour pushes any Home or Auto source's effective bid (with its campaign modifiers) past its 1st-position RPC;
- the account is paused, cancelled, or under 90 days old (any change to a live campaign).

**Never change the live schedule.** Recommend; the account manager applies it.

**Post-change check:** 14 days after a change, re-pull by-hour covering only the post-change days and compare the changed hours against the pre-change window.

---

## Client-Facing

Show hours in **agent local time with the zone named** ("Sept 1 to 30 · Central Time"). Describe schedule changes by direction and hours ("We increased bids from 8 AM to 11 AM") with the metric behind them. **Leave out the percentages**, the hourly effective bids, and any bid detail.
