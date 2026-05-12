# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: P_LOCAL_001 Final Result Audit Prep (docs 93–94)
- Branch: `claude-code/p-local-001-final-result-audit-prep`
- Owner: none
- Lane: Stage 4 field pilot execution
- Status: awaiting_next_branch
- Runtime changes allowed: no live app integration; governance/docs only
- Tests required: pytest -v, pre-commit run --all-files
- Validation result: pending (governance docs only, no real data committed)
- Browser validation required: no; governance/docs only, no runtime UI changes
- Popup scope changes allowed: no
- Real data protection: all P_LOCAL_001 data remains local-only, no real files committed

## Goal

Prepare independent audit framework for verifying Codex's final P_LOCAL_001 consolidation
outputs and explicitly confirm the remaining Phase 4 requirements for Stage 4C authorization.

Deliverables:
- Doc 91: P_LOCAL_001 Field-Capture Result Template (ready for filling after Codex consolidation)
- Doc 92: P_LOCAL_001 Final Review Checklist (ready for Noel to use immediately)
- Updated control files recording the framework preparation
- No real data committed
- Stage 4C remains blocked

## Scope

- Create P_LOCAL_001 Field-Capture Result Template (doc 91) with sections for:
  - Pilot metadata
  - Source files expected after Codex consolidation
  - Pole structure count (9 structures, 10 individual supports with H-frame clarification)
  - Photo evidence count and linking
  - Validator result section (quantitative metrics, verdict)
  - High-risk field verification checklist
  - Known limitations (what P_LOCAL_001 proves/doesn't prove)
  - Technical confirmations for SPEN-QMM20, POLE-GARDEN-XFMR-001, etc.
  - Final verdict section (PASS / PARTIAL / NO-GO options)
  - Explicit statement: does not authorize Stage 4C runtime integration

- Create P_LOCAL_001 Final Review Checklist (doc 92) with step-by-step verification of:
  - All 9 structures present
  - H-frame count handled correctly
  - Photo references match corrected photo mapping
  - High-risk technical fields remain unknown unless verified
  - SPEN-QMM20 LV classification and no streetlight misattribution
  - POLE-GARDEN-XFMR-001 wording (limits access, not blocks DNO access)
  - POLE-RURAL-ROAD-001 inspection plate dates from photo only
  - POLE-VILLAGE-LSTC2021 photo mapping correct
  - Stage 4C remains blocked confirmation

- Update control files to record framework preparation
- Keep `real_pilot_data/`, `uploads/`, and `validation_runs/` out of tracked commits

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Real evidence or report commits.
- Archive files.

## Acceptance Criteria

- Doc 91 (Result Template) is ready but not falsely completed
  - All sections present with clear prompts for Noel to fill
  - Explicit Stage 4C block statement included
  - No assumptions made about validator results

- Doc 92 (Final Review Checklist) is ready for Noel's immediate use
  - 10 verification sections covering all required checks
  - H-frame counting rule clearly explained
  - Technical confirmations specific to each problematic pole
  - Decision guide provides PASS / PARTIAL / NO-GO clarity

- Control files updated:
  - 00_PROJECT_BOARD.md records task completion
  - 02_CURRENT_TASK.md (this file) documents scope
  - 03_WORKER_LOG.md records work completion
  - 04_VALIDATION_LOG.md records validation pass
  - 05_HANDOFF.md updated for next task
  - CHANGELOG.md records the deliverables

- Validation confirms:
  - pytest -v passes
  - pre-commit run --all-files passes
  - python3.13 scripts/repo_health.py passes
  - python3.13 scripts/merge_safety_check.py passes
  - git status confirms no real data committed

- Stage 4C remains BLOCKED

## Current Next Action

1. Open the next branch for `P_LOCAL_001` baseline build/validation from Noel's actual local survey/photos.
2. Reuse the exact `pole_id` workflow and local starter/baseline conversion guidance already merged to `master`.
3. Keep all real survey/photos/validation outputs local-only.
