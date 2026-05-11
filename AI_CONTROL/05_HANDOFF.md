# GridFlow Current Handoff

Purpose: latest handoff for the next worker or Noel. This file must be updated before any worker stops.

## Active Handoff

<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->
- Task: Stage 4C controlled pilot baseline helper v1
- Owner: codex
- Branch: `codex/stage4c-controlled-pilot-baseline-helper-v1`
- Status: ready_for_review
- Summary: A new helper now reads the local `P_CONTROLLED_001` baseline CSV, extracts exact baseline `pole_id` candidates, writes a Stage 4 starter capture CSV, and compares completed pilot rows back to baseline using exact-match-only rules. The current local baseline is a raw controller export with `57` scanned rows and `40` candidate support rows. Real pilot evidence paths, `uploads/`, and validation output paths remain excluded from commit. Stage 4C remains blocked.
- Updated: 2026-05-11T20:40:07Z
- Audit Note: After validation and merge, Noel should use the generated starter CSV and extract report, complete the controlled field capture, then run exact-match compare mode against the completed pilot CSV. Do not commit `real_pilot_data/`, `validation_runs/`, local `uploads/` CSVs, photos, or runtime changes from this handoff state.
<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->

## What This Branch Adds

- `AI_CONTROL/79_EXISTING_SURVEY_BASELINE_CANDIDATE_AUDIT.md` remains the clean-audit provenance record: that separate audit worktree did not contain tracked candidate baseline files.
- `AI_CONTROL/80_CONTROLLED_PILOT_FIELD_PACK_V1.md` is now present and ready: field-day procedure, pre-field checklist, per-pole capture flow, end-of-day organization, and validation commands.
- `AI_CONTROL/81_CONTROLLED_PILOT_PHOTO_AND_EVIDENCE_RULES.md` is now present and ready: evidence/photo requirements, naming protocol, special-situation handling, and acceptance checklist.
- `AI_CONTROL/82_CONTROLLED_PILOT_OPERATOR_DECISION_NOTES.md` is now present and ready: operator friction log, unknown-field log, access log, mismatch notes, confidence notes, and decision guidance.
- `scripts/prepare_stage4_controlled_pilot.py` adds prepare mode and exact-match compare mode for the controlled baseline workflow.
- `docs/STAGE4_CONTROLLED_BASELINE_PILOT_OPERATOR_GUIDE.md` gives Noel the operator-facing workflow for prepare mode and match mode.
- `P_REAL_001_MINI` remains a successful workflow shakedown only. It does not approve Stage 4C runtime integration.

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
- `python3.13 scripts/merge_safety_check.py codex/stage4c-controlled-pilot-baseline-helper-v1`
- `git status --ignored --short real_pilot_data validation_runs uploads`
- Browser validation: not required; control/docs only, no runtime UI changes.
- Manual review report: n/a.

## Current Validation State

- Helper implementation complete; focused baseline-helper tests passed.
- Full validation passed: `pytest -v`, `pre-commit run --all-files`, and `python3.13 scripts/repo_health.py` completed. `merge_safety_check.py` remains warning-only until the branch commit exists.
- Local baseline extract produced starter CSV and extract notes under ignored local paths.
- Stage 4C runtime integration remains blocked.

## Next Action

1. Complete full validation on `codex/stage4c-controlled-pilot-baseline-helper-v1`.
2. Merge this helper branch after review.
3. Use the generated starter CSV and extract notes to execute the controlled baseline pilot.
4. Run exact-match compare mode against the completed pilot CSV.
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
