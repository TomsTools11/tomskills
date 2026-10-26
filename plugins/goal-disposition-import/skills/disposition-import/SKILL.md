---
name: disposition-import
description: "This skill should be used when the user asks to \"import disposition data\", \"prepare disposition data\", \"map CRM dispositions\", \"clean disposition export\", \"bulk import dispositions\", \"convert CRM data for GOAL\", or uploads a CSV/XLS file containing lead statuses, dispositions, or CRM export data that needs to be transformed for GOAL Platform's Conversion Bulk Import.\n"
version: '0.2.0'
---

# GOAL Disposition Data Import

Transform raw CRM disposition exports into clean, correctly mapped CSV files for bulk import into GOAL via **Settings → Conversion Bulk Import**.

## Why This Matters

Disposition data (Contacted, Quoted, Bound) drives GOAL's campaign optimization and true CPA calculations. Incorrect mapping — especially marking non-contacts as contacted — corrupts optimization data and can require manual cleanup. **Precision matters more than speed.**

## Required Output Format

The output must be the **FULL original spreadsheet** with all original columns preserved exactly as-is, plus three new columns inserted. Rules:

1. **Keep every original column** — do not remove, reorder, or rename any columns from the source file (except normalizing phone column values to 10 digits).
2. **Add exactly 3 new columns**: `contacted`, `quoted`, `bound` — inserted **directly to the right of the status/disposition column**.
3. **Column values**: Use `1` to indicate true. **Leave the cell blank for false — do NOT use `0`.**
4. **Do NOT create a separate `premium` column.** If premium data exists in the original file, leave it in its original position untouched.

| New Column | Description | Format |
|---|---|---|
| `contacted` | Live human-to-human contact confirmed? | `1` or blank (never `0`) |
| `quoted` | Quote provided? | `1` or blank (never `0`) |
| `bound` | Policy sold/issued? | `1` or blank (never `0`) |

**Example:** If the original columns are `[Name, Phone, Email, Status, Premium, Agent]`, the output should be `[Name, Phone, Email, Status, contacted, quoted, bound, Premium, Agent]` — the 3 new columns inserted immediately after `Status`, all other columns unchanged in their original positions.

## Critical Mapping Rules

### contacted = 1 (ONLY when live human contact is confirmed)

**YES — mark as contacted:**
- "Contacted" (explicit confirmation)
- Any status confirmed as contacted in a client-specific mapping override

**NO — leave blank (NEVER mark as contacted):**
- **"Transferred"** — A transfer attempt is NOT confirmation of contact. This is the #1 most common error and has historically inflated contact rates above 50%.
- **"Contact Attempted"** — An attempt is NOT a successful contact.
- "No Answer," "Voicemail," "Left Message," "Callback," "Busy," "Disconnected"
- Any automated status ("SMS Sent," "Email Sent") without confirmed live conversation

### quoted = 1

Only when the CRM data explicitly indicates a quote was provided during contact.

### bound = 1

A policy was sold, issued, or bound. Look for: "Bound," "Sold," "Policy Issued," "Policy (Pixel)," or equivalent.

### premium (original column only)

Do NOT create a new premium column. If the original file contains a premium/revenue column, leave it in its original position unchanged. Do not modify its values.

## Processing Workflow

### Step 1: Load and Inspect

Load the file (CSV or XLS/XLSX). Identify and print:
- All column names (these will all be preserved in the output)
- The phone number column (may be "Phone," "Phone Number," "Contact Phone," "Mobile," etc.)
- The status/disposition column (may be "Status," "Disposition," "Lead Status," "Outcome," etc.) — **this is where the 3 new columns will be inserted after**
- Unique values in the status column with counts (for mapping verification)
- Statuses that look like Do Not Call ("Do Not Call", "DNC", "Do Not Contact", "No Contact", or a client-specific name for the same thing). Ask the user to confirm any you're unsure of; they map like any other non-contact (blank) and are counted in the summary

### Step 2: Validate Phone Numbers

- Confirm a phone column exists. **If none found, STOP and report the error.**
- Normalize: strip all non-digit characters
- For US numbers: keep last 10 digits (drop leading `1` country code)
- Flag rows with missing or invalid phone numbers (fewer than 10 digits)

### Step 3: Insert Disposition Columns

Insert three new columns — `contacted`, `quoted`, `bound` — **directly to the right of the status/disposition column**. Initialize all values as blank (empty string). Do NOT add a `premium` column — if one exists in the original data, leave it where it is.

### Step 4: Map Statuses

For each row:
1. Check for client-specific mapping override first — use it if provided
2. Otherwise apply default mapping rules
3. **If a status is unrecognized, do NOT guess.** Leave blank and flag it for review.

Read `references/mapping-rules.md` for detailed mapping rules and client-specific override examples.

### Step 5: Clean Data

- Remove completely empty rows
- Remove duplicates (same phone + same status). Keep rows with different statuses for the same phone.
- Ensure `contacted`, `quoted`, `bound` contain ONLY `1` or blank — **never `0`, never any other value**
- Strip stray whitespace from the new columns

### Step 6: Assemble Output

- **Preserve the full original column order.** The only change is the 3 new columns (`contacted`, `quoted`, `bound`) inserted directly after the status/disposition column.
- Do NOT rename any original columns (phone column keeps its original name).
- Do NOT reorder any original columns.
- Save as CSV (UTF-8, comma-delimited)
- Save to the user's workspace folder

### Step 7: Summary Report

Print a summary after processing:

```
=== Disposition Data Prep Summary ===
Client: [name]
Input file: [filename]
Total rows processed: [count]
Total columns in original file: [count]
Total columns in output file: [count] (original + 3 disposition columns)

Phone Validation:
  Rows with valid phone: [count]
  Rows flagged (invalid/missing phone): [count]

Status Mapping Results:
  contacted = 1: [count] rows ([percentage]%)
  quoted = 1: [count] rows
  bound = 1: [count] rows

Disposition columns inserted after: "[status column name]"

Unrecognized statuses (flagged for review):
  - "[status]": [count] occurrences

Do Not Call-type statuses (finding for the account manager):
  - "[status]": [count] rows ([percentage]% of rows)

Output file: [filename]
===
```

## Validation Checklist

Before finalizing, verify:
- All original columns are present and in their original order
- The 3 new columns (`contacted`, `quoted`, `bound`) are inserted directly after the status/disposition column
- Phone numbers in the phone column are normalized to 10 digits
- `contacted`, `quoted`, `bound` contain only `1` or blank — **no zeros, no other values**
- "Transferred" is NOT marked as contacted
- "Contact Attempted" is NOT marked as contacted
- Contact rate is plausible (typically 20–40% for insurance leads; above 50% suggests mapping error)
- All unrecognized statuses are flagged, not guessed
- Output is CSV with UTF-8 encoding
- Output column count = original column count + 3

## Import Modes (for reference)

| Mode | When to Use |
|---|---|
| Initial Import | Only for the very first upload on a new account |
| Overwrite | For all subsequent uploads to update existing records |

## Do Not Call Statuses Are a Finding

Rows sitting in a Do Not Call status (or a renamed equivalent) stay blank in all three columns, but report the count every time. Agents sometimes leave hundreds of GOAL leads untouched because of that status. GOAL's guidance (10/15/26 enablement): GOAL leads carry consumer consent, which takes them off a prior DNC registration, so agents can work them. The account manager raises it with the agency; legal questions go to your compliance contact.

## Error Fixing Priority

When reviewing import errors, prioritize fixing **Quoted** and **Bound** records first — they directly impact CPA calculations.

## Key Warnings

1. **Never mark "Transferred" as contacted.** This has required data deletion and re-import in the past.
2. **Never mark "Contact Attempted" as contacted.**
3. **When in doubt, leave blank and flag.** A false negative is far less damaging than a false positive.
4. **Client-specific mappings change.** Always use the provided override. Never carry over from one client to another.
5. **Phone number is sacred.** No phone = cannot match in GOAL. Flag it, never fabricate.
6. **Manual portal entry does NOT push to analytics.** Bulk import is the only path.
