# Stage 4 Pilot Validation Instructions

## What this validates

These steps validate a real pilot CSV through the existing Stage 4B preview
rules. They do not merge any data into GridFlow runtime outputs.

## Save location

After the field session, keep the raw CSV out of Git and save it under:

`real_pilot_data/<pilot-name>/csv/pilot_real_<jobid>.csv`

Examples:

- `real_pilot_data/P_REAL_001/csv/pilot_real_P008_F001.csv`
- `real_pilot_data/P_REAL_002/csv/pilot_real_P010.csv`

Synthetic committed fixtures remain under `tests/fixtures/stage4/`. Real pilot
raw data should not be committed unless Noel explicitly approves a redacted
example.

## File preparation rules

Before validating:

1. Keep the header row intact.
2. Save as UTF-8 CSV.
3. Keep `capture_date` in `YYYY-MM-DD`.
4. Keep `pole_id` exactly aligned to Trimble identity.
5. Use `structured_capture` in the `source` column.
6. Use `none` only where explicitly allowed by the field dictionary.

## One-command pilot validation

Run the pilot validator after capture:

```bash
python3.13 scripts/validate_stage4_pilot.py \
  --csv real_pilot_data/P_REAL_001/csv/pilot_real_P008_F001.csv \
  --pilot-name P_REAL_001 \
  --evidence-dir real_pilot_data/P_REAL_001/photos \
  --out validation_runs/stage4_pilots/P_REAL_001
```

If your environment exposes `python` rather than `python3.13`, the same script
can be run as `python scripts/validate_stage4_pilot.py ...`.

The command prints a terminal summary and writes:

- `validation_runs/stage4_pilots/<pilot-name>/pilot_validation_report.json`
- `validation_runs/stage4_pilots/<pilot-name>/pilot_validation_report.md`

## Repo validation checks

Run the package tests first:

```bash
pytest -v tests/test_stage4_pilot_package.py tests/test_stage4_field_pilot_execution.py
```

Then run the full repo checks required for this branch:

```bash
pytest -v
pre-commit run --all-files
python scripts/repo_health.py
python scripts/merge_safety_check.py codex/real-field-pilot-execution-system-v1
```

## What to inspect

Look for these outcomes:

- header validation passes
- no blocked rows caused by missing/unsafe `pole_id`
- no invalid rows caused by slash dates or bad enum values
- explicit `none` values only appear in allowed fields
- duplicate `pole_id` rows are detected when present
- the evidence section clearly reports missing referenced photos, unreferenced
  photos, duplicate names, and invalid filename patterns
- runtime isolation tests remain green

## Pass / fail interpretation

Treat the pilot as operationally successful only if:

- the real pilot CSV validates without blocked rows from identity mistakes
- invalid rows are explainable and fixable
- the template was usable in the field without repeated guesswork
- Noel can explain every warning or review-required result

Treat the pilot as a NO-GO for Stage 4C if:

- `pole_id` matching is unreliable
- date/enum guidance caused repeated user error
- several fields were unclear on the iPad
- the CSV required post-hoc guesswork to pass validation

## Failure recording

Record failures in
[STAGE4_PILOT_RESULT_SUMMARY_TEMPLATE.md](/Users/noelcollins/Unitas-GridFlow/docs/STAGE4_PILOT_RESULT_SUMMARY_TEMPLATE.md)
under:

- validation result
- report output paths
- issues found
- field workflow friction
- missing fields
- unnecessary fields

## Do not commit by default

Keep these local-only unless Noel explicitly approves a redacted artifact:

- `real_pilot_data/`
- `validation_runs/stage4_pilots/`

Committed test fixtures remain synthetic only.

## Runtime boundary

Do not treat a passing pilot CSV as approval for Stage 4C. Runtime integration
stays blocked until Noel records a separate go/no-go decision.
