---
status: ACTIVE
created: 2026-05-10
branch: codex/stage4b-4c-safety-pilot-harness
---

# 52 — Real Field Pilot Checklist

Fill this in when running the real field pilot described in
`51_REAL_FIELD_PILOT_PLAN.md`.

---

## Pre-pilot setup

- [ ] Template exported: `python scripts/generate_structured_capture_template.py`
- [ ] Template loaded on iPad / spreadsheet
- [ ] Job chosen: ________________ (e.g. `P008/F001`)
- [ ] Trimble pole IDs listed below (copy from survey file)
- [ ] `capture_source` value agreed: ________________
- [ ] `captured_by` value agreed: ________________
- [ ] `capture_date` format confirmed as YYYY-MM-DD

---

## Pole ID reference list

Copy the Trimble pole IDs for the pilot set here before starting capture.

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
| 11 | | | |
| 12 | | | |
| 13 | | | |
| 14 | | | |
| 15 | | | |

---

## Capture observation log

Note anything during capture that was confusing, unclear, or required guesswork.

| Issue | Field affected | Proposed fix |
|---|---|---|
| | | |
| | | |
| | | |

---

## Post-capture checklist

- [ ] CSV saved as UTF-8 (not UTF-16 from Excel/Numbers)
- [ ] Header row intact and unmodified
- [ ] No merged cells, no formula cells
- [ ] `capture_date` column is YYYY-MM-DD for every row (not MM/DD/YYYY)
- [ ] No blank rows between data rows
- [ ] Saved to `tests/fixtures/stage4/pilot_real_<jobid>.csv`

---

## Validation run

```bash
python scripts/validate_stage4_csv.py tests/fixtures/stage4/pilot_real_<jobid>.csv
```

Record raw output in `53_REAL_FIELD_PILOT_RESULT_TEMPLATE.md`.

---

## Template usability questions

Answer these after completing capture:

1. Was the `pole_id` column obvious and easy to fill? YES / NO / NOTES:
2. Were any field names ambiguous or confusing? YES / NO / NOTES:
3. Were allowed values (enums) clear without documentation? YES / NO / NOTES:
4. Was the date format requirement obvious? YES / NO / NOTES:
5. Would a new surveyor be able to fill this without explanation? YES / NO / NOTES:

---

## Sign-off

Pilot completed by: ________________

Date: ________________

Template version used (from CSV header): ________________
