# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Field Pilot Command Center v1
- Branch: `codex/field-pilot-command-center-v1`
- Owner: codex
- Lane: Stage 4 field pilot execution
- Status: ready_for_review
- Requested by: Noel
- Runtime changes allowed: no live app integration; command-center polish, docs, ignored local-data paths, fixtures, and tests only
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python3.13 scripts/repo_health.py`; `python3.13 scripts/merge_safety_check.py codex/field-pilot-command-center-v1`; run `scripts/validate_stage4_pilot.py` on valid, invalid, duplicate, and golden dry-run fixtures
- Validation result: `pytest -v` passed with 1062 passed, 2 skipped; `pre-commit run --all-files` passed; `python3.13 scripts/repo_health.py` is warning-only for known numbering collisions; `python3.13 scripts/merge_safety_check.py codex/field-pilot-command-center-v1` is safe to merge; dry-run CLI coverage now includes pilot, duplicate, and golden fixtures with stable JSON/Markdown reports
- Browser validation required: no; Stage 4B is not live-integrated into UI/runtime
- Popup scope changes allowed: no

## Goal

Turn the field-pilot validator into a full operator-facing command center with
clear terminal verdicts, stronger Markdown/JSON reporting, evidence-folder
edge-case handling, and dry-run coverage against the synthetic pilot fixtures.

## Scope

- Upgrade `validate_stage4_pilot.py` with operator-facing PASS/PARTIAL/NO-GO output.
- Stabilize JSON report keys for future automation.
- Improve Markdown report sections so Noel can use them directly after field capture.
- Harden evidence-folder handling for missing, empty, malformed, duplicate, and multi-reference cases.
- Extend dry-run coverage across pilot and golden CSV fixtures.
- Update operator docs, control files, and changelog.

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Archive files.

## Acceptance Criteria

- Noel has one command to validate a real pilot CSV after capture.
- The CLI writes terminal, JSON, and Markdown output without touching live job outputs.
- Evidence folder filename/reference checks report missing, empty, duplicate, invalid, multi-reference, and unreferenced cases.
- Real pilot raw data and local validation outputs are git-ignored by default.
- The execution system does not add runtime/UI Stage 4 integration.
- `pytest -v`, `pre-commit run --all-files`, `repo_health.py`, and
  `merge_safety_check.py` pass or report only known non-blocking warnings.

## Current Next Action

Review/merge this branch, then run the command center against Noel's real local
pilot CSV and evidence folder. Stage 4C remains blocked until Noel records the
pilot result and a manual go/no-go decision.
