# Stage 4 Real Survey Baseline Conversion Guide

Purpose: describe how to use local real survey controller exports as Stage 4 baseline conversion references without committing survey evidence or authorizing runtime integration.

## Boundary

This guide is for:

- local-only baseline inspection
- exact support identity extraction
- Stage 4 starter CSV generation
- compatibility review of capture-shaped survey files

This guide does not authorize:

- Stage 4C runtime integration
- live upload/intake changes
- automatic approval of a controlled pilot
- committing raw survey evidence, PDFs, photos, or local validation outputs

## Input Types

### Raw controller-export CSVs

Typical usable signals:

- point number / point identity in column 0 or equivalent
- easting/northing/level columns
- feature code column
- remarks and height attributes in later paired columns

Examples from the current local pack:

- Bellsprings sample controller export
- Gordon original
- Gordon PR2

### Capture-compatible CSVs

These are already shaped like Stage 4 capture files and are useful for compatibility checks only.

Example from the current local pack:

- `pole_survey_2026-05-11_complete.csv`

Do not treat a capture-compatible CSV as a raw baseline source unless the identity workflow explicitly supports that use.

## Recommended Local Workflow

### 1. Inspect the raw source locally

Confirm:

- support identity source exists
- feature code/type signal exists
- support counts are large enough for the intended rehearsal
- no duplicate exact identities block the file

### 2. Generate a local-only starter CSV

Use the controlled baseline helper:

```bash
python3.13 scripts/prepare_stage4_controlled_pilot.py \
  --baseline-csv real_pilot_data/P_BASELINE_SURVEY_PACK/raw/<source>.csv \
  --pilot-name <pilot_name> \
  --out real_pilot_data/P_BASELINE_SURVEY_PACK/csv/<starter>.csv \
  --notes-out real_pilot_data/P_BASELINE_SURVEY_PACK/notes/<extract>.md
```

### 3. Review the extract notes

Check for:

- total scanned rows
- support candidate count
- identity source
- type/code source
- duplicate identity blockers

### 4. Keep technical fields conservative

The starter CSV is for baseline preparation only.

Use:

- exact baseline `pole_id`
- blank or `unknown` for unconfirmed technical fields
- no inferred voltage, conductor size, pole class, or equipment rating unless independently confirmed

### 5. Use field evidence separately

A raw baseline export helps with:

- exact `pole_id` matching
- route/context alignment
- starter capture preparation

It does not replace:

- field photos
- access observations
- defect evidence
- live condition assessment

## Current Local Recommendations

### Best compact baseline

- Bellsprings sample controller export
- `40` support rows

### Best large baseline

- Gordon original
- `128` support rows

### Secondary usable baseline

- Gordon PR2
- `53` support rows

### Not currently safe for exact-match controlled work

- Gordon PR1
- blocked by duplicate point identity `4`

### Compatibility review only

- Noel's `pole_survey_2026-05-11_complete.csv`

## Data Protection Rules

Do not commit:

- `real_pilot_data/`
- `uploads/` local candidate CSVs
- `validation_runs/`
- raw survey PDFs
- real field photos

Tracked outputs from this workflow should stay limited to:

- control/audit summaries
- operator guides
- non-sensitive aggregate findings

## Stage 4C Gate Rule

Baseline conversion evidence is preparation evidence only.

Stage 4C remains blocked until:

1. a controlled pilot is run against a real baseline,
2. exact `pole_id` matching is demonstrated,
3. validator results are recorded,
4. the signed decision workflow is completed.
