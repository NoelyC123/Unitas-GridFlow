# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: READY FOR NEXT TASK
- Branch: `none`
- Owner: none
- Lane: Stage 4 field pilot execution
- Status: awaiting_next_branch
- Requested by: Noel
- Runtime changes allowed: no live app integration; governance/control state only until the next branch is opened
- Tests required: none for the idle master state beyond normal merge validation
- Validation result: Stage 4 Real Survey Pack Readiness Review (docs 87–88) merged; Stage 4 real survey baseline conversion review (doc 86 + guide) merged; merge validation pending/complete outside this record
- Browser validation required: no; governance/docs only, no runtime UI changes
- Popup scope changes allowed: no

## Goal

No active implementation task is open on `master`.

The next required branch should build and validate `P_LOCAL_001` from Noel's
actual local survey/photos using the current Stage 4 controlled baseline
workflow, without committing real evidence and without starting Stage 4C runtime
integration.

## Scope

- Preserve merged docs 86, 87, and 88 as the current source of truth for baseline conversion readiness
- Preserve Stage 4C as blocked until a real controlled pilot result is recorded
- Use the local baseline conversion outputs and exact `pole_id` workflow for the next pilot branch
- Keep `real_pilot_data/`, `uploads/`, and `validation_runs/` out of tracked commits

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Real evidence or report commits.
- Archive files.

## Acceptance Criteria

- `master` reflects both completed governance states:
  - Stage 4 Real Survey Pack Readiness Review (docs 87–88)
  - Stage 4 real survey baseline conversion review (doc 86 + guide)
- Bellsprings, Gordon original, and Gordon PR2 remain documented as suitable baseline conversion inputs
- Gordon PR1 remains documented as blocked by duplicate point identity `4`
- Noel local survey CSV remains documented as Stage 4 capture-compatible, not a raw baseline extract
- All real Bellsprings/Gordon/local survey files remain uncommitted and git-ignored
- Stage 4C remains blocked

## Current Next Action

1. Open the next branch for `P_LOCAL_001` baseline build/validation from Noel's actual local survey/photos.
2. Reuse the exact `pole_id` workflow and local starter/baseline conversion guidance already merged to `master`.
3. Keep all real survey/photos/validation outputs local-only.
