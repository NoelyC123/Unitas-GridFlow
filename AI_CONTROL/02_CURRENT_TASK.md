# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Real Field Pilot Readiness + Stage 4C Decision Gate Audit
- Branch: `claude-code/real-field-pilot-readiness-stage4c-gate-audit`
- Owner: Claude Code
- Lane: Stage 4 field pilot governance + Stage 4C decision framework
- Status: in_progress
- Requested by: conversation
- Runtime changes allowed: NO; governance and control layer only
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python scripts/repo_health.py`; `python scripts/merge_safety_check.py claude-code/real-field-pilot-readiness-stage4c-gate-audit`
- Validation result: (pending — will run before commit)
- Browser validation required: no; governance documents only
- Popup scope changes allowed: no

## Goal

Produce a field-day operating checklist, success metrics, risk control matrix, and
decision board template. These enable Noel to execute the real iPad pilot with
measurable go/no-go criteria and clear Stage 4C gate requirements.

## Scope

**Create 5 governance documents**:

- AI_CONTROL/61: Real Field Pilot Readiness Audit (GO / GO WITH CAUTIONS / NO-GO verdict)
- AI_CONTROL/62: Field Day Operating Checklist (practical per-phase guide)
- AI_CONTROL/63: Field Pilot Success Metrics (quantitative thresholds)
- AI_CONTROL/64: Field Pilot Risk Control Matrix (R01–R08 mitigations)
- AI_CONTROL/65: Stage 4C Decision Board Template (post-pilot go/no-go decision)

**Update control center docs**:

- AI_CONTROL/00_PROJECT_BOARD.md
- AI_CONTROL/02_CURRENT_TASK.md (this file)
- AI_CONTROL/03_WORKER_LOG.md
- AI_CONTROL/04_VALIDATION_LOG.md
- AI_CONTROL/05_HANDOFF.md
- CHANGELOG.md

## Out Of Scope

- Runtime Stage 4C implementation.
- Stage 4 fields in popups or Review OS.
- Backend changes to QA, geometry, intake, or map rendering.
- Archive files.
- Codex execution branch (do not modify).
- App code changes.

## Acceptance Criteria

- All 5 governance documents (61–65) created and complete.
- Readiness audit verdict is clear (GO / CAUTIONS / NO-GO).
- Field day checklist is operationally usable (per-phase, per-pole).
- Success metrics have quantitative thresholds for every measurement.
- Risk control matrix maps R01–R08 to field/validation/evidence/go-no-go.
- Decision board template has space for pilot results and final decision.
- Control center docs updated with current task and next actions.
- `pytest -v`, `pre-commit run --all-files`, `repo_health.py`, and
  `merge_safety_check.py` pass with no blocking issues.

## Current Next Action

Complete this branch, validate, commit, push. Noel can then execute real field
pilot using checklist 62, measure results against metrics 63, evaluate risks
per matrix 64, and fill decision board 65 post-pilot.
