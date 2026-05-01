"""Phase 3G — replacement pair confidence."""

from __future__ import annotations

from app.replacement_pairs import (
    REPLACEMENT_MATCH_TYPES,
    calculate_replacement_confidence,
    enrich_replacement_pair_intelligence,
)


def test_match_types_non_empty() -> None:
    assert "direct_replacement" in REPLACEMENT_MATCH_TYPES


def test_confidence_direct_offset() -> None:
    ex = {"pole_id": "1", "height": 9.0, "pole_class": "Class 4", "material": "timber"}
    pr = {"pole_id": "2", "height": 9.1, "pole_class": "Class 4", "material": "timber"}
    out = calculate_replacement_confidence(ex, pr, 0.2)
    assert out["match_type"] == "direct_replacement"
    assert out["confidence_pct"] >= 70


def test_confidence_wide_offset() -> None:
    ex = {"pole_id": "1", "height": 9.0}
    pr = {"pole_id": "2", "height": 12.0}
    out = calculate_replacement_confidence(ex, pr, 25.0)
    assert out["match_type"] == "repositioned"
    assert "offset_band" in out["factors"]


def test_confidence_no_offset() -> None:
    ex = {"pole_id": "1"}
    pr = {"pole_id": "2"}
    out = calculate_replacement_confidence(ex, pr, None)
    assert out["confidence_pct"] >= 0


def test_enrich_pair_on_both_poles() -> None:
    data = {
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [1, 1]},
                "properties": {
                    "pole_id": "EX1",
                    "structure_type": "EXpole",
                    "being_replaced_by": "PR1",
                    "match_offset_m": 0.3,
                    "height": 8.0,
                    "pole_class": "4",
                },
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [1, 1]},
                "properties": {
                    "pole_id": "PR1",
                    "structure_type": "PRpole",
                    "replacing": "EX1",
                    "match_offset_m": 0.3,
                    "height": 8.0,
                    "pole_class": "4",
                },
            },
        ],
        "metadata": {},
    }
    enrich_replacement_pair_intelligence(data)
    ex_p = data["features"][0]["properties"]
    pr_p = data["features"][1]["properties"]
    assert ex_p["replacement_pair_audit"]["pair_id"] == "EX1_PR1"
    assert (
        pr_p["replacement_pair_audit"]["confidence_pct"]
        == ex_p["replacement_pair_audit"]["confidence_pct"]
    )
    assert data["metadata"]["replacement_pair_audit_count"] == 1


def test_enrich_skips_unpaired() -> None:
    data = {
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0, 0]},
                "properties": {"pole_id": "A", "structure_type": "EXpole"},
            },
        ],
        "metadata": {},
    }
    enrich_replacement_pair_intelligence(data)
    assert data["metadata"]["replacement_pair_audit_count"] == 0
