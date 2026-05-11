# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Controlled Pilot Field Pack v1
- Branch: `claude-code/controlled-pilot-field-pack-v1`
- Owner: claude-code
- Lane: Stage 4 field pilot execution
- Status: ready_for_validation
- Requested by: Noel (implicit from controlled baseline pilot requirements)
- Runtime changes allowed: no live app integration; control/docs only; no real evidence may be committed
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python3.13 scripts/repo_health.py`; `python3.13 scripts/merge_safety_check.py claude-code/controlled-pilot-field-pack-v1`
- Validation result: pending (expected: 1050+ passed, 1 skipped; pre-commit clean; repo_health warning-only; merge_safety_check safe)
- Browser validation required: no; control/docs only, no runtime UI changes
- Popup scope changes allowed: no

## Goal

Create the operator-facing field pack that Noel will use after Codex selects
the baseline candidate for P_CONTROLLED_001. Provide simple, actionable
guidance for field capture (30–50 poles), evidence organization, and decision
notes that inform the controlled pilot verdict.

## Scope

- Create `AI_CONTROL/80_CONTROLLED_PILOT_FIELD_PACK_V1.md` — simple field-day procedure, what to prepare, what to capture per pole, end-of-day organization, validation commands.
- Create `AI_CONTROL/81_CONTROLLED_PILOT_PHOTO_AND_EVIDENCE_RULES.md` — photo requirements per pole, naming protocol, handling special situations, evidence acceptance checklist.
- Create `AI_CONTROL/82_CONTROLLED_PILOT_OPERATOR_DECISION_NOTES.md` — post-field notes template (friction log, unknown fields, access log, confidence assessment, decision criteria).
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

- All three operator-facing documents (80–82) are created and reference docs 73–75.
- Doc 80 provides simple, actionable field-day procedure independent of baseline selection.
- Doc 81 details photo requirements and naming protocol with handling for special situations.
- Doc 82 provides post-field note templates (friction, unknown fields, access, confidence, decision criteria).
- All guidance is non-prescriptive; Noel can customize based on real conditions.
- All 6 control files updated to reflect field-pack task completion.
- `pytest -v` passes with 1050+ tests, 1 skipped.
- `pre-commit run --all-files` passes clean.
- `python3.13 scripts/repo_health.py` reports warning-only (known collisions only).
- `python3.13 scripts/merge_safety_check.py` confirms safe to merge.
- `real_pilot_data/` and `validation_runs/` remain git-ignored with zero real evidence committed.
- Branch ready for merge to master.

## Current Next Action

1. Run full validation suite on field-pack branch (pytest, pre-commit, repo_health, merge_safety_check).
2. Commit and push branch with summary of 3 documents + 6 control file updates.
3. Merge to master when validation passes.
4. Codex selects baseline candidate for P_CONTROLLED_001.
5. Noel uses docs 80–82 to prepare and execute field capture of 30–50 poles.
6. Noel uses doc 73 (prep), doc 74 (protocol), and doc 82 (decision notes) to fill doc 75 (decision template).
7. Noel signs GO/CONDITIONAL GO/NO-GO/STOP verdict on decision template.
8. GO verdict authorizes new Stage 4C runtime implementation task.
