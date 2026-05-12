# GridFlow Current Handoff

Purpose: latest handoff for the next worker or Noel. This file must be updated before any worker stops.

## Active Handoff

<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->
- Task: P_LOCAL_001 Field-Capture Readiness Review (docs 89–90)
- Owner: none
- Branch: `claude-code/p-local-001-field-capture-readiness-review`
- Status: awaiting_next_branch
- Summary: Two governance review documents now classify P_LOCAL_001 as accessible field-capture validation proof and explain Phase 4 (baseline+field combined) requirements for Stage 4C authorization. Control files updated. All P_LOCAL_001 data remains local-only and git-ignored. Stage 4C remains blocked until Phase 4 complete.
- Updated: 2026-05-12T12:00:00Z
- Audit Note: Do not treat the baseline conversion review as runtime authorization. The next branch should stay local-evidence-safe and use the existing exact `pole_id` workflow.
<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->

## What This Branch Adds

- `AI_CONTROL/86_REAL_SURVEY_BASELINE_CONVERSION_REVIEW.md`: tracked review of Bellsprings, Gordon, and Noel local survey files, including support counts, field-structure findings, suitability classification, and local-only output paths.
- `docs/STAGE4_REAL_SURVEY_BASELINE_CONVERSION_GUIDE.md`: local conversion workflow guide for real controller-export files and capture-compatible CSVs.
- `AI_CONTROL/87_REAL_SURVEY_PACK_READINESS_REVIEW.md`: baseline-vs-field readiness framing for Stage 4C authorization boundaries.
- `AI_CONTROL/88_BASELINE_VS_FIELD_EVIDENCE_DECISION_MEMO.md`: 4-phase sequencing and Phase 4 authorization rules.
- All real baseline/field CSV, PDF, photo files remain local-only and git-ignored.

## Local Checkout Reality

- The earlier clean audit branch correctly reported no tracked candidate files in that separate worktree.
- This local main checkout contains the raw survey baseline pack under `real_pilot_data/P_BASELINE_SURVEY_PACK/raw/`.
- The conversion review confirmed:
  - Bellsprings: `40` support rows
  - Gordon original: `128` support rows
  - Gordon PR1: `86` support rows with duplicate point `4`
  - Gordon PR2: `53` support rows
- Noel's `pole_survey_2026-05-11_complete.csv` already matches the Stage 4 header set, with 3 extra local-only columns and 1 blank trailing header column.
- Local starter CSVs were created under `real_pilot_data/P_BASELINE_SURVEY_PACK/csv/`.
- `real_pilot_data/`, `uploads/`, and `validation_runs/` remain ignored/uncommitted local evidence paths.

## Validation Plan

- `pytest -v`
- `pre-commit run --all-files`
- `python3.13 scripts/repo_health.py`
- `python3.13 scripts/merge_safety_check.py codex/stage4-real-survey-baseline-conversion-pack`
- `git status --ignored --short real_pilot_data uploads validation_runs`
- Browser validation: not required; governance review docs only, no runtime UI changes.
- Manual review report: n/a.

## Current Validation State

- Stage 4 Real Survey Pack Readiness Review merged to `master`.
- Stage 4 real survey baseline conversion review merged to `master`.
- Merge validation pending/complete in the current merge resolution flow.
- All real baseline/field files remain local-only and git-ignored.
- Stage 4C remains blocked.

## Next Action

1. Complete merge validation on `master`.
2. Open the next branch to build and validate `P_LOCAL_001` from Noel's actual local survey/photos.
3. Keep all real baseline/field/design files git-ignored.
4. Do not start Stage 4C runtime integration until a controlled pilot result is recorded and approved.

## Do Not Start

- Stage 4 runtime upload integration.
- Stage 4 popup or Review OS surfacing.
- C2E2 popup field scope changes.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Archive edits.
- Branch deletion or merge operations.

## Stable Milestones To Preserve

- `c2e2-popup-scope-reduction-complete`
- `c2e2-map-navigation-followups-complete`
- `gridflow-control-center-v1-complete`
- `project-control-center-foundation-complete`
- `project-control-center-first-use-polish-complete`
- `stage4-structured-capture-foundation-complete`
- `c2f-review-focus-issue-filtering-complete`
- `technical-docs-field-architecture-complete`
- `c2g-lifecycle-replacement-visualization-complete`
- `project-control-worker-bootstrap-complete`
- `stage4-readiness-specification-complete`
- `branch-retirement-control-deconfliction-complete`
- `stage4c-architecture-gate-complete`
- `real-field-pilot-execution-system-v1-complete`
- `pre-pilot-cleanroom-release-readiness-audit-complete`
- `p-real-001-mini-independent-gate-audit-complete`
- `stage4c-controlled-baseline-pilot-prep-complete`
- `existing-survey-baseline-candidate-audit-complete`
- `controlled-pilot-field-pack-v1-complete`
- `p-controlled-001-readiness-gate-complete`
- `stage4-real-survey-pack-readiness-review-complete`
- `stage4-real-survey-baseline-conversion-review-complete`
