# GridFlow Current Handoff

Purpose: latest operational handoff for Noel and AI workers.

## Summary

- Master is stable.
- Latest completed milestone: `project-control-center-foundation-complete`.
- Prior stable milestone: `c2e2-popup-expansion-implementation-complete`.
- Current active branch is `codex/project-control-worker-bootstrap`.
- This branch is control-layer only and adds worker start/finish process guidance plus a control status script.
- No app runtime files should be touched on this branch.
- Expected next action: review the control-layer changes, confirm validation is clean, then merge/tag if approved.

## Active Task

<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->
- Task: Project Control Worker Bootstrap Enforcement
- Owner: codex
- Branch: `codex/project-control-worker-bootstrap`
- Status: ready for review
- Summary: Added worker start/finish checklists, prompt templates, control status script, README guidance, and worker-rule updates
- Commit: final branch HEAD; exact SHA reported in git history and Codex handoff response
- Validation: `pytest tests/test_control_status.py -v`, `pytest tests/test_project_control_scripts.py -v`, `pytest -v`, and `pre-commit run --all-files` passed
- Updated: 2026-05-09T21:34:00Z
<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->

## Worker Bootstrap Status

- **Branch:** `codex/project-control-worker-bootstrap`
- **Commit:** final branch HEAD; exact SHA reported in git history and Codex handoff response
- **What changed:**
  - `AI_CONTROL/07_WORKER_START_CHECKLIST.md` - standard pre-coding worker checklist
  - `AI_CONTROL/08_WORKER_FINISH_CHECKLIST.md` - standard pre-handoff worker checklist
  - `AI_CONTROL/09_WORKER_PROMPT_TEMPLATES.md` - reusable worker assignment templates
  - `scripts/control_status.py` - read-only project control status snapshot with text and JSON output
  - `tests/test_control_status.py` - unit tests for status output, JSON mode, git failure handling, dirty-tree warnings, and no-write behavior
  - `README_PROJECT_CONTROL.md` - bootstrap workflow, script responsibilities, and multi-worker usage guidance
  - `AI_CONTROL/06_WORKER_RULES.md` - explicit checklist and `control_status.py` requirements
- **Validation status:**
  - `pytest tests/test_control_status.py -v` - passed
  - `pytest tests/test_project_control_scripts.py -v` - passed
  - `pytest -v` - 861 passed, 1 skipped
  - `pre-commit run --all-files` - passed
  - Manual review harness not required; no UI, map, popup, or review workflow files changed
- **Warning:** no app runtime files should be touched on this branch
- **Next action:** review the control-layer changes, confirm the branch stays control-only, then merge/tag if approved

## Stage 4 Foundation — Status

- **Branch:** `claude-code/stage4-structured-capture-foundation`
- **Commit:** pending (filled in by post-commit follow-up)
- **What changed:**
  - `app/structured_capture_schema.py` — canonical Stage 4 field catalogue (26 fields across 6 groups; pure stdlib).
  - `app/structured_capture_validators.py` — pure validation helpers (`is_blank`, `normalise_bool`, `validate_allowed_value`, `validate_required_fields`, `validate_stage4_row`, `validate_stage4_rows`, `classify_stage4_completeness`, `normalise_stage4_row`).
  - `scripts/generate_structured_capture_template.py` — CSV template generator (default output `templates/structured_capture_template.csv`; `--include-descriptions`, `--stdout` flags).
  - `docs/STAGE4_STRUCTURED_CAPTURE.md` — why Stage 4 exists, the captured/derived/structured separation, validation rules, future integration points.
  - `docs/STRUCTURED_CAPTURE_TEMPLATE_GUIDE.md` — how to generate and fill the template, allowed values, examples, blank/unknown semantics.
  - `tests/test_structured_capture_schema.py`, `tests/test_structured_capture_validators.py`, `tests/test_generate_structured_capture_template.py` — 23 new unit tests.
  - `templates/structured_capture_template.csv` — generated reference CSV.
- **What is NOT implemented yet:**
  - No upload route or live ingest pathway accepts Stage 4 files.
  - No QA gate, design-readiness gate, or popup field reads from Stage 4 data.
  - No persistence layer stores Stage 4 rows against existing jobs.
  - No app runtime files (`app/routes/api_intake.py`, `app/controller_intake.py`, `app/qa_engine.py`, `app/geometry_pipeline.py`, `app/span_generator.py`, `app/static/js/map-viewer.js`) modified.
- **Validation status:**
  - `pytest tests/test_structured_capture_schema.py tests/test_structured_capture_validators.py tests/test_generate_structured_capture_template.py -v` — 23 passed.
  - `pytest -v` — 855 passed.
  - `pre-commit run --all-files` — all hooks pass.
  - Manual review harness not required (no UI changes).
- **Next action:**
  - Review schema, validators, and docs.
  - Tag/merge after review.
  - Open a separate Stage 4 *integration* branch when ready to wire into the upload/QA/popup flow.

## Next Action

- Review the worker bootstrap control changes.
- Confirm tests and pre-commit are clean.
- Merge/tag after review if the branch remains control-only.

## Do Not Start On This Branch

- Any app runtime feature work.
- Any UI, Flask, geometry, qa_engine, span generation, or structured-capture integration work.
- Technical docs field/architecture package.
- DNO-grade rulepack implementation.

## Completed stable milestone

- `stage4-structured-capture-foundation-complete` is already merged to master.
