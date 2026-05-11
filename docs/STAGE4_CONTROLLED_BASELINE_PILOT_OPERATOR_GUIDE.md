# Stage 4 Controlled Baseline Pilot Operator Guide

Purpose: explain how Noel should use the controlled baseline helper before and after the real `P_CONTROLLED_001` field capture.

This guide is for the **baseline helper workflow only**. It does not approve or implement Stage 4C runtime integration.

## What This Helper Does

`scripts/prepare_stage4_controlled_pilot.py` has two modes:

1. **Prepare mode**
   - inspects the local baseline CSV
   - extracts exact `pole_id` candidates
   - generates a Stage 4 starter capture CSV with current Stage 4 headers
   - writes a Markdown extract report

2. **Match mode**
   - compares a completed Stage 4 pilot CSV back to the baseline
   - uses exact `pole_id` matching only
   - blocks on duplicates and missing/unsafe `pole_id` values
   - writes a Markdown match report for Noel's decision board

## Inputs That Must Stay Local

These paths are local-only and must not be committed:

- `real_pilot_data/`
- `uploads/`
- `validation_runs/`

That includes:

- the local baseline CSV
- any generated starter or completed pilot CSV
- photos
- local reports written by the helper

## Exact Match Rule

The helper follows docs 73–75:

- exact `pole_id` match only
- no fuzzy matching
- normalisation allowed only for:
  - leading/trailing whitespace
  - case
- no underscore-to-dash or punctuation rewriting

Examples:

- `P008-001` matches ` p008-001 `
- `P008-001` does **not** match `P008_001`
- `P008-001` does **not** match `P008.001`

## Prepare Mode

Use this before field capture.

```bash
python3.13 scripts/prepare_stage4_controlled_pilot.py \
  --baseline-csv real_pilot_data/P_CONTROLLED_001/baseline/baseline.csv \
  --pilot-name P_CONTROLLED_001 \
  --out real_pilot_data/P_CONTROLLED_001/csv/stage4_controlled_capture_starter.csv \
  --notes-out real_pilot_data/P_CONTROLLED_001/notes/baseline_pole_id_extract.md
```

### What prepare mode writes

- `real_pilot_data/P_CONTROLLED_001/csv/stage4_controlled_capture_starter.csv`
- `real_pilot_data/P_CONTROLLED_001/notes/baseline_pole_id_extract.md`

### What the starter CSV contains

- exact baseline `pole_id`
- Stage 4 template headers
- safe starter defaults only
- blank or `unknown` values for anything not yet field-confirmed

The helper does **not** pretend that technical fields are known.

### What Noel should check after prepare mode

1. Starter CSV exists.
2. Extract report exists.
3. Candidate `pole_id` list looks plausible.
4. There are no duplicate baseline `pole_id` blockers.
5. The selected row count is acceptable for the controlled pilot.

## Match Mode

Use this after field capture and after Noel has filled the completed Stage 4 pilot CSV.

```bash
python3.13 scripts/prepare_stage4_controlled_pilot.py \
  --baseline-csv real_pilot_data/P_CONTROLLED_001/baseline/baseline.csv \
  --pilot-csv real_pilot_data/P_CONTROLLED_001/csv/stage4_controlled_capture_completed.csv \
  --pilot-name P_CONTROLLED_001 \
  --match-report-out real_pilot_data/P_CONTROLLED_001/notes/pole_id_match_report.md
```

### What match mode checks

- exact baseline match for each pilot `pole_id`
- missing or unsafe `pole_id`
- duplicate `pole_id` in the completed pilot CSV
- baseline rows not captured in the pilot CSV
- pilot rows that do not match any baseline `pole_id`

### What match mode writes

- `real_pilot_data/P_CONTROLLED_001/notes/pole_id_match_report.md`

## How This Fits the Full Pilot Workflow

Use the helper together with the existing controlled-pilot docs:

- [AI_CONTROL/73_STAGE4C_CONTROLLED_BASELINE_PILOT_PREP.md](/Users/noelcollins/Unitas-GridFlow/AI_CONTROL/73_STAGE4C_CONTROLLED_BASELINE_PILOT_PREP.md)
- [AI_CONTROL/74_STAGE4C_BASELINE_POLE_ID_MATCH_PROTOCOL.md](/Users/noelcollins/Unitas-GridFlow/AI_CONTROL/74_STAGE4C_BASELINE_POLE_ID_MATCH_PROTOCOL.md)
- [AI_CONTROL/75_STAGE4C_CONTROLLED_PILOT_DECISION_TEMPLATE.md](/Users/noelcollins/Unitas-GridFlow/AI_CONTROL/75_STAGE4C_CONTROLLED_PILOT_DECISION_TEMPLATE.md)
- [AI_CONTROL/80_CONTROLLED_PILOT_FIELD_PACK_V1.md](/Users/noelcollins/Unitas-GridFlow/AI_CONTROL/80_CONTROLLED_PILOT_FIELD_PACK_V1.md)
- [AI_CONTROL/81_CONTROLLED_PILOT_PHOTO_AND_EVIDENCE_RULES.md](/Users/noelcollins/Unitas-GridFlow/AI_CONTROL/81_CONTROLLED_PILOT_PHOTO_AND_EVIDENCE_RULES.md)
- [AI_CONTROL/82_CONTROLLED_PILOT_OPERATOR_DECISION_NOTES.md](/Users/noelcollins/Unitas-GridFlow/AI_CONTROL/82_CONTROLLED_PILOT_OPERATOR_DECISION_NOTES.md)

Recommended sequence:

1. Run helper in prepare mode.
2. Review extracted baseline `pole_id` list.
3. Capture the real field pilot using the starter CSV.
4. Run `scripts/validate_stage4_pilot.py` on the completed pilot CSV.
5. Run helper in match mode.
6. Fill the decision template using:
   - validator report
   - helper match report
   - Noel's operator notes

## Blocking Conditions

The helper should be treated as blocking if it reports:

- duplicate baseline `pole_id` values
- duplicate pilot `pole_id` values
- missing/unsafe pilot `pole_id` values

If those appear, Noel should not move toward Stage 4C runtime decisions until they are resolved.

## Stage 4C Boundary

This helper does **not**:

- integrate Stage 4 into runtime uploads
- write to live job outputs
- update map data
- change popups
- change Review OS
- approve Stage 4C

Stage 4C remains blocked until Noel records a controlled pilot result and signs the decision board.
