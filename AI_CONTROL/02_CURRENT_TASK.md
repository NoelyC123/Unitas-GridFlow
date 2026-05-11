# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Stage 4C Controlled Baseline Pilot Preparation Pack
- Branch: `claude-code/stage4c-controlled-baseline-pilot-prep`
- Owner: claude-code
- Lane: Stage 4 field pilot execution
- Status: ready_for_validation
- Requested by: Noel (implicit from Stage 4C gate requirements)
- Runtime changes allowed: no live app integration; control/docs only; no real evidence may be committed
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python3.13 scripts/repo_health.py`; `python3.13 scripts/merge_safety_check.py claude-code/stage4c-controlled-baseline-pilot-prep`
- Validation result: pending (expected: 1050+ passed, 1 skipped; pre-commit clean; repo_health warning-only; merge_safety_check safe)
- Browser validation required: no; control/docs only, no runtime UI changes
- Popup scope changes allowed: no

## Goal

Create a complete governance package for the next Stage 4C controlled baseline
pilot (30–50 real poles with Trimble baseline). Define exact pole_id matching
rules, pilot workflow, and decision template so Noel has all specifications
needed to execute the real pilot that will determine Stage 4C merge readiness.

## Scope

- Create `AI_CONTROL/73_STAGE4C_CONTROLLED_BASELINE_PILOT_PREP.md` — full preparation guide for 30–50 pole pilot.
- Create `AI_CONTROL/74_STAGE4C_BASELINE_POLE_ID_MATCH_PROTOCOL.md` — exact pole_id matching rules and decision thresholds.
- Create `AI_CONTROL/75_STAGE4C_CONTROLLED_PILOT_DECISION_TEMPLATE.md` — template for recording pilot results and verdicts.
- Update control files: 00_PROJECT_BOARD, 02_CURRENT_TASK, 03_WORKER_LOG, 04_VALIDATION_LOG, 05_HANDOFF, CHANGELOG.
- Run full validation suite and prepare branch for merge.

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Real evidence or report commits.
- Archive files.

## Acceptance Criteria

- All three governance documents (73–75) are created and consistent with Stage 4C architecture docs.
- Documents define complete workflow for 30–50 pole controlled baseline pilot.
- Exact pole_id matching protocol established with decision thresholds (≥80% GO, 75–80% CONDITIONAL GO, <75% NO-GO).
- Decision template includes all required verification steps (row counts, match rates, attribute verification, operator friction assessment, risk assessment).
- All 6 control files updated to reflect prep-pack task completion.
- `pytest -v` passes with 1050+ tests, 1 skipped.
- `pre-commit run --all-files` passes clean.
- `python3.13 scripts/repo_health.py` reports warning-only (known collisions only).
- `python3.13 scripts/merge_safety_check.py` confirms safe to merge.
- `real_pilot_data/` and `validation_runs/` remain git-ignored with zero real evidence committed.
- Branch ready for merge to master.

## Current Next Action

1. Run full validation suite on prep-pack branch (pytest, pre-commit, repo_health, merge_safety_check).
2. Commit and push branch with summary of 3 documents + 6 control file updates.
3. Merge to master when validation passes.
4. Noel executes controlled baseline pilot per docs 73–75 specifications.
5. Noel records results on decision template (doc 75) and signs GO/CONDITIONAL GO/NO-GO/STOP verdict.
6. GO verdict authorizes Stage 4C runtime implementation task.
