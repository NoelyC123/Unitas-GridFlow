"""Phase 3D — enriched electrical display belongs on spans/cables, not pole points."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app import create_app
from app.field_ownership import (
    finalize_field_ownership_metadata,
    point_enriched_electrical_leaks,
    strip_enriched_electrical_from_point_props,
)
from app.routes import map_preview

REPO_ROOT = Path(__file__).resolve().parents[1]
J12946_MAP = REPO_ROOT / "uploads" / "jobs" / "J12946" / "map_data.json"


def test_point_enriched_electrical_leaks_empty() -> None:
    assert point_enriched_electrical_leaks({}) == []


def test_point_enriched_electrical_leaks_ignores_none_blank() -> None:
    assert point_enriched_electrical_leaks({"voltage_detail": None}) == []
    assert point_enriched_electrical_leaks({"voltage_detail": ""}) == []
    assert point_enriched_electrical_leaks({"voltage_detail": {}}) == []


def test_point_enriched_electrical_leaks_voltage_detail() -> None:
    leaks = point_enriched_electrical_leaks({"voltage_detail": {"label": "11kV"}})
    assert leaks == ["voltage_detail"]


def test_point_enriched_electrical_leaks_multiple_keys() -> None:
    props = {
        "voltage_detail": {"x": 1},
        "conductor_detail": {"y": 2},
        "phase_detail": {"z": 3},
    }
    leaks = point_enriched_electrical_leaks(props)
    assert set(leaks) == {"voltage_detail", "conductor_detail", "phase_detail"}
    assert len(leaks) == 3


def test_point_enriched_electrical_leaks_boolean_counts() -> None:
    assert point_enriched_electrical_leaks({"is_overhead": True}) == ["is_overhead"]
    assert point_enriched_electrical_leaks({"is_overhead": False}) == ["is_overhead"]


def test_strip_enriched_electrical_from_point_props_alias() -> None:
    props = {
        "voltage_detail": {"label": "LV"},
        "pole_id": "P1",
        "voltage": "400V",
    }
    strip_enriched_electrical_from_point_props(props)
    assert "voltage_detail" not in props
    assert props.get("voltage") == "400V"
    assert props.get("pole_id") == "P1"


def test_finalize_field_ownership_metadata_counts() -> None:
    data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [0, 0]},
                "properties": {},
            },
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": [[0, 0], [1, 1]]},
                "properties": {},
            },
        ],
        "span_features": [{"type": "Feature"}],
        "cable_features": [{"type": "Feature"}, {"type": "Feature"}],
        "metadata": {"job_id": "J"},
    }
    finalize_field_ownership_metadata(data, point_leak_total=4)
    fo = data["metadata"]["field_ownership_3d"]
    assert fo["policy_version"] == 1
    assert fo["point_enriched_electrical_keys_found_pre_strip"] == 4
    assert fo["point_features"] == 1
    assert fo["span_features"] == 1
    assert fo["cable_features"] == 2
    assert fo["policy"] == "enriched_electrical_display_on_spans_and_cables_only"


def test_finalize_field_ownership_metadata_skips_non_dict_metadata() -> None:
    data = {"metadata": "broken", "features": []}
    finalize_field_ownership_metadata(data, point_leak_total=0)
    assert data["metadata"] == "broken"


def test_finalize_field_ownership_metadata_creates_metadata() -> None:
    data = {"features": []}
    finalize_field_ownership_metadata(data, point_leak_total=0)
    assert isinstance(data["metadata"], dict)
    assert "field_ownership_3d" in data["metadata"]


def test_map_data_strips_enriched_electrical_from_points(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_FO_STRIP"
    job_dir.mkdir(parents=True)
    (job_dir / "map_data.json").write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "metadata": {"job_id": "J_FO_STRIP"},
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [-3.0, 54.5]},
                        "properties": {
                            "pole_id": "P1",
                            "is_overhead": None,
                            "is_underground": None,
                            "voltage_detail": {"label": "11kV"},
                            "conductor_detail": {"code": "AAC"},
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    (job_dir / "sequenced_route.json").write_text(
        json.dumps({"status": "ok", "chain": [{"point_id": "P1", "lat": 54.5, "lon": -3.0}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)
    app = create_app()
    client = app.test_client()
    res = client.get("/map/data/J_FO_STRIP")
    assert res.status_code == 200
    body = res.get_json()
    props = body["features"][0]["properties"]
    assert "voltage_detail" not in props
    assert "conductor_detail" not in props
    fo = body["metadata"]["field_ownership_3d"]
    assert fo["point_enriched_electrical_keys_found_pre_strip"] == 2


@pytest.mark.skipif(not J12946_MAP.is_file(), reason="Local J12946 validation job not present")
def test_j12946_map_data_includes_field_ownership_3d(monkeypatch, tmp_path) -> None:
    """Operational smoke: real job envelope runs enrichment and records Phase 3D audit."""
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J12946"
    job_dir.mkdir(parents=True)
    (job_dir / "map_data.json").write_bytes(J12946_MAP.read_bytes())
    seq_src = REPO_ROOT / "uploads" / "jobs" / "J12946" / "sequenced_route.json"
    if seq_src.is_file():
        (job_dir / "sequenced_route.json").write_bytes(seq_src.read_bytes())
    else:
        (job_dir / "sequenced_route.json").write_text(
            json.dumps({"status": "ok", "chain": []}), encoding="utf-8"
        )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)
    app = create_app()
    client = app.test_client()
    res = client.get("/map/data/J12946")
    assert res.status_code == 200
    body = res.get_json()
    assert "field_ownership_3d" in (body.get("metadata") or {})
    for feat in body.get("features") or []:
        if not isinstance(feat, dict):
            continue
        geom = feat.get("geometry") or {}
        if geom.get("type") != "Point":
            continue
        props = feat.get("properties") or {}
        for k in (
            "voltage_detail",
            "conductor_detail",
            "cable_detail",
            "phase_detail",
        ):
            assert k not in props
