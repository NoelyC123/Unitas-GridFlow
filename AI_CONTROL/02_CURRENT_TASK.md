# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Stage 4 Real Survey Pack Readiness Review (docs 87–88)
- Branch: `claude-code/stage4-real-survey-pack-readiness-review`
- Owner: claude-code
- Lane: Stage 4 field pilot execution
- Status: ready_for_review
- Requested by: Noel (implicit: understand what real survey files can support for Stage 4)
- Runtime changes allowed: no live app integration; governance review docs only; no real evidence may be committed
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python3.13 scripts/repo_health.py`; `python3.13 scripts/merge_safety_check.py claude-code/stage4-real-survey-pack-readiness-review`
- Validation result: docs 87–88 created; control files updated; validation pending
- Browser validation required: no; governance review docs only, no runtime UI changes
- Popup scope changes allowed: no

## Goal

Create two readiness review documents (87–88) that classify real Trimble baseline and design-pack
files as baseline-conversion evidence, clarify the distinction between baseline files and field
evidence, and document the 4-phase sequencing required to authorize Stage 4C. Clarify that
Bellsprings/Gordon baselines alone and Noel's local field survey alone are insufficient; only
Phase 4 (full controlled pilot with validator pass + signed verdict) authorizes Stage 4C.

## Scope

- Create AI_CONTROL/87_REAL_SURVEY_PACK_READINESS_REVIEW.md: classify baseline/design files, document risks/mitigations, recommend controls
- Create AI_CONTROL/88_BASELINE_VS_FIELD_EVIDENCE_DECISION_MEMO.md: explain 3 pilot types, 4-phase sequencing, why each phase is necessary
- Update 6 control files with real-survey-pack-readiness-review context: 00_PROJECT_BOARD.md, 02_CURRENT_TASK.md, 03_WORKER_LOG.md, 04_VALIDATION_LOG.md, 05_HANDOFF.md, CHANGELOG.md
- Keep all real survey files local-only; never commit raw CSVs, PDFs, photos, or baseline data
- Cross-reference docs 73–85 (prep, protocol, template, field pack, readiness gates) to establish Phase 4 requirements

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Real evidence or report commits.
- Archive files.

## Acceptance Criteria

- AI_CONTROL/87_REAL_SURVEY_PACK_READINESS_REVIEW.md created: classifies baselines as evidence, documents risks/controls, clarifies field-evidence distinction
- AI_CONTROL/88_BASELINE_VS_FIELD_EVIDENCE_DECISION_MEMO.md created: explains 3 pilot types, 4-phase sequencing, Phase 4 authorization requirements
- All 6 control files updated with real-survey-pack-readiness-review context
- `pytest -v` passes.
- `pre-commit run --all-files` passes clean.
- `python3.13 scripts/repo_health.py` reports warning-only (known collisions only).
- `python3.13 scripts/merge_safety_check.py` confirms safe to merge for `claude-code/stage4-real-survey-pack-readiness-review`.
- All real Bellsprings/Gordon/local survey files remain uncommitted and git-ignored.
- Real data remains local-only; no raw CSVs, PDFs, photos, or baselines in repo.
- Stage 4C remains blocked until Phase 4 (full controlled pilot) is complete with signed verdict.

## Current Next Action

1. Complete control file updates (03_WORKER_LOG, 04_VALIDATION_LOG, 05_HANDOFF, CHANGELOG).
2. Run full validation suite: pytest -v, pre-commit, repo_health, merge_safety_check.
3. Verify all real survey files remain git-ignored (git status --ignored --short).
4. Commit and push branch `claude-code/stage4-real-survey-pack-readiness-review`.
5. Deliver final report with commit hash, files changed, baseline conversion readiness verdict, field-evidence distinction summary, Phase 4 sequence, validation results.
6. Next: Codex executes Phase 1 (baseline extraction); Noel executes Phase 2 (field-capture learning); combined Phase 3 (baseline-field analysis); Phase 4 (full controlled pilot with signed verdict).
