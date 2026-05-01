"""Phase 3E — pole / support canonical fields."""

from __future__ import annotations

from app.pole_field_schema import (
    enrich_pole_support_props,
    field_groups_for_role,
    infer_support_schema_role,
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
