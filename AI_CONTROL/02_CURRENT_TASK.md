# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Review Workspace v2 — Design-Readiness Command Center
- Branch: `codex/review-workspace-v2-command-center`
- Owner: codex
- Lane: Frontend / review workspace
- Status: ready_for_review
- Requested by: Noel
- Runtime changes allowed: yes, limited to review/map UI files named in the prompt
- Tests required: `pytest -v`; `pre-commit run --all-files`
- Validation result: passed, 868 passed, 1 skipped, 13 existing warnings; pre-commit passed
- Browser validation required: yes, on `/map/view/project/P008/F001` and `/map/view/project/P010/F001`
- Browser validation result: passed on both jobs; console clean
- Popup scope changes allowed: no

## Goal

Upgrade GridFlow's review workspace into a professional design-readiness command center that helps a planner or designer see what is ready, blocked, needs review, or lacks evidence without changing the C2E2 popup field model.

## Scope

- Add a visible review summary and job-level design-readiness decision state.
- Group the review queue by design blockers, review required, evidence gaps, planner awareness, route/span checks, and lifecycle/replacement checks.
- Surface existing evidence quality signals, including measured height, missing height, missing material, and low-confidence or field-verification-required data.
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

- Review workspace gives a clear design-readiness overview.
- Review queue is grouped by real planning concerns using existing map/job metadata only.
- Evidence gaps and blockers are visible without requiring screenshots.
- Existing map controls still work.
- C2E2 popup scope remains unchanged.
- Tests and pre-commit pass.
- Browser validation passes for `P008/F001` and `P010/F001`.

## Current Next Action

Review, merge, tag, and update Control Center files on master after merge.
