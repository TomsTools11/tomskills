---
name: "review-recap-note"
description: "Turn the latest account review meeting for a GOAL client into a Notion recap note plus Notion tasks, grouped by campaign, verified against Fathom and the account folder. Use when {{USER_NAME}} asks to recap, document, or capture action items from a client review."
---

# Review Recap Note

Produce one Notion recap note from a client's most recent account review: a detailed meeting overview up top, then the agreed action items grouped by campaign, each one a real task in the Tasks database. The note is what {{USER_NAME}} works from between reviews and carries into the next one, so accuracy beats speed: every number must trace to the transcript, and every action item must be something actually discussed on the call.

Notion is the system of record. Craft and Bear are retired: never write to either. Older Craft and Bear recap notes are history; read them only if Notion has nothing on the account, and leave them alone.

<!-- config:start -->
## Configuration

This skill is personalized with `{{...}}` placeholders. Fill them by running `python3 scripts/build.py` with your values in `config/profile.yaml` (see the repo README), or replace them by hand. If any placeholder below is still unfilled when the skill runs, ask the user for those values once, use them for this run, and suggest saving them to memory so you don't ask again.

| Placeholder | What it is |
|---|---|
| `{{USER_NAME}}` / `{{USER_FULL_NAME}}` | The account manager's first name / full name |
| `{{ACCOUNTS_FOLDER}}` | Local folder holding one subfolder per client account |
| `{{NOTION_TASKS_DS}}`, `{{NOTION_NOTES_DS}}`, `{{NOTION_ACCOUNTS_DS}}`, `{{NOTION_CONTACTS_DS}}` | Notion data source IDs (the part after `collection://`) |
| `{{NOTION_TASK_TEMPLATE_ID}}`, `{{NOTION_NOTE_TEMPLATE_ID}}` | Fallback default template page IDs |
<!-- config:end -->

## Step 1: Resolve the account

The user gives an account name, or sometimes just the contact person's name. Before touching Fathom, build context:

1. Locate the account folder under `{{ACCOUNTS_FOLDER}}` (e.g., `{{ACCOUNTS_FOLDER}}/[Account Name]/`). List its contents, especially the review folder (`account-reviews/` on newer accounts, `Account Reviews/` on older ones) and any `Meeting Transcripts/` subfolder.
2. Note the campaign names for this client (e.g., "CA Auto", "CA Home", "MN Commercial"). Campaign CSVs, analysis briefs, and prior review notes in the folder reveal these. Campaign naming is [State] [LOB].
3. Check auto-memory (if loaded in context) for this account: contact names, client-specific constraints (e.g., a client who never wants the base bid touched), and any nicknames. {{USER_NAME}} sometimes refers to an account by the owner's first name rather than the agency name — resolve both directions.
4. Note the review cadence: review subfolders are named with the review date (`account-review-M-D-YY`, `review-M-D-YY`, or `[account]-account-review-M-D-YY` on older accounts). The newest folder with content tells you when the last review happened; an empty folder dated today is prep for an upcoming review, not a past one.
5. Find the account in Notion: query the Accounts data source (`collection://{{NOTION_ACCOUNTS_DS}}`, title `Client Account`, rows mode `string_contains` on the most distinctive word; Notion titles are short forms like "Lindqvist" or "Harbor Point Agencies"). Keep the Account page URL. Then collect what Step 6 links to: the account's Contacts (`collection://{{NOTION_CONTACTS_DS}}`), its Notes pages (`collection://{{NOTION_NOTES_DS}}`, e.g. the prior recap, the onboarding note, right-pricing or campaign-config notes), and its open Tasks (`collection://{{NOTION_TASKS_DS}}`, Status not Complete) so you do not duplicate a task that already exists.

## Step 2: Find the meeting in Fathom

Fathom is the source of truth for what was said. Local transcript folders are often stale (they lag weeks behind), so search Fathom first and use local files only as fallback.

Search strategy, in order:

1. `search_meetings` with the account name, `recorded_by: "anyone"`, `created_after` set a few weeks before the last-review date from Step 1.
2. If no hit, search again with the contact person's first or last name. Client meetings are frequently titled generically ("Impromptu Google Meet Meeting", "Google Meet") and won't match the agency name — but the summary usually mentions the people and campaigns.
3. `search_meetings` scans a bounded window (~250 meetings) and reports the date range it actually covered. If that range doesn't reach today, also run `list_meetings` for the uncovered recent days — a meeting from yesterday or this morning can be invisible to search.
4. If the user named a specific date or pasted a Fathom URL, skip the search and resolve directly.

Before pulling a transcript, call `get_meeting_summary` on the candidate and confirm it is the right account (campaign names, contact names, product references). A keyword hit is not confirmation — {{USER_NAME}}'s calendar is full of other agencies' reviews.

If no Fathom transcript exists — the meeting can't be found, or it happened but wasn't recorded — do not reconstruct the note from account-folder data. Stop and ask {{USER_NAME}} exactly this: "A transcript couldn't be found in Fathom, can you provide a transcript?" If they say yes, wait for them to provide it (pasted text or a file) and continue from Step 4 using that transcript. If they say no, ask what they want included in the note, then build it from what they specify. In either case, tell them what was searched (date ranges, names tried) so they can redirect if the meeting exists somewhere that was missed.

## Step 3: Pull the transcript

Call `get_meeting_transcript` with both `recording_id` and `url` (the url enables timestamped deep links). Read the whole thing. The summary alone is not enough — Fathom summaries mislabel speakers, compress decisions, and occasionally attribute source names incorrectly (e.g., collapsing "Premium Paid Search 2" to "Premium Paid Search"). The transcript plus the account folder resolve these.

Also read the most recent analysis brief or prep doc in the review folder if one exists. It gives you base bids, current multipliers, and exact source names — the reference data needed to verify what was agreed on the call.

## Step 4: Extract

From the transcript, capture:

- **Meeting metadata**: date, duration, attendees. Fathom speaker labels can differ from how {{USER_NAME}} refers to the client — nicknames are common (e.g., Summit Choice's contact is one person: Fathom labels them "Jordan Hale", {{USER_NAME}} calls them "Jo"). Resolve labels against known contacts in memory and the account folder before treating two names as two people; when a nickname mapping is known, write the attendee once with both names. Get this right — attributing a decision to the wrong person is worse than omitting it.
- **Performance numbers discussed**: leads, contacts, quotes, policies, rates, spend — with the exact figures said on the call and their date window.
- **Decisions and agreements**: bid/multiplier changes with exact from→to values, targeting changes, new campaign ideas, KPI/reporting changes.
- **Schedule changes** (hour-of-day bid adjustments): the day(s), the hours, the from→to % for each hour (0% means off), and the time zone the campaign's schedule uses. If the call doesn't say which zone the hours are in, write the hours as spoken and note "zone not stated on the call"; never convert or assume a zone. GOAL's hourly analytics are in Pacific time, so an hour read off that report on the call may be Pacific even when the schedule is set in another zone: flag any mismatch.
- **Client conditions**: guardrails the client attached ("only if it doesn't touch current targeting", "pennies yes, dollars no", "never move the base bid"). These are commitments; they go in the note verbatim in spirit.
- **Things completed live on the call** (report updates, data fixes): these are noted in the recap as done on the call, not created as tasks.

Action items come from the meeting discussion only. Do not import recommendations from the analysis brief that were never raised on the call — the note documents what was agreed with the client, not the internal wishlist. Exception: when a meeting decision conflicts with something the brief flagged (e.g., agreeing to raise a multiplier on a source the brief marked as a structural investigation), add a clearly labeled flag item so {{USER_NAME}} sees the tension before executing.

## Step 5: Verify before writing

Run these checks; fix failures rather than caveating around them:

1. Recompute every effective bid mentioned: Effective Bid = Base Bid x (Multiplier / 100). Confirm the direction of each change matches the discussion (a raise raises, a cut cuts). For schedule changes, confirm each hour's from→to % moves in the agreed direction and stays between 0% and 300%.
2. Trace every number in your draft to a transcript line or the analysis brief. No number gets invented, rounded into a different value, or pulled from memory of other accounts.
3. Use exact source names from the account's source-settings data or brief (numbered variants matter: "Premium Paid Search 2" is not "Premium Paid Search").
4. Confirm each action item was actually discussed. If an item is your inference rather than an explicit agreement, either drop it or label it as a flag.
5. Never state CPL anywhere. If account health or CPA comes up, keep Paid Search separate from Premium Referral.

## Step 6: Create the Notion note and tasks

Everything goes in HQ > Backend > Databases. Fetch the Notes and Tasks data sources first for the live schema and default templates (property names match exactly, and {{USER_NAME}} edits these databases). Read `notion://docs/enhanced-markdown-spec` via notion-fetch before the first write.

**Always create from the database's default template.** Every Notes page and every Task page starts from its database's `default_page_template` (fallback: Notes "New Note" `{{NOTION_NOTE_TEMPLATE_ID}}`, Tasks "New Task" `{{NOTION_TASK_TEMPLATE_ID}}`; always prefer what the fetch returns). Templates and inline content cannot be combined in one call, so the sequence is always:
1. notion-create-pages with the data source as parent, `template_id`, and properties only. No `content`.
2. Fetch the page until the template content has landed (button and divider present); wait on `get_async_task` first if the create went async.
3. notion-update-page `insert_content` at the end of the page for the body. Never `replace_content` a templated page.
If a template is rejected or never lands, stop and ask {{USER_NAME}}. Never fall back to a bare page.

**6a. The recap note** (Notes database):
- `Title`: `[Account] - Review Recap MM-DD-YY`, the meeting date, not today's.
- `Type`: `Meeting Notes`.
- `Account`: the Account page from Step 1.
- `Contact(s)`: each client attendee who exists in Contacts (match by email, then name; confirm the contact's Account matches). Never create Contact records here; name any attendee missing from Contacts in your reply.
- `Task(s)`: set after 6b, once the tasks exist.

**6b. The action items** (Tasks database). One Task page per open action item, created only after checking the account's open tasks from Step 1: an item that already exists as an open task is not recreated. Add one dated line to that task's body, add the recap note to its `Notes` relation (existing values plus the recap), and mention it in the note.
- `Task` title: short and executable, verb first, key value included, about 8 words max, no account name, no em dash: "Raise Home Search multiplier to 103%". The full from and to values, effective bids, and rationale go in the body.
- `Status`: To-Do. Waiting on Client for things the client owes (a list, a file, a decision).
- `Due`: only when a date was agreed on the call. Otherwise blank.
- `Account`: the Account page. `Contact(s)`: the client person the item involves, else the account's `Main PoC`. `Notes`: the recap note from 6a.
- Body, inserted after the template lands: the exact change (source or setting, from and to, effective bid), the one-line rationale, the client's condition if one applies, and a link to the Fathom moment when useful.
- **Schedule changes** get one task per campaign titled `Update schedule`. Body: one line per day group and hour range with from→to % ("Mon to Fri, 8 AM to 11 AM: 100% to 115%"), the schedule's time zone (and the agent's local time beside it if different), the metric behind it as said on the call, and any client condition. List the task under that campaign's action-items group.
- Flag items (a decision that conflicts with the analysis brief) are tasks too, titled `Check: ...` so {{USER_NAME}} sees them before executing.
- Items completed live on the call are NOT tasks. They go in the note as plain text under the group they belong to.

Then set the note's `Task(s)` relation to every task created or referenced, with `update_properties`.

**Note body structure** (inserted after the template content):

```markdown
**Meeting:** [Month D, YYYY], ~[N] min [format, e.g., Google Meet]
**Attendees:** {{USER_FULL_NAME}} (GOAL), [Client name(s)] ([Agency]). [Notable references, e.g., owner referenced but not present.]
**Recording:** [Fathom](https://fathom.video/calls/...)
**Related:** <mention prior recap note>, <mention onboarding or right-pricing note>
## Overview
[Short paragraphs, not bullets. Bold the key numbers. Cover: what kind of session it was and what data it ran on; per-campaign performance discussed with exact figures; the major decisions and the client's conditions; any philosophy or constraints confirmed (bid approach, base-bid stance); KPI or reporting changes; how the call ended and what was scheduled next.]
## CA Auto: Action Items
- <mention Task>
- <mention Task>
## CA Home: Action Items
- <mention Task>
## Reporting: Action Items   (only if reporting changes were discussed)
- Done on the call: [item completed live]
- <mention Task>
## Follow-up
- <mention Task>
```

**Linking (native Notion mentions).**
- Every action item in the note is a page mention of its Task, never retyped text, so {{USER_NAME}} clicks through to the task and its Status.
- The `**Related:**` line mentions two to four of the account's Notes pages that bear on this review (the prior recap, the onboarding note, right-pricing or campaign-config notes). Omit the line if none exist.
- Use only pages found this run. A wrong mention is worse than none.

**Formatting rules** ({{USER_NAME}}'s standing conventions; the note looks wrong to them otherwise):
- No em dashes anywhere in Notion. Use a colon or comma (group headings read `CA Auto: Action Items`).
- No `---` horizontal rules in the body you add, and no double blank lines.
- Group strictly by campaign. Use a Reporting group for dashboard or report work and a Follow-up group for scheduling; do not force non-campaign items under a campaign.
- Never write a `0` value or vague items like "look into bids". Every task names the source or setting and the exact change.
- Dollar amounts are written plainly (`$250`).

**Verify after writing.** Fetch the note and every task. Confirm: both came from their default templates; the note's Type is Meeting Notes and Account, Contact(s), and Task(s) are set; every task has Account, Contact(s) where one was sourced, Notes pointing at the recap, a short title, and a body with the exact values; every mention resolves to a page found this run; no em dash was written.

## Step 7: Respond to {{USER_NAME}}

After creating the note, reply concisely: which meeting was used (date, attendees), the recap note and how many tasks were created or reused (counts per group), and surface any flags — especially decisions that conflict with the analysis brief or numbers that could not be verified. End with a Sources section linking the Fathom recording and any account-folder files used.

## Edge cases

- **Ambiguous meeting**: if two candidate meetings are plausible (e.g., a scheduled review and a same-week impromptu call), pick the most recent one that actually covers campaign performance, and state the assumption in your reply so {{USER_NAME}} can redirect.
- **The account's last review predates Fathom's search window**: widen `created_after` progressively (3, 6, 12 months) before concluding no transcript exists and asking {{USER_NAME}}.
- **Paused or cancelled accounts**: still produce the note if asked, but lead your reply with the account's status so {{USER_NAME}} has context.
- **A recap for this meeting already exists** (same account, same meeting date): stop before creating anything and ask {{USER_NAME}} whether to update the existing note or replace it. Never create a second recap or add duplicate lines to its tasks without their answer. There is no delete tool: to remove a page created in error, tell {{USER_NAME}} which one so they can press its Archive button.