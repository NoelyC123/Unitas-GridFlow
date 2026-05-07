from __future__ import annotations

from app.routes.map_preview import _build_validation_summary
from app.span_generator import (
    _apply_cluster_gating,
    _apply_design_gating,
    annotate_geometry_issue_clusters,
    build_span_feature,
    generate_span_features_geojson,
)


def _span(props: dict) -> dict:
    return {"type": "Feature", "geometry": None, "properties": props}


def test_design_gating_emits_structured_reasons_and_review_status() -> None:
    spans = [_span({"span_validity": "suspect", "distance_m": 6.0})]

    _apply_design_gating(spans)

    props = spans[0]["properties"]
    assert props["design_status"] == "REVIEW"
    assert props["design_blocker_reasons"] == [
        {
            "type": "geometry",
            "severity": "medium",
            "message": "Suspect span distance (5-8 m) — verify route geometry",
        }
    ]


def test_design_status_blocks_extreme_invalid_span() -> None:
    span = build_span_feature(
        "A",
        "B",
        -3.0,
        54.0,
        -2.99999,
        54.0,
        {},
        {},
        rulepack_id=None,
        distance_m=1.0,
    )
    spans = [span]

    _apply_design_gating(spans)

    props = spans[0]["properties"]
    assert props["design_status"] == "BLOCKED"
    assert props["design_blocker_reasons"][0]["severity"] == "blocker"


def test_unverified_geometry_maps_to_review() -> None:
    spans = [
        _span(
            {
                "span_validity": "valid",
                "distance_m": 40.0,
                "source_confidence_detail": {"geometry_trust": "unverified"},
            }
        )
    ]

    _apply_design_gating(spans)

    props = spans[0]["properties"]
    assert props["design_status"] == "REVIEW"
    assert {
        "type": "geometry_trust",
        "severity": "medium",
        "message": "Unverified geometry - field verification required before design use",
    } in props["design_blocker_reasons"]


def test_cluster_gating_requires_multi_span_suspect_cluster() -> None:
    spans = [
        _span({"span_validity": "invalid", "distance_m": 3.0}),
        _span({"span_validity": "valid", "distance_m": 25.0}),
    ]

    _apply_design_gating(spans)
    annotate_geometry_issue_clusters(spans)
    _apply_cluster_gating(spans)

    assert spans[0]["properties"]["geometry_issue_cluster"] is False
    assert all(
        r["type"] != "geometry_cluster" for r in spans[0]["properties"]["design_blocker_reasons"]
    )


def test_cluster_gating_adds_high_severity_cluster_reason() -> None:
    spans = [
        _span({"span_validity": "invalid", "distance_m": 3.0}),
        _span({"span_validity": "suspect", "distance_m": 6.0}),
    ]

    _apply_design_gating(spans)
    annotate_geometry_issue_clusters(spans)
    _apply_cluster_gating(spans)

    for span in spans:
        reasons = span["properties"]["design_blocker_reasons"]
        assert {
            "type": "geometry_cluster",
            "severity": "high",
            "message": "Multiple suspect spans detected",
        } in reasons


def test_cluster_gating_executes_annotation_and_canonicalizes_legacy_reasons() -> None:
    spans = [
        _span(
            {
                "span_validity": "invalid",
                "distance_m": 3.0,
                "design_blocker_reasons": ["Invalid span distance (< 5 m)"],
            }
        ),
        _span(
            {
                "span_validity": "suspect",
                "distance_m": 6.0,
                "design_blocker_reasons": [
                    {
                        "type": "geometry",
                        "severity": "medium",
                        "message": "Suspect span distance (5-8 m) — verify route geometry",
                    }
                ],
            }
        ),
    ]

    _apply_cluster_gating(spans)

    for span in spans:
        props = span["properties"]
        assert props["geometry_issue_cluster"] is True
        assert props["cluster_size"] == 2
        assert all(isinstance(r, dict) for r in props["design_blocker_reasons"])
        assert all(
            set(r) == {"type", "severity", "message"} for r in props["design_blocker_reasons"]
        )
        assert {
            "type": "geometry_cluster",
            "severity": "high",
            "message": "Multiple suspect spans detected",
        } in props["design_blocker_reasons"]


def test_replacement_spans_are_not_geometry_clustered() -> None:
    spans = [
        _span(
            {
                "span_validity": "invalid",
                "distance_m": 1.0,
                "relationship": "replacement_pair",
            }
        ),
        _span({"span_validity": "invalid", "distance_m": 1.0}),
    ]

    _apply_cluster_gating(spans)

    for span in spans:
        props = span["properties"]
        assert props["geometry_issue_cluster"] is False
        assert props["cluster_size"] is None
        assert props["design_blocker_reasons"] == []


def test_near_high_tier_crossing_sets_blocker_status() -> None:
    point_features = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.0, 54.0]},
            "properties": {"pole_id": "A"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-2.999, 54.0]},
            "properties": {"pole_id": "B"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-2.9995, 54.0]},
            "properties": {"pole_id": "ROAD", "structure_type": "Road", "record_role": "context"},
        },
    ]
    seq = {
        "status": "ok",
        "chain": [
            {"point_id": "A", "lat": 54.0, "lon": -3.0, "span_to_next_m": 70.0},
            {"point_id": "B", "lat": 54.0, "lon": -2.999},
        ],
    }

    spans = generate_span_features_geojson(point_features, seq, {})

    props = spans[0]["properties"]
    assert props["crossing_risk_level"] == "BLOCKER"
    assert props["design_status"] == "BLOCKED"
    assert any(
        r["type"] == "clearance" and r["severity"] == "blocker"
        for r in props["design_blocker_reasons"]
    )


def test_validation_summary_counts_tri_state_span_statuses() -> None:
    data = {
        "span_features": [
            _span({"design_status": "PASS"}),
            _span(
                {
                    "design_status": "REVIEW",
                    "source_confidence_detail": {"geometry_trust": "unverified"},
                }
            ),
            _span({"design_status": "BLOCKED"}),
        ]
    }

    assert _build_validation_summary(data) == {
        "pass": 1,
        "review": 1,
        "blocked": 1,
        "unverified_geometry": 1,
    }
