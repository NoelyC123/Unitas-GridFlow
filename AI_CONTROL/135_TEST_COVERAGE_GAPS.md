# Test Coverage Gaps

**Date:** 2026-05-18
**Test baseline:** 1470 passed, 9 skipped
**Source:**
- `find gridflow/ -name "*.py" -not -name "__init__.py"`
- `find tests/ -name "*.py" -not -name "__init__.py"`

---

## Coverage by Module

| gridflow module | Test file | Status | Priority |
|---|---|---|---|
| `gridflow/baseline/coordinate_transformer.py` | `tests/baseline/test_coordinate_transformer.py` | ✅ COVERED | — |
| `gridflow/baseline/csv_parser.py` | `tests/baseline/test_csv_parser.py` | ✅ COVERED | — |
| `gridflow/baseline/models.py` | *(no dedicated test file)* | ⚠️ INDIRECT | LOW |
| `gridflow/baseline/route_reconstructor.py` | `tests/baseline/test_route_reconstructor.py` | ✅ COVERED | — |
| `gridflow/baseline/schema_validator.py` | `tests/baseline/test_schema_validator.py` | ✅ COVERED | — |
| `gridflow/baseline/support_number_normalizer.py` | `tests/baseline/test_support_number_normalizer.py` | ✅ COVERED | — |
| `gridflow/conflict_detector/detector.py` | `tests/test_conflict_detector.py` | ✅ COVERED | — |
| `gridflow/enwl_trace/parser.py` | `tests/test_enwl_trace_parser.py` | ✅ COVERED | — |
| `gridflow/evidence_combiner/combiner.py` | `tests/test_evidence_combiner.py` | ✅ COVERED | — |
| `gridflow/evidence_combiner/linker.py` | `tests/test_linker.py` | ✅ COVERED | — |
| `gridflow/field/dataset_validator.py` | `tests/field/test_dataset_validator.py` | ✅ COVERED | — |
| `gridflow/field/evidence_quality_scorer.py` | `tests/field/test_evidence_quality_scorer.py` | ✅ COVERED | — |
| `gridflow/field/folder_scanner.py` | `tests/field/test_folder_scanner.py` | ✅ COVERED | — |
| `gridflow/field/models.py` | *(no dedicated test file)* | ⚠️ INDIRECT | LOW |
| `gridflow/field/notes_parser.py` | `tests/field/test_notes_parser.py` | ✅ COVERED | — |
| `gridflow/matching/confidence_scorer.py` | `tests/matching/test_confidence_scorer.py` | ✅ COVERED | — |
| `gridflow/matching/models.py` | *(no dedicated test file)* | ⚠️ INDIRECT | LOW |
| `gridflow/matching/register_builder.py` | `tests/matching/test_register_builder.py` | ✅ COVERED | — |
| `gridflow/matching/support_number_matcher.py` | `tests/matching/test_support_number_matcher.py` | ✅ COVERED | — |
| `gridflow/merge/conflict_detector.py` | `tests/merge/test_conflict_detector.py` | ✅ COVERED | — |
| `gridflow/merge/data_merger.py` | `tests/merge/test_data_merger.py` | ✅ COVERED | — |
| `gridflow/merge/models.py` | *(no dedicated test file)* | ⚠️ INDIRECT | LOW |
| `gridflow/merge/qa_report_generator.py` | `tests/merge/test_qa_report_generator.py` | ✅ COVERED | — |
| `gridflow/merge/verification_flag_generator.py` | `tests/merge/test_verification_flag_generator.py` | ✅ COVERED | — |
| `gridflow/photos/loader.py` | `tests/test_photo_loader.py` | ✅ COVERED | — |
| `gridflow/readiness/assessor.py` | `tests/test_readiness_assessor.py` | ✅ COVERED | — |
| `gridflow/registration.py` | `tests/test_registration.py` | ✅ COVERED | — |
| `gridflow/reports/design_readiness_reporter.py` | `tests/reports/test_design_readiness_reporter.py` | ✅ COVERED | — |
| `gridflow/reports/dno_request_reporter.py` | `tests/reports/test_dno_request_reporter.py` | ✅ COVERED | — |
| `gridflow/reports/evidence_provenance_reporter.py` | `tests/reports/test_evidence_provenance_reporter.py` | ✅ COVERED | — |
| `gridflow/reports/match_confidence_reporter.py` | `tests/reports/test_match_confidence_reporter.py` | ✅ COVERED | — |
| `gridflow/reports/pilot_index_reporter.py` | `tests/reports/test_pilot_index_reporter.py` | ✅ COVERED | — |
| `gridflow/reports/verification_flags_reporter.py` | `tests/reports/test_verification_flags_reporter.py` | ✅ COVERED | — |
| `gridflow/workspace/enwl_evidence_adapter.py` | `tests/test_workspace_enwl_evidence.py` | ✅ COVERED | — |
| `gridflow/workspace/readiness_adapter.py` | `tests/test_workspace_readiness.py` | ✅ COVERED | — |
| `gridflow/workspace/review_data_provider.py` | `tests/workspace/test_review_data_provider.py` | ✅ COVERED | — |

---

## Gaps Summary

| Module | Gap type | Priority | Notes |
|---|---|---|---|
| `gridflow/baseline/models.py` | No dedicated test file | LOW | `BaselinePole` and `BaselineDataset` are Pydantic models tested indirectly through `test_csv_parser.py`. Field validators (`validate_easting`, `validate_northing`) have no explicit unit tests. |
| `gridflow/field/models.py` | No dedicated test file | LOW | `FieldPole` and `FieldDataset` are Pydantic models tested indirectly through `test_folder_scanner.py`. |
| `gridflow/matching/models.py` | No dedicated test file | LOW | `MatchResult` and `MatchRegister` are Pydantic models tested indirectly through matcher and register builder tests. |
| `gridflow/merge/models.py` | No dedicated test file | LOW | `MergedPole` and `MergedDataset` are Pydantic models tested indirectly through `test_data_merger.py`. `design_ready` flag logic not tested in isolation. |

---

## Gap Assessment

**No HIGH priority gaps.** Every active pipeline module has a dedicated test file.

All four gaps are LOW priority. They are Pydantic model files whose field validation
and default values are exercised thoroughly by the tests for the modules that construct
them. The gaps are:

- **Model field validators** — `BaselinePole.validate_easting/northing` run on
  construction but have no isolated unit tests. They would catch out-of-bounds BNG values
  (e.g., > 700,000 m easting) that no test currently exercises explicitly.

- **`MergedPole.design_ready` flag logic** — the merger sets `design_ready = False` by
  default and the readiness assessor conditionally sets it `True`. There is no test that
  explicitly asserts `design_ready` cannot be set `True` without all conditions met; this
  is instead covered by the integration-level `test_pipeline.py` tests.

**Suggested additions (low priority, not blocking):**

1. `tests/baseline/test_baseline_models.py` — test BNG coordinate bounds validators
   with out-of-range values
2. `tests/merge/test_merged_pole_model.py` — assert `design_ready` defaults `False`,
   `design_blocked` defaults `True`, and required field types

---

## Modules with Multiple Test Files

Some modules are tested by more than one test file:

| Module | Test files |
|---|---|
| `gridflow/conflict_detector/detector.py` | `tests/test_conflict_detector.py` + `tests/merge/test_conflict_detector.py` (different layers) |
| `gridflow/evidence_combiner/combiner.py` | `tests/test_evidence_combiner.py` + `tests/test_export_combined_evidence_bundle.py` |
| `gridflow/workspace/` | `tests/test_workspace_*.py` (3 files) + `tests/workspace/` directory |

---

## App Layer (Not in gridflow/)

`app/` (Stage 1/2 Trimble GNSS pipeline) has a separate test layer. Key coverage:

| Module | Test file | Status |
|---|---|---|
| `app/qa_engine.py` | `tests/test_qa_engine.py` | ✅ |
| `app/routes/workspace.py` | `tests/workspace/test_routes.py` | ✅ |
| `app/routes/api_intake.py` | `tests/test_api_intake.py` | ✅ |

`app/routes/photos.py` does not exist yet (Stage 7B) — no tests yet.
