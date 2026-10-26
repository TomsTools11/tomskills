# Disposition Mapping Rules — Detailed Reference

## Default Status-to-Column Mapping

This table covers the most common CRM statuses seen across insurance agency CRMs (Ricochet, Agency Zoom, Allstate Lead Manager, etc.).

### Statuses that map to `contacted = 1`

| CRM Status | Notes |
|---|---|
| Contacted | Explicit confirmation of live contact |
| Spoke With | Alternate wording for confirmed contact |
| Reached | Confirmed live conversation |

### Statuses that are NOT contacted (leave blank)

| CRM Status | Why NOT contacted |
|---|---|
| **Transferred** | Transfer attempt ≠ confirmed contact. #1 cause of inflated contact rates. |
| **Contact Attempted** | Attempt ≠ success |
| No Answer | Not reached |
| Voicemail | Not reached — left message |
| Left Message | Not reached |
| Callback | Scheduled but not yet contacted |
| Busy | Not reached |
| Disconnected | Number not valid |
| Wrong Number | Not the prospect |
| Do Not Call (or a renamed equivalent, e.g. "DNC", "Do Not Contact", "No Contact") | Not contacted. GOAL leads carry consumer consent, so a prior DNC registration doesn't block outreach (10/15/26 enablement). Count these rows and report them (SKILL.md Step 7) |
| SMS Sent | Automated, no live conversation |
| Email Sent | Automated, no live conversation |
| Nurture | Marketing automation, not live contact |
| New / Unworked | Not yet attempted |
| Pending | Not yet attempted |

### Statuses that map to `quoted = 1`

| CRM Status | Notes |
|---|---|
| Quoted | Explicit quote provided |
| Quote Given | Alternate wording |
| Rate Provided | Alternate wording |
| Shopping | May indicate quote stage — confirm with client |

**Note:** `quoted = 1` implies `contacted = 1` as well (you can't quote without contact).

### Statuses that map to `bound = 1`

| CRM Status | Notes |
|---|---|
| Bound | Policy issued |
| Sold | Policy issued |
| Policy Issued | Explicit |
| Policy (Pixel) | GOAL-specific pixel tracking confirmation |
| Won | Sale completed |
| Closed Won | Sale completed |

**Note:** `bound = 1` implies both `contacted = 1` and `quoted = 1`.

### Premium field (original column — do not create new)

Do NOT create a new premium column. If the original file has a premium/revenue column, leave it untouched in its original position. Do not modify its values or format.

---

## Client-Specific Mapping Overrides

Some clients use non-standard CRM terminology. **When a client-specific override is provided, it takes precedence over defaults.**

### Example Override — "Acme"

| CRM Status | GOAL Column | Value | Notes |
|---|---|---|---|
| Contacted | `contacted` | `1` | Standard |
| Contact Attempted | `contacted` | blank | Standard |
| Transferred | `contacted` | blank | Standard |
| Underwriting | `contacted` | `1` | **Client-specific:** "Underwriting" means contacted for Acme, NOT bound |
| Policy (Pixel) | `bound` | `1` | Standard |

**Warning:** "Underwriting" means different things for different clients. For Acme it means contacted. For other clients it may mean something else entirely. Never assume — always check the override or flag for review.

### How to apply overrides

1. User provides a mapping table or instructions (e.g., "For this client, Underwriting = contacted")
2. Build a lookup dictionary from the override
3. For any status in the override, use the override mapping
4. For statuses NOT in the override, fall back to default rules
5. For unrecognized statuses not in either, flag for review

---

## Phone Number Normalization Rules

### Standard normalization

```
Input               → Output
(555) 123-4567      → 5551234567
555.123.4567        → 5551234567
+1-555-123-4567     → 5551234567
1-555-123-4567      → 5551234567
15551234567         → 5551234567
555-123-4567 ext 2  → 5551234567 (strip extensions)
```

### Validation

- After normalization, phone must be exactly 10 digits
- Numbers with fewer than 10 digits after normalization → flag as invalid
- Numbers with more than 10 digits after stripping country code → flag as invalid
- Empty/null phone → flag as invalid (cannot match in GOAL)

### Edge cases

- Some CRMs export phone as a number (e.g., `5.55123E+09`). Convert scientific notation to full number first.
- Leading zeros may be stripped by Excel. Re-pad if the area code is known to start with 0.

---

## Data Quality Checks

### Contact rate sanity check

- Typical contact rate for insurance leads: **20–40%**
- If contact rate exceeds **50%**, likely mapping error — review "Transferred" and "Contact Attempted" statuses
- If contact rate is below **5%**, may indicate overly conservative mapping or wrong status column

### Duplicate handling

- Same phone + same status = remove duplicate
- Same phone + different status = keep both rows (GOAL handles deduplication)
- If all rows have identical status, flag as unusual (may be filtered export or wrong file)

### Data merging (advanced)

When lead attribution is unclear:
1. Export disposition data from CRM AND lead data from GOAL
2. Join on phone number as primary key
3. Identify GOAL leads that may be incorrectly attributed to other vendors
4. Correct attribution in the import file before processing

---

## Error Handling

| Error | Action |
|---|---|
| No phone column found | **STOP.** Report error. Cannot proceed without matching key. |
| No status column found | **STOP.** Report error. Cannot map without status field. |
| File empty or unreadable | **STOP.** Report error. |
| Unrecognized status | Do NOT guess. Flag in summary. Leave disposition blank. |
| All rows same status | Flag as unusual. May be wrong file or filtered export. |
| Contact rate > 50% | Flag as potential mapping error. Review transferred/attempted. |
| Scientific notation in phone | Convert to full number before normalization. |

---

## Import Process Reference

After the CSV is prepared:

1. Log into client's GOAL account → **Settings → Conversion Bulk Import**
2. Upload the prepared CSV (drag and drop)
3. Map fields: phone → phone, contacted → contacted, quoted → quoted, bound → bound
4. Select mode:
   - **Initial Import**: First-ever upload for this account
   - **Overwrite**: All subsequent uploads
5. Click Import and review results
6. Fix errors: prioritize Quoted and Bound records (they impact CPA directly)
7. Re-upload corrections using Overwrite mode
