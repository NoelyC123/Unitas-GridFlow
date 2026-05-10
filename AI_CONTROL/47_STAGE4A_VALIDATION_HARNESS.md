# 47 — Stage 4A Validation Harness

Companion to: [46_STAGE4A_SAFETY_AUDIT.md](46_STAGE4A_SAFETY_AUDIT.md)
Snapshot: master HEAD `857861e`, date 2026-05-10.

## Purpose

This document describes every test that Codex must satisfy to clear the
Stage 4A merge gate. It is structured as a checklist that can be verified
mechanically by running pytest.

---

## Harness Test Files

| File | Status on master | Purpose |
|------|-----------------|---------|
| `tests/test_stage4a_safety_boundary.py` | New (this branch) | VLD-1/2/3 xfail + library isolation |
| `tests/test_structured_capture_leakage.py` | New (this branch) | Runtime leakage guards |
| `tests/test_structured_capture_validators.py` | Existing | Baseline validator behaviour |
| `tests/test_structured_capture_schema.py` | Existing | Baseline schema behaviour |
| `tests/test_generate_structured_capture_template.py` | Existing | Template generation |
| `tests/test_c2e2_popup_fields.py` | Existing | C2E2 field reference guard |
| `tests/test_c2e2_popup_rendering.py` | Existing | Popup rendering regression guard |

---

## What Codex Must Prove

### VLD-1: `none` blank-token fix

Codex must make every test in `TestVLD1*` pass by removing `"none"` from
`_BLANK_TOKENS` in `app/structured_capture_validators.py`.

Required test outcomes after fix:

| Test | Expected after fix |
|------|--------------------|
| `test_vld1_none_is_not_blank` | PASS (was xfail) |
| `test_vld1_stay_type_none_is_valid_enum` | PASS (was xfail) |
| `test_vld1_equipment_type_none_is_valid_enum` | PASS (was xfail) |
| `test_vld1_lean_direction_none_is_valid_enum` | PASS (was xfail) |
| `test_vld1_lean_severity_none_is_valid_enum` | PASS (was xfail) |
| `test_vld1_completeness_does_not_erase_none_enum_values` | PASS (was xfail) |
| `test_vld1_none_case_variants_treated_as_enum_for_allowed_field` | PASS (was xfail) |

Regression guard (must still pass after fix):

| Test | Must still be |
|------|--------------|
| `test_vld1_condition_does_not_allow_none_as_valid_enum` | PASS |
| `test_true_blank_tokens_remain_blank_after_vld1_fix[*]` | PASS (11 parametrized cases) |

**Acceptance criteria for VLD-1:** `is_blank("none")` returns `False`. The four
fields that declare `"none"` as an enum member accept it and normalise it to the
string `"none"`. Fields that do not declare `"none"` (e.g. `condition`) continue
to reject it.

---

### VLD-2: `pole_id` row identity fix

Codex must add `pole_id` to the Stage 4 schema and template, making every
`test_vld2_*` test pass.

Required test outcomes after fix:

| Test | Expected after fix |
|------|--------------------|
| `test_vld2_pole_id_field_exists_in_schema` | PASS (was xfail) |
| `test_vld2_pole_id_in_template_headers` | PASS (was xfail) |
| `test_vld2_missing_pole_id_fails_required_field_check` | PASS (was xfail) |
| `test_vld2_blank_or_unknown_pole_id_is_rejected[*]` | PASS (7 parametrized cases, was xfail) |

**Acceptance criteria for VLD-2:** `get_stage4_field_definition("pole_id")`
returns a definition. `pole_id` appears in `get_stage4_template_headers()` and
in the generated template CSV. `validate_required_fields` rejects rows without
`pole_id`. Blank tokens (`""`, `"n/a"`, `"unknown"`) are rejected as `pole_id`
values.

---

### VLD-3: `structured_capture` source registration

Codex must register `"structured_capture"` as a source label in
`app/field_reference.py`, making `test_vld3_structured_capture_registered_as_source`
pass.

Required test outcomes after fix:

| Test | Expected after fix |
|------|--------------------|
| `test_vld3_structured_capture_registered_as_source` | PASS (was xfail) |

Regression guard (must still pass after fix):

| Test | Must still be |
|------|--------------|
| `test_vld3_existing_source_labels_unchanged` | PASS |
| `TestFieldReferenceLeakage::test_live_field_source_labels_are_known_set` | Update to allow `structured_capture` |
| `TestFieldReferenceLeakage::test_structured_capture_not_in_live_source_labels` | Update per VLD-3 fix notes |

**Acceptance criteria for VLD-3:** `structured_capture` is accepted as a source
label in the field reference vocabulary. The existing `survey`, `derived`, and
`trimble_attr` labels are unchanged. No Stage 4 fields appear in
`POPUP_FIELD_GROUPS` or `FIELD_DEFINITIONS`.

---

### Leakage tests (must stay green throughout)

Every test in `test_structured_capture_leakage.py` must pass throughout Stage 4A
and after merge. These tests must not be deleted or weakened.

| Class | Tests |
|-------|-------|
| `TestMapViewerLeakage` | 6 tests — map-viewer.js has no Stage 4 tokens |
| `TestApiIntakeLeakage` | 3 tests — api_intake.py has no Stage 4 wiring |
| `TestQAEngineLeakage` | 2 tests — qa_engine.py has no Stage 4 references |
| `TestControllerIntakeLeakage` | 1 test — controller_intake.py clean |
| `TestC2E2PopupLeakage` | 4 tests — popup groups and field definitions clean |
| `TestFieldReferenceLeakage` | 2 tests (update after VLD-3) |
| `TestReviewOSLeakage` | 1 test — HTML templates clean |

---

### Library isolation tests (must stay green)

| Test | Guards |
|------|--------|
| `test_stage4_library_has_no_runtime_imports[*]` | Stage 4 library files have no Flask/pandas/runtime imports |
| `test_structured_capture_schema_is_stdlib_only` | Schema module uses only stdlib |
| `test_structured_capture_schema_current_status_constant` | All fields carry `stage4_future_capture` |
| `test_structured_capture_schema_source_constant` | All fields carry `structured_capture` |

---

### Identity safety tests (must stay green)

| Test | Guards |
|------|--------|
| `test_non_dict_row_is_rejected` | Non-dict inputs produce clear errors |
| `test_empty_row_is_partial_not_valid` | Empty dict fails required fields |
| `test_required_metadata_blank_tokens_fail` | Blank required fields are rejected |

---

## Full Pytest Run Requirement

Before Stage 4A merges, the following commands must all succeed:

```bash
pytest tests/test_stage4a_safety_boundary.py -v
pytest tests/test_structured_capture_leakage.py -v
pytest tests/test_structured_capture_validators.py -v
pytest tests/test_structured_capture_schema.py -v
pytest tests/test_generate_structured_capture_template.py -v
pytest tests/test_c2e2_popup_fields.py -v
pytest tests/test_c2e2_popup_rendering.py -v
pytest -v   # full suite
pre-commit run --all-files
python scripts/merge_safety_check.py codex/stage4a-library-correctness-fixes
```

---

## Updating This Harness

If Codex needs to change a test assertion to reflect a correct fix, the
change must:

1. Be documented in the PR description with a reason.
2. Not weaken any leakage guard.
3. Not remove any xfail test that was not satisfied by the corresponding fix.
4. Not change `test_c2e2_popup_rendering.py` without a clear popup-regression reason.
