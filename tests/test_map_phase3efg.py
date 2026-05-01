"""Map preview enrichment: Phase 3E–3G metadata wiring."""

from __future__ import annotations

import json
from pathlib import Path

from app import create_app
from app.routes import map_preview


def _write(p: Path, payload: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def test_map_data_phase3_support_schema_on_points(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_P3E"
    _write(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_P3E", "rulepack_id": "SPEN_11kV"},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-3.0, 54.5]},
                    "properties": {"pole_id": "E1", "structure_type": "EXpole", "height": 9.0},
                },
            ],
        },
    )
    _write(
        job_dir / "sequenced_route.json",
        {"status": "ok", "chain": [{"point_id": "E1", "lat": 54.5, "lon": -3.0}]},
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)
    app = create_app()
    res = app.test_client().get("/map/data/J_P3E")
    body = res.get_json()
    props = body["features"][0]["properties"]
    assert props.get("support_schema_role") == "existing"
    assert props.get("measured_height_m") == 9.0


def test_map_data_phase3f_context_counts(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_P3F"
    _write(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_P3F", "rulepack_id": "SPEN_11kV"},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-3.0, 54.5]},
                    "properties": {"pole_id": "P1", "structure_type": "EXpole"},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-3.001, 54.501]},
                    "properties": {"pole_id": "P2", "structure_type": "EXpole"},
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-3.0005, 54.5003]},
                    "properties": {
                        "pole_id": "CX",
                        "record_role": "context",
                        "structure_type": "road",
                    },
                },
            ],
        },
    )
    _write(
        job_dir / "sequenced_route.json",
        {
            "status": "ok",
            "chain": [
                {"point_id": "P1", "lat": 54.5, "lon": -3.0},
                {"point_id": "P2", "lat": 54.501, "lon": -3.001},
            ],
        },
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)
    app = create_app()
    body = app.test_client().get("/map/data/J_P3F").get_json()
    assert body["metadata"].get("context_crossing_phase3f_count") == 1
    ctx_props = next(
        p["properties"] for p in body["features"] if p["properties"].get("pole_id") == "CX"
    )
    assert ctx_props.get("context_type_profile")


def test_map_data_phase3g_replacement_audit(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_P3G"
    _write(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_P3G", "rulepack_id": "SPEN_11kV"},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-3.0, 54.5]},
                    "properties": {
                        "pole_id": "EX9",
                        "structure_type": "EXpole",
                        "being_replaced_by": "PR9",
                        "match_offset_m": 1.0,
                        "height": 8.0,
                    },
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-3.0, 54.5]},
                    "properties": {
                        "pole_id": "PR9",
                        "structure_type": "PRpole",
                        "replacing": "EX9",
                        "match_offset_m": 1.0,
                        "height": 8.1,
                    },
                },
            ],
        },
    )
    _write(
        job_dir / "sequenced_route.json",
        {
            "status": "ok",
            "chain": [
                {"point_id": "EX9", "lat": 54.5, "lon": -3.0},
                {"point_id": "PR9", "lat": 54.5, "lon": -3.0},
            ],
        },
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)
    app = create_app()
    body = app.test_client().get("/map/data/J_P3G").get_json()
    assert body["metadata"].get("replacement_pair_audit_count") == 1
    assert "replacement_pair_audit" in body["features"][0]["properties"]


def test_measured_height_surfaces_when_only_height_alias(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_HT"
    _write(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_HT"},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {"pole_id": "z", "structure_type": "EXpole", "height": 7.5},
                },
            ],
        },
    )
    _write(
        job_dir / "sequenced_route.json",
        {"status": "ok", "chain": [{"point_id": "z", "lat": 0, "lon": 0}]},
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)
    app = create_app()
    props = app.test_client().get("/map/data/J_HT").get_json()["features"][0]["properties"]
    assert props["measured_height_m"] == 7.5


def test_field_ownership_still_present(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_FO"
    _write(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_FO"},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {
                        "pole_id": "a",
                        "structure_type": "EXpole",
                        "is_overhead": None,
                        "is_underground": None,
                    },
                },
            ],
        },
    )
    _write(
        job_dir / "sequenced_route.json",
        {"status": "ok", "chain": [{"point_id": "a", "lat": 0, "lon": 0}]},
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)
    app = create_app()
    meta = app.test_client().get("/map/data/J_FO").get_json()["metadata"]
    assert "field_ownership_3d" in meta


def test_linked_support_id_from_replacing(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_LS"
    _write(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_LS"},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {
                        "pole_id": "pr",
                        "structure_type": "PRpole",
                        "replacing": "ex",
                        "height": 9.0,
                    },
                },
            ],
        },
    )
    _write(
        job_dir / "sequenced_route.json",
        {"status": "ok", "chain": [{"point_id": "pr", "lat": 0, "lon": 0}]},
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)
    app = create_app()
    props = app.test_client().get("/map/data/J_LS").get_json()["features"][0]["properties"]
    assert props["linked_support_id"] == "ex"
    assert props["replacement_status"] == "replacing_existing"


def test_context_crossing_assessment_action_for_high(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_CA"
    feats = [
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.01, 54.5]},
            "properties": {"pole_id": "A", "structure_type": "EXpole"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.02, 54.51]},
            "properties": {"pole_id": "B", "structure_type": "EXpole"},
        },
        {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [-3.015, 54.505]},
            "properties": {"pole_id": "R", "record_role": "context", "structure_type": "BT line"},
        },
    ]
    _write(
        job_dir / "map_data.json",
        {"type": "FeatureCollection", "metadata": {"job_id": "J_CA"}, "features": feats},
    )
    _write(
        job_dir / "sequenced_route.json",
        {
            "status": "ok",
            "chain": [
                {"point_id": "A", "lat": 54.5, "lon": -3.01},
                {"point_id": "B", "lat": 54.51, "lon": -3.02},
            ],
        },
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)
    app = create_app()
    body = app.test_client().get("/map/data/J_CA").get_json()
    rprops = next(
        p["properties"] for p in body["features"] if p["properties"].get("pole_id") == "R"
    )
    assert rprops["context_type_profile"]["context_kind"] == "bt"
    ca = rprops.get("context_crossing_assessment") or {}
    assert ca.get("risk_level")


def test_angle_support_schema_role(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_AN"
    _write(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_AN"},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {
                        "pole_id": "ag",
                        "structure_type": "11kVangle",
                        "stay_evidence_status": "missing",
                    },
                },
            ],
        },
    )
    _write(
        job_dir / "sequenced_route.json",
        {"status": "ok", "chain": [{"point_id": "ag", "lat": 0, "lon": 0}]},
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)
    app = create_app()
    props = app.test_client().get("/map/data/J_AN").get_json()["features"][0]["properties"]
    assert props["support_schema_role"] == "angle"
    assert "stay_evidence_required" in (props.get("unresolved_decisions") or [])


def test_replacement_audit_symmetric_ids(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_SYM"
    _write(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_SYM"},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {
                        "pole_id": "x",
                        "structure_type": "EXpole",
                        "being_replaced_by": "y",
                    },
                },
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {"pole_id": "y", "structure_type": "PRpole", "replacing": "x"},
                },
            ],
        },
    )
    _write(
        job_dir / "sequenced_route.json",
        {
            "status": "ok",
            "chain": [{"point_id": "x", "lat": 0, "lon": 0}, {"point_id": "y", "lat": 0, "lon": 0}],
        },
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)
    app = create_app()
    body = app.test_client().get("/map/data/J_SYM").get_json()
    a1 = body["features"][0]["properties"]["replacement_pair_audit"]
    a2 = body["features"][1]["properties"]["replacement_pair_audit"]
    assert a1["pair_id"] == a2["pair_id"]


def test_stay_support_schema_and_parent_alias(tmp_path, monkeypatch) -> None:
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J_ST"
    _write(
        job_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "metadata": {"job_id": "J_ST"},
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [0, 0]},
                    "properties": {
                        "pole_id": "st1",
                        "record_role": "anchor",
                        "structure_type": "stay",
                        "parent_support_id": "P99",
                    },
                },
            ],
        },
    )
    _write(
        job_dir / "sequenced_route.json",
        {"status": "ok", "chain": [{"point_id": "st1", "lat": 0, "lon": 0}]},
    )
    monkeypatch.setattr(map_preview, "JOBS_ROOT", jobs_root)
    app = create_app()
    props = app.test_client().get("/map/data/J_ST").get_json()["features"][0]["properties"]
    assert props["support_schema_role"] == "stay"
    assert props["parent_pole_id"] == "P99"
