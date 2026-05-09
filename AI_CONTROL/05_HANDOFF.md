# GridFlow Current Handoff

Purpose: latest operational handoff for Noel and AI workers.

## Summary

- Master is stable.
- Latest completed milestone: `project-control-center-foundation-complete`.
- Prior stable milestone: `c2e2-popup-expansion-implementation-complete`.
- Current active branch is `claude-code/stage4-structured-capture-foundation`.
- This branch adds the Stage 4 structured-capture foundation: schema, validators, template generator, docs, tests, and a generated CSV template. **No app runtime files are modified.**
- Next expected action after review: tag/merge, then plan Stage 4 integration into upload/QA/popup flows on a separate branch.

## Active Task

<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->
- Task: Stage 4 Structured Capture Foundation
- Owner: claude-code
- Branch: `claude-code/stage4-structured-capture-foundation`
- Status: ready for review
- Summary: Schema, validators, template generator, docs, and tests for the future Stage 4 structured-capture layer. No live integration.
- Updated: 2026-05-09T20:32:31Z
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

- Review this Stage 4 foundation branch.
- Merge/tag after review.
- Plan Stage 4 integration on a separate branch when Noel is ready.

## Do Not Start On This Branch

- Stage 4 *integration* into the upload/QA/popup flow (separate branch).
- Technical docs field/architecture package
- Lifecycle visualization feature work
- DNO-grade rulepack implementation
