"""Tests for GeoJSON span (LineString) generation."""

from __future__ import annotations

from app.span_generator import (
    attach_span_features_to_collection,
    build_span_feature,
    coalesce_electrical_source,
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
