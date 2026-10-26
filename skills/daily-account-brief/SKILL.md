---
name: "daily-account-brief"
description: "Weekday-morning digest in Notion. Confirms with {{USER_NAME}} which open tasks are done, scans email, Fathom, and Slack, creates each new action item as a task in the Notion Tasks database (default template, relations filled), and builds today's Daily Brief note in the Notion Notes database linking every open task. Use for the morning brief, daily brief, today's brief, or 'what's on my plate today'."
---

# Daily Account Brief (Notion)

Generate or refresh {{USER_NAME}}'s daily account brief in Notion. This usually runs as a scheduled task with no one watching, so resolve every ambiguity with the rules below or flag it inside the note. There is exactly ONE required stop: STEP 6, where {{USER_NAME}} confirms which open tasks are done. Nothing is created or changed in Notion before they answer. Never stop to ask about anything else.

<!-- config:start -->
## Configuration

This skill is personalized with `{{...}}` placeholders. Fill them by running `python3 scripts/build.py` with your values in `config/profile.yaml` (see the repo README), or replace them by hand. If any placeholder below is still unfilled when the skill runs, ask the user for those values once, use them for this run, and suggest saving them to memory so you don't ask again.

| Placeholder | What it is |
|---|---|
| `{{USER_NAME}}` / `{{USER_FULL_NAME}}` | The account manager's first name / full name |
| `{{PRIMARY_EMAIL}}` | Main mailbox scanned in Superhuman |
| `{{WORK_EMAIL}}` / `{{WORK_HANDLE}}` | Work address used by Fathom, Slack, and Close / Slack handle |
| `{{TIMEZONE}}` | IANA timezone, e.g. `America/Chicago` |
| `{{NOTION_TASKS_DS}}`, `{{NOTION_NOTES_DS}}`, `{{NOTION_ACCOUNTS_DS}}`, `{{NOTION_CONTACTS_DS}}` | Notion data source IDs (the part after `collection://`) |
| `{{NOTION_TASK_TEMPLATE_ID}}`, `{{NOTION_NOTE_TEMPLATE_ID}}` | Fallback default template page IDs |
| `{{SLACK_NEW_CUSTOMERS_CHANNEL_ID}}`, `{{SLACK_WORKSPACE}}` | Slack channel announcing new accounts, and its workspace domain |

<!-- config:end -->

WHERE THE BRIEF LIVES

Two places in Notion (HQ > Backend > Databases), and nowhere else:

- **Tasks database:** every job is ONE Task page for its whole life. A job carried from yesterday is the same page, not a copy. New jobs found today become new Task pages.
- **Notes database:** one note per day, `Type = Daily Brief`, titled `Daily Brief MM-DD-YY` (e.g. `Daily Brief 09-29-26`). It is the scannable view: priorities, then each account's open tasks as page mentions, then new accounts. The `daily-action-items` skill writes into the SAME note, so whichever skill runs first each day creates it and the other merges into it.

Craft and Bear are retired. Never read them for tasks and never write to them.

GOAL OF THIS BRIEF

One place {{USER_NAME}} opens each morning, and re-checks through the day, to see what they owe across their GOAL accounts. Every line should be something they can act on. Nothing important slips, and the brief stays short enough to triage in under a minute. Length comes from padding, not coverage: cut words per item and cap what is displayed per account; never drop a real client task to hit a length target. The CONCISION LIMITS section is binding.

WHY TOM CONFIRMS COMPLETION

Most of {{USER_NAME}}'s tasks are changes inside the GOAL dashboard: bids, multipliers, budgets, filters, geos, schedules, go-lives, pauses, imports. Claude cannot see the dashboard, so it cannot tell whether those happened, and {{USER_NAME}} does not always mark the task Complete when they finish. A task that is not Complete is therefore NOT proof the work is still open. {{USER_NAME}}'s answer in STEP 6 is the only source of truth for completion. Email, meeting, or Slack evidence can suggest a task is done, but it never closes one by itself.

CONTEXT

- {{USER_FULL_NAME}}, account manager at GOAL Platform (performance marketing SaaS for insurance agencies).
- Mail is {{PRIMARY_EMAIL}} (Superhuman); Fathom, Slack, and Close use {{WORK_EMAIL}}. If Superhuman has more than one mail account linked (list_accounts), scan each one. Client mail often lands on the {{WORK_EMAIL}} address.
- Timezone: {{TIMEZONE}}. At the start, read the current local date and time and use it for the note title and for every "past 24 hours" window.

NOTION TARGETS

Fetch the Tasks and Notes data sources at the start of every run for the live schema and the current default templates. Property names match exactly, and {{USER_NAME}} edits these databases.

| Database | Data source | Properties this skill sets |
|---|---|---|
| Tasks | `collection://{{NOTION_TASKS_DS}}` | Task (title), Status, Due, Account, Contact(s), Notes |
| Notes | `collection://{{NOTION_NOTES_DS}}` | Title, Type, Account, Contact(s), Task(s) |
| Accounts | `collection://{{NOTION_ACCOUNTS_DS}}` | read only; title is `Client Account` |
| Contacts | `collection://{{NOTION_CONTACTS_DS}}` | read only; Name, email, Role, Account |

- Task Status options: To-Do, Waiting on Client, In Progress, Complete. There is no Dropped option. Never create options.
- Read-only on Tasks: `PoC` and `Note(s)` are rollups; `Finished` and `Archive` are buttons. Notes `Date` and `Updated` are automatic. Never try to set these.
- Fallback default templates: Tasks "New Task" `{{NOTION_TASK_TEMPLATE_ID}}`; Notes "New Note" `{{NOTION_NOTE_TEMPLATE_ID}}`. Always use whatever `default_page_template` the fetch returns; these IDs are only the fallback.
- Non-client work belongs to the Account named `GOAL Internal`.

**Always create from the default template.** Every Task page and every Daily Brief note starts from its database's default template. Templates and inline content cannot be combined in one call, so the sequence is always:
1. notion-create-pages with the data source as parent, `template_id`, and properties only. No `content`.
2. Fetch the page until the template content has landed (the template's button and divider are present). If the create returned an async task, wait for `get_async_task` to succeed first.
3. notion-update-page `insert_content` at the end of the page to add the body. Never `replace_content` on a templated page; it wipes the template.
If a template is rejected or never lands, stop creating, say which pages are affected in the run output, and never fall back to a bare page.

Read `notion://docs/enhanced-markdown-spec` via notion-fetch before the first write of the run. No em dashes in anything written to Notion except the priority separator described below. Dollar amounts are written plainly (`$250`); no escaping.

STEP 1: FIND TODAY'S NOTE (read only)

Query Notes for `Type = 'Daily Brief'` and a Title of `Daily Brief <today MM-DD-YY>`.
- Found -> UPDATE run. Either this skill or `daily-action-items` already built it and the confirmation already happened. Keep its URL and fetch it. Skip STEP 5, STEP 6, and STEP 8; gather sources (STEP 2 to 4), then follow MERGE RULES.
- Not found -> FIRST run.

STEP 2: EMAIL (Superhuman, past 24 hours, plus sent mail since the prior brief)

List or search threads from the last 24 hours across every linked mail account. Keep only threads to or from a client account (match per ACCOUNT MATCHING). Drop newsletters, promos, and internal-only threads with no client action.

Also drop budget notifications: budget updates, increases or decreases, spend or pacing alerts, rebill notices, and any automated platform email whose subject is a budget or billing figure changing. {{USER_NAME}} already receives these. The one exception: a client explicitly asking {{USER_NAME}} to act on a budget or a charge (approve a change, explain a drop, resolve a disputed deduction) is a real action item.

On a FIRST run, also pull {{USER_NAME}}'s SENT mail since the prior brief's date (STEP 5). It is used only for completion hints, never to close a task.

If list_threads output exceeds the token limit, delegate the filtering to a subagent: give it the account list, the exclusion rules, and ask it to return per thread the account, sender, date, subject, snippet verbatim, and the action {{USER_NAME}} owes.

STEP 3: MEETINGS (Fathom, past 24 hours)

List meetings from the last 24 hours recorded by {{WORK_EMAIL}} with include_summary and include_action_items. For each client meeting, extract action items, decisions, and commitments {{USER_NAME}} owns, tied to the account. Skip internal meetings unless they carry an action item for one of {{USER_NAME}}'s accounts. Keep the Fathom URL for each item; it goes in the task body.

STEP 4: NEW ACCOUNTS (Slack new-customers channel, past 24 hours)

Read the new-customers channel ({{SLACK_NEW_CUSTOMERS_CHANNEL_ID}}, workspace {{SLACK_WORKSPACE}}) for the last 24 hours. Capture any account newly assigned to {{USER_NAME}} ({{USER_NAME}}, @{{USER_NAME}}, or {{WORK_HANDLE}}): agency, type, carrier, and who sold it. slack_read_channel paginates FORWARD from `oldest`, so compute the epoch seconds for 24 hours ago carefully and confirm the year before trusting an empty result. Never search this channel further back than 30 days.

STEP 5: REVIEW THE PRIOR BRIEF (first run only, read only)

Getting completion wrong is the most visible failure mode: re-listing something {{USER_NAME}} finished makes the whole brief look untrustworthy.

1. Find the most recent Daily Brief note dated BEFORE today (query Notes by Type, order by Date). Do not compute "yesterday"; on a Monday that lands on Sunday. That note's date is also the lookback floor for sent mail.
2. Collect its tasks: the note's `Task(s)` relation, plus every Tasks page mentioned in its body (older briefs only have mentions). Fetch the current Status of each.
3. ALREADY CLOSED: a task whose Status is now Complete is finished. It does not appear today in any form and is not listed in STEP 6, even if an older email still mentions it.
4. OPEN JOBS: every task still To-Do, In Progress, or Waiting on Client. This is the list {{USER_NAME}} confirms in STEP 6.
5. NEW SINCE THE PRIOR BRIEF: open tasks that are not in the prior brief (not in its `Task(s)` relation or body mentions) and were created after it (SQL mode exposes `createdTime` on Tasks) are {{USER_NAME}}'s own or from `daily-action-items`. They are not asked about and go straight into today's brief.
6. No prior Daily Brief exists: treat every open task in Tasks as an open job.
7. REOPENED: a Complete task may come back only when a source dated after it was completed shows the job is live again (the client re-asked, an import failed). Create it as a NEW task worded to the new ask; never flip the old one back.
8. COMPLETION HINTS (suggestions only): for each open job, look in this run's sources and {{USER_NAME}}'s sent mail for a sign it was finished: {{USER_NAME}}'s own email or Slack saying it is done or delivering the thing, a Fathom recap saying so, a calendar invite that now exists. At most one short hint per job. For GOAL dashboard changes, hint ONLY when {{USER_NAME}} personally wrote that they made the change. A hint never closes a job.

STEP 6: CONFIRM OPEN JOBS WITH TOM (required stop, first run only)

Skip only when STEP 5 found zero open jobs. Otherwise, before creating or changing anything in Notion:

1. Send {{USER_NAME}} one message (SendUserMessage when available, otherwise the reply itself):

```
Before I build today's brief: which of these from the 9/28 brief are done?

Harbor Point Agencies
1. Shift budgets to Home $75/day, Auto $25/day
2. Add Maria Lopez to the onboarding invite (likely done: invite sent 9/28)

The Lindqvist Agency
3. Find out why account 445 flipped to paused

Reply with the numbers that are done, like "done 1, 3". Add "drop 2" for anything no longer needed. "none" keeps everything open.
```

   - Grouped by Account in the prior brief's order; tasks with no Account last under "No account". Numbered straight through.
   - Task title exactly as it reads in Notion, so {{USER_NAME}} recognizes it.
   - Hints in parentheses only where STEP 5 found one. No commentary, no new items.
2. In a scheduled or unattended run, also send a push notification when a notification tool is available: "Daily brief: confirm N open tasks so I can finish today's note."
3. End the turn and wait. Do not write the brief, do not guess, and do not fall back to a default after a delay.
4. Read the reply: numbers after "done" -> DONE; after "drop" -> DROPPED; everything unnamed stays OPEN; "none" keeps all open; "all done" closes all. Plain language is fine when the match is unambiguous ("the Cedar Ridge one is done"). A note about an open job ("Lindqvist is waiting on Sam") may change its Status to Waiting on Client or add a line to its body. If part of the reply is ambiguous, ask once about only those jobs. Ignore numbers not on the list and say so in the run output.
5. Before writing, re-run STEP 1. If today's Daily Brief appeared while waiting (`daily-action-items` ran), switch to an UPDATE run on that note and still apply DONE and DROPPED per STEP 8.

STEP 7: WRITE THE BRIEF

**7a. Build the job list.** Jobs {{USER_NAME}} confirmed OPEN, open tasks new since the prior brief, and new items from this run's sources. DONE and DROPPED jobs do not appear. Dedupe on substance, not text: an item from today's sources that matches an existing open task (same account, same job) is NOT created again; if it adds a genuinely new fact (a new date, the client re-asked), update that task instead (Due, or one dated line appended to its body). Never list the same job twice, and never under two accounts. The one deliberate exception is a Top Priority, which mentions a task that also appears in its account group.

**7b. Create the new tasks.** One Task page per new job, from the default template (see NOTION TARGETS).
- `Task` title: the shortest phrase that identifies the job, verb first, 8 words max, no account name (the relation carries it), no source tags, no em dashes. Real figures stay: "Credit $250 duplicate debit". Detail goes in the body.
- `Status`: To-Do; Waiting on Client when {{USER_NAME}} is waiting on the client. Never Complete on creation.
- `Due`: only when the source states a date or deadline, resolved to an ISO date in {{TIMEZONE}}. Otherwise blank.
- `Account`, `Contact(s)`: per ACCOUNT MATCHING. Leave a relation blank rather than guess.
- `Notes`: when the item came from a page in the Notes database (a meeting or recap note), link that page.
- Body (inserted after the template lands), two to four short lines: what exactly is owed with the real numbers, dates, and names; where it came from with a link {{USER_NAME}} can open (Fathom URL, Superhuman thread subject and date, Slack permalink, or a mention of the Notes page); the client's own words when they carry intent.

**7c. Create the Daily Brief note.** From the Notes default template, with properties:
- `Title`: `Daily Brief MM-DD-YY` (today, {{TIMEZONE}}).
- `Type`: `Daily Brief`.
- `Account`: every account that has a group in the brief.
- `Contact(s)`: the union of the Contact(s) on the tasks in the brief.
- `Task(s)`: every Task page mentioned in the brief (priorities, visible items, and toggle children). This relation is what tomorrow's STEP 5 reads, so it must be complete.

Then insert the body at the end of the note, in this shape and order. Nothing else. Every task line is a native page mention of the Task page, never retyped text, so {{USER_NAME}} clicks straight through to it and its Status.

```
## Top Priorities
- <mention Account> — <mention Task> — finalize call today 10am CT, launching this week
- <mention Account> — <mention Task> — Dana questioning bandwidth, churn signal
- <mention Account> — <mention Task> — Raj cutting spend, retention risk
## <mention Account>
- <mention Task>
- <mention Task>
- <mention Task>
- <mention Task>
<details>
<summary>More open</summary>
	- <mention Task>
</details>
## <mention Account>
- <mention Task>
## <mention GOAL Internal>
- <mention Task>
## Unmatched, needs account
- <mention Task>
## New Accounts
- Summit Insurance, New Business, Independent, sold by Pat Reyes
```

- **Top Priorities:** first section, always present, at most three. `<Account> — <Task> — reason it ranks`, reason 10 words max. These two `—` separators are the only em dashes allowed. Every priority's task also appears in its account group. Rank by: (1) hard deadline today or overdue; (2) an explicit promise to a client that is aging; (3) revenue or retention risk (paused, dark, churn signal); (4) {{USER_NAME}} is the blocker. Break ties toward higher-spend accounts and fresher signals. Fewer than three real candidates is fine; never pad.
- **Account groups:** one H2 per account with open tasks, the heading a mention of the Account page. Order accounts most urgent first, and each account's most urgent task first. Waiting on Client tasks sort to the bottom of their group.
- **More open toggle:** when an account has more than 4 open tasks, show the 4 most urgent, then a `More open` toggle holding the rest as mentions. No count in the toggle title.
- **GOAL Internal:** truly internal work, after the client accounts.
- **Unmatched, needs account:** a client-facing task you could not pin to one account. Create the task with no Account and mention it here so the gap stays visible.
- **New Accounts:** last section. Accounts newly assigned to {{USER_NAME}} per STEP 4, one plain bullet each: `Agency, Type, Carrier, sold by <rep>`. Not tasks. If none: `- None`.
- **Callout (conditional, at most one):** after New Accounts, only for a genuine cross-account risk (an account dark or paused over money, a promise past due on an at-risk account, a churn pattern) or a source that errored or was unavailable. Two sentences max, otherwise omitted.
- No scan stats in the note: windows, thread counts, exclusion counts, and connector details go in the run output only.

STEP 8: APPLY TOM'S ANSWERS (first run only, after STEP 7 passes the self-check)

- DONE -> notion-update-page `update_properties` `Status: Complete`.
- DROPPED -> the Status field has no Dropped option and the Archive button is UI-only. Leave Status as it is, `insert_content` one line at the end of the task body: `Dropped per {{USER_NAME}} MM-DD-YY. Archive this task.`, keep it out of today's brief, and list it in the run output so {{USER_NAME}} can press Archive on it. A task whose body carries that line is closed: never list it in STEP 6, never carry it into a brief, and never treat it as a dedupe match that blocks or absorbs a new item.
- OPEN -> nothing to change; the same Task page is mentioned again in today's note. There are no copies to cancel.
- Never change Status on a task {{USER_NAME}} did not answer about. Never rename a task {{USER_NAME}} may have edited.

CONCISION LIMITS

| Rule | Limit |
|---|---|
| New task title | 8 words max, verb first |
| Visible tasks per account group | 4 max, the rest in the "More open" toggle |
| Priorities | 3 max, reason 10 words max |
| Callout | 2 sentences, or omitted |
| Whole brief | under ~25 visible task lines, not counting priorities or toggle children; over that, move lower items into toggles |
| Confirmation message (STEP 6) | one line per job, one hint max |
| Run output | 2 lines |

- Lead with the verb. No source parentheticals in titles, no backstory clauses, no em dashes in titles.
- Keep the real numbers. Concision cuts words, never figures, dollar amounts, dates, or names.

ACCOUNT MATCHING

The Notion Accounts database is the canonical account list; a relation can only point at a page there. Query it live each run.

1. **Direct name** in the item, normalized (lowercase; drop `the`, `LLC`, `Inc.`, `Agency`, `Insurance`, punctuation). Notion titles are short forms: "Lindqvist" is `The Lindqvist Agency`, "Harbor" is `Harbor Point Agencies`, "Ana Ruiz" is `ARC Insurance`, "Dana Kerr" / "Lee Moss" is `Kerr Agency`. Search `string_contains` on the most distinctive word and confirm the match.
2. **Known contact:** look the person up in Contacts by email, then name; their `Account` relation gives the account. Not in Notion: Close `lead_search` on the name or email.
3. **Email domain** mapped through Contacts emails or Close.
4. Carrier plus state only to choose between two candidates, never alone.

Contact(s): the specific person the task involves, matched by email then name, whose Account equals the task's Account. No specific person but client-facing: the account's `Main PoC` if one exists. Internal tasks: none. Never create Account or Contact records here; a new account without a Notion record gets no Account relation and is flagged in the run output (creating it is the `account-onboarding` skill's job).

MERGE RULES (update runs only)

Update runs do not re-ask {{USER_NAME}}.

- Dedupe new items against every open task in Tasks (account plus substance), skipping tasks marked Dropped. Create only genuinely new tasks, per 7b.
- Add each new task's mention to its account group with notion-update-page `update_content`: old_str is the last task mention line in that group (or the toggle's last child), new_str is that line plus the new line. If the group already shows 4 visible tasks, add it inside that group's `More open` toggle, creating the toggle after the 4th task if needed.
- New account group: insert the H2 and its tasks directly above `## GOAL Internal` (or above `## Unmatched, needs account` / `## New Accounts`, whichever comes first).
- Relations: `update_properties` replaces a relation's whole list, so write the existing values plus the new ones for `Task(s)`, `Account`, and `Contact(s)`. Never drop an existing value.
- Top Priorities: add a replacement only when fewer than three listed priorities are still open. Never remove a priority line, including one whose task is now Complete.
- Never delete a line already in the note, including lines {{USER_NAME}} added personally. Never `replace_content` the note.
- Update New Accounts and the callout in place with `update_content` when their content changes.

SELF-CHECK BEFORE FINISHING

- Exactly one Daily Brief note titled with today's date exists; it came from the Notes default template (template content present above the brief body); Type is Daily Brief.
- Its `Task(s)` relation contains every task mentioned in the body, and its `Account` relation every account with a group.
- Every task created this run came from the Tasks default template, has a title of 8 words or fewer with no em dash, a valid Status, an Account (unless listed under Unmatched), Contact(s) wherever a contact was sourced, and a body with the source link.
- First run: every job {{USER_NAME}} confirmed OPEN appears exactly once (visible or in a toggle), no DONE or DROPPED job appears, and no task that was already Complete appears unless reopened as a new task. Update run: every previously listed line is still in place (a task completed since the first run stays listed; its mention shows its Status).
- Every DONE task now reads Complete.
- No account group shows more than 4 visible tasks; at most three priorities, each with its task also in its account group.
- No item added this run is a budget or rebill notification.
- Every mention and relation points to a page found this run. No invented pages.
- All sources were queried; any that errored or came back empty is named in the callout.

RUN OUTPUT

Two lines. Line 1: open-task count and the three priorities. Line 2: "Created N tasks, closed N done, N dropped to archive, carried N" plus scan stats and any unmatched or new accounts. Never paste the brief; it is in Notion.

HARD RULES

- Never mark a task Complete without {{USER_NAME}}'s answer in STEP 6. Completion hints are suggestions.
- Never assume a GOAL dashboard change happened. Claude cannot see the dashboard.
- Write only to the Notion Tasks and Notes databases. Read-only everywhere else. Never write to Craft or Bear, never send email or Slack, never modify Close.
- Never create duplicate Tasks, Notes, Accounts, or Contacts. Search before every create.
- If a source errors or returns nothing, say so in the callout and continue. Never fail the whole run over one source.
