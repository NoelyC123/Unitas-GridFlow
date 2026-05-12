# GridFlow Current Handoff

Purpose: latest handoff for the next worker or Noel. This file must be updated before any worker stops.

## Active Handoff

<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->
- Task: Stage 4 Real Survey Pack Readiness Review (docs 87–88)
- Owner: claude-code
- Branch: `claude-code/stage4-real-survey-pack-readiness-review`
- Status: ready_for_review
- Summary: Two readiness review documents (87–88) now classify Bellsprings/Gordon baselines as baseline-conversion evidence and explain 4-phase sequencing to Stage 4C authorization. Clarifies that baseline alone and field evidence alone are insufficient; only Phase 4 (full controlled pilot with validator pass + signed verdict) authorizes Stage 4C. Control files updated. All real baseline/field files remain local-only and git-ignored. Stage 4C remains blocked until Phase 4 complete.
- Updated: 2026-05-12T08:30:00Z
- Audit Note: After validation and merge, Codex executes Phase 1 (baseline extraction from Bellsprings/Gordon), Noel executes Phase 2 (field-capture learning), combined Phase 3 (baseline-field matching analysis), and Phase 4 (full controlled pilot with signed verdict).
<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->

## What This Branch Adds

- `AI_CONTROL/87_REAL_SURVEY_PACK_READINESS_REVIEW.md`: classify Bellsprings/Gordon/design files as baseline-conversion evidence, document what they can/cannot support, risks and mitigations, recommended controls.
- `AI_CONTROL/88_BASELINE_VS_FIELD_EVIDENCE_DECISION_MEMO.md`: explain 3 pilot types (baseline conversion, field-capture learning, full controlled pilot), document 4-phase sequencing, clarify why baseline+field combined evidence required for Phase 4 authorization.
- All 6 control files (00, 02, 03, 04, 05, CHANGELOG) updated with real-survey-pack-readiness-review context.
- All real baseline/field CSV, PDF, photo files remain local-only and git-ignored.

## Local Checkout Reality

- The earlier clean audit branch correctly reported no tracked candidate files in that separate worktree.
- This local main checkout does contain a usable local baseline at `real_pilot_data/P_CONTROLLED_001/baseline/baseline.csv`.
- The helper extracted `40` structural candidate rows from `57` scanned rows in that raw controller export using point number as the exact identity source.
- Any local baseline CSVs under `uploads/`, `validation_data/`, or `real_pilot_data/` must remain out of this helper branch commit.
- `real_pilot_data/` and `validation_runs/` remain ignored/uncommitted local evidence paths.

## Validation Plan

- `pytest -v`
- `pre-commit run --all-files`
- `python3.13 scripts/repo_health.py`
- `python3.13 scripts/merge_safety_check.py claude-code/stage4-real-survey-pack-readiness-review`
- `git status --ignored --short real_pilot_data uploads validation_runs`
- Browser validation: not required; governance review docs only, no runtime UI changes.
- Manual review report: n/a.

## Current Validation State

- Two governance review documents (87–88) created and complete.
- Control files updated with real-survey-pack-readiness-review context.
- Validation suite ready to run: `pytest -v`, `pre-commit run --all-files`, `python3.13 scripts/repo_health.py`, and `python3.13 scripts/merge_safety_check.py` pending.
- All real baseline/field files remain local-only and git-ignored.
- Stage 4C remains blocked until Phase 4 (full controlled pilot with signed verdict) complete.

## Next Action

1. Complete full validation suite on `claude-code/stage4-real-survey-pack-readiness-review`.
2. Verify all real baseline/field/design files remain git-ignored (git status --ignored --short).
3. Commit and push real-survey-pack-readiness-review branch.
4. Deliver final report with branch, commit hash, files changed, baseline conversion readiness verdict, field-evidence distinction summary, Phase 4 sequencing, validation results.
5. Codex: Execute Phase 1 (baseline extraction from Bellsprings/Gordon). Noel: Execute Phase 2 (field-capture learning). Combined: Phase 3 (baseline-field analysis). Full pilot: Phase 4 (controlled pilot + signed verdict).
6. Phase 4 signed verdict gates Stage 4C implementation authorization.

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
