# GridFlow Current Handoff

Purpose: latest handoff for the next worker or Noel. This file must be updated before any worker stops.

## Active Handoff

<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->
- Task: P_CONTROLLED_001 controlled baseline pilot setup
- Owner: Noel / next worker
- Branch: `master`
- Status: ready_to_start
- Summary: The clean baseline audit branch was merged as provenance and recorded that its separate clean worktree had no tracked candidate files. This local main checkout does contain local candidate upload and baseline CSVs, and controlled pilot field-pack docs 80–82 are now ready. Real pilot evidence paths remain excluded from commit. Stage 4C remains blocked.
- Updated: 2026-05-11T21:19:00Z
- Audit Note: Use the local baseline CSV for `P_CONTROLLED_001`, then build/run the controlled baseline pilot helper with exact `pole_id` matching. Do not commit `real_pilot_data/`, `validation_runs/`, local `uploads/` CSVs, photos, or runtime changes from this handoff state.
<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->

## What This Merge Preserved

- `AI_CONTROL/79_EXISTING_SURVEY_BASELINE_CANDIDATE_AUDIT.md` remains the clean-audit provenance record: that separate audit worktree did not contain tracked candidate baseline files.
- `AI_CONTROL/80_CONTROLLED_PILOT_FIELD_PACK_V1.md` is now present and ready: field-day procedure, pre-field checklist, per-pole capture flow, end-of-day organization, and validation commands.
- `AI_CONTROL/81_CONTROLLED_PILOT_PHOTO_AND_EVIDENCE_RULES.md` is now present and ready: evidence/photo requirements, naming protocol, special-situation handling, and acceptance checklist.
- `AI_CONTROL/82_CONTROLLED_PILOT_OPERATOR_DECISION_NOTES.md` is now present and ready: operator friction log, unknown-field log, access log, mismatch notes, confidence notes, and decision guidance.
- `P_REAL_001_MINI` remains a successful workflow shakedown only. It does not approve Stage 4C runtime integration.

## Local Checkout Reality

- The earlier clean audit branch correctly reported no tracked candidate files in that separate worktree.
- This local main checkout does contain candidate baseline CSVs under local `uploads/` and `validation_data/` paths.
- Those local CSVs must remain out of this governance merge.
- `real_pilot_data/` and `validation_runs/` remain ignored/uncommitted local evidence paths.

## Validation Plan

- `pytest -v`
- `pre-commit run --all-files`
- `python3.13 scripts/repo_health.py`
- `python3.13 scripts/merge_safety_check.py claude-code/controlled-pilot-field-pack-v1`
- `git status --ignored --short real_pilot_data validation_runs uploads`
- Browser validation: not required; control/docs only, no runtime UI changes.
- Manual review report: n/a.

## Current Validation State

- Merge conflicts resolved semantically across board/task/log/handoff/changelog control files.
- Validation pending completion after merge commit.
- Docs 80–82 are staged for inclusion.
- Stage 4C runtime integration remains blocked.

## Next Action

1. Complete this governance merge on `master`.
2. Use a local baseline CSV for `P_CONTROLLED_001`.
3. Build/run the controlled baseline pilot helper on a new follow-on branch.
4. Execute the controlled baseline pilot with exact `pole_id` matching.
5. Keep Stage 4C runtime integration blocked until the controlled pilot verdict is recorded.

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
