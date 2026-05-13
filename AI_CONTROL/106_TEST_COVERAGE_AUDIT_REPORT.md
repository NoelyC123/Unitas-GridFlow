# Stage 4C Test Coverage Audit Report

## Purpose

Document the Stage 4C baseline/field/matching test coverage audit, test additions, and Pydantic warning fixes completed as part of production-readiness hardening.

## Audit Scope

Source modules audited:

- `gridflow/baseline/coordinate_transformer.py`
- `gridflow/baseline/csv_parser.py`
- `gridflow/baseline/models.py`
- `gridflow/baseline/route_reconstructor.py`
- `gridflow/baseline/schema_validator.py`
- `gridflow/baseline/support_number_normalizer.py`
- `gridflow/field/dataset_validator.py`
- `gridflow/field/evidence_quality_scorer.py`
- `gridflow/field/folder_scanner.py`
- `gridflow/field/models.py`
- `gridflow/field/notes_parser.py`
- `gridflow/matching/confidence_scorer.py`
- `gridflow/matching/models.py`
- `gridflow/matching/register_builder.py`
- `gridflow/matching/support_number_matcher.py`

Test files updated in place:

- `tests/baseline/test_coordinate_transformer.py`
- `tests/baseline/test_csv_parser.py`
- `tests/baseline/test_route_reconstructor.py`
- `tests/baseline/test_schema_validator.py`
- `tests/baseline/test_support_number_normalizer.py`
- `tests/field/test_dataset_validator.py`
- `tests/field/test_evidence_quality_scorer.py`
- `tests/field/test_folder_scanner.py`
- `tests/field/test_notes_parser.py`
- `tests/matching/test_confidence_scorer.py`
- `tests/matching/test_register_builder.py`
- `tests/matching/test_support_number_matcher.py`

## Summary

- Previous target suite size: 117 tests
- New target suite size: 146 tests
- New tests added: 29
- Target suite result: 146 passed
- Combined measured coverage for baseline/field/matching packages: 90%
- Pydantic deprecation warnings fixed: 4 class-based `Config` blocks migrated to `ConfigDict`

## Coverage Gaps Found and Fixed

### Baseline Modules

`gridflow/baseline/models.py`

- Gap: Pydantic v2 class-based `Config` warnings on four models.
- Fix: Migrated `BaselinePole`, `ValidationIssue`, `ValidationReport`, and `BaselineDataset` to `model_config = ConfigDict(...)`.

`gridflow/baseline/csv_parser.py`

- Gap: Generic CSV with completely missing required columns was not explicitly tested.
- Added test: parser returns an empty dataset without crashing.
- Gap: Encoding fallback was not explicitly tested.
- Added test: latin-1 encoded CSV parses through fallback handling.

`gridflow/baseline/coordinate_transformer.py`

- Gap: UK coordinate boundary values were not tested.
- Added tests for exact OSGB36 and WGS84 boundary acceptance.
- Gap: Empty dataset transformation was not tested.
- Added test confirming empty datasets pass through safely.

`gridflow/baseline/route_reconstructor.py`

- Gap: Large route continuity gaps were not tested.
- Added test confirming gaps above threshold are reported.
- Gap: Full sequence reconstruction for a single-pole dataset was not tested.
- Added test confirming deterministic synthetic route/sequence assignment.

`gridflow/baseline/schema_validator.py`

- Gap: Empty baseline dataset handling was not directly asserted.
- Added warning-only empty dataset test.
- Gap: All poles sharing one duplicate support number was not tested.
- Added test confirming duplicate support warning visibility.

`gridflow/baseline/support_number_normalizer.py`

- Gap: Very long support strings were not tested.
- Added test for >50-character noisy string extraction.
- Gap: Pure alphabetic support numbers needed explicit coverage.
- Added invalid-format test.
- Gap: Duplicate detection after normalization was not tested.
- Added duplicate grouping test for prefix/separator variants.

### Field Modules

`gridflow/field/folder_scanner.py`

- Gap: Malformed folders that partially match `NN_SUPPORT_*` but have alphabetic support IDs were not integration-tested.
- Added test confirming scan returns `UNKNOWN` support and `UNKNOWN_SUPPORT` flag.
- Gap: Non-UTF-8 notes fallback was not tested.
- Added latin-1 notes file test.
- Gap: Alphabetic support extraction was only indirectly covered.
- Added direct extraction test.

`gridflow/field/notes_parser.py`

- Gap: Empty sections with headers but no content were not tested.
- Added empty-section parser test.
- Gap: Unicode notes content was not tested.
- Added unicode parser preservation test.

`gridflow/field/evidence_quality_scorer.py`

- Gap: Exactly 3 photos boundary condition was not explicit.
- Added boundary HIGH test.
- Gap: Exactly 0 photos was not explicit.
- Added LOW test.
- Gap: Empty dataset scoring was not tested.
- Added empty dataset scoring test.

`gridflow/field/dataset_validator.py`

- Gap: Alphabetic/unknown support numbers from partial folders needed explicit warning coverage.
- Added warning test.
- Gap: Duplicate UNKNOWN support numbers were not tested.
- Added duplicate UNKNOWN support test.

### Matching Modules

`gridflow/matching/support_number_matcher.py`

- Gap: Empty baseline/field datasets were not tested.
- Added empty input test.
- Gap: Duplicate field support numbers were not tested.
- Added deterministic current-behaviour test showing last duplicate wins, requiring upstream validation.
- Gap: Alphabetic field support vs numeric baseline was not tested.
- Added no-match test.

`gridflow/matching/confidence_scorer.py`

- Gap: Voltage conflict detection path was not tested.
- Added LV/HV conflict test.
- Gap: Register-level scoring propagation was not tested.
- Added `score_register` test for conflict propagation and stat recompute.

`gridflow/matching/register_builder.py`

- Gap: Match register with duplicate support numbers was not tested.
- Added duplicate support preservation test.
- Gap: Empty register build was not tested.
- Added empty register test.

## Integration-Style Gaps Addressed

The audit added tests that exercise realistic combinations rather than only isolated helpers:

- Folder scanner reading a real temporary folder with latin-1 notes
- Folder scanner processing malformed-but-partially-valid folder names
- Register builder preserving duplicate support rows
- Confidence scorer updating a full register from baseline and field datasets
- Empty dataset handling through transformer, scorer, matcher, and register builder

## Remaining Known Gaps

Remaining uncovered paths are acceptable for the current stage but should be revisited before wider production deployment:

- `coordinate_transformer.py`: pyproj import failure and `transform_pole` path need more direct tests.
- `csv_parser.py`: low-level mapping helpers and parser exception branches remain partly uncovered.
- `folder_scanner.py`: some private path helpers and logging/error fallback branches remain uncovered.
- Matching currently has no coordinate-proximity fallback module; support-number matching remains the implemented path.
- Duplicate field support numbers are currently deterministic but not resolved by matcher; upstream validation must keep flagging them.

## Measured Coverage

Coverage command:

```bash
pytest tests/baseline tests/field tests/matching --cov=gridflow.baseline --cov=gridflow.field --cov=gridflow.matching --cov-report=term-missing -q
```

Measured package/module coverage:

- `gridflow/baseline/coordinate_transformer.py`: 70%
- `gridflow/baseline/csv_parser.py`: 80%
- `gridflow/baseline/models.py`: 88%
- `gridflow/baseline/route_reconstructor.py`: 100%
- `gridflow/baseline/schema_validator.py`: 90%
- `gridflow/baseline/support_number_normalizer.py`: 84%
- `gridflow/field/dataset_validator.py`: 99%
- `gridflow/field/evidence_quality_scorer.py`: 94%
- `gridflow/field/folder_scanner.py`: 89%
- `gridflow/field/models.py`: 88%
- `gridflow/field/notes_parser.py`: 92%
- `gridflow/matching/confidence_scorer.py`: 97%
- `gridflow/matching/models.py`: 100%
- `gridflow/matching/register_builder.py`: 100%
- `gridflow/matching/support_number_matcher.py`: 96%

Total measured coverage: 90%.

## Final Validation

Targeted validation:

```bash
pytest tests/baseline tests/field tests/matching -q
```

Result:

```text
146 passed
```

Full validation required by task:

```bash
pytest tests/ -v --tb=short 2>&1 | tail -30
```

Result should be recorded in final worker response.
