# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Stage 4C controlled pilot baseline helper v1
- Branch: `codex/stage4c-controlled-pilot-baseline-helper-v1`
- Owner: codex
- Lane: Stage 4 field pilot execution
- Status: ready_for_review
- Requested by: Noel
- Runtime changes allowed: no live app integration; control/helper only; no real evidence may be committed
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python3.13 scripts/repo_health.py`; `python3.13 scripts/merge_safety_check.py <next branch>`
- Validation result: helper implemented; focused tests passed; full validation passed; Stage 4C remains blocked
- Browser validation required: no; control/docs only, no runtime UI changes
- Popup scope changes allowed: no

## Goal

Use the real local baseline CSV already present in this checkout to generate
the `P_CONTROLLED_001` starter capture sheet, extract exact baseline
`pole_id` candidates, and provide an exact-match comparison helper for the
completed pilot CSV.

## Scope

- Use the preserved clean-worktree audit result in `AI_CONTROL/79_EXISTING_SURVEY_BASELINE_CANDIDATE_AUDIT.md` as provenance for the earlier control-only branch.
- Use the local `real_pilot_data/P_CONTROLLED_001/baseline/baseline.csv` as the working baseline in this checkout without committing it.
- Use docs 73–75 and 80–82 together for execution planning:
  - docs 73–75: baseline pilot prep, exact `pole_id` protocol, formal decision template
  - docs 80–82: operator field-day procedure, photo/evidence rules, operator decision notes
- Build/run the controlled baseline pilot helper on this branch.
- Keep `uploads/`, `real_pilot_data/`, and `validation_runs/` out of governance commits.

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Real evidence or report commits.
- Archive files.

## Acceptance Criteria

- `scripts/prepare_stage4_controlled_pilot.py` supports prepare mode and match mode.
- `docs/STAGE4_CONTROLLED_BASELINE_PILOT_OPERATOR_GUIDE.md` gives Noel exact CLI and workflow instructions.
- `tests/test_stage4_controlled_pilot_baseline.py` proves:
  - raw controller baseline extraction works
  - exact-match-only rules are enforced
  - duplicates/missing `pole_id` values are blocking
  - original `pole_id` text is preserved in reports
- Project state reflects that:
  - the clean audit worktree had no tracked candidate files
  - this local main checkout does contain the local `P_CONTROLLED_001` baseline CSV
  - the local baseline currently yields `57` scanned rows and `40` candidate support rows
  - `P_REAL_001_MINI` remains only a successful shakedown
  - Stage 4C runtime integration remains blocked
- `pytest -v` passes.
- `pre-commit run --all-files` passes clean.
- `python3.13 scripts/repo_health.py` reports warning-only (known collisions only).
- `python3.13 scripts/merge_safety_check.py` confirms safe to merge for `codex/stage4c-controlled-pilot-baseline-helper-v1`.
- `real_pilot_data/`, `validation_runs/`, and local `uploads/` CSVs remain uncommitted.

## Current Next Action

1. Run the full validation suite on this helper branch.
2. Merge the helper branch after review.
3. Use the generated starter CSV and extract report to execute the controlled baseline pilot.
4. Run helper match mode on the completed pilot CSV with exact `pole_id` matching.
5. Keep Stage 4C runtime integration blocked until the controlled pilot verdict is recorded.
