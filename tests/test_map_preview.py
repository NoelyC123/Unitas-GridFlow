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
    assert data["metadata"].get("span_layer_origin") == "provisional_route"
    pa = next(p["properties"] for p in data["features"] if p["properties"].get("pole_id") == "PA")
    assert "voltage" not in pa
    assert "conductor_type" not in pa
    fo = data["metadata"].get("field_ownership_3d") or {}
    assert fo.get("policy") == "network_electrical_on_spans_and_cables_only"
    assert "point_features" in fo
    assert fo.get("post_enrichment_clean") is True
    assert fo.get("post_enrichment_violation_count") == 0


def test_map_data_endpoint_backfills_c2d_popup_fields(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_C2D_BACKFILL"
    _write_json(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_C2D_BACKFILL"},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-3.014, 54.521]},
                    "properties": {"pole_id": "P1", "structure_type": "Angle"},
                }
            ],
        },
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)

    app = create_app()
    client = app.test_client()
    res = client.get("/map/data/J_C2D_BACKFILL")

    assert res.status_code == 200
    props = res.get_json()["features"][0]["properties"]
    assert "stay_evidence_status" in props
    assert "nearest_stay_distance_m" in props
    assert "wayleave_notes" in props
    assert props["support_schema_role"] == "angle"
    catalog = res.get_json()["metadata"]["popup_priority_field_catalog"]
    angle = catalog["roles"]["angle"]
    assert angle["section_order"][0] == "Physical evidence"
    assert any(
        item["field"] == "stay_present_evidence" and item["popup_group"] == "Mechanical"
        for item in angle["fields"]
    )
    proposed = catalog["roles"]["proposed"]
    assert any(
        item["field"] == "voltage_carried" and item["visibility"] == "hidden"
        for item in proposed["fields"]
    )


def test_map_viewer_includes_span_label_mode_select() -> None:
    app = create_app()
    client = app.test_client()
    res = client.get("/map/view/J_ANY")
    assert res.status_code == 200
    html = res.data.decode("utf-8")
    assert 'id="span-label-mode"' in html
    assert "Show on hover" in html
    assert "map-viewer.css?v=8" in html
    assert "Pin critical anomalies only" in html
    assert "Pin crossing / context spans" in html
