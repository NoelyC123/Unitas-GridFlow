"""Phase 3F — context / crossing linkage."""

from __future__ import annotations

from app.context_crossing import (
    CONTEXT_TYPES,
    assess_crossing_risk,
    context_profile_for_structure,
    enrich_context_crossing_records,
    is_crossing_context_record,
)


def test_context_types_has_road() -> None:
    assert "road" in CONTEXT_TYPES


def test_is_crossing_context_record_by_role() -> None:
    assert is_crossing_context_record({"record_role": "context", "structure_type": "foo"})


def test_is_crossing_context_record_by_structure() -> None:
    assert is_crossing_context_record({"record_role": "", "structure_type": "11xing"})


def test_is_crossing_context_negative() -> None:
    assert not is_crossing_context_record({"record_role": "structural", "structure_type": "EXpole"})


def test_context_profile_road() -> None:
    p = context_profile_for_structure("Public road crossing")
    assert p["context_kind"] == "road"
    assert "Highway" in p["owner"] or "authority" in p["owner"]


def test_context_profile_unknown() -> None:
    p = context_profile_for_structure("")
    assert p["context_kind"] == "unknown"


def test_assess_crossing_high_tier() -> None:
    ctx = {
        "structure_type": "road",
        "clearance_measured": None,
        "span_crossing_links": [{"crossing_tier": "high"}],
    }
    r = assess_crossing_risk(ctx, None)
    assert r["risk_level"] == "high"
    assert r["designer_action"]


def test_assess_crossing_measured_ok() -> None:
    ctx = {
        "structure_type": "road",
        "clearance_measured": 6.0,
        "span_crossing_links": [{"crossing_tier": "medium"}],
    }
    r = assess_crossing_risk(ctx, None)
    assert r["clearance_measured_m"] == 6.0


def test_enrich_context_reverse_links() -> None:
    data = {
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0, 0]},
                "properties": {"pole_id": "C1", "record_role": "context", "structure_type": "road"},
            },
        ],
        "span_features": [
            {
                "type": "Feature",
                "properties": {
                    "from_point_id": "A",
                    "to_point_id": "B",
                    "crossing_risk_level": "high",
                    "crossing_hits_survey": [
                        {"point_id": "C1", "distance_m": 12.0, "crossing_tier": "high"},
                    ],
                },
            },
        ],
    }
    enrich_context_crossing_records(data)
    props = data["features"][0]["properties"]
    assert len(props["span_crossing_links"]) == 1
    assert props["context_type_profile"]["context_kind"] == "road"
    assert props["context_crossing_assessment"]["risk_level"] == "high"
    assert data["metadata"]["context_crossing_phase3f_count"] == 1


def test_enrich_context_skips_structural() -> None:
    data = {
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0, 0]},
                "properties": {"pole_id": "P1", "structure_type": "EXpole"},
            },
        ],
        "span_features": [],
        "metadata": {},
    }
    enrich_context_crossing_records(data)
    assert data["metadata"]["context_crossing_phase3f_count"] == 0
