"""Tests for underground cable LineString generation (Phase 3C)."""

from __future__ import annotations

from app.cable_generator import (
    attach_cable_features_to_collection,
    build_cable_feature,
    collect_directed_cable_edges,
    derive_cable_designer_actions,
    generate_cable_features_geojson,
    index_point_lonlat_by_pole_id,
)


def test_index_point_lonlat() -> None:
    feats = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.0, 54.0]},
            "properties": {"pole_id": "A"},
        }
    ]
    idx = index_point_lonlat_by_pole_id(feats)
    assert idx["A"] == (-3.0, 54.0)


def test_collect_edge_cable_to_only() -> None:
    feats = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.01, 54.0]},
            "properties": {"pole_id": "P1", "cable_to_asset_id": "P2"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.02, 54.0]},
            "properties": {"pole_id": "P2"},
        },
    ]
    edges = collect_directed_cable_edges(feats)
    assert len(edges) == 1
    fr, to, _ = edges[0]
    assert {fr, to} == {"P1", "P2"}


def test_collect_dedup_bidirectional() -> None:
    feats = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.01, 54.0]},
            "properties": {"pole_id": "P1", "cable_to_asset_id": "P2"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.02, 54.0]},
            "properties": {"pole_id": "P2", "cable_to_asset_id": "P1"},
        },
    ]
    edges = collect_directed_cable_edges(feats)
    assert len(edges) == 1


def test_collect_explicit_from_to() -> None:
    feats = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.015, 54.01]},
            "properties": {
                "pole_id": "MID",
                "cable_from_asset_id": "A",
                "cable_to_asset_id": "B",
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.01, 54.0]},
            "properties": {"pole_id": "A"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.02, 54.0]},
            "properties": {"pole_id": "B"},
        },
    ]
    edges = collect_directed_cable_edges(feats)
    assert any({e[0], e[1]} == {"A", "B"} for e in edges)


def test_underground_support_span() -> None:
    feats = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.01, 54.0]},
            "properties": {
                "pole_id": "S1",
                "is_underground": True,
                "from_support_id": "S1",
                "to_support_id": "S2",
                "cable_type": "XLPE",
            },
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.02, 54.0]},
            "properties": {"pole_id": "S2"},
        },
    ]
    cables = generate_cable_features_geojson(feats, {"rulepack_id": "SPEN_11kV"})
    assert len(cables) == 1
    assert cables[0]["geometry"]["type"] == "LineString"
    p = cables[0]["properties"]
    assert p["feature_type"] == "underground_cable_segment"
    assert p["routing_source"] == "support_span"
    assert p.get("cable_type") == "XLPE"


def test_generate_cable_includes_crossing_and_actions() -> None:
    feats = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.01, 54.0]},
            "properties": {"pole_id": "A", "cable_to_asset_id": "B", "voltage": "11kV"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.02, 54.0]},
            "properties": {"pole_id": "B"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.015, 54.0]},
            "properties": {"pole_id": "R1", "structure_type": "Road", "record_role": "context"},
        },
    ]
    cables = generate_cable_features_geojson(feats, {})
    assert len(cables) == 1
    p = cables[0]["properties"]
    assert p["crossing_risk_level"] == "high"
    assert isinstance(p.get("designer_suggested_actions"), list)
    assert len(p["designer_suggested_actions"]) >= 1


def test_derive_cable_designer_actions_missing_type() -> None:
    acts = derive_cable_designer_actions({"crossing_risk_level": "none"})
    assert any("underground cable type" in a.lower() for a in acts)


def test_attach_cable_features_to_collection() -> None:
    fc = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-3.01, 54.0]},
                "properties": {"pole_id": "U1", "cable_to_asset_id": "U2"},
            },
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [-3.02, 54.0]},
                "properties": {"pole_id": "U2"},
            },
        ],
        "metadata": {},
    }
    attach_cable_features_to_collection(fc)
    assert fc["metadata"]["cable_feature_count"] == 1
    assert len(fc["cable_features"]) == 1


def test_build_cable_feature_merge_burial() -> None:
    f1 = {"voltage": "11kV", "burial_depth_m": "1.2"}
    f2 = {"cable_type": "XLPE"}
    wit: dict = {}
    feat = build_cable_feature(
        "A",
        "B",
        -3.01,
        54.0,
        -3.02,
        54.0,
        f1,
        f2,
        wit,
        rulepack_id="SPEN_11kV",
        cable_index=0,
        routing_source="cable_link",
        point_features=[],
    )
    assert feat["properties"]["burial_depth_m"] == "1.2"
    assert feat["properties"]["feature_type"] == "underground_cable_segment"


def test_generate_skips_missing_coords() -> None:
    feats = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.01, 54.0]},
            "properties": {"pole_id": "X", "cable_to_asset_id": "Y"},
        },
    ]
    assert generate_cable_features_geojson(feats, {}) == []
