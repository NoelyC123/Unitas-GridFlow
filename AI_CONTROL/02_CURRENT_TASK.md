# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Real iPad Field Pilot Package v1
- Branch: `codex/real-ipad-field-pilot-package-v1`
- Owner: codex
- Lane: Stage 4 field pilot operating pack
- Status: ready_for_review
- Requested by: Noel
- Runtime changes allowed: no live app integration; docs/templates/fixtures/tests only
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python scripts/repo_health.py`; `python scripts/merge_safety_check.py codex/real-ipad-field-pilot-package-v1`
- Validation result: `pytest -v` passed with 1042 passed, 1 skipped; `pre-commit run --all-files` passed; `python3.13 scripts/repo_health.py` is warning-only for known numbering collisions; `python3.13 scripts/merge_safety_check.py codex/real-ipad-field-pilot-package-v1` is safe to merge
- Browser validation required: no; Stage 4B is not live-integrated into UI/runtime
- Popup scope changes allowed: no

## Goal

Build the practical end-to-end iPad field pilot package Noel can use to capture
10 to 20 supports and validate the resulting CSV through the existing Stage 4B
preview rules.

## Scope

- Create a real-world field pilot guide, field dictionary, validation instructions,
  evidence-folder protocol, and result-summary template.
- Create an iPad-friendly structured capture pilot template aligned with the
  Stage 4B schema.
- Add pilot fixture CSVs covering valid, invalid, and duplicate-identity field use.
- Add tests proving the pilot package aligns with Stage 4B validation rules and
  stays runtime/UI isolated.
- Update Control Center logs, handoff, and changelog.

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Archive files.

## Acceptance Criteria

- Noel can use the docs and pilot template on an iPad without runtime help.
- Pilot CSV fixtures validate exactly as intended under Stage 4B rules.
- ISO date rules and explicit-`none` rules are clear and test-covered.
- The pilot package does not add runtime/UI Stage 4 integration.
- `pytest -v`, `pre-commit run --all-files`, `repo_health.py`, and
  `merge_safety_check.py` pass or report only known non-blocking warnings.

## Current Next Action

Hand back for review and real-world field execution. Stage 4C remains blocked
until Noel records a real pilot result and go/no-go decision.
