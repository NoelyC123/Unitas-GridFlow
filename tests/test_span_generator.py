"""Tests for GeoJSON span (LineString) generation."""

from __future__ import annotations

from app.span_generator import (
    attach_span_features_to_collection,
    build_span_feature,
    coalesce_electrical_source,
    derive_designer_actions_for_span,
    distance_point_to_segment_m,
    generate_span_features_geojson,
    haversine_distance_m,
    index_point_features_by_pole_id,
)


def test_haversine_distance_london_scale() -> None:
    d = haversine_distance_m(54.521, -3.014, 54.522, -3.013)
    assert 100 <= d <= 200


def test_index_point_features_by_pole_id() -> None:
    feats = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.0, 54.0]},
            "properties": {"pole_id": "A"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": [[-3, 54], [-3.1, 54.1]]},
            "properties": {"pole_id": "X"},
        },
    ]
    idx = index_point_features_by_pole_id(feats)
    assert set(idx.keys()) == {"A"}


def test_coalesce_electrical_prefers_from_then_to() -> None:
    from_p = {"voltage": "11kV", "conductor_type": "ACSR"}
    to_p = {"voltage": "33kV", "phase_count": "3-phase"}
    m = coalesce_electrical_source(from_p, to_p, "SPEN_11kV")
    assert m["voltage"] == "11kV"
    assert m["conductor_type"] == "ACSR"
    assert m["phase_count"] == "3-phase"


def test_generate_span_features_geojson_skips_bad_sequence() -> None:
    assert generate_span_features_geojson([], {"status": "error"}, {}) == []
    assert generate_span_features_geojson([], {"status": "ok", "chain": []}, {}) == []


def test_generate_span_features_from_chain() -> None:
    point_features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.014, 54.521]},
            "properties": {
                "pole_id": "P-1001",
                "voltage": "11kV",
                "conductor_type": "AAC",
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.013, 54.522]},
            "properties": {"pole_id": "P-1002", "phase_count": "3-phase"},
        },
    ]
    seq = {
        "status": "ok",
        "chain": [
            {
                "point_id": "P-1001",
                "lat": 54.521,
                "lon": -3.014,
                "span_to_next_m": 75.0,
                "design_pole_number": 1,
                "section_id": "S1",
            },
            {
                "point_id": "P-1002",
                "lat": 54.522,
                "lon": -3.013,
                "design_pole_number": 2,
            },
        ],
    }
    spans = generate_span_features_geojson(point_features, seq, {"rulepack_id": "SPEN_11kV"})
    assert len(spans) == 1
    assert spans[0]["geometry"]["type"] == "LineString"
    assert spans[0]["geometry"]["coordinates"] == [[-3.014, 54.521], [-3.013, 54.522]]
    prop = spans[0]["properties"]
    assert prop["from_point_id"] == "P-1001"
    assert prop["to_point_id"] == "P-1002"
    assert prop["distance_m"] == 75.0
    assert prop.get("voltage_detail")


def test_attach_span_features_to_collection_mutates() -> None:
    fc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-3.014, 54.521]},
                "properties": {"pole_id": "P1", "voltage": "11kV"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-3.013, 54.522]},
                "properties": {"pole_id": "P2"},
            },
        ],
        "metadata": {"rulepack_id": "SPEN_11kV"},
    }
    seq = {
        "status": "ok",
        "chain": [
            {"point_id": "P1", "lat": 54.521, "lon": -3.014, "span_to_next_m": 10},
            {"point_id": "P2", "lat": 54.522, "lon": -3.013},
        ],
    }
    attach_span_features_to_collection(fc, seq)
    assert fc["metadata"]["span_feature_count"] == 1
    assert len(fc["span_features"]) == 1


def test_distance_point_to_segment_midpoint_zero() -> None:
    d = distance_point_to_segment_m(54.521, -3.014, 54.521, -3.014, 54.522, -3.013)
    assert d < 1.0


def test_crossing_risk_blocker_when_road_context_on_span() -> None:
    point_features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.014, 54.521]},
            "properties": {"pole_id": "P-1001", "voltage": "11kV"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.013, 54.522]},
            "properties": {"pole_id": "P-1002"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.0135, 54.5215]},
            "properties": {
                "pole_id": "CTX-R1",
                "structure_type": "Road",
                "record_role": "context",
            },
        },
    ]
    seq = {
        "status": "ok",
        "chain": [
            {
                "point_id": "P-1001",
                "lat": 54.521,
                "lon": -3.014,
                "span_to_next_m": 75.0,
                "design_pole_number": 1,
                "section_id": "S1",
            },
            {
                "point_id": "P-1002",
                "lat": 54.522,
                "lon": -3.013,
                "design_pole_number": 2,
            },
        ],
    }
    spans = generate_span_features_geojson(point_features, seq, {"rulepack_id": "SPEN_11kV"})
    assert len(spans) == 1
    prop = spans[0]["properties"]
    assert prop["crossing_risk_level"] == "BLOCKER"
    assert prop["design_status"] == "BLOCKED"
    assert prop["span_sequence_label"] == "1 of 1"
    assert len(prop["crossing_hits_survey"]) >= 1


def test_span_sequence_adjacent_links() -> None:
    point_features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.02, 54.51]},
            "properties": {"pole_id": "A"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.019, 54.511]},
            "properties": {"pole_id": "B"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.018, 54.512]},
            "properties": {"pole_id": "C"},
        },
    ]
    seq = {
        "status": "ok",
        "chain": [
            {"point_id": "A", "lat": 54.51, "lon": -3.02, "span_to_next_m": 50},
            {"point_id": "B", "lat": 54.511, "lon": -3.019, "span_to_next_m": 50},
            {"point_id": "C", "lat": 54.512, "lon": -3.018},
        ],
    }
    spans = generate_span_features_geojson(point_features, seq, {})
    assert len(spans) == 2
    first = spans[0]["properties"]
    assert "previous_span" not in first
    assert first["next_span"]["from_point_id"] == "B"
    mid = spans[1]["properties"]
    assert mid["previous_span"]["to_point_id"] == "B"
    assert "next_span" not in mid


def test_derive_designer_actions_includes_voltage_gap() -> None:
    acts = derive_designer_actions_for_span(
        {"crossing_risk_level": "none", "is_underground": False}
    )
    assert any("voltage" in a.lower() for a in acts)


def test_attach_span_features_sets_crossing_counts() -> None:
    point_features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.014, 54.521]},
            "properties": {"pole_id": "P1"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.0135, 54.5215]},
            "properties": {"pole_id": "R1", "structure_type": "Road", "record_role": "context"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.013, 54.522]},
            "properties": {"pole_id": "P2"},
        },
    ]
    fc = {
        "type": "FeatureCollection",
        "features": point_features,
        "metadata": {"rulepack_id": "SPEN_11kV"},
    }
    seq = {
        "status": "ok",
        "chain": [
            {"point_id": "P1", "lat": 54.521, "lon": -3.014, "span_to_next_m": 70},
            {"point_id": "P2", "lat": 54.522, "lon": -3.013},
        ],
    }
    attach_span_features_to_collection(fc, seq)
    assert fc["metadata"]["span_crossing_high_count"] >= 1


def test_derive_designer_actions_long_span() -> None:
    acts = derive_designer_actions_for_span(
        {"crossing_risk_level": "none", "is_underground": True, "distance_m": 300},
    )
    assert any("Long span" in a for a in acts)


def test_distance_point_to_segment_far_from_line() -> None:
    d = distance_point_to_segment_m(54.53, -3.0, 54.521, -3.014, 54.522, -3.013)
    assert d > 500


def test_build_span_feature_computes_distance_when_missing() -> None:
    feat = build_span_feature(
        "A",
        "B",
        -3.014,
        54.521,
        -3.013,
        54.522,
        {"voltage": "LV"},
        {},
        rulepack_id=None,
        distance_m=None,
        span_index=0,
    )
    assert feat["properties"]["distance_m"] > 0
    assert feat["geometry"]["coordinates"][0] == [-3.014, 54.521]
