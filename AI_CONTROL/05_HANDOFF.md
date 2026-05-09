# GridFlow Current Handoff

Purpose: latest operational handoff for Noel and AI workers.

## Summary

- Master is stable.
- Latest completed milestone: `project-control-center-foundation-complete`.
- Prior stable milestone: `c2e2-popup-expansion-implementation-complete`.
- Current active branch is `codex/c2f-review-focus-issue-filtering`.
- This branch implements the C2F review focus mode and issue filtering workspace.
- Backend validation, geometry, span generation, intake, and C2E2 field truthfulness rules were not changed.
- Manual review harness passed for `P008/F001` and `P010/F001`.
- Next expected action after merge: review the UI workflow, then continue with the next validation-led product task.

## Active Task

<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->
- Task: C2F Review Focus + Issue Filtering Workspace
- Owner: codex
- Branch: `codex/c2f-review-focus-issue-filtering`
- Status: ready for review
- Summary: Added review focus state, compact issue focus controls, focused/muted map styling, navigation integration, review focus checklist support, and tests.
- Commit: branch commit recorded in git history; final hash is reported by Codex after commit creation.
- Validation: `pytest tests/test_review_focus_mode.py -v`, `pytest tests/test_review_navigation_layer.py -v`, `pytest tests/test_c2e2_popup_rendering.py -v`, `pytest -v`, `pre-commit run --all-files`, and manual review harness passed.
- Manual review report: `validation_runs/20260509_204010/validation_report.md`
- Updated: 2026-05-09T20:41:00Z
<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->

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

- Review the C2F focus/filter workflow.
- Merge/tag after review.
- Continue with the next validation-led product task on a separate branch.

## Do Not Start On This Branch

- Stage 4 *integration* into the upload/QA/popup flow (separate branch).
- Technical docs field/architecture package
- Lifecycle visualization feature work
- DNO-grade rulepack implementation

## Completed stable milestone

- `stage4-structured-capture-foundation-complete` is already merged to master.
