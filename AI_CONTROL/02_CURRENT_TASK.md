# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: GridFlow Review Operating System v3
- Branch: `codex/review-operating-system-v3`
- Owner: codex
- Lane: Frontend / review workspace
- Status: ready_for_review
- Requested by: Noel
- Runtime changes allowed: yes, limited to review/map UI files named in the prompt
- Tests required: `pytest -v`; `pre-commit run --all-files`
- Validation result: passed, 869 passed, 1 skipped, 13 existing warnings; pre-commit passed
- Browser validation required: yes, on `/map/view/project/P008/F001` and `/map/view/project/P010/F001`
- Browser validation result: passed on both jobs; console clean
- Popup scope changes allowed: no

## Goal

Evolve Review Workspace v2 into a planner-facing review operating system with deeper issue intelligence, queues, overlays, filters, and readiness scoring without changing the C2E2 popup field model.

## Scope

- Add issue aggregation by severity, category, lifecycle risk, evidence quality, confidence, route/span risk, and replacement impact.
- Add an active issue queue, local reviewed state, remaining blocker indicators, and review progress tracking.
- Add advanced filters for severity, category, lifecycle, evidence, confidence, route/span risk, and unresolved-only mode.
- Add map-level review intensity overlays without changing backend data or popup content.
- Add readiness scoring and explanation using existing review signals only.
- Preserve existing Next / Previous, Release Map, route highlight, planner awareness toggle, review category navigation, map layer toggles, and C2E2 popup truthfulness.
- Update Control Center files for this task.

## Out Of Scope

- C2E2 popup field scope or section changes.
- Stage 4 structured capture.
- Survey data model changes.
- Backend QA, geometry, span generation, or intake changes.
- Archive files.
- Fake or inferred survey/evidence fields.

## Acceptance Criteria

- Review workspace gives a stronger planner operating layer around existing map/job data.
- Issue queue, filters, progress, overlays, and readiness score use existing signals only.
- Evidence gaps, route risks, lifecycle risks, and remaining blockers are visible without requiring screenshots.
- Existing map controls still work.
- C2E2 popup scope remains unchanged.
- Tests and pre-commit pass.
- Browser validation passes for `P008/F001` and `P010/F001`.

## Current Next Action

Review, merge, tag, and update Control Center files on master after merge.
