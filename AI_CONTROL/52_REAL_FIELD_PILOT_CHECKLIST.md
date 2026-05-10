---
status: ACTIVE
created: 2026-05-10
---

# 52 — Real Field Pilot Checklist

Companion to `51_REAL_FIELD_PILOT_PLAN.md`. Fill in during/after the pilot.

## Pre-pilot setup

- [ ] Template exported: `python scripts/generate_structured_capture_template.py`
- [ ] Template loaded on iPad / spreadsheet
- [ ] Job chosen: ________________ (e.g. `P008/F001`)
- [ ] Trimble pole IDs listed below
- [ ] `capture_source` value agreed: ________________
- [ ] `captured_by` value agreed: ________________
- [ ] `capture_date` format confirmed as YYYY-MM-DD

## Pole ID reference list

| # | Trimble pole_id | Captured? | Notes |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |

## Capture observation log

| Issue | Field affected | Proposed fix |
|---|---|---|
| | | |
| | | |

## Post-capture checklist

- [ ] CSV saved as UTF-8 (not UTF-16 from Excel/Numbers)
- [ ] Header row intact and unmodified
- [ ] No merged cells, no formula cells
- [ ] `capture_date` column is YYYY-MM-DD for every row
- [ ] No blank rows between data rows
- [ ] Saved to `tests/fixtures/stage4/pilot_real_<jobid>.csv`

## Validation run

`python scripts/validate_stage4_csv.py tests/fixtures/stage4/pilot_real_<jobid>.csv`

## Template usability

1. Was the `pole_id` column obvious and easy to fill? YES / NO / NOTES:
2. Were any field names ambiguous? YES / NO / NOTES:
3. Were allowed values clear without documentation? YES / NO / NOTES:
4. Was the date format requirement obvious? YES / NO / NOTES:
5. Would a new surveyor be able to fill this without explanation? YES / NO / NOTES:

## Sign-off

Pilot completed by: ________________
Date: ________________
Template version: ________________
