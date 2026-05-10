"""Tests for the Stage 4 structured-capture validators."""

from __future__ import annotations

from app.structured_capture_validators import (
    classify_stage4_completeness,
    extract_stage4_row_identity,
    field_allows_explicit_none,
    is_blank,
    is_blank_for_field,
    normalise_bool,
    normalise_stage4_row,
    validate_allowed_value,
    validate_required_fields,
    validate_stage4_row,
    validate_stage4_rows,
)

VALID_REQUIRED = {
    "pole_id": "P008-001",
    "capture_source": "office_audit",
    "captured_by": "N. Collins",
    "capture_date": "2026-05-09",
}


def test_blank_detection() -> None:
    assert is_blank(None)
    assert is_blank("")
    assert is_blank("   ")
    assert is_blank("N/A")
    assert is_blank("?")
    assert is_blank("tbc")
    assert not is_blank("none")
    assert not is_blank("good")
    assert not is_blank(0)  # numeric zero is a real value


def test_none_is_field_aware_not_globally_destructive() -> None:
    assert not is_blank_for_field("stay_type", "none")
    assert not is_blank_for_field("equipment_type", "none")
    assert not is_blank_for_field("lean_direction", "none")
    assert not is_blank_for_field("lean_severity", "none")
    assert not is_blank_for_field("condition", "none")
    assert field_allows_explicit_none("stay_type")
    assert field_allows_explicit_none("equipment_type")
    assert not field_allows_explicit_none("condition")


def test_bool_normalisation_yes_no_unknown() -> None:
    assert normalise_bool("yes") == "yes"
    assert normalise_bool("Y") == "yes"
    assert normalise_bool("TRUE") == "yes"
    assert normalise_bool("1") == "yes"
    assert normalise_bool("no") == "no"
    assert normalise_bool("FALSE") == "no"
    assert normalise_bool("0") == "no"
    assert normalise_bool("unknown") == "unknown"
    assert normalise_bool(None) == "unknown"
    assert normalise_bool("") == "unknown"
    assert normalise_bool("garbage") == "unknown"


def test_allowed_value_validation_passes_for_valid_values() -> None:
    result = validate_allowed_value("condition", "good")
    assert result["valid"]
    assert result["normalised"]["condition"] == "good"

    # case-insensitive and preserves canonical voltage casing
    result = validate_allowed_value("voltage_carried", "11kv")
    assert result["valid"]
    assert result["normalised"]["voltage_carried"] == "11kV"

    # alias resolves to canonical name
    result = validate_allowed_value("voltage", "LV")
    assert result["valid"]
    assert result["normalised"]["voltage_carried"] == "LV"

    for field_name in ("stay_type", "equipment_type", "lean_direction", "lean_severity"):
        result = validate_allowed_value(field_name, "none")
        assert result["valid"], result["errors"]
        assert result["normalised"][field_name] == "none"


def test_allowed_value_validation_rejects_invalid_values() -> None:
    result = validate_allowed_value("condition", "excellent")
    assert not result["valid"]
    assert any("condition" in err for err in result["errors"])

    # unknown field is itself an error
    bad_field = validate_allowed_value("not_a_field", "anything")
    assert not bad_field["valid"]

    none_not_allowed = validate_allowed_value("condition", "none")
    assert not none_not_allowed["valid"]
    assert "condition" in none_not_allowed["errors"][0]

    bool_none = validate_allowed_value("stay_present", "none")
    assert not bool_none["valid"]


def test_required_field_validation() -> None:
    missing_all = validate_required_fields({})
    assert not missing_all["valid"]
    assert len(missing_all["errors"]) >= 3  # at least the three required fields

    full = validate_required_fields(VALID_REQUIRED)
    assert full["valid"]
    assert full["errors"] == []


def test_row_validation_returns_valid_false_with_errors() -> None:
    row = {**VALID_REQUIRED, "condition": "atrocious"}  # invalid enum
    result = validate_stage4_row(row)
    assert not result["valid"]
    assert any("condition" in err for err in result["errors"])


def test_row_validation_returns_valid_true_for_valid_row() -> None:
    row = {
        **VALID_REQUIRED,
        "condition": "good",
        "voltage_carried": "11kV",
        "stay_present": "yes",
        "equipment_present": "no",
        "confidence_level": "high",
    }
    result = validate_stage4_row(row)
    assert result["valid"], result["errors"]
    assert result["normalised"]["voltage_carried"] == "11kV"
    assert result["normalised"]["stay_present"] == "yes"
    assert result["pole_id"] == "P008-001"
    assert result["row_id"] == "P008-001"
    assert result["merge_ready"] is True
    assert result["source"] == "structured_capture"


def test_completeness_classification() -> None:
    assert classify_stage4_completeness({}) == "empty"
    assert classify_stage4_completeness({"condition": "good"}) == "partial"
    assert classify_stage4_completeness(VALID_REQUIRED) == "minimum"

    rich = {
        **VALID_REQUIRED,
        "pole_class": "medium",
        "pole_material": "wood",
        "condition": "fair",
        "defect_type": "split",
        "defect_severity": "medium",
        "voltage_carried": "11kV",
        "conductor_type": "covered",
        "phase_configuration": "three",
        "stay_present": "yes",
        "stay_type": "down",
        "stay_condition": "good",
        "equipment_present": "no",
        "confidence_level": "medium",
    }
    assert classify_stage4_completeness(rich) == "complete"


def test_normalise_row_lowercases_and_standardises() -> None:
    row = {
        **VALID_REQUIRED,
        "condition": "  GOOD ",
        "voltage_carried": "11kv",
        "stay_present": "Y",
        "equipment_present": "FALSE",
        "captured_by": "  N. Collins  ",  # free text gets stripped
    }
    normalised = normalise_stage4_row(row)
    assert normalised["condition"] == "good"
    assert normalised["voltage_carried"] == "11kV"
    assert normalised["stay_present"] == "yes"
    assert normalised["equipment_present"] == "no"
    assert normalised["captured_by"] == "N. Collins"


def test_unknown_optional_fields_do_not_crash() -> None:
    row = {
        **VALID_REQUIRED,
        "made_up_column": "something",
        "another_unknown": 42,
    }
    result = validate_stage4_row(row)
    assert result["valid"], result["errors"]
    assert any("Unknown Stage 4 columns" in w for w in result["warnings"])

    # rows-level validation also tolerates unknown columns
    rows_result = validate_stage4_rows([row, {**VALID_REQUIRED, "pole_id": "P008-002"}])
    assert rows_result["valid"]
    assert len(rows_result["row_results"]) == 2


def test_row_identity_extraction_accepts_pole_id_aliases() -> None:
    row = {
        "Point": "P010-123",
        "capture_source": "office_audit",
        "captured_by": "N. Collins",
        "capture_date": "2026-05-09",
        "project_id": "P010",
        "file_id": "F001",
    }
    identity = extract_stage4_row_identity(row)
    assert identity["valid"]
    assert identity["pole_id"] == "P010-123"
    assert identity["row_id"] == "P010/F001/P010-123"
    assert identity["merge_ready"] is True


def test_missing_pole_id_is_detected_and_not_merge_ready() -> None:
    row = {k: v for k, v in VALID_REQUIRED.items() if k != "pole_id"}
    result = validate_stage4_row(row)
    assert not result["valid"]
    assert result["invalid"]
    assert result["merge_ready"] is False
    assert result["pole_id"] is None
    assert any("pole_id" in err for err in result["errors"])
    assert any(fr["field_name"] == "pole_id" and fr["invalid"] for fr in result["field_results"])


def test_duplicate_pole_id_invalidates_rows_validation() -> None:
    result = validate_stage4_rows([VALID_REQUIRED, {**VALID_REQUIRED, "condition": "good"}])
    assert not result["valid"]
    assert any("Duplicate pole_id" in err for err in result["errors"])
    assert not result["row_results"][0]["merge_ready"]
    assert not result["row_results"][1]["merge_ready"]


def test_validation_result_model_contains_per_field_provenance() -> None:
    result = validate_stage4_row({**VALID_REQUIRED, "stay_type": "none"})
    assert result["valid"], result["errors"]
    field = next(fr for fr in result["field_results"] if fr["field_name"] == "stay_type")
    assert field["valid"]
    assert field["invalid"] is False
    assert field["value"] == "none"
    assert field["source"] == "structured_capture"
    assert field["pole_id"] == "P008-001"
