# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Record P_REAL_001_MINI Mini Pilot Result
- Branch: `codex/p-real-001-mini-result-record`
- Owner: codex
- Lane: Stage 4 field pilot execution
- Status: ready_for_review
- Requested by: Noel
- Runtime changes allowed: no live app integration; control/docs/changelog updates only; no real photos, real CSV, or local validation outputs may be committed
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python3.13 scripts/repo_health.py`; `python3.13 scripts/merge_safety_check.py codex/p-real-001-mini-result-record`
- Validation result: `pytest -v` passed with 1068 passed, 1 skipped; `pre-commit run --all-files` passed; `python3.13 scripts/repo_health.py` is warning-only for known numbering collisions; `python3.13 scripts/merge_safety_check.py codex/p-real-001-mini-result-record` is safe to merge; tracked record created from the local `P_REAL_001_MINI` final pilot result without committing `real_pilot_data/` or `validation_runs/`
- Browser validation required: no; Stage 4B is not live-integrated into UI/runtime
- Popup scope changes allowed: no

## Goal

Create a tracked, non-sensitive project record of the `P_REAL_001_MINI` local
mini-pilot result so the project can retain the verdict, warning profile, and
Stage 4C gate outcome without committing raw evidence or local-only reports.

## Scope

- Add `AI_CONTROL/70_P_REAL_001_MINI_FIELD_PILOT_RESULT.md`.
- Record the mini-pilot row counts, evidence-cleanup result, warning profile, and gate verdict.
- Update board, task tracker, worker log, validation log, handoff, and changelog.
- Keep all raw pilot evidence, CSV data, and local validation reports ignored and untracked.

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Real evidence or report commits.
- Archive files.

## Acceptance Criteria

- The project has a tracked control-layer record of the mini-pilot outcome.
- The tracked record contains no raw photos, raw CSV payload, or local validation artefacts.
- Stage 4C remains explicitly blocked and the next recommended pilot is recorded.
- `pytest -v`, `pre-commit run --all-files`, `repo_health.py`, and
  `merge_safety_check.py` pass or report only known non-blocking warnings.

## Current Next Action

Review/merge this control-record branch, then plan the next controlled pilot
against a real GridFlow/Trimble job baseline with exact `pole_id` matching.
Stage 4C remains blocked until that stronger pilot result and Noel's manual
go/no-go decision exist.
