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

## Dry-run examples

Validate a known-good sample:

```bash
python3.13 scripts/validate_stage4_pilot.py \
  --csv tests/fixtures/stage4/pilot_valid_sample.csv \
  --pilot-name SAMPLE_VALID \
  --evidence-dir tests/fixtures/stage4/evidence/valid \
  --out /tmp/stage4_sample_valid
```

Validate a known-bad sample:

```bash
python3.13 scripts/validate_stage4_pilot.py \
  --csv tests/fixtures/stage4/pilot_invalid_sample.csv \
  --pilot-name SAMPLE_INVALID \
  --out /tmp/stage4_sample_invalid
```

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
python scripts/merge_safety_check.py codex/field-pilot-command-center-v1
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
- the terminal summary clearly shows `PASS`, `PARTIAL`, or `NO-GO`
- the report gives a clear next action and a Stage 4C gate implication

## How to read the command output

The terminal summary is the operator quick read:

- verdict headline
- row counts
- blocker counts
- evidence status
- top issues
- next action
- JSON and Markdown report paths

The Markdown report is the detailed operator record:

- executive summary
- pilot verdict
- Stage 4C gate implication
- row and field issue detail
- evidence/photo findings
- recommended fixes
- what Noel should do next

## Pass / fail interpretation

Treat the pilot as operationally successful only if:

- the real pilot CSV validates without blocked rows from identity mistakes
- invalid rows are explainable and fixable
- the template was usable in the field without repeated guesswork
- Noel can explain every warning or review-required result

Interpret the final decision like this:

- `PASS` / `GO`: good enough for Noel to review as real Stage 4C input, but still not automatic approval
- `PARTIAL / RE-PILOT REQUIRED`: useful evidence exists, but more capture or cleanup is needed
- `NO-GO`: fix the CSV/evidence/template problems before any Stage 4C discussion

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

If the command returns `NO-GO` because the CSV could not be loaded, record that
as an execution failure first. Do not treat it as row-level pilot evidence.

## Do not commit by default

Keep these local-only unless Noel explicitly approves a redacted artifact:

- `real_pilot_data/`
- `validation_runs/stage4_pilots/`

Committed test fixtures remain synthetic only.

Do commit only:

- synthetic fixtures
- docs
- tests
- explicitly approved redacted examples

Do not commit:

- real photos
- raw field CSVs
- automatic local operator reports

## Using an existing survey workbook as a rehearsal dataset

If Noel already has a workbook export such as `survey_records_sorted_tabs.xlsx`,
use it as a rehearsal dataset before the fresh iPad pilot. Keep the workbook
local under:

`real_pilot_data/<pilot-name>/source/survey_records_sorted_tabs.xlsx`

Convert the most relevant sheet to a Stage 4 pilot CSV:

```bash
python3.13 scripts/convert_stage4_workbook_to_pilot_csv.py \
  --xlsx real_pilot_data/P011_EXISTING/source/survey_records_sorted_tabs.xlsx \
  --sheet "Raw Capture" \
  --out real_pilot_data/P011_EXISTING/csv/pilot_existing_P011.csv
```

Then validate it with the existing pilot validator:

```bash
python3.13 scripts/validate_stage4_pilot.py \
  --csv real_pilot_data/P011_EXISTING/csv/pilot_existing_P011.csv \
  --pilot-name P011_EXISTING \
  --evidence-dir real_pilot_data/P011_EXISTING/evidence \
  --out validation_runs/stage4_pilots/P011_EXISTING
```

Treat this as rehearsal evidence only. It is useful for checking field
coverage, naming consistency, and validator fit, but it does not replace a
fresh iPad pilot for capture UX, photo workflow, and live operator friction.

## Runtime boundary

Do not treat a passing pilot CSV as approval for Stage 4C. Runtime integration
stays blocked until Noel records a separate go/no-go decision.
