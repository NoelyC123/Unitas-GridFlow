"""Phase 3E — pole / support canonical fields."""

from __future__ import annotations

from app.pole_field_schema import (
    C2D_PRIORITY_FIELD_INVENTORY,
    enrich_pole_support_props,
    field_groups_for_role,
    infer_support_schema_role,
    popup_priority_field_catalog,
    popup_priority_fields_for_role,
    validate_support_field_coverage,
)


def test_infer_role_context() -> None:
    assert (
        infer_support_schema_role({"record_role": "context", "structure_type": "road"}) == "context"
    )


def test_infer_role_stay() -> None:
    assert infer_support_schema_role({"record_role": "anchor", "structure_type": "stay"}) == "stay"


def test_infer_role_angle() -> None:
    assert infer_support_schema_role({"structure_type": "11kVangle"}) == "angle"


def test_infer_role_proposed() -> None:
    assert (
        infer_support_schema_role({"structure_type": "PRpole", "asset_intent": "proposed"})
        == "proposed"
    )


def test_infer_role_existing_expole() -> None:
    assert (
        infer_support_schema_role({"structure_type": "EXpole", "asset_intent": "existing"})
        == "existing"
    )


def test_infer_role_third_party() -> None:
    assert (
        infer_support_schema_role({"primary_type": "third_party_infrastructure"}) == "third_party"
    )


def test_enrich_point_id_and_measured_height() -> None:
    props = {"pole_id": "12", "height": 9.2, "structure_type": "EXpole"}
    enrich_pole_support_props(props)
    assert props["point_id"] == "12"
    assert props["measured_height_m"] == 9.2
    assert props["support_schema_role"] == "existing"


def test_enrich_proposed_height() -> None:
    props = {"pole_id": "13", "height": 10.0, "structure_type": "PRpole"}
    enrich_pole_support_props(props)
    assert props["proposed_height_m"] == 10.0
    assert props.get("measured_height_m") is None


def test_enrich_replacement_linkage() -> None:
    props = {"pole_id": "A", "structure_type": "EXpole", "being_replaced_by": "B", "height": 8.0}
    enrich_pole_support_props(props)
    assert props["replacement_status"] == "being_replaced"
    assert props["linked_support_id"] == "B"


def test_field_groups_existing_includes_existing_block() -> None:
    groups = field_groups_for_role("existing")
    assert len(groups) == 2


def test_validate_existing_missing_height() -> None:
    props = {"support_schema_role": "existing", "pole_id": "1"}
    assert "existing_pole_height_missing" in validate_support_field_coverage(props)


def test_validate_stay_missing_parent() -> None:
    props = {"support_schema_role": "stay", "pole_id": "S1", "structure_type": "stay"}
    assert "stay_parent_missing" in validate_support_field_coverage(props)


def test_field_groups_proposed_is_universal_plus_proposed() -> None:
    groups = field_groups_for_role("proposed")
    assert len(groups) == 2


def test_enrich_independent_replacement_status() -> None:
    props = {"pole_id": "Z", "structure_type": "EXpole", "height": 8.0}
    enrich_pole_support_props(props)
    assert props.get("replacement_status") == "independent"


def test_validate_proposed_height_gap() -> None:
    props = {"support_schema_role": "proposed", "pole_id": "p1"}
    assert "proposed_height_missing" in validate_support_field_coverage(props)


def test_c2d_priority_inventory_declares_span_owned_electrical_fields() -> None:
    fields = {item["field"]: item for item in C2D_PRIORITY_FIELD_INVENTORY}

    assert len(fields) >= 15
    assert fields["pole_class"]["source_status"] == "present_displayable_controller_alias"
    assert fields["voltage_carried"]["display_owner"] == "span_or_cable"
    assert fields["conductor_cable_type"]["display_owner"] == "span_or_cable"
    assert "network_voltage" in fields["voltage_carried"]["display_fields"]
    assert "wayleave_notes" in fields["action_access_wayleave"]["display_fields"]


def test_popup_priority_fields_for_existing_role_have_labels_and_groups() -> None:
    fields = {item["field"]: item for item in popup_priority_fields_for_role("existing")}

    assert fields["pole_class"]["display_label"] == "Pole class / strength"
    assert fields["pole_class"]["popup_group"] == "Physical evidence"
    assert fields["equipment_presence"]["popup_group"] == "Equipment & pole-top"
    assert fields["action_access_wayleave"]["popup_group"] == "Design requirements"
    assert "voltage_carried" not in fields


def test_popup_priority_field_catalog_exposes_proposed_section_order() -> None:
    catalog = popup_priority_field_catalog()
    proposed = catalog["roles"]["proposed"]

    assert proposed["section_order"] == [
        "Specification",
        "Design requirements",
        "Equipment & pole-top",
        "Survey metadata and evidence",
    ]
    assert any(
        item["field"] == "measured_design_height" and item["popup_group"] == "Specification"
        for item in proposed["fields"]
    )


def test_popup_priority_field_catalog_is_complete_for_existing_proposed_and_context() -> None:
    catalog = popup_priority_field_catalog()

    for role in ("existing", "proposed", "context"):
        assert len(catalog["roles"][role]["fields"]) == len(C2D_PRIORITY_FIELD_INVENTORY)


def test_popup_priority_field_catalog_marks_context_hidden_and_conditional_fields() -> None:
    catalog = popup_priority_field_catalog()
    context_fields = {item["field"]: item for item in catalog["roles"]["context"]["fields"]}

    assert context_fields["pole_class"]["visibility"] == "hidden"
    assert context_fields["pole_class"]["hidden_reason"] == "Hidden for context records."
    assert context_fields["measured_design_height"]["visibility"] == "conditional"
    assert context_fields["measured_design_height"]["popup_group"] == "Crossing details"
    assert (
        context_fields["measured_design_height"]["missing_value_text"]
        == "not measured in current export"
    )
    assert context_fields["survey_metadata"]["visibility"] == "visible"


def test_popup_priority_field_catalog_marks_span_owned_fields_hidden_on_proposed() -> None:
    catalog = popup_priority_field_catalog()
    proposed_fields = {item["field"]: item for item in catalog["roles"]["proposed"]["fields"]}

    assert proposed_fields["voltage_carried"]["visibility"] == "hidden"
    assert "field-ownership policy" in (proposed_fields["voltage_carried"]["hidden_reason"] or "")
    assert proposed_fields["lean"]["visibility"] == "conditional"
    assert proposed_fields["lean"]["missing_value_text"] == "not applicable yet"
