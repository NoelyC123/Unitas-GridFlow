"""Tests for Stage 5C map overlay routes."""

from __future__ import annotations

import json
from pathlib import Path

from app import create_app
from app.routes import map_overlay


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _make_job(tmp_path: Path) -> tuple[Path, str]:
    """Create a minimal job directory with all four required overlay files."""
    jobs_root = tmp_path / "uploads" / "jobs"
    job_id = "OVERLAY_TEST_001"
    job_dir = jobs_root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    _write_json(
        job_dir / "03_match_register.json",
        [
            {
                "support_number": "TEST001",
                "baseline_support_number": "TEST001",
                "field_support_number": "TEST001",
                "match_confidence": "HIGH",
                "conflict_flags": {},
            },
            {
                "support_number": "TEST002",
                "baseline_support_number": "TEST002",
                "field_support_number": "TEST002",
                "match_confidence": "LOW",
                "conflict_flags": {"voltage_conflict": True},
            },
        ],
    )

    _write_json(
        job_dir / "01_baseline_dataset.json",
        [
            {"support_number": "TEST001", "latitude": 54.5, "longitude": -2.0, "voltage": "11kV"},
            {"support_number": "TEST002", "latitude": 54.51, "longitude": -2.01, "voltage": "11kV"},
        ],
    )

    _write_json(
        job_dir / "02_field_dataset.json",
        [
            {
                "support_number": "TEST001",
                "latitude": 54.5001,
                "longitude": -2.0001,
                "evidence_quality": "HIGH",
            },
            {
                "support_number": "TEST002",
                "latitude": 54.512,
                "longitude": -2.015,
                "evidence_quality": "MEDIUM",
            },
        ],
    )

    _write_json(
        job_dir / "04_merged_dataset.json",
        [
            {"support_number": "TEST001", "design_ready": True, "verification_flags": {}},
            {
                "support_number": "TEST002",
                "design_ready": False,
                "verification_flags": {"conductor_spec_missing": True},
            },
        ],
    )

    return jobs_root, job_id


def test_overlay_view_renders(tmp_path, monkeypatch):
    """Overlay view route returns 200 and contains expected heading text."""
    jobs_root, job_id = _make_job(tmp_path)
    monkeypatch.setattr(map_overlay, "JOBS_ROOT", jobs_root)
    client = create_app().test_client()

    res = client.get(f"/map/overlay/{job_id}")
    assert res.status_code == 200
    assert b"Overlay Map" in res.data


def test_overlay_data_returns_json(tmp_path, monkeypatch):
    """Overlay data endpoint returns valid JSON with all required keys."""
    jobs_root, job_id = _make_job(tmp_path)
    monkeypatch.setattr(map_overlay, "JOBS_ROOT", jobs_root)
    client = create_app().test_client()

    res = client.get(f"/map/overlay/data/{job_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert "baseline_poles" in data
    assert "field_poles" in data
    assert "match_lines" in data
    assert "statistics" in data


def test_overlay_data_baseline_poles(tmp_path, monkeypatch):
    """Baseline poles are GeoJSON Features with correct layer tag."""
    jobs_root, job_id = _make_job(tmp_path)
    monkeypatch.setattr(map_overlay, "JOBS_ROOT", jobs_root)
    client = create_app().test_client()

    data = client.get(f"/map/overlay/data/{job_id}").get_json()
    assert len(data["baseline_poles"]) == 2
    pole = data["baseline_poles"][0]
    assert pole["geometry"]["type"] == "Point"
    assert "support_number" in pole["properties"]
    assert pole["properties"]["layer"] == "baseline"


def test_overlay_data_field_poles(tmp_path, monkeypatch):
    """Field poles carry the 'field' layer tag."""
    jobs_root, job_id = _make_job(tmp_path)
    monkeypatch.setattr(map_overlay, "JOBS_ROOT", jobs_root)
    client = create_app().test_client()

    data = client.get(f"/map/overlay/data/{job_id}").get_json()
    assert len(data["field_poles"]) == 2
    assert data["field_poles"][0]["properties"]["layer"] == "field"


def test_overlay_data_match_lines(tmp_path, monkeypatch):
    """Match lines include confidence, color, distance_m, and LineString geometry."""
    jobs_root, job_id = _make_job(tmp_path)
    monkeypatch.setattr(map_overlay, "JOBS_ROOT", jobs_root)
    client = create_app().test_client()

    data = client.get(f"/map/overlay/data/{job_id}").get_json()
    assert len(data["match_lines"]) == 2
    line = data["match_lines"][0]
    assert line["geometry"]["type"] == "LineString"
    assert "match_confidence" in line["properties"]
    assert "color" in line["properties"]
    assert "distance_m" in line["properties"]


def test_overlay_statistics(tmp_path, monkeypatch):
    """Statistics counts are calculated correctly from test fixtures."""
    jobs_root, job_id = _make_job(tmp_path)
    monkeypatch.setattr(map_overlay, "JOBS_ROOT", jobs_root)
    client = create_app().test_client()

    data = client.get(f"/map/overlay/data/{job_id}").get_json()
    stats = data["statistics"]
    assert stats["total_baseline"] == 2
    assert stats["total_field"] == 2
    assert stats["total_matched"] == 2
    assert stats["high_confidence"] == 1
    assert stats["low_confidence"] == 1


def test_overlay_confidence_colors(tmp_path, monkeypatch):
    """HIGH confidence lines are green (#10b981), LOW are red (#ef4444)."""
    jobs_root, job_id = _make_job(tmp_path)
    monkeypatch.setattr(map_overlay, "JOBS_ROOT", jobs_root)
    client = create_app().test_client()

    data = client.get(f"/map/overlay/data/{job_id}").get_json()
    by_sn = {m["properties"]["support_number"]: m["properties"] for m in data["match_lines"]}
    assert by_sn["TEST001"]["color"] == "#10b981"
    assert by_sn["TEST002"]["color"] == "#ef4444"


def test_overlay_job_not_found(tmp_path, monkeypatch):
    """Unknown job_id returns 404."""
    jobs_root = tmp_path / "uploads" / "jobs"
    jobs_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(map_overlay, "JOBS_ROOT", jobs_root)
    client = create_app().test_client()

    res = client.get("/map/overlay/data/NONEXISTENT_JOB_XYZ")
    assert res.status_code == 404


def test_overlay_view_unknown_job_still_renders(tmp_path, monkeypatch):
    """Overlay HTML view renders regardless of job existence (JS fetches data later)."""
    jobs_root = tmp_path / "uploads" / "jobs"
    jobs_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(map_overlay, "JOBS_ROOT", jobs_root)
    client = create_app().test_client()

    res = client.get("/map/overlay/FAKE_JOB_ID")
    assert res.status_code == 200


def test_overlay_data_accepts_pipeline_dataset_shape(tmp_path, monkeypatch):
    """Overlay data accepts pipeline JSON shaped as dicts with poles arrays."""
    jobs_root = tmp_path / "uploads" / "jobs"
    job_id = "PIPELINE_SHAPE"
    job_dir = jobs_root / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    _write_json(
        job_dir / "01_baseline_dataset.json",
        {
            "poles": [
                {
                    "support_no": "903203",
                    "latitude": 54.1,
                    "longitude": -2.9,
                    "voltage_level": "LV",
                    "asset_type": "POLE",
                }
            ]
        },
    )
    _write_json(
        job_dir / "02_field_dataset.json",
        {
            "poles": [
                {
                    "support_no": "903203",
                    "latitude": 54.1001,
                    "longitude": -2.9001,
                    "evidence_quality": "HIGH",
                }
            ]
        },
    )
    _write_json(
        job_dir / "03_match_register.json",
        {"entries": [{"support_no": "903203", "match_confidence": "HIGH"}]},
    )
    _write_json(
        job_dir / "04_merged_dataset.json",
        {
            "poles": [
                {
                    "support_no": "903203",
                    "design_ready": False,
                    "conductor_verification_required": True,
                }
            ]
        },
    )

    monkeypatch.setattr(map_overlay, "JOBS_ROOT", jobs_root)
    client = create_app().test_client()

    res = client.get(f"/map/overlay/data/{job_id}")
    assert res.status_code == 200
    data = res.get_json()
    assert data["statistics"]["total_baseline"] == 1
    assert data["statistics"]["total_field"] == 1
    assert data["statistics"]["total_matched"] == 1
    assert data["design_status"]["903203"]["verification_flags"]["conductor_verification_required"]
