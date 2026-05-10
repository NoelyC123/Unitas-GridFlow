"""Tests for the Stage 4 structured capture schema."""

from __future__ import annotations

import pytest

from app.structured_capture_schema import (
    CURRENT_STATUS,
    GROUPS,
    SOURCE,
    get_stage4_field_definition,
    get_stage4_fields,
    get_stage4_fields_by_group,
    get_stage4_required_fields,
    get_stage4_template_headers,
    is_stage4_field,
)

EXPECTED_GROUPS = {
    "row_identity",
    "pole_specification",
    "condition_defects",
    "electrical_conductor",
    "structural_support",
    "equipment_pole_top",
    "capture_metadata",
}

EXPECTED_FIELDS = {
    # row identity
    "pole_id",
    "project_id",
    "file_id",
    "structure_type",
    "asset_intent",
    # pole specification
    "material",
    "pole_class",
    "pole_strength",
    "pole_material",
    "measured_height_m",
    "height_source",
    "specification",
    # condition / defects
    "condition",
    "defect_type",
    "defect_severity",
    "defect_notes",
    "access_notes",
    "survey_notes",
    # electrical / conductor
    "voltage_carried",
    "conductor_type",
    "conductor_size",
    "phase_configuration",
    # structural support
    "stay_present",
    "stay_required",
    "stay_type",
    "stay_condition",
    "lean_direction",
    "lean_severity",
    # equipment
    "equipment_present",
    "equipment_type",
    "equipment_condition",
    "equipment_notes",
    # capture metadata
    "capture_source",
    "source",
    "evidence_status",
    "photo_reference",
    "captured_by",
    "capture_date",
    "confidence_level",
    "verification_required",
}


def test_all_expected_groups_exist() -> None:
    assert set(GROUPS.keys()) == EXPECTED_GROUPS


def test_all_expected_fields_exist() -> None:
    actual = {definition["field_name"] for definition in get_stage4_fields()}
    missing = EXPECTED_FIELDS - actual
    assert not missing, f"Missing Stage 4 fields: {sorted(missing)}"


def test_template_headers_include_key_fields() -> None:
    headers = get_stage4_template_headers()
    for key in (
        "pole_class",
        "structure_type",
        "asset_intent",
        "measured_height_m",
        "height_source",
        "material",
        "condition",
        "voltage_carried",
        "stay_present",
        "stay_required",
        "equipment_type",
        "capture_source",
        "source",
        "evidence_status",
        "captured_by",
        "capture_date",
    ):
        assert key in headers, f"{key} missing from template headers"
    assert headers[:5] == ["pole_id", "project_id", "file_id", "structure_type", "asset_intent"]
    # headers must be unique and stable
    assert len(headers) == len(set(headers))


def test_required_fields_returned() -> None:
    required = get_stage4_required_fields()
    assert "pole_id" in required
    assert "capture_source" in required
    assert "captured_by" in required
    assert "capture_date" in required
    # asset fields should remain optional in the foundation
    assert "condition" not in required
    assert "voltage_carried" not in required


def test_get_fields_by_group_works() -> None:
    identity = {d["field_name"] for d in get_stage4_fields_by_group("row_identity")}
    assert {"pole_id", "project_id", "file_id", "structure_type", "asset_intent"} <= identity

    pole_spec = {d["field_name"] for d in get_stage4_fields_by_group("pole_specification")}
    assert {
        "material",
        "pole_class",
        "pole_strength",
        "pole_material",
        "measured_height_m",
        "height_source",
        "specification",
    } <= pole_spec

    metadata = {d["field_name"] for d in get_stage4_fields_by_group("capture_metadata")}
    assert {
        "capture_source",
        "source",
        "evidence_status",
        "photo_reference",
        "captured_by",
        "capture_date",
    } <= metadata

    with pytest.raises(ValueError):
        get_stage4_fields_by_group("not_a_real_group")


def test_aliases_resolve() -> None:
    # canonical and alias both resolve via is_stage4_field / get_definition
    assert is_stage4_field("pole_class")
    assert is_stage4_field("class")  # alias for pole_class
    assert is_stage4_field("Point")  # alias for pole_id
    assert is_stage4_field("voltage")  # alias for voltage_carried
    assert not is_stage4_field("totally_invented_field")

    by_alias = get_stage4_field_definition("voltage")
    assert by_alias is not None
    assert by_alias["field_name"] == "voltage_carried"

    case_alias = get_stage4_field_definition("Has_Stay")
    assert case_alias is not None
    assert case_alias["field_name"] == "stay_present"

    pole_alias = get_stage4_field_definition("support_id")
    assert pole_alias is not None
    assert pole_alias["field_name"] == "pole_id"


def test_all_fields_have_stage4_future_capture_status() -> None:
    for definition in get_stage4_fields():
        assert definition["current_status"] == CURRENT_STATUS == "stage4_future_capture"


def test_all_fields_have_structured_capture_source() -> None:
    for definition in get_stage4_fields():
        assert definition["source"] == SOURCE == "structured_capture"
