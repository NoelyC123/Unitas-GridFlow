# GridFlow Control Center Board

Purpose: single operational board for ChatGPT, Codex, Claude Code, Claude Desktop, Cursor, and Noel.

This board is the first file to read after `01_CURRENT_STATE.md`. It records the active task, branch ownership, validation state, open follow-ups, and merge readiness. Older control files that are not listed in the v1 file set are historical unless a current task explicitly names them.

## Current Stable Milestones

- `c2e2-popup-scope-reduction-complete`
- `c2e2-popup-expansion-implementation-complete`
- `c2e2-map-navigation-followups-complete`
- `project-control-center-foundation-complete`
- `project-control-center-first-use-polish-complete`
- `stage4-structured-capture-foundation-complete`
- `c2f-review-focus-issue-filtering-complete`
- `technical-docs-field-architecture-complete`
- `c2g-lifecycle-replacement-visualization-complete`
- `project-control-worker-bootstrap-complete`

## Active Task

<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->
- Task: Real iPad Field Pilot Package v1
- Branch: `codex/real-ipad-field-pilot-package-v1`
- Owner: codex
- Status: ready_for_review
- Summary: Built the real-world iPad field pilot docs, template, fixtures, and validation package on top of Stage 4B
<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->

## In Progress

| Task | Branch | Owner | Lane | Status |
| --- | --- | --- | --- | --- |
| Real iPad Field Pilot Package v1 | `codex/real-ipad-field-pilot-package-v1` | codex | Stage 4 field pilot operating pack | ready for review |

## Review / Validation

- `pytest -v`: passed, 1042 passed, 1 skipped.
- `pre-commit run --all-files`: passed.
- `python3.13 scripts/repo_health.py`: warning-only; known numbering collisions only.
- `python3.13 scripts/merge_safety_check.py codex/real-ipad-field-pilot-package-v1`: safe to merge.
- Browser validation: not required for this docs/template/test-only Stage 4 package.

## Blocked

- None recorded.

## Done

- Branch retirement and control file deconfliction closed and tagged.
- Stage 4 readiness specification closed and tagged.
- C2E2 popup scope reduction closed and tagged.
- C2E2 map navigation follow-ups closed and tagged.
- C2F review focus + issue filtering closed and tagged.
- C2G lifecycle replacement visualization closed and tagged.
- Stage 4 structured capture foundation closed and tagged; runtime integration remains a future branch.
- Stage 4B structured capture validation preview complete; runtime integration remains blocked pending pilot evidence.
- Stage 4B/4C safety pilot harness complete; Stage 4C remains blocked pending a real pilot result.
- Technical documentation field/architecture package closed and tagged.
- Project Control Center foundation, polish, and worker bootstrap closed and tagged.
- GridFlow Control Center v1.0 closed and tagged.
- Stage 4A library correctness fixes closed and tagged.

## Backlog / Next Candidates

- Stage 4C controlled runtime integration, only after Stage 4B is merged and tagged and the go/no-go gate is approved.
- DNO-grade rulepack planning.
- PoleCAD export planning.
- Electrical asset / line / cable interaction layer.
- Lifecycle visualization follow-up enhancements.

## Operating Rule

Only one active implementation task may be open at a time. A second branch may exist only for review, audit, or emergency rollback work and must not overlap the active branch scope.
