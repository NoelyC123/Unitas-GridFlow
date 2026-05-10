# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Stage 4A Library Correctness Fixes
- Branch: `codex/stage4a-library-correctness-fixes`
- Owner: codex
- Lane: Stage 4 library foundation
- Status: merge_commit_pending
- Requested by: Noel
- Runtime changes allowed: no live app integration; library/schema/provenance fixes only
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python scripts/repo_health.py`; `python scripts/merge_safety_check.py`
- Validation result: `pytest -v tests/test_stage4a_safety_boundary.py` passed, 43 passed; `pytest -v` passed, 992 passed; `pre-commit run --all-files` passed
- Browser validation required: no; Stage 4A is not live-integrated into UI/runtime
- Popup scope changes allowed: no

## Goal

Implement the safe Stage 4A structured-capture library correctness fixes identified in the Stage 4 readiness specification, without wiring Stage 4 data into live upload, QA, map rendering, Review OS, or C2E2 popups.

## Scope

- Preserve `"none"` as a valid explicit Stage 4 value for `stay_type`, `equipment_type`, `lean_direction`, and `lean_severity`.
- Keep true blanks and placeholder tokens blank without globally destroying valid `"none"` values.
- Add deterministic row identity handling around `pole_id`, with no anonymous rows considered merge-ready.
- Register `source="structured_capture"` as a valid library-level provenance source.
- Add a row/field validation result model with validity, warnings, errors, source, row identity, reason, and recommendation fields.
- Add and align regression tests proving Stage 4 remains out of C2E2 popups and Review OS/map-viewer runtime behaviour.
- Remove strict xfail markers from fixed Stage 4A safety-boundary tests.
- Update Control Center logs, handoff, and changelog.

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4B schema/field validation expansion.
- Stage 4C runtime integration.
- Stage 4D browser/review workspace surfacing.
- Archive files.

## Acceptance Criteria

- Stage 4 validators preserve valid `"none"` values for allowed fields and reject invalid `"none"` values where appropriate.
- Missing `pole_id` is detected and rows without `pole_id` are not merge-ready.
- Valid `pole_id` and aliases are accepted deterministically.
- `structured_capture` is accepted in the library provenance path but no Stage 4 fields are added to live C2E2 popups or Review OS.
- C2E2 popup truthfulness regression tests pass.
- `pytest -v`, `pre-commit run --all-files`, `repo_health.py`, and `merge_safety_check.py` pass or report only known non-blocking warnings.
- Safety harness reports no XPASS(strict) and no failing VLD-2 placeholder identity tests.

## Current Next Action

Commit the completed merge, rerun repo health and merge safety, and hand back.
