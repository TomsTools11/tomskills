# GOAL Disposition Import

Transform raw CRM disposition exports into clean, correctly mapped CSV files ready for GOAL Platform's Conversion Bulk Import.

## What It Does

Takes a client's CRM export (CSV or XLS) and:
- Identifies phone number and status columns
- Normalizes phone numbers to 10-digit US format
- Maps CRM statuses to GOAL's `contacted`, `quoted`, `bound`, and `premium` columns
- Flags unrecognized statuses for manual review (never guesses)
- Validates data quality (contact rate sanity checks, duplicate removal)
- Outputs a clean CSV ready for upload at Settings → Conversion Bulk Import

## Components

| Component | Name | Purpose |
|-----------|------|---------|
| Skill | `disposition-import` | Domain knowledge for mapping rules, validation, and the full processing workflow |
| Command | `/import-dispositions` | Explicit trigger to process an uploaded file for a named client |

## Usage

### Automatic (skill trigger)

Upload a CRM export file and say something like:
- "Prepare this disposition data for GOAL import"
- "Map these CRM dispositions for bulk import"
- "Clean this client data for GOAL"

### Explicit (command)

```
/import-dispositions Acme
```

Upload the file and provide the client name. The command walks through the full workflow.

### Client-Specific Overrides

Some clients use non-standard CRM terminology. Provide a mapping override like:

> "For this client, Underwriting = contacted, Policy (Pixel) = bound"

The override takes precedence over default mapping rules.

## Critical Safety Rules

- **"Transferred" is NEVER contacted** — transfer attempts don't confirm live contact
- **"Contact Attempted" is NEVER contacted** — attempts aren't successes
- **When in doubt, leave blank and flag** — false negatives are far less damaging than false positives
- **Client mappings don't carry over** — each client gets its own mapping

## Setup

No external services or API keys required. The plugin uses Python (pandas) for data processing, which it installs automatically if needed.
