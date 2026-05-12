# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Stage 4 real survey baseline conversion review
- Branch: `codex/stage4-real-survey-baseline-conversion-pack`
- Owner: codex
- Lane: Stage 4 field pilot execution
- Status: ready_for_review
- Requested by: Noel
- Runtime changes allowed: no live app integration; review/docs only; no real evidence may be committed
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python3.13 scripts/repo_health.py`
- Validation result: review docs and control files complete; `pytest -v` passed with `1075 passed, 1 skipped`; `pre-commit run --all-files` passed; `python3.13 scripts/repo_health.py` warning-only for known numbering collisions
- Browser validation required: no; governance review docs only, no runtime UI changes
- Popup scope changes allowed: no

## Goal

Review the real survey files under `real_pilot_data/P_BASELINE_SURVEY_PACK/raw/`,
classify their usefulness as Stage 4 baseline conversion inputs, generate local-only
starter outputs and notes, and record the review in tracked docs without committing
any real survey evidence. Keep Stage 4C blocked.

## Scope

- Inspect Bellsprings, Gordon, and Noel local survey CSVs
- Identify point number, grid, feature code, remarks, and height fields
- Count `Pol`, `EXpole`, and `Angle` support rows
- Generate local-only starter CSVs and extract notes under `real_pilot_data/P_BASELINE_SURVEY_PACK/`
- Create `AI_CONTROL/86_REAL_SURVEY_BASELINE_CONVERSION_REVIEW.md`
- Create `docs/STAGE4_REAL_SURVEY_BASELINE_CONVERSION_GUIDE.md`
- Update the standard control files and keep all local evidence paths out of commit

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Real evidence or report commits.
- Archive files.

## Acceptance Criteria

- `AI_CONTROL/86_REAL_SURVEY_BASELINE_CONVERSION_REVIEW.md` created with suitability classification for Bellsprings, Gordon variants, and Noel's local survey CSV
- `docs/STAGE4_REAL_SURVEY_BASELINE_CONVERSION_GUIDE.md` created with local conversion workflow and boundary rules
- Local-only starter CSVs and extract notes created for usable raw controller-export files
- Bellsprings and Gordon support counts documented
- Noel local survey CSV compatibility documented
- All 6 control files updated with conversion-review context
- `pytest -v` passes.
- `pre-commit run --all-files` passes clean.
- `python3.13 scripts/repo_health.py` reports warning-only (known collisions only).
- All real Bellsprings/Gordon/local survey files remain uncommitted and git-ignored.
- Real data remains local-only; no raw CSVs, PDFs, photos, or baselines in repo.
- Stage 4C remains blocked.

## Current Next Action

1. Verify no `real_pilot_data/`, `validation_runs/`, or `uploads/` content is committed.
2. Commit branch `codex/stage4-real-survey-baseline-conversion-pack`.
3. Deliver final report with support counts, suitability classification, and local-only output paths.
