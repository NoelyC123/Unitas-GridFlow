---
status: ACTIVE
created: 2026-05-10
branch: claude-code/real-field-pilot-readiness-stage4c-gate-audit
---

# 62 — Field Day Operating Checklist

This is a practical, repeatable checklist for Noel to use during the real iPad field pilot. This is NOT a design document; it is an operational checklist to carry into the field.

---

## Before you leave (office)

- [ ] Export Stage 4 CSV template
  ```bash
  python scripts/generate_structured_capture_template.py
  ```
  Confirm file: `templates/structured_capture_template.csv`

- [ ] Load template on iPad
  Open in Numbers, Google Sheets, or Excel. Do NOT alter the header row.

- [ ] Confirm job and Trimble baseline
  Job: __________ (e.g., P008/F001)
  Trimble pole IDs: Pull from sample_data/ and write below

- [ ] Print or load Trimble pole ID reference
  (See checklist 52 pole ID reference table)
  Pole count to capture: __________ (target 10–20)

- [ ] Set capture parameters
  capture_source: __________ (office_audit / surveyor_tablet)
  captured_by: __________ (your name)
  capture_date: __________ (today's date, YYYY-MM-DD)

- [ ] Prepare evidence folder on iPad/laptop
  Location: `field_pilot/<jobid>/photos/`
  Create directory structure before field day

- [ ] Bring equipment
  - [ ] iPad / tablet with template loaded
  - [ ] Camera (phone or dedicated)
  - [ ] Pole ID reference list (printed or on screen)
  - [ ] Data dictionary (printed or on screen)
  - [ ] Notebook for observation log
  - [ ] Chargers / power bank

---

## On site: per-pole capture procedure

For each pole you visit:

### Step 1: Confirm pole_id

- [ ] Match visible pole label or Trimble baseline ID
- [ ] Write pole_id in CSV: use EXACT ID from Trimble list
  - Example: `P008-001` (not `P008001`, not `p008-001`)
  - No spaces at start or end
- [ ] If pole_id does not match list:
  - STOP. Note the mismatch in observation log.
  - Ask: Is this an extra pole not in Trimble baseline?
  - If yes: record pole_id as-is; flag as unmatched in result template later
  - If no: skip this pole and move to next

### Step 2: Capture metadata

- [ ] Fill required fields (every pole must have):
  - pole_id (just filled)
  - capture_source (pre-filled: office_audit / surveyor_tablet)
  - captured_by (pre-filled: your name)
  - capture_date (pre-filled: today YYYY-MM-DD)

### Step 3: Capture observable detail (optional but encouraged)

Choose 4–6 optional fields based on what you can observe:

- [ ] condition (good / fair / poor)
  - Guidance: Look for rust, damage, cracks, wood rot, corrosion
- [ ] voltage_carried (11kV / 33kV / etc. — from Trimble or visible labeling)
- [ ] stay_present (yes / no)
  - If yes: fill stay_type (stay_down / stay_up / flying_down)
  - If no: leave stay_type blank or fill "none"
- [ ] equipment_present (yes / no)
  - If yes: fill equipment_type (transformer / switchgear / etc.)
  - If no: leave equipment_type blank or fill "none"
- [ ] lean_direction (north / south / east / west / none)
  - Only if pole visibly leans; otherwise leave blank

**Key rule**: Do NOT invent values. Leave a field blank if you can't observe it.

### Step 4: Capture evidence (photos)

- [ ] Take ≥1 context photo (full pole, surrounding)
  Name: `<pole_id>_01_context.jpg`
  Example: `P008-001_01_context.jpg`

- [ ] Take ≥1 detail photo (defect, equipment, stay, or key feature)
  Name: `<pole_id>_02_detail.jpg`
  Example: `P008-001_02_detail.jpg`

- [ ] Link photos in CSV
  In `photo_reference` column: `P008-001_01_context.jpg,P008-001_02_detail.jpg`

- [ ] Store photos in evidence folder
  Location: `field_pilot/<jobid>/photos/`

### Step 5: Log observations

If you encounter anything confusing or unusual, note it:

| Observation | Pole_id | Field | Fix? |
|---|---|---|---|
| Example: pole ID has trailing space | P008-001 | pole_id | Trim whitespace on import |
| | | | |
| | | | |

---

## After survey: file preparation

- [ ] Ensure CSV is saved as UTF-8 (NOT UTF-16 from Excel/Numbers)
  - If in Numbers/Excel: File → Export → select UTF-8 encoding
  - If in Google Sheets: File → Download → CSV (UTF-8 encoding)

- [ ] Verify header row is intact (first row unchanged)

- [ ] Remove any blank rows between data rows (delete rows, not just clear cells)

- [ ] Confirm capture_date is YYYY-MM-DD for every row
  - Check at least 3 random rows
  - If format is different (MM/DD/YYYY, slashes, etc.), correct ALL rows

- [ ] Save CSV to GridFlow project location
  ```bash
  cp <path-to-pilot-csv> tests/fixtures/stage4/pilot_real_<jobid>.csv
  ```
  Example: `tests/fixtures/stage4/pilot_real_P008F001.csv`

- [ ] Confirm photos are in `field_pilot/<jobid>/photos/` directory

- [ ] Record observation log in document 52

---

## Before importing to GridFlow: validation setup

- [ ] Ensure Git repository is up to date
  ```bash
  cd /Users/noelcollins/Unitas-GridFlow
  git pull origin master
  ```

- [ ] Confirm Stage 4B is merged
  ```bash
  git log --oneline | head -5
  # Look for: "Implement Stage 4B structured capture validation preview"
  ```

---

## Run validation

```bash
# Validate pilot CSV
python scripts/validate_stage4_csv.py tests/fixtures/stage4/pilot_real_<jobid>.csv

# Run full pytest
pytest -v tests/test_stage4_golden_samples.py tests/test_structured_capture_validators.py

# Run pre-commit
pre-commit run --all-files

# Run repo health check
python scripts/repo_health.py
```

Save output to file:
```bash
pytest -v tests/test_stage4_golden_samples.py > pilot_validation_results.txt 2>&1
cat pilot_validation_results.txt
```

---

## After validation: record outcomes

- [ ] Fill template 53 (REAL_FIELD_PILOT_RESULT_TEMPLATE.md)
  - Paste raw validation output
  - Fill pole_id match analysis table
  - Fill defect log
  - Fill summary metrics

- [ ] Calculate key metrics
  - Rows captured: __________
  - Validation pass rate: __________% (merge_ready count / total rows)
  - pole_id match rate: __________% (matched poles / captured poles)
  - Unmatched pole_ids: __________

- [ ] Answer template usability questions (section in 52)
  1. Was pole_id entry clear? __________ (yes/no/notes)
  2. Were field names ambiguous? __________ (yes/no/notes)
  3. Were enum values obvious? __________ (yes/no/notes)
  4. Date format issues? __________ (yes/no/notes)
  5. Would a new surveyor manage? __________ (yes/no/notes)

---

## After result recording: go/no-go decision

- [ ] Review success criteria (document 63)
  Does pilot meet all GO conditions? __________

  - Rows captured ≥10: __________ (YES / NO)
  - Validation pass rate ≥90%: __________ (YES / NO)
  - pole_id match rate ≥80%: __________ (YES / NO)
  - Template usable without docs: __________ (YES / NO)
  - Completeness includes partial/complete: __________ (YES / NO)

- [ ] If all YES: VERDICT = GO

- [ ] If any NO, check for NO-GO conditions (document 59)
  - Is this a critical defect? __________
  - Is it fixable? __________
  - Should we re-pilot? __________

- [ ] Fill decision board (document 65)
  - Pilot summary
  - Validation stats
  - Evidence stats
  - Defects
  - Risks
  - Recommendation
  - Final decision

- [ ] Sign off in template 53
  - Signed by: __________
  - Date: __________

---

## Stop conditions (when to abort pilot)

STOP and do NOT continue if:

- [ ] pole_id matching is impossible
  - Example: Trimble baseline not available, can't verify IDs
  - Action: Wait until IDs are confirmed

- [ ] Template crashes or becomes unusable
  - Example: Numbers/Excel freezes, CSV becomes corrupted
  - Action: Restart template, check for merged cells or formula corruption

- [ ] Critical validation error blocks all rows
  - Example: capture_date column not found, CSV header corrupted
  - Action: Verify header row is intact; re-export template

- [ ] Evidence folder protocol cannot be followed
  - Example: Photos cannot be saved to GridFlow location
  - Action: Ensure you have write access; use alternate storage temporarily

- [ ] More than 50% of captured rows are invalid
  - Example: Only 3 of 10 rows pass validation due to schema issues
  - Action: Review defect log (59), identify root cause, decide: fix-and-retry or NO-GO

---

## Summary

**In the field**: Fill one row per pole; capture 1–2 photos; use data dictionary for guidance.

**Back at GridFlow**: Run validation scripts; record outcomes; fill decision board.

**Decision**: Does pilot meet success thresholds? GO or NO-GO.

**Outcome**: If GO, proceed to Stage 4C implementation. If NO-GO, document blockers and decide: re-pilot, fix Stage 4B, or stop.
