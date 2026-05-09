# GridFlow Validation Workflow

This document describes **when** and **how** to run each validation
step, how the manual review harness fits with pytest and pre-commit,
and where the evidence lands. It is the practical companion to
[ARCHITECTURE.md](ARCHITECTURE.md) and
[FIELD_REFERENCE_GUIDE.md](FIELD_REFERENCE_GUIDE.md).

GridFlow is **validation-led, not feature-led**. No change is "done"
until the appropriate validation gate has passed.

## The Three Gates

| Gate | What it covers | When required |
|---|---|---|
| **`pytest`** | Pure unit tests for parsers, validators, schemas, scripts. ~860 tests today. | After **any** code change. |
| **`pre-commit`** | Whitespace, EOL, YAML/JSON syntax, large-file guard, ruff (lint), ruff-format. | Always before commit (the hooks run automatically on `git commit`). |
| **`scripts/manual_review.py`** | Real-browser map viewer behaviour: load, popups, route highlight, review navigation, planner-awareness toggle, console cleanliness. | After any change to the map viewer, popups, planner-awareness layer, review navigation, or rulepack/QA logic that surfaces in the UI. |

## When to Run Each

### Run `pytest`

```bash
.venv312/bin/pytest -v
```

- After every code change, no exceptions.
- For a fast loop while writing one feature, scope to the relevant file:
  `pytest tests/test_<module>.py -v`.
- The full suite is fast (~2 s). Always run it before committing.

### Run `pre-commit`

```bash
.venv312/bin/pre-commit run --all-files
```

- Hooks fire automatically on `git commit`. If a hook auto-formats or
  auto-fixes a file, the commit fails — re-stage and commit again.
- Run with `--all-files` manually before opening a PR.
- **Do not** bypass with `--no-verify` unless Noel has explicitly
  authorised it.

### Run the manual review harness

```bash
.venv312/bin/python scripts/manual_review.py \
  --jobs P008/F001 P010 \
  --suite baseline
```

- Required after any UI / map-viewer / popup / review-navigation change.
- Optional but encouraged after rulepack / QA-engine changes that
  surface different popup content.
- Add `--checklist` flags for task-specific assertions.

## Recommended Validation Jobs

Always run against at least these — they cover the real-world variation
the project has been validated against:

| Job | What it stress-tests |
|---|---|
| `P008/F001` (alias `Bellsprings`) | Full Bellsprings 11 kV survey; planner-awareness layer populated. |
| `P010` (alias `Gordon`) | Gordon Pt1 with 157 records; the densest real route. |
| `P005/F001` | Mixed-density survey for span-distance edges. |

For task-specific work the spec usually pins which jobs to use.

## Validation Checklists

`validation_checklists/` contains small YAML files that layer
task-specific assertions on top of the baseline review suite. Existing
checklists:

- `c2e2_popup.yml` — popup section/field assertions for the C2E2 model.
- `planner_awareness.yml` — planner-awareness layer presence.
- `route_highlight.yml` — route highlight DOM class.
- `review_focus.yml` — C2F review focus / issue filter checks.

Each item has at minimum `id` and `type`. Supported `type` values are
documented in [README_MANUAL_REVIEW.md](../README_MANUAL_REVIEW.md).

To use a checklist:

```bash
.venv312/bin/python scripts/manual_review.py \
  --jobs P008/F001 \
  --suite baseline \
  --checklist validation_checklists/c2e2_popup.yml \
  --checklist validation_checklists/route_highlight.yml
```

## What `validation_runs/<UTC>/` Contains

Every harness invocation writes a timestamped folder:

```
validation_runs/20260509_204010/
├── validation_report.md   # human-readable, one row per check
├── console_log.txt        # every browser console entry observed
├── failures.json          # array of failed CheckResult dicts (or [])
└── screenshots/           # only failed checks (unless --evidence-screenshot)
```

### Reading `validation_report.md`

The header tells you the run timestamp, the base URL, the jobs tested,
and any checklists applied. The table that follows has one row per
check with status (`PASS` / `FAIL`), a one-line message, and a
relative path to the screenshot (only present for failures).

### Reading `failures.json`

Empty array (`[]`) means the run is clean. Otherwise each failure is:

```json
{
  "job": "P008/F001",
  "check_id": "popup_remains_readable",
  "description": "Popup remains readable",
  "status": "fail",
  "message": "Popup exceeds viewport: 1480x430",
  "screenshot": "screenshots/P008_F001__popup_remains_readable.png"
}
```

When triaging:

1. Check `console_log.txt` for SEVERE entries from around the failure.
   Real JS errors usually mean the failure is downstream of a console
   error — fix the console error first.
2. Open the screenshot. The viewport is 1440×1000; expect the failure
   to be visible.
3. Re-run with `--evidence-screenshot` if you want a screenshot for the
   passing checks too (useful when a regression is intermittent).

### Screenshot policy

- **Failures only** by default.
- Add `--evidence-screenshot` to capture every passed check too.
- Add `--overview-screenshot` to capture one final viewport screenshot
  per job (handy for design review of the overall map state).

## Logging Validation in Project Control Center

After a validation run, log it in the control layer so the next worker
can see the evidence path:

```bash
.venv312/bin/python scripts/log_validation_run.py \
  --branch claude-code/<your-branch> \
  --commit <sha> \
  --status pass \
  --jobs P008/F001 P010 \
  --command "pytest -v && pre-commit run --all-files && \
             python scripts/manual_review.py --jobs P008/F001 P010 --suite baseline" \
  --report validation_runs/20260509_204010/validation_report.md \
  --failures "[]" \
  --notes "Brief context — what changed, why this validation set"
```

This appends an entry to:

- `AI_CONTROL/04_VALIDATION_LOG.md` — the validation evidence ledger.
- `AI_CONTROL/03_WORKER_LOG.md` — a `worker: validation` entry.

Use `pass` / `fail` (lowercase) for `--status`. Anything else is passed
through verbatim, useful for `partial` or `blocked`.

For non-validation worker activity, use `log_worker_update.py`:

```bash
.venv312/bin/python scripts/log_worker_update.py \
  --worker claude-code \
  --branch claude-code/<your-branch> \
  --summary "Implemented X. Refactored Y." \
  --files "app/foo.py,tests/test_foo.py" \
  --validation "pytest passing; pre-commit clean" \
  --next-action "Run manual review and update handoff"
```

## Updating the Handoff

`AI_CONTROL/05_HANDOFF.md` is the latest operational handoff. Before
ending a session or handing back to Noel:

- The marked active-task section is overwritten by `start_task.py` /
  `update-handoff` flows; do not edit it by hand unless updating
  status/summary.
- Add a task-specific status block (like the "Stage 4 Foundation —
  Status" block) when a multi-file task lands, listing:
  - branch, commit
  - what changed
  - what is **not** implemented yet
  - validation status
  - next action

## How Human Visual Review Fits In

The harness covers what a machine can verify. It cannot verify:

- Whether a popup row's wording is **right** for a designer.
- Whether a colour combination meets accessibility expectations on a
  real screen.
- Whether the order of issues feels useful in a real review session.

For UI changes, after the harness is green, **open the page in a real
browser** and click through the golden path and a few edge cases on
each recommended job. The harness verifies behaviour; you verify
**experience**.

If something feels off in human review, treat it as a regression. Add
a checklist item for the next run so the harness picks it up next time.

## Common Failure Modes and Their Triage

| Symptom in `failures.json` | Likely cause | First fix to try |
|---|---|---|
| `console_clean: SEVERE …` | Real JS error | Fix the JS error; the other failures usually disappear. |
| `popup_remains_readable: Popup exceeds viewport` | CSS regression | Check `.leaflet-popup-content` `max-width` / `max-height` in `map-viewer.css`. |
| `route_highlight_works: 0 highlighted span elements` | `gridflowMapViewer` API drift | Confirm `_spanLineRefs` and `handleDirectSpanClick` still match the harness's expectation. |
| `target_map_loads: timed out` | Map data fetch slow or rulepack badge stuck on "Loading…" | Inspect the network response for `/map/data/...` and the rulepack inference path. |
| `planner_awareness_toggle_works: toggle disabled` | Planner-awareness data missing for the job | Verify the dataset has awareness markers; otherwise scope a checklist exclusion. |

## Final Rule

If a change introduces a new UI surface, **add a checklist item for
it**. The harness only catches what it knows to look for; the moment
something becomes load-bearing, it deserves a check. Validation
coverage compounds over time the same way unit-test coverage does.
