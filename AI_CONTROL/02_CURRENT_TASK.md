# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: P_CONTROLLED_001 controlled baseline pilot setup
- Branch: `master`
- Owner: Noel / next worker
- Lane: Stage 4 field pilot execution
- Status: ready_to_start
- Requested by: Noel
- Runtime changes allowed: no live app integration; control/helper only; no real evidence may be committed
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python3.13 scripts/repo_health.py`; `python3.13 scripts/merge_safety_check.py <next branch>`
- Validation result: governance and audit merge pending completion on `master`; Stage 4C remains blocked
- Browser validation required: no; control/docs only, no runtime UI changes
- Popup scope changes allowed: no

## Goal

Use a real local baseline CSV already present in this checkout to prepare
`P_CONTROLLED_001`, then build/run the controlled baseline pilot helper with
exact `pole_id` matching and the field-pack/operator documents now merged.

## Scope

- Use the preserved clean-worktree audit result in `AI_CONTROL/79_EXISTING_SURVEY_BASELINE_CANDIDATE_AUDIT.md` as provenance for the earlier control-only branch.
- Select a local candidate baseline CSV from this main checkout for `P_CONTROLLED_001`.
- Use docs 73–75 and 80–82 together for execution planning:
  - docs 73–75: baseline pilot prep, exact `pole_id` protocol, formal decision template
  - docs 80–82: operator field-day procedure, photo/evidence rules, operator decision notes
- Build/run the controlled baseline pilot helper on a separate follow-on branch.
- Keep `uploads/`, `real_pilot_data/`, and `validation_runs/` out of governance commits.

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Real evidence or report commits.
- Archive files.

## Acceptance Criteria

- Baseline audit and field-pack governance docs are merged cleanly on `master`.
- `AI_CONTROL/79_EXISTING_SURVEY_BASELINE_CANDIDATE_AUDIT.md` remains as the clean-audit provenance record.
- Docs 80–82 are available for Noel and the next worker.
- Project state reflects that:
  - the clean audit worktree had no tracked candidate files
  - this local main checkout does contain local candidate upload/baseline CSVs
  - `P_REAL_001_MINI` remains only a successful shakedown
  - Stage 4C runtime integration remains blocked
- `pytest -v` passes.
- `pre-commit run --all-files` passes clean.
- `python3.13 scripts/repo_health.py` reports warning-only (known collisions only).
- `python3.13 scripts/merge_safety_check.py` confirms safe to merge for the governance branch being merged.
- `real_pilot_data/`, `validation_runs/`, and local `uploads/` CSVs remain uncommitted.

## Current Next Action

1. Complete the current governance merge on `master`.
2. Use a local baseline CSV for `P_CONTROLLED_001`.
3. Build/run the controlled baseline pilot helper on a new follow-on branch.
4. Execute the controlled baseline pilot with exact `pole_id` matching.
5. Keep Stage 4C runtime integration blocked until the controlled pilot verdict is recorded.
