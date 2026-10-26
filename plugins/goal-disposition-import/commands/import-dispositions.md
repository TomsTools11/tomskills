---
description: Transform CRM disposition data into GOAL-ready CSV
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
argument-hint:
- client-name
---

Process the uploaded disposition data file for client "$ARGUMENTS" and prepare it for GOAL bulk import.

First, read the disposition-import skill for the full mapping rules and workflow:
@${CLAUDE_PLUGIN_ROOT}/skills/disposition-import/SKILL.md

Then read the detailed mapping reference:
@${CLAUDE_PLUGIN_ROOT}/skills/disposition-import/references/mapping-rules.md

Follow the complete 7-step processing workflow from the skill:

1. **Load and inspect** the uploaded file. Print ALL column names and unique status values with counts.
2. **Ask the user** to confirm:
   - Which column is the phone number
   - Which column is the status/disposition (the 3 new columns will be inserted directly after this column)
   - Whether there are any client-specific mapping overrides
3. **Validate phone numbers** — normalize to 10-digit US format. Flag invalid entries.
4. **Insert 3 disposition columns** — `contacted`, `quoted`, `bound` — directly to the right of the status/disposition column. Do NOT add a premium column.
5. **Map statuses** using the confirmed mapping. Use `1` for true, **blank for false (never use 0)**. For any unrecognized status, leave blank and flag it — NEVER guess.
6. **Clean the data** — remove empty rows, deduplicate, validate column values.
7. **Save the output CSV** (full original spreadsheet + 3 new columns) to the user's workspace folder and print the summary report.

OUTPUT FORMAT — enforce these at all times:
- The output must contain ALL original columns in their original order
- The 3 new columns are inserted directly after the status/disposition column
- Use `1` for true, blank for false — NEVER use `0`
- Do NOT rename any original columns
- Do NOT create a separate premium column

CRITICAL MAPPING RULES — enforce these at all times:
- "Transferred" is NEVER marked as contacted
- "Contact Attempted" is NEVER marked as contacted
- If contact rate exceeds 50%, flag it and review the mapping before saving
- Unrecognized statuses are flagged, never guessed
- Do Not Call-type statuses (including renamed equivalents) stay blank and their row count is reported as a finding
- Phone number is the required matching key — no phone = flag the row

Use Python (pandas) via Bash for the data processing. Install pandas with `pip install pandas openpyxl --break-system-packages -q` if needed.
