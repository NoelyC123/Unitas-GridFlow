"""Map preview route: span_features embedded in map JSON."""

from __future__ import annotations

import json
from pathlib import Path

from app import create_app
from app.routes import map_preview


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_map_data_endpoint_adds_span_features(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_MAP_SPAN"
    _write_json(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_MAP_SPAN", "rulepack_id": "SPEN_11kV"},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-3.014, 54.521]},
                    "properties": {"pole_id": "PA", "voltage": "11kV", "conductor_type": "AAC"},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-3.013, 54.522]},
                    "properties": {"pole_id": "PB"},
                },
            ],
        },
    )
    _write_json(
        job_dir / "sequenced_route.json",
        {
            "status": "ok",
            "chain": [
                {"point_id": "PA", "lat": 54.521, "lon": -3.014, "span_to_next_m": 88},
                {"point_id": "PB", "lat": 54.522, "lon": -3.013},
            ],
        },
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)

    app = create_app()
    client = app.test_client()
    res = client.get("/map/data/J_MAP_SPAN")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data.get("span_features") or []) == 1
    sf = data["span_features"][0]
    assert sf["geometry"]["type"] == "LineString"
    assert sf["properties"]["distance_m"] == 88
    assert sf["properties"].get("voltage_detail")
    assert "cable_features" in data
    assert data["metadata"].get("cable_feature_count") == 0
    fo = data["metadata"].get("field_ownership_3d") or {}
    assert fo.get("policy") == "enriched_electrical_display_on_spans_and_cables_only"
    assert "point_features" in fo
    assert fo.get("post_enrichment_clean") is True
    assert fo.get("post_enrichment_violation_count") == 0
