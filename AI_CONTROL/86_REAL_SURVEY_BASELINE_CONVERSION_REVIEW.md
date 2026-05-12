# Stage 4 Real Survey Baseline Conversion Review

Purpose: record the suitability of locally available real survey files as Stage 4 baseline conversion inputs without committing any real survey evidence.

## Scope

Reviewed local-only files under `real_pilot_data/P_BASELINE_SURVEY_PACK/raw/`:

- `Sample/Bellsprings - CSV File.csv`
- `Sample/*.pdf`
- `gordon_original.csv`
- `gordon_pr1.csv`
- `gordon_pr2.csv`
- `pole_survey_2026-05-11_complete.csv`

## Review Method

- Header-level and aggregate row-count inspection only for tracked documentation.
- No raw survey rows copied into tracked files.
- Local-only starter CSVs and notes created under `real_pilot_data/P_BASELINE_SURVEY_PACK/`.
- Stage 4C runtime integration remains blocked.

## Field Structure Findings

### Raw controller-export pattern

The Bellsprings and Gordon controller exports share the same broad structure:

- column 0: point number / support identity
- column 1: easting
- column 2: northing
- column 3: level
- column 4: feature code
- later paired attributes include `REMARK`, `HEIGHT`, and land-use style fields

This makes them usable as baseline conversion sources for exact identity extraction and Stage 4 starter generation.

### Noel local survey CSV pattern

`pole_survey_2026-05-11_complete.csv` is not a raw controller baseline.

Findings:

- Includes all current Stage 4 headers
- Includes 3 extra local-only columns:
  - `DNO_marking`
  - `warning_sign_present`
  - `inspection_plates`
- Includes 1 blank trailing header column

Conclusion: useful as a Stage 4 capture-compatibility sample, not as a baseline controller extract for exact `pole_id` extraction.

## Support Counts

### Bellsprings sample controller export

- Total rows inspected: `58`
- Support rows:
  - `Pol`: `26`
  - `EXpole`: `11`
  - `Angle`: `3`
- Estimated support total: `40`
- Suitability: `SUITABLE`
- Reason: compact, clean controller-export structure with enough support rows for a controlled pilot fallback or starter extraction.

### Gordon original

- Total rows inspected: `164`
- Support rows:
  - `Pol`: `97`
  - `EXpole`: `24`
  - `Angle`: `7`
- Estimated support total: `128`
- Suitability: `SUITABLE`
- Reason: strongest large baseline source in the local pack; enough support density for a broader conversion rehearsal or controlled pilot preparation.

### Gordon PR1

- Total rows inspected: `114`
- Support rows:
  - `Pol`: `62`
  - `EXpole`: `17`
  - `Angle`: `7`
- Estimated support total: `86`
- Suitability: `NOT SUITABLE` for strict exact-match use in current form
- Reason: duplicate point identity `4` is a blocking issue for exact `pole_id` matching.

### Gordon PR2

- Total rows inspected: `70`
- Support rows:
  - `Pol`: `41`
  - `EXpole`: `8`
  - `Angle`: `4`
- Estimated support total: `53`
- Suitability: `SUITABLE`
- Reason: enough support rows for a controlled baseline subset and no known duplicate identity blocker found during the aggregate review.

## Bellsprings PDF Pack Review

High-level only:

- Pole schedule PDF: useful reference context for support numbering/type review
- Route map PDF: useful route/context reference
- Profile PDF: engineering profile context
- TIS PDF: supporting technical reference

These PDFs are reference evidence only in this review. They are not treated as direct Stage 4 row inputs.

## Local-Only Outputs Created

### Starter CSVs

- `real_pilot_data/P_BASELINE_SURVEY_PACK/csv/bellsprings_stage4_starter.csv`
- `real_pilot_data/P_BASELINE_SURVEY_PACK/csv/gordon_original_stage4_starter.csv`
- `real_pilot_data/P_BASELINE_SURVEY_PACK/csv/gordon_pr1_stage4_starter.csv`
- `real_pilot_data/P_BASELINE_SURVEY_PACK/csv/gordon_pr2_stage4_starter.csv`

### Extract notes

- `real_pilot_data/P_BASELINE_SURVEY_PACK/notes/bellsprings_stage4_extract.md`
- `real_pilot_data/P_BASELINE_SURVEY_PACK/notes/gordon_original_stage4_extract.md`
- `real_pilot_data/P_BASELINE_SURVEY_PACK/notes/gordon_pr1_stage4_extract.md`
- `real_pilot_data/P_BASELINE_SURVEY_PACK/notes/gordon_pr2_stage4_extract.md`
- `real_pilot_data/P_BASELINE_SURVEY_PACK/notes/noel_local_survey_stage4_compatibility.md`

## Suitability Summary

### Best large baseline candidate

- `gordon_original.csv`
- Reason: `128` support rows and raw controller-export structure suitable for baseline extraction and larger exact-identity preparation work

### Best compact baseline candidate

- `Bellsprings - CSV File.csv`
- Reason: `40` support rows, clean compact structure, practical for smaller conversion rehearsal and fallback pilot preparation

### Usable secondary candidate

- `gordon_pr2.csv`
- Reason: `53` support rows and suitable controller-export structure

### Blocked candidate

- `gordon_pr1.csv`
- Reason: duplicate point identity `4`

### Compatibility-only file

- `pole_survey_2026-05-11_complete.csv`
- Reason: Stage 4-style capture file, not a baseline extract

## Conversion Limitations

- No exact pole-by-pole truth claims should be inferred from this review alone.
- Raw controller exports are suitable for identity extraction and starter generation, not automatic Stage 4C approval.
- Gordon PR1 requires duplicate identity cleanup before strict exact-match use.
- Noel local survey CSV should not be mistaken for a baseline source.
- Real survey files remain local-only and excluded from tracked commits.

## Verdict

- Bellsprings, Gordon original, and Gordon PR2 are suitable local baseline conversion inputs.
- Gordon PR1 is not suitable for exact-match controlled pilot work until duplicate identity is resolved.
- Noel's local survey CSV is useful compatibility evidence but not a baseline source.
- Stage 4C remains blocked.
