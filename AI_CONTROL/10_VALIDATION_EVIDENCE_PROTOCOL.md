# Validation Evidence Protocol

Purpose: define what evidence is required before claiming branch readiness.

## Baseline Validation

Run on every branch unless the task explicitly says otherwise:

```bash
pytest -v
pre-commit run --all-files
```

Record both commands in `AI_CONTROL/04_VALIDATION_LOG.md`.

## Browser / Manual Review Rules

Browser validation is required when changes touch:

- `app/static/js/map-viewer.js`
- `app/static/css/map-viewer.css`
- `app/templates/map_viewer.html`
- popup content or layout
- review navigation
- route highlight
- release map behavior
- planner awareness
- lifecycle visualization
- manual review harness semantics

Use the manual review harness when possible:

```bash
python scripts/manual_review.py --jobs P008/F001 P010 --suite baseline --overview-screenshot
```

Add a task-specific checklist when one exists.

## Required Real Jobs

Default UI/map validation jobs:

- `P008/F001`
- `P010/F001` or `P010`

Use Gordon and Bellsprings when the task touches real-job robustness, lifecycle, or structured-capture planning.

## Screenshot Rules

- Do not require screenshots for passed checks.
- Capture screenshots only for failed checks unless `--evidence-screenshot` or `--overview-screenshot` is requested.
- If overview screenshots are captured, record them as overview evidence, not failure evidence.
- Record screenshot state as `yes`, `no`, or `unknown`.

## Failures JSON Rules

- If the manual review harness runs, record the `validation_runs/<timestamp>/failures.json` status.
- `[]` means no harness failures.
- Any non-empty array must be summarized in the failed-validation report.

## Console Log Rules

- Browser console output must be recorded when using the manual review harness.
- Treat runtime JavaScript errors as validation failures unless proven unrelated browser-extension noise.
- Favicon 404 noise is acceptable and should not block merge.

## Evidence Log Format

Each validation entry must include:

- timestamp
- branch
- commit
- jobs tested
- command run
- report path
- failures status
- screenshots
- verdict
- notes for skipped browser validation
