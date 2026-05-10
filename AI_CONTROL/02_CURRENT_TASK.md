# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Stage 4B Structured Capture Validation Preview
- Branch: `codex/stage4b-structured-capture-validation-preview`
- Owner: codex
- Lane: Stage 4 library foundation
- Status: ready_for_review
- Requested by: Noel
- Runtime changes allowed: no live app integration; validation/schema/preview only
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python scripts/repo_health.py`; `python scripts/merge_safety_check.py codex/stage4b-structured-capture-validation-preview`
- Validation result: `pytest -v` passed, 1035 passed; `pre-commit run --all-files` passed; repo health and merge safety warning-only before commit because the tree was dirty/uncommitted
- Browser validation required: no; Stage 4B is not live-integrated into UI/runtime
- Popup scope changes allowed: no

## Goal

Build a complete pre-runtime structured-capture validation and import-preview system that can validate CSV-style Stage 4 rows before any future runtime merge is allowed.

## Scope

- Harden the Stage 4 schema around identity, lifecycle intent, height, material, condition, stay/equipment, evidence, notes, source, and photo-reference fields.
- Add field-level validation metadata: raw value, normalised value, validity, severity, reason, recommendation, source, row id, and pole id.
- Add row-level classification: `merge-ready`, `valid but not merge-ready`, `review-required`, `invalid`, and `blocked`.
- Add file/import preview validation for headers, unknown/missing columns, duplicate pole IDs, summary counts, warnings, errors, and safe preview verdict.
- Regenerate the structured-capture CSV template from the hardened schema.
- Add Stage 4B tests and preserve Stage 4A, C2E2 popup, Review OS, and runtime leakage regression coverage.
- Update Control Center logs, handoff, and changelog.

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Stage 4D browser/review workspace surfacing.
- Archive files.

## Acceptance Criteria

- Clean structured-capture rows produce a safe pre-runtime import preview.
- Missing, unsafe, or duplicate `pole_id` values block preview merge readiness.
- Invalid enums, invalid heights, missing required metadata, unknown sources, and contradictory evidence are classified with clear reasons and recommendations.
- Template headers align with the schema.
- Stage 4 remains isolated from live upload/intake, QA, map rendering, Review OS, and C2E2 popups.
- `pytest -v`, `pre-commit run --all-files`, `repo_health.py`, and `merge_safety_check.py` pass or report only known non-blocking warnings.

## Current Next Action

Commit the completed Stage 4B branch, rerun repo health and merge safety from the committed tree, then hand back for review.
