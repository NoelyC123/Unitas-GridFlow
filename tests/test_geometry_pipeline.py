from __future__ import annotations

from app.geometry_pipeline import (
    merge_duplicates,
    normalize_geometry_for_span_generation,
    remove_zero_length_sequences,
    snap_nearby_points,
)
from app.span_generator import attach_span_features_to_collection


def _point(pid: str, lon: float, lat: float) -> dict:
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {"pole_id": pid},
    }


def test_duplicate_route_points_collapse_to_one() -> None:
    features = [
        _point("A", -3.000000, 54.000000),
        _point("B", -3.000006, 54.000006),
    ]

    snapped = snap_nearby_points(features, threshold_m=3.0)
    merged, aliases = merge_duplicates(snapped, threshold_m=2.0)

    assert len(merged) == 1
    assert merged[0]["properties"]["pole_id"] == "A"
    assert aliases == {"B": "A"}


def test_one_metre_sequence_step_removed_before_span_creation() -> None:
    features = [
        _point("A", -3.000000, 54.000000),
        _point("B", -2.999986, 54.000000),
        _point("C", -2.999700, 54.000000),
    ]
    seq = {
        "status": "ok",
        "chain": [
            {"point_id": "A", "lat": 54.000000, "lon": -3.000000},
            {"point_id": "B", "lat": 54.000000, "lon": -2.999986},
            {"point_id": "C", "lat": 54.000000, "lon": -2.999700},
        ],
    }

    result = normalize_geometry_for_span_generation(features, seq)
    chain = result.sequence_payload["chain"]

    assert [item["point_id"] for item in chain] == ["A", "C"]

    fc = {
        "type": "FeatureCollection",
        "features": features,
        "metadata": {},
    }
    attach_span_features_to_collection(fc, seq)

    assert fc["metadata"]["span_feature_count"] == 1
    span = fc["span_features"][0]["properties"]
    assert span["from_point_id"] == "A"
    assert span["to_point_id"] == "C"
    assert span["distance_m"] > 10


def test_remove_zero_length_sequences_recomputes_span_distances() -> None:
    cleaned = remove_zero_length_sequences(
        {
            "status": "ok",
            "chain": [
                {"point_id": "A", "lat": 54.000000, "lon": -3.000000},
                {"point_id": "B", "lat": 54.000000, "lon": -2.999986},
                {"point_id": "C", "lat": 54.000000, "lon": -2.999700},
            ],
        },
        threshold_m=2.0,
    )

    assert [item["point_id"] for item in cleaned["chain"]] == ["A", "C"]
    assert cleaned["chain"][0]["span_to_next_m"] > 10
    assert cleaned["chain"][1]["span_to_next_m"] is None
