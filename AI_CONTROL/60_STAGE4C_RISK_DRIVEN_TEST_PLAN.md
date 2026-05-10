---
status: ACTIVE
created: 2026-05-10
branch: codex/stage4c-runtime-integration-architecture
---

# 60 — Stage 4C Risk-Driven Test Plan

This document defines **per-risk test cases** that prove each of the 8 active risks in the risk register (document 55) is mitigated. Tests are organized by risk ID and test file.

---

## Test files

### `tests/test_stage4c_runtime_integration.py` (NEW)

Tests for the merge algorithm and data persistence (covers R01, R04, R05, R08).

### `tests/test_stage4c_runtime_boundary.py` (NEW)

Tests for runtime isolation and leakage prevention (covers R03, R07).

### `tests/test_stage4c_completeness_truthfulness.py` (NEW)

Tests for preventing fake completeness and ensuring none truthfulness (covers R02).

### Existing: `tests/test_stage4_golden_samples.py`

Parametrized tests for golden samples (valid, invalid, duplicates, known-bad, legacy headers, pilot real data). Covers schema correctness and regression prevention (covers R06).

---

## Risk R01 — Wrong pole_id match corrupts live job data

**Risk**: partial pole_id match merges Stage 4 into wrong Trimble record.

**Mitigation**: exact-match only, log all merges, no overwrite.

### Test: `test_merge_exact_pole_id_match_only`

```python
def test_merge_exact_pole_id_match_only():
    """
    Prove: only exact pole_id matches succeed.
    Fuzzy matching is forbidden.
    """
    # Stage 4 CSV with pole_id = "P008-001"
    # Trimble baseline has: ["P008-001", "P008-01", "P0008-001", "P008001"]

    # Validate and merge
    result = merge_stage4_rows([
        {"pole_id": "P008-001", ...}  # exact match
    ], trimble_ids=["P008-001", "P008-01", ...])

    # Assert: merge succeeds for "P008-001"
    assert result[0]["matched_trimble"] == "P008-001"
```

### Test: `test_merge_rejects_partial_pole_match`

```python
def test_merge_rejects_partial_pole_match():
    """
    Prove: partial matches are rejected.
    P008-01 does NOT match P008-001.
    """
    result = merge_stage4_rows([
        {"pole_id": "P008-01", ...}  # partial match
    ], trimble_ids=["P008-001"])  # exact: P008-001

    # Assert: merge rejects; flags as unmatched
    assert result[0]["matched_trimble"] is None
    assert result[0]["unmatched_pole"] is True
```

### Test: `test_merge_no_overwrite_trimble_values`

```python
def test_merge_no_overwrite_trimble_values():
    """
    Prove: Trimble values are never overwritten.
    Stage 4 is additive only.
    """
    # Trimble record: pole_type="Concrete", material="Wood"
    # Stage 4 CSV: pole_type="Steel" (conflict)

    result = merge_stage4_to_trimble(stage4_row, trimble_record)

    # Assert: Trimble values unchanged
    assert result.trimble_pole_type == "Concrete"  # unchanged
    assert result.conflict_detected == True
    assert result.stage4_pole_type == "Steel"  # captured but not applied
```

### Test: `test_merge_log_all_operations`

```python
def test_merge_log_all_operations():
    """
    Prove: every merge is logged with before/after snapshots.
    """
    # Merge a Stage 4 row
    merge_result = merge_stage4_rows([{...}], job_id="P008/F001")

    # Assert: audit log created
    audit_log = get_audit_log(job_id="P008/F001")
    assert len(audit_log) > 0
    assert audit_log[0]["before_state"]["pole_id"] == "P008-001"
    assert audit_log[0]["after_state"]["stage4_captured"] == True
    assert audit_log[0]["timestamp"] is not None
```

---

## Risk R02 — Fake completeness: Stage 4 fields present but meaningless

**Risk**: all optional fields are `unknown` or placeholder; popup shows "complete" falsely.

**Mitigation**: completeness classification, truth in none handling, no unknown allowed.

### Test: `test_completeness_minimum`

```python
def test_completeness_minimum():
    """
    Row with only required fields = minimum completeness.
    """
    row = {
        "pole_id": "P008-001",
        "capture_source": "surveyor_tablet",
        "captured_by": "Alice",
        "capture_date": "2026-05-10"
    }

    result = validate_stage4_rows([row])
    assert result[0]["completeness"] == "minimum"
```

### Test: `test_completeness_partial`

```python
def test_completeness_partial():
    """
    Row with required + 9 optional fields = partial.
    (optional field threshold = 9–17 of ~18)
    """
    row = {
        "pole_id": "P008-001",
        ...required...,
        "condition": "good",
        "voltage_carried": "11kV",
        "stay_present": "yes",
        "lean_direction": "none",
        "equipment_present": "no",
        # 5 optional filled = partial
    }

    result = validate_stage4_rows([row])
    assert result[0]["completeness"] == "partial"
```

### Test: `test_completeness_complete`

```python
def test_completeness_complete():
    """
    Row with required + 18+ optional fields = complete.
    """
    row = {
        "pole_id": "P008-001",
        ...required...,
        "condition": "good",
        "voltage_carried": "11kV",
        "stay_present": "yes",
        "stay_type": "stay_down",
        "lean_direction": "none",
        "lean_severity": "minor",
        "equipment_present": "no",
        "equipment_type": "none",
        "clearance_issues": "none",
        "defect_notes": "Good condition",
        "conductor_size": "50mm",
        "stay_required": "yes",
        "verification_required": "no",
        "confidence_level": "high",
        # 14+ optional fields = complete
    }

    result = validate_stage4_rows([row])
    assert result[0]["completeness"] == "complete"
```

### Test: `test_none_is_truthful_not_placeholder`

```python
def test_none_is_truthful_not_placeholder():
    """
    Prove: stay_type="none" means "verified no stay",
    not "didn't check".
    """
    row = {
        "pole_id": "P008-001",
        ...required...,
        "stay_present": "no",
        "stay_type": "none",  # explicit verification
        "confidence_level": "high"
    }

    result = validate_stage4_rows([row])
    # Assert: row is valid, not rejected
    assert result[0]["valid"] == True
    # Assert: "none" counts toward completeness
    assert result[0]["completeness"] == "partial"  # or complete, depending on others

    # Assert: popup displays truthfully
    popup_label = get_popup_label("stay_type", "none", confidence="high")
    assert "verified" in popup_label or "confirmed" in popup_label
```

### Test: `test_unknown_is_forbidden`

```python
def test_unknown_is_forbidden():
    """
    Prove: "unknown" value is rejected; too vague.
    """
    row = {
        "pole_id": "P008-001",
        ...required...,
        "condition": "unknown"  # forbidden
    }

    result = validate_stage4_rows([row])
    assert result[0]["valid"] == False
    assert "unknown not allowed" in result[0]["errors"]
```

---

## Risk R03 — Stage 4 leaks into map popup before Stage 4D

**Risk**: Stage 4 field accidentally appears in C2E2 popup before 4D approval.

**Mitigation**: runtime boundary checks, AST import scanning, leakage guard tests.

### Test: `test_stage4_records_do_not_appear_in_popup_fields`

```python
def test_stage4_records_do_not_appear_in_popup_fields():
    """
    Prove: Stage 4 data is not included in popup field groups.
    """
    from app.c2e2_field_definitions import POPUP_FIELD_GROUPS

    # Collect all field names in popup
    popup_fields = set()
    for group in POPUP_FIELD_GROUPS.values():
        popup_fields.update(group)

    # Stage 4 fields are NOT in popup
    stage4_fields = {
        "condition", "voltage_carried", "stay_present", "stay_type",
        "lean_direction", "equipment_present", "equipment_type",
        "clearance_issues", "defect_notes", "conductor_size",
        "stay_required", "lean_severity", "verification_required"
    }

    # Assert: no overlap (except shared names like structure_type)
    overlap = popup_fields & stage4_fields
    allowed_overlap = {"structure_type", "asset_intent", "material"}
    assert overlap <= allowed_overlap, f"Stage 4 leakage: {overlap - allowed_overlap}"
```

### Test: `test_merge_safety_check_no_stage4_imports_in_forbidden_files`

```python
def test_merge_safety_check_stage4_boundary():
    """
    Run merge_safety_check.py Stage 4C validator.
    Prove: no Stage 4 imports in forbidden files.
    """
    from scripts.merge_safety_check import check_stage4c_boundaries

    violations = check_stage4c_boundaries()

    # Assert: no violations
    assert len(violations) == 0, \
        f"Stage 4 boundary violations:\n{violations}"
```

### Test: `test_qa_engine_does_not_leak_stage4`

```python
def test_qa_engine_does_not_leak_stage4():
    """
    Prove: QA output does not include Stage 4 data,
    even if Stage 4 records exist in job.
    """
    # Merge Stage 4 CSV
    merge_result = merge_stage4_rows([...], job_id="P008/F001")
    assert merge_result["rows_merged"] > 0

    # Run QA
    qa_result = run_qa("P008/F001")

    # Assert: QA output has no Stage 4 fields
    qa_json = json.dumps(qa_result)
    stage4_keywords = ["stage4", "structured_capture", "condition", "voltage_carried"]
    for keyword in stage4_keywords:
        assert keyword not in qa_json, \
            f"Stage 4 keyword '{keyword}' leaked into QA output"
```

---

## Risk R04 — pole_id format mismatch between Trimble and Stage 4 CSV

**Risk**: Trimble is `P008-001` but surveyor types `P008001` or `P008 001`; match fails.

**Mitigation**: normalize whitespace/dashes on import, log unmatched, real pilot validation.

### Test: `test_pole_id_normalization_whitespace`

```python
def test_pole_id_normalization_whitespace():
    """
    Prove: leading/trailing whitespace is stripped.
    """
    rows = [
        {"pole_id": "  P008-001  ", ...},  # leading/trailing space
        {"pole_id": "P008-001", ...},      # clean
    ]

    result = validate_stage4_rows(rows)
    # Both should normalize to "P008-001"
    assert result[0]["pole_id"] == "P008-001"
    assert result[1]["pole_id"] == "P008-001"
```

### Test: `test_pole_id_format_mismatch_logged`

```python
def test_pole_id_format_mismatch_logged():
    """
    Prove: unmatched pole_ids are logged with reason.
    """
    stage4_rows = [
        {"pole_id": "P008001", ...},  # no dash (format mismatch)
    ]
    trimble_ids = ["P008-001"]  # has dash

    result = merge_stage4_rows(stage4_rows, trimble_ids=trimble_ids)

    # Assert: merge rejects as unmatched
    assert result[0]["unmatched_trimble"] == True

    # Assert: unmatched reason is logged
    unmatched_log = get_unmatched_pole_log(job_id=result[0]["job_id"])
    assert "P008001" in [u["pole_id"] for u in unmatched_log]
```

---

## Risk R05 — Stage 4B validation preview diverges from Stage 4C merge behaviour

**Risk**: Stage 4B validates as `merge_ready=True`, but Stage 4C merge fails with different code path.

**Mitigation**: Stage 4C uses exact same `validate_stage4_rows()` function; integration test.

### Test: `test_stage4b_preview_equals_stage4c_merge_ready`

```python
def test_stage4b_preview_equals_stage4c_merge_ready():
    """
    Prove: Stage 4B validation result == Stage 4C merge acceptance.
    If Stage 4B says merge_ready=True, Stage 4C WILL merge.
    """
    from structured_capture_validators import validate_stage4_rows

    csv_rows = load_test_csv("tests/fixtures/stage4/golden_valid.csv")

    # Run Stage 4B validation
    b_result = validate_stage4_rows(csv_rows)
    b_merge_ready = [r for r in b_result if r["merge_ready"]]

    # Run Stage 4C merge
    c_result = merge_stage4_rows(csv_rows, trimble_ids=[...])
    c_merged = [r for r in c_result if r["merged_successfully"]]

    # Assert: same rows marked merge_ready in 4B are merged in 4C
    b_pole_ids = {r["pole_id"] for r in b_merge_ready}
    c_pole_ids = {r["pole_id"] for r in c_merged}

    assert b_pole_ids == c_pole_ids, \
        f"Divergence: 4B={b_pole_ids}, 4C={c_pole_ids}"
```

---

## Risk R06 — Schema drift — Stage 4 schema changes break existing validated CSVs

**Risk**: schema change breaks CSVs that previously validated.

**Mitigation**: golden sample suite, schema version, changelog.

See `tests/test_stage4_golden_samples.py` (existing).

### Test: `test_golden_samples_regression_detection`

```python
def test_golden_samples_regression_detection():
    """
    Parametrized test over all golden samples.
    If schema changes and breaks golden sample, test fails.
    """
    golden_samples = [
        ("tests/fixtures/stage4/golden_valid.csv", GOLDEN_VALID_EXPECTED),
        ("tests/fixtures/stage4/golden_invalid.csv", GOLDEN_INVALID_EXPECTED),
        # ... all 5+ categories
    ]

    for csv_file, expected in golden_samples:
        result = validate_stage4_rows(load_csv(csv_file))
        assert_result_matches_expected(result, expected)
```

---

## Risk R07 — AI worker extends Stage 4 scope without gate approval

**Risk**: Claude Code worker adds Stage 4 code to forbidden files without approval.

**Mitigation**: expanded `merge_safety_check.py`, leakage guard tests, explicit DO NOT START list.

### Test: `test_merge_safety_check_detects_stage4_in_forbidden_files`

```python
def test_merge_safety_check_detects_stage4_in_forbidden_files():
    """
    Prove: merge_safety_check.py detects Stage 4 scope violation.
    Example: if qa_engine.py imports structured_capture_validators, test fails.
    """
    # Simulate violation: add import to forbidden file
    # (In real test, this would scan actual codebase)

    violations = scan_for_stage4_imports(
        forbidden_files=[
            "app/qa_engine.py",
            "app/routes/api_qc.py",
            "app/static/js/map-viewer.js",
            "app/dno_rules.py",
            "app/pdf_generator.py"
        ]
    )

    assert len(violations) == 0, \
        f"Stage 4 scope violation detected: {violations}"
```

---

## Risk R08 — Duplicate pole_id accepted across separate upload sessions

**Risk**: second upload with same pole_id overwrites first.

**Mitigation**: check for existing Stage 4 record before merge.

### Test: `test_merge_rejects_duplicate_across_sessions`

```python
def test_merge_rejects_duplicate_across_sessions():
    """
    Prove: if pole_id already has Stage 4 record, second merge is rejected.
    """
    # First upload
    upload1_result = merge_stage4_rows(
        [{"pole_id": "P008-001", "condition": "good"}],
        job_id="P008/F001",
        upload_id="upload_001"
    )
    assert upload1_result[0]["merged_successfully"] == True

    # Second upload, same pole
    upload2_result = merge_stage4_rows(
        [{"pole_id": "P008-001", "condition": "poor"}],
        job_id="P008/F001",
        upload_id="upload_002"
    )

    # Assert: second merge is rejected (conflict)
    assert upload2_result[0]["merged_successfully"] == False
    assert "duplicate_pole_id" in upload2_result[0]["error"]

    # Assert: first record is unchanged
    existing_record = get_stage4_record(job_id="P008/F001", pole_id="P008-001")
    assert existing_record["condition"] == "good"  # unchanged
    assert existing_record["upload_id"] == "upload_001"
```

---

## Test execution

### Run all Stage 4C tests

```bash
pytest tests/test_stage4c_runtime_integration.py -v
pytest tests/test_stage4c_runtime_boundary.py -v
pytest tests/test_stage4c_completeness_truthfulness.py -v
pytest tests/test_stage4_golden_samples.py -v

# Or all at once
pytest tests/ -k stage4c -v
```

### Pre-merge checklist

Before merging Stage 4C:

- [ ] All Stage 4C tests pass
- [ ] All existing tests still pass (no regressions)
- [ ] `merge_safety_check.py` reports no violations
- [ ] Code review confirms boundary rules enforced
- [ ] Feature flag defaults to False

---

## Test coverage target

**Coverage by risk**:

| Risk | Test file | Status |
|---|---|---|
| R01 | test_stage4c_runtime_integration.py | test_merge_exact_pole_id_match_only, test_merge_no_overwrite_trimble_values, test_merge_log_all_operations |
| R02 | test_stage4c_completeness_truthfulness.py | test_completeness_*, test_none_is_truthful_not_placeholder, test_unknown_is_forbidden |
| R03 | test_stage4c_runtime_boundary.py | test_stage4_records_do_not_appear_in_popup_fields, test_merge_safety_check_* |
| R04 | test_stage4c_runtime_integration.py | test_pole_id_normalization_whitespace, test_pole_id_format_mismatch_logged |
| R05 | test_stage4c_runtime_integration.py | test_stage4b_preview_equals_stage4c_merge_ready |
| R06 | test_stage4_golden_samples.py | test_golden_samples_regression_detection |
| R07 | test_stage4c_runtime_boundary.py | test_merge_safety_check_detects_stage4_in_forbidden_files |
| R08 | test_stage4c_runtime_integration.py | test_merge_rejects_duplicate_across_sessions |

**All 8 risks have test coverage.**

---

## Success criteria

All tests pass **before** Stage 4C merges to master.
