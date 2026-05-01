"""Stage 4 — field capture HTTP API."""

from __future__ import annotations

import json
from io import BytesIO

import pytest

from app import create_app
from app.project_manager import create_project


@pytest.fixture
def fc_root(tmp_path, monkeypatch):
    root = tmp_path / "projects"
    root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.field_capture.PROJECTS_ROOT", root)
    monkeypatch.setattr("app.routes.api_field_capture.PROJECTS_ROOT", root)
    monkeypatch.setattr("app.routes.map_preview.PROJECTS_ROOT", root)
    return root


@pytest.fixture
def client(fc_root):
    return create_app().test_client()


def test_field_capture_page_loads(client):
    res = client.get("/field-capture?project_id=P001")
    assert res.status_code == 200
    assert b"field_capture.js" in res.data


def test_session_requires_project(client, fc_root):
    res = client.post(
        "/api/field_capture/session",
        json={"job_id": "missing"},
    )
    assert res.status_code == 404


def test_create_session_and_list(client, fc_root):
    create_project(fc_root, "Demo", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    res = client.post(
        "/api/field_capture/session",
        json={"job_id": pid, "surveyor": "Alex"},
    )
    assert res.status_code == 200
    body = res.get_json()
    assert body["ok"] is True
    sid = body["session_id"]
    res2 = client.get(f"/api/field_capture/sessions/{pid}")
    assert res2.status_code == 200
    lst = res2.get_json()["sessions"]
    assert any(s["id"] == sid for s in lst)


def test_pole_record_validation_no_photo(client, fc_root):
    create_project(fc_root, "X", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = client.post("/api/field_capture/session", json={"job_id": pid}).get_json()["session_id"]
    res = client.post(
        "/api/field_capture/record",
        data={
            "session_id": sid,
            "record_kind": "pole",
            "fields": json.dumps({"point_id": "1", "record_type": "EXpole"}),
            "gnss": json.dumps({}),
        },
        content_type="multipart/form-data",
    )
    assert res.status_code == 400
    assert res.get_json()["details"]


def test_pole_record_multipart_ok(client, fc_root):
    create_project(fc_root, "Y", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = client.post("/api/field_capture/session", json={"job_id": pid}).get_json()["session_id"]
    data = {
        "session_id": sid,
        "record_kind": "pole",
        "fields": json.dumps({"point_id": "P44", "record_type": "EXpole", "height_m": 8.0}),
        "gnss": json.dumps({"latitude": 54.521, "longitude": -3.014}),
    }
    res = client.post(
        "/api/field_capture/record",
        data={**data, "photos": (BytesIO(b"\xff\xd8\xff\x00"), "snap.jpg")},
        content_type="multipart/form-data",
    )
    assert res.status_code == 200, res.get_data(as_text=True)
    js = res.get_json()
    assert js["ok"] is True
    assert js["photos"]


def test_span_json_record(client, fc_root):
    create_project(fc_root, "Z", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = client.post("/api/field_capture/session", json={"job_id": pid}).get_json()["session_id"]
    res = client.post(
        "/api/field_capture/record",
        json={
            "session_id": sid,
            "record_kind": "span",
            "fields": {"from_pole_id": "a", "to_pole_id": "b", "conductor_type": "AAC"},
            "gnss": {},
        },
    )
    assert res.status_code == 200


def test_list_records_requires_job_or_resolve(client, fc_root):
    create_project(fc_root, "R", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = client.post("/api/field_capture/session", json={"job_id": pid}).get_json()["session_id"]
    res = client.get(f"/api/field_capture/session/{sid}/records")
    assert res.status_code == 200
    assert len(res.get_json()["records"]) == 0


def test_import_session_creates_processed_file(client, fc_root):
    create_project(fc_root, "Imp", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = client.post("/api/field_capture/session", json={"job_id": pid}).get_json()["session_id"]
    r1 = client.post(
        "/api/field_capture/record",
        data={
            "session_id": sid,
            "record_kind": "pole",
            "fields": json.dumps(
                {"point_id": "CAP1", "record_type": "EXpole", "height_m": 11.0, "material": "Wood"}
            ),
            "gnss": json.dumps({"latitude": 54.521, "longitude": -3.014}),
            "photos": (BytesIO(b"\xff\xd8\xff\x00"), "p.jpg"),
        },
        content_type="multipart/form-data",
    )
    assert r1.status_code == 200, r1.get_data(as_text=True)

    imp = client.post(
        f"/api/field_capture/import/{sid}?job_id={pid}",
        json={"dno": "SPEN_11kV"},
    )
    assert imp.status_code == 200, imp.get_data(as_text=True)
    body = imp.get_json()
    assert body["ok"] is True
    assert body["file_id"]
    meta_path = fc_root / pid / "files" / body["file_id"] / "meta.json"
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta.get("status") == "complete"


def test_import_empty_session_fails(client, fc_root):
    create_project(fc_root, "NoRec", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = client.post("/api/field_capture/session", json={"job_id": pid}).get_json()["session_id"]
    imp = client.post(f"/api/field_capture/import/{sid}?job_id={pid}", json={})
    assert imp.status_code == 400


def test_context_record_multipart(client, fc_root):
    create_project(fc_root, "Ctx", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = client.post("/api/field_capture/session", json={"job_id": pid}).get_json()["session_id"]
    res = client.post(
        "/api/field_capture/record",
        data={
            "session_id": sid,
            "record_kind": "context",
            "fields": json.dumps({"structure_type": "road", "distance_m": 3.0, "remarks": "r"}),
            "gnss": json.dumps({"latitude": 54.1, "longitude": -2.8}),
        },
        content_type="multipart/form-data",
    )
    assert res.status_code == 200


def test_record_invalid_kind(client, fc_root):
    create_project(fc_root, "Bad", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = client.post("/api/field_capture/session", json={"job_id": pid}).get_json()["session_id"]
    res = client.post(
        "/api/field_capture/record",
        json={"session_id": sid, "record_kind": "widget", "fields": {}, "gnss": {}},
    )
    assert res.status_code == 400


def test_map_data_available_after_capture_import(client, fc_root):
    create_project(fc_root, "Map", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = client.post("/api/field_capture/session", json={"job_id": pid}).get_json()["session_id"]
    client.post(
        "/api/field_capture/record",
        data={
            "session_id": sid,
            "record_kind": "pole",
            "fields": json.dumps({"point_id": "M1", "record_type": "EXpole", "height_m": 9.0}),
            "gnss": json.dumps({"latitude": 54.521, "longitude": -3.014}),
            "photos": (BytesIO(b"\xff\xd8\xff\x00"), "m.jpg"),
        },
        content_type="multipart/form-data",
    )
    imp_resp = client.post(
        f"/api/field_capture/import/{sid}?job_id={pid}",
        json={"dno": "SPEN_11kV"},
    )
    imp = imp_resp.get_json()
    assert imp_resp.status_code == 200
    assert imp["ok"]
    fid = imp["file_id"]
    md = client.get(f"/map/data/project/{pid}/{fid}")
    assert md.status_code == 200
    data = md.get_json()
    assert data.get("features")


def test_list_records_with_explicit_job_id(client, fc_root):
    create_project(fc_root, "LR", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = client.post("/api/field_capture/session", json={"job_id": pid}).get_json()["session_id"]
    client.post(
        "/api/field_capture/record",
        json={
            "session_id": sid,
            "record_kind": "context",
            "fields": {"structure_type": "fence"},
            "gnss": {},
        },
    )
    res = client.get(f"/api/field_capture/session/{sid}/records?job_id={pid}")
    assert len(res.get_json()["records"]) == 1


def test_sessions_404_unknown_project(client, fc_root):
    res = client.get("/api/field_capture/sessions/nope000")
    assert res.status_code == 404


def test_record_session_not_found(client, fc_root):
    res = client.post(
        "/api/field_capture/record",
        json={
            "session_id": "00000000-0000-0000-0000-000000000000",
            "record_kind": "span",
            "fields": {"from_pole_id": "a", "to_pole_id": "b"},
            "gnss": {},
        },
    )
    assert res.status_code == 404


def test_span_validation_missing_to(client, fc_root):
    create_project(fc_root, "Spv", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = client.post("/api/field_capture/session", json={"job_id": pid}).get_json()["session_id"]
    res = client.post(
        "/api/field_capture/record",
        json={
            "session_id": sid,
            "record_kind": "span",
            "fields": {"from_pole_id": "a"},
            "gnss": {},
        },
    )
    assert res.status_code == 400
