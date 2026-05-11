# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Real Field Pilot Execution System v1
- Branch: `codex/real-field-pilot-execution-system-v1`
- Owner: codex
- Lane: Stage 4 field pilot execution
- Status: ready_for_review
- Requested by: Noel
- Runtime changes allowed: no live app integration; local pilot validation, docs, ignored local-data paths, fixtures, and tests only
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python scripts/repo_health.py`; `python scripts/merge_safety_check.py codex/real-field-pilot-execution-system-v1`; run `scripts/validate_stage4_pilot.py` on valid and invalid pilot fixtures
- Validation result: `pytest -v` passed with 1049 passed, 2 skipped; `pre-commit run --all-files` passed; `python3.13 scripts/repo_health.py` is warning-only for known numbering collisions; `python3.13 scripts/merge_safety_check.py codex/real-field-pilot-execution-system-v1` is safe to merge; CLI runs produced JSON/Markdown reports for valid and invalid pilot fixtures
- Browser validation required: no; Stage 4B is not live-integrated into UI/runtime
- Popup scope changes allowed: no

## Goal

Build the practical execution system Noel will use after field capture to
validate a real pilot CSV, inspect evidence filenames, generate reports, and
record whether Stage 4C remains blocked, partial, or ready for manual review.

## Scope

- Create a standalone `validate_stage4_pilot.py` CLI for CSV validation,
  evidence-folder checking, and JSON/Markdown report output.
- Add evidence-fixture coverage for clean and problematic filename/reference sets.
- Protect local raw pilot data and validation outputs from accidental Git commits.
- Update pilot validation docs and result template around the new local workflow.
- Add execution-system tests proving report generation, evidence checks, git-ignore
  protection, and runtime-output isolation.
- Update Control Center logs, handoff, and changelog.

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Archive files.

## Acceptance Criteria

- Noel has one command to validate a real pilot CSV after capture.
- The CLI writes terminal, JSON, and Markdown output without touching live job outputs.
- Evidence folder filename/reference checks report missing, duplicate, invalid, and unreferenced photos.
- Real pilot raw data and local validation outputs are git-ignored by default.
- The execution system does not add runtime/UI Stage 4 integration.
- `pytest -v`, `pre-commit run --all-files`, `repo_health.py`, and
  `merge_safety_check.py` pass or report only known non-blocking warnings.

## Current Next Action

Review/merge this branch, then use the CLI against Noel's real local pilot CSV
and evidence folder. Stage 4C remains blocked until Noel records the pilot
result and go/no-go decision.
