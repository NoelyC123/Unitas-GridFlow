# GridFlow Current Handoff

Purpose: latest operational handoff for Noel and AI workers.

## Summary

- Master is stable.
- Latest completed milestones: `technical-docs-field-architecture-complete`, `stage4-structured-capture-foundation-complete`, `c2f-review-focus-issue-filtering-complete`, `project-control-center-first-use-polish-complete`, `project-control-center-foundation-complete`, `c2e2-popup-expansion-implementation-complete`.
- Current active branch is `codex/c2g-lifecycle-replacement-visualization`.
- This branch implements C2G lifecycle and replacement relationship visualization in the map viewer.
- Backend QA, geometry, span generation, intake, Stage 4 schema/validators, and C2E2 field truthfulness rules were not changed.
- The branch is being rebased onto latest master after the technical documentation merge.
- Next expected action: run post-rebase pytest, pre-commit, and manual review validation, then merge/tag if clean.

## Active Task

<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->
- Task: C2G Lifecycle + Replacement Relationship Visualization
- Owner: codex
- Branch: `codex/c2g-lifecycle-replacement-visualization`
- Status: rebased onto latest master; post-rebase validation required before merge
- Summary: Implement lifecycle relationship connectors, lifecycle focus controls, compact legend/toggle updates, and manual review checklist coverage.
- Next action: run post-rebase pytest/pre-commit/manual_review validation, then merge/tag if clean.
- Updated: 2026-05-09T21:20:00Z
<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->

## C2G Lifecycle Replacement Visualization — Status

- **Branch:** `codex/c2g-lifecycle-replacement-visualization`
- **Commit:** pending post-rebase commit hash.
- **What changed:**
  - Added explicit lifecycle focus state and controls for replacement pairs, existing assets, and proposed assets.
  - Upgraded replacement relationship connectors to use explicit `replacing` / `being_replaced_by` data only.
  - Added lifecycle connector/focus styling and a compact map key entry.
  - Kept C2E2 popup truthfulness intact and omitted empty lifecycle relationship sections.
  - Added `validation_checklists/lifecycle_visualization.yml` and lifecycle-focused frontend tests.
- **Pre-rebase validation status:**
  - `pytest tests/test_lifecycle_visualization.py -v` — 4 passed.
  - `pytest tests/test_review_focus_mode.py -v` — 3 passed.
  - `pytest tests/test_c2e2_popup_rendering.py -v` — 4 passed.
  - `pytest tests/test_review_navigation_layer.py -v` — 9 passed.
  - `pytest -v` — 858 passed, 1 skipped, 13 warnings.
  - `pre-commit run --all-files` — all hooks pass.
  - Manual review harness passed: `validation_runs/20260509_211538/validation_report.md`.
  - `validation_runs/20260509_211538/failures.json` — `[]`.
- **Post-rebase validation:** pending.

## Technical Documentation Package — Status

- **Branch:** `claude-code/technical-docs-field-architecture`
- **Milestone:** `technical-docs-field-architecture-complete`
- **Docs created:**
  - `docs/FIELD_REFERENCE_GUIDE.md` — every per-pole field by truth category (Trimble / GridFlow-derived / Stage 4 / not-truthful-today). Grounded in the C2E2 Field Reality Audit.
  - `docs/ARCHITECTURE.md` — purpose, full data-flow diagram, major backend + frontend modules, manual review harness, project control center, branch/worker workflow, extension points (Stage 4 integration, DNO rulepacks, PoleCAD export, lifecycle viz, electrical asset layer).
  - `docs/API_REFERENCE.md` — function/class signatures and side effects across `app/controller_intake.py`, `app/routes/api_intake.py`, `app/qa_engine.py`, `app/geometry_pipeline.py`, `app/field_reference.py`, `app/field_validators.py`, the Stage 4 modules, and every script under `scripts/`.
  - `docs/VALIDATION_WORKFLOW.md` — when to run pytest / pre-commit / manual review harness, recommended jobs, screenshot policy, control-script logging, common-failure triage table, the role of human visual review.
- **What is NOT changed:**
  - No app runtime files modified.
  - No tests added or removed.
  - No validation logic changed.
  - No map-viewer / popup / QA / parser behaviour changed.
- **Validation status:**
  - `pytest -v` — 855 passed.
  - `pre-commit run --all-files` — all hooks pass.
  - Manual review harness not required (no UI changes).

## Stage 4 Foundation — Status

- **Branch:** `claude-code/stage4-structured-capture-foundation` (merged)
- **Milestone:** `stage4-structured-capture-foundation-complete`
- Schema, validators, template generator, docs, and tests for the Stage 4 structured-capture layer — library code only, not wired into runtime.

## Next Action

- Run post-rebase C2G validation: focused pytest suites, full pytest, pre-commit, and manual review harness.
- Review the C2G lifecycle/replacement workflow.
- Merge/tag after validation and review.
- Pick up the next validation-led product task on a separate branch.

## Do Not Start On This Branch

- Stage 4 *integration* into the upload/QA/popup flow (separate branch).
- Technical docs follow-up work.
- DNO-grade rulepack implementation.
- Unrelated backend QA, geometry, span generation, intake, or schema changes.

## Completed Stable Milestones

- `technical-docs-field-architecture-complete` — merged to master.
- `stage4-structured-capture-foundation-complete` — merged to master.
- `c2f-review-focus-issue-filtering-complete` — merged to master.
- `project-control-center-first-use-polish-complete` — merged to master.
- `project-control-center-foundation-complete` — merged to master.
- `c2e2-popup-expansion-implementation-complete` — merged to master.
