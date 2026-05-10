# Stage 4 Pilot Validation Instructions

## What this validates

These steps validate a real pilot CSV through the existing Stage 4B preview
rules. They do not merge any data into GridFlow runtime outputs.

## Save location

After the field session, save the pilot file as:

`tests/fixtures/stage4/pilot_real_<jobid>.csv`

Examples:

- `tests/fixtures/stage4/pilot_real_P008_F001.csv`
- `tests/fixtures/stage4/pilot_real_P010.csv`

## File preparation rules

Before validating:

1. Keep the header row intact.
2. Save as UTF-8 CSV.
3. Keep `capture_date` in `YYYY-MM-DD`.
4. Keep `pole_id` exactly aligned to Trimble identity.
5. Use `structured_capture` in the `source` column.
6. Use `none` only where explicitly allowed by the field dictionary.

## Validation commands

Run the package-specific tests first:

```bash
pytest -v tests/test_stage4_pilot_package.py
```

If a real pilot CSV has been saved in `tests/fixtures/stage4/`, run the
real-pilot check directly:

```bash
pytest -v tests/test_stage4_pilot_package.py -k real_pilot
```

Then run the full repo checks required for this branch:

```bash
pytest -v
pre-commit run --all-files
python scripts/repo_health.py
python scripts/merge_safety_check.py codex/real-ipad-field-pilot-package-v1
```

## What to inspect

Look for these outcomes:

- header validation passes
- no blocked rows caused by missing/unsafe `pole_id`
- no invalid rows caused by slash dates or bad enum values
- explicit `none` values only appear in allowed fields
- duplicate `pole_id` rows are detected when present
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
- issues found
- field workflow friction
- missing fields
- unnecessary fields

## Runtime boundary

Do not treat a passing pilot CSV as approval for Stage 4C. Runtime integration
stays blocked until Noel records a separate go/no-go decision.
