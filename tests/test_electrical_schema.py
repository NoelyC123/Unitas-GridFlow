"""Tests for D2-A conductor/cable display schema helpers."""

from __future__ import annotations

from app.electrical_schema import (
    merge_electrical_fields_into_props,
    merge_equipment_fields_into_props,
    normalize_overhead_conductor_type,
    normalize_phase_config_key,
    normalize_underground_cable_type,
    normalize_voltage_key,
    parse_conductor_data,
    row_suggests_hv_overhead,
)


def test_normalize_voltage_key_common_variants() -> None:
    assert normalize_voltage_key("11kV") == "11kV"
    assert normalize_voltage_key("11 KV") == "11kV"
    assert normalize_voltage_key("11-kV") == "11kV"
    assert normalize_voltage_key("LV") == "LV"
    assert normalize_voltage_key("400V") == "LV"
    assert normalize_voltage_key(None) is None


def test_normalize_overhead_conductor_acsr_aac() -> None:
    assert normalize_overhead_conductor_type("ACSR") == "ACSR"
    assert normalize_overhead_conductor_type("aac 95") == "AAC"
    assert normalize_overhead_conductor_type("copper") == "Cu"


def test_normalize_underground_cable_xlpe() -> None:
    assert normalize_underground_cable_type("XLPE SWA") == "XLPE"
    assert normalize_underground_cable_type("pilc") == "PILC"


def test_normalize_phase_config_aliases() -> None:
    assert normalize_phase_config_key("3 phase") == "3-phase"
    assert normalize_phase_config_key("single_phase") == "single"


def test_parse_overhead_hv_acsr() -> None:
    out = parse_conductor_data(
        {
            "voltage": "11kV",
            "conductor_type": "ACSR",
            "conductor_size": "95mm²",
            "phase_count": "3-phase_no_neutral",
        }
    )
    assert out["is_overhead"] is True
    assert out["is_underground"] is False
    assert out["voltage_detail"].get("label") == "11kV High Voltage"
    assert out["conductor_type_normalized"] == "ACSR"
    assert out["conductor_detail"].get("name") == "Aluminium Conductor Steel Reinforced"
    assert out["conductor_size"] == "95mm²"
    assert out["conductor_size_description"] == "95mm² (LV service/main)"
    assert out["phase_detail"].get("conductors") == 3


def test_parse_underground_suppresses_overhead_conductor() -> None:
    out = parse_conductor_data(
        {
            "voltage": "11kV",
            "cable_type": "XLPE",
            "conductor_size": "185mm²",
            "cores_phases": "3",
        }
    )
    assert out["is_underground"] is True
    assert out["is_overhead"] is False
    assert out["cable_type"] == "XLPE"
    assert out["cable_detail"].get("name") == "Cross-Linked Polyethylene"
    assert out["cable_size"] == "185mm²"
    assert out["conductor_type_normalized"] is None
    assert out["conductor_detail"] == {}


def test_row_suggests_hv_overhead_respects_route_and_voltage() -> None:
    assert row_suggests_hv_overhead({"voltage": "11kV", "route_type": "overhead"}) is True
    assert row_suggests_hv_overhead({"voltage": "11kV", "cable_type": "XLPE"}) is False
    assert row_suggests_hv_overhead({"voltage": "LV"}) is False


def test_merge_electrical_fields_mutates_props() -> None:
    props: dict = {"voltage": "33kV", "conductor": "AAAC"}
    merge_electrical_fields_into_props(props)
    assert props["conductor_type_normalized"] == "AAAC"
    assert props["voltage_detail"]["range"] == "33kV"
    assert props["is_overhead"] is True


def test_network_voltage_alias_parses_for_span_owned_electrical_display() -> None:
    out = parse_conductor_data({"network_voltage": "11kV", "conductor": "AAC"})

    assert out["voltage_detail"]["range"] == "11kV"
    assert out["conductor_type_normalized"] == "AAC"


def test_merge_equipment_fields_parses_kva_and_ratio() -> None:
    props: dict = {
        "equipment": "Transformer",
        "equipment_rating": "11/0.4kV 100 kVA",
        "structure_type": "Pol",
        "pole_top_arrangement": "terminal",
        "insulator_type": "Pin",
        "earthing_status": "TT",
        "asset_plate_id": "TX-001",
        "equipment_mounting": "pole mounted",
    }
    merge_equipment_fields_into_props(props)
    assert props["equipment_kva"] == 100.0
    assert props["equipment_voltage_ratio"] == "11kV / 0.4kV"
    assert props["pole_top_arrangement"] == "terminal"
    assert props["equipment_mounting"] == "pole"
