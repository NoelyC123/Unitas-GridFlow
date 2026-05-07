"""Planner awareness overlay contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from app import create_app
from app.routes import map_preview

REPO_ROOT = Path(__file__).resolve().parent.parent
MAP_JS = REPO_ROOT / "app/static/js/map-viewer.js"
MAP_HTML = REPO_ROOT / "app/templates/map_viewer.html"

ALLOWED_SEVERITIES = {"INFO", "WARNING", "REVIEW", "BLOCKER"}


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_map_preview_response_includes_mock_planner_awareness(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_AWARENESS"
    _write_json(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_AWARENESS", "rulepack_id": "SPEN_11kV"},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-3.014, 54.521]},
                    "properties": {"pole_id": "PA"},
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

    res = create_app().test_client().get("/map/data/J_AWARENESS")

    assert res.status_code == 200
    data = res.get_json()
    awareness = data["planner_awareness"]
    assert 3 <= len(awareness) <= 5
    assert data["metadata"]["planner_awareness_count"] == len(awareness)
    for item in awareness:
        assert set(item) >= {"id", "lat", "lon", "category", "severity", "message"}
        assert isinstance(item["lat"], float)
        assert isinstance(item["lon"], float)
        assert item["severity"] in ALLOWED_SEVERITIES
        assert item.get("related_span_id")


def test_map_preview_preserves_real_planner_awareness(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_REAL_AWARENESS"
    real_item = {
        "id": "access-1",
        "lat": 54.521,
        "lon": -3.014,
        "category": "access",
        "severity": "BLOCKER",
        "message": "Locked gate reported by surveyor.",
        "related_span_id": "PA->PB",
    }
    _write_json(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_REAL_AWARENESS"},
            "features": [],
            "planner_awareness": [real_item],
        },
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)

    data = create_app().test_client().get("/map/data/J_REAL_AWARENESS").get_json()

    assert data["planner_awareness"] == [real_item]
    assert data["metadata"]["planner_awareness_count"] == 1


def test_empty_map_preview_response_has_safe_awareness_list(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(map_preview, "JOBS_ROOT", tmp_path / "jobs")

    data = create_app().test_client().get("/map/data/MISSING").get_json()

    assert data["planner_awareness"] == []
    assert data["metadata"].get("planner_awareness_count") == 0


def test_frontend_planner_awareness_layer_contract() -> None:
    js = MAP_JS.read_text(encoding="utf-8")
    html = MAP_HTML.read_text(encoding="utf-8")

    assert "plannerAwarenessLayer" in js
    assert "renderPlannerAwareness" in js
    assert "L.circleMarker" in js
    assert "Planner Awareness" in js
    assert "planner_awareness || []" in js
    assert 'data-layer="plannerAwareness"' in html
