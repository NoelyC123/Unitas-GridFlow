# GridFlow Current Task

Purpose: active task tracker. This file is the canonical current task record alongside `00_PROJECT_BOARD.md`.

## Active Task

- Task: Audit Existing Survey Files for Stage 4C Controlled Baseline Pilot Suitability
- Branch: `codex/audit-existing-files-for-stage4c-baseline-pilot`
- Owner: codex
- Lane: Stage 4 field pilot execution
- Status: validated_ready_for_merge
- Requested by: Noel
- Runtime changes allowed: no live app integration; control/docs only; no real evidence may be committed
- Tests required: `pytest -v`; `pre-commit run --all-files`; `python3.13 scripts/repo_health.py`; `python3.13 scripts/merge_safety_check.py codex/audit-existing-files-for-stage4c-baseline-pilot`
- Validation result: pass (`pytest -v`: 1067 passed, 2 skipped; `pre-commit run --all-files`: passed; `python3.13 scripts/repo_health.py`: warning-only for known numbering collisions; `python3.13 scripts/merge_safety_check.py codex/audit-existing-files-for-stage4c-baseline-pilot`: safe to merge)
- Browser validation required: no; control/docs only, no runtime UI changes
- Popup scope changes allowed: no

## Goal

Audit the real survey/job CSV files already present in the repository checkout
and determine whether any existing file is suitable as the baseline for the
next Stage 4C controlled pilot. If no suitable tracked file exists, record that
explicitly and state what Noel needs to provide.

## Scope

- Inspect the named priority candidate CSV paths first.
- Scan all other tracked real survey/job CSVs in the checkout, excluding mock/template/fixture/archive data.
- Create `AI_CONTROL/79_EXISTING_SURVEY_BASELINE_CANDIDATE_AUDIT.md`.
- Update control files with the audit result.
- Run full validation suite and prepare branch for merge.

## Out Of Scope

- Runtime upload integration.
- Stage 4 fields in popups or Review OS.
- Backend QA, geometry, span generation, intake, or map rendering changes.
- Stage 4C runtime integration.
- Real evidence or report commits.
- Archive files.

## Acceptance Criteria

- `AI_CONTROL/79_EXISTING_SURVEY_BASELINE_CANDIDATE_AUDIT.md` records path-level, header-level, and aggregate-level audit findings without exposing row contents.
- Each named priority candidate is classified as `SUITABLE`, `POSSIBLE FALLBACK`, `NOT SUITABLE`, or `UNKNOWN / NEEDS MANUAL REVIEW`.
- Best baseline candidate is identified, or the document explicitly states that none are available in this checkout.
- Control files are updated to reflect the audit result and Stage 4C remains blocked pending a real accessible baseline.
- `pytest -v` passes.
- `pre-commit run --all-files` passes clean.
- `python3.13 scripts/repo_health.py` reports warning-only (known collisions only).
- `python3.13 scripts/merge_safety_check.py` confirms safe to merge.
- `real_pilot_data/` and `validation_runs/` remain git-ignored with zero real evidence committed.

## Current Next Action

1. Merge the audit record.
2. Noel provides an accessible real Trimble baseline CSV, preferably `P008/F001` or `P009/F001`.
3. Re-run the candidate audit against the actual file.
4. Execute the controlled baseline pilot only after a real baseline file is confirmed suitable.
