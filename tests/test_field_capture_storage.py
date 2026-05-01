"""Stage 4 — field capture storage and CSV export."""

from __future__ import annotations

import pytest

from app.field_capture import (
    CaptureRecord,
    add_record,
    create_session,
    get_session,
    list_records,
    list_sessions,
    mark_session_imported,
    record_to_intake_row,
    session_to_csv_text,
    validate_context_payload,
    validate_pole_payload,
    validate_span_payload,
)
from app.project_manager import create_project


@pytest.fixture
def fc_root(tmp_path, monkeypatch):
    root = tmp_path / "projects"
    root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.field_capture.PROJECTS_ROOT", root)
    monkeypatch.setattr("app.routes.api_field_capture.PROJECTS_ROOT", root)
    return root


def test_validate_pole_requires_id_and_photo():
    assert "missing_point_id" in validate_pole_payload({}, 1)
    no_photo = validate_pole_payload({"point_id": "1", "record_type": "EXpole"}, 0)
    assert "pole_requires_photo" in no_photo
    assert validate_pole_payload({"point_id": "1", "record_type": "EXpole"}, 1) == []


def test_validate_span_and_context():
    assert "missing_from_pole_id" in validate_span_payload({"to_pole_id": "b"})
    assert validate_span_payload({"from_pole_id": "a", "to_pole_id": "b"}) == []
    assert "missing_structure_type" in validate_context_payload({})
    assert validate_context_payload({"structure_type": "road"}) == []


def test_record_to_intake_row_pole_pr_mapping():
    rec = CaptureRecord(
        id="r1",
        session_id="s",
        record_type="pole",
        fields={
            "point_id": "99",
            "record_type": "PR",
            "height_m": 9.5,
            "material": "wood",
            "stay_required": True,
            "remarks": "note",
        },
        photos=["field_capture/x/p/p.jpg"],
        gnss_data={"latitude": 54.5, "longitude": -3.1, "elevation": 120},
        timestamp="t",
    )
    row = record_to_intake_row(rec)
    assert row["pole_id"] == "99"
    assert row["structure_type"] == "PRpole"
    assert row["height"] == 9.5
    assert row["latitude"] == 54.5
    assert "stay_required" in row or "stay_required=yes" in (row.get("location") or "")


def test_record_to_intake_row_context_mapping():
    rec = CaptureRecord(
        id="r2",
        session_id="s",
        record_type="context",
        fields={"structure_type": "crossing", "distance_m": 2.5, "remarks": "near road"},
        photos=[],
        gnss_data={},
        timestamp="t",
    )
    row = record_to_intake_row(rec)
    assert row["structure_type"] == "11xing"
    assert row["distance_from_route_m"] == 2.5


def test_session_csv_roundtrip(fc_root):
    create_project(fc_root, "T", "")
    job_id = "P001"
    # create_project uses P001 if empty root - actually next_project_id
    projects = list(fc_root.iterdir())
    job_id = projects[0].name

    create_session(job_id, "sam")
    sessions = list_sessions(job_id)
    sid = sessions[0].id
    add_record(
        job_id,
        sid,
        "pole",
        {"point_id": "1", "record_type": "EXpole", "height_m": 10.0},
        {"latitude": 54.52, "longitude": -3.02},
        [("a.jpg", b"\xff\xd8\xff")],
    )
    add_record(
        job_id,
        sid,
        "span",
        {"from_pole_id": "1", "to_pole_id": "2", "conductor_type": "AAC", "phases": 3},
        {},
        [],
    )
    text = session_to_csv_text(job_id, sid)
    assert "pole_id" in text and "latitude" in text
    assert "S-1-2" in text or "from_pole_id" in text


def test_add_record_rejects_unknown_session(fc_root):
    fields = {"point_id": "1", "record_type": "EXpole"}
    bad = ("P404", "nope", "pole", fields, {}, [("x.jpg", b"x")])
    with pytest.raises(ValueError, match="session_not_found"):
        add_record(*bad)


def test_session_to_csv_empty(fc_root):
    create_project(fc_root, "E", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    create_session(pid, "")
    sid = list_sessions(pid)[0].id
    assert session_to_csv_text(pid, sid) == ""


def test_validate_pole_bad_height():
    errs = validate_pole_payload({"point_id": "1", "record_type": "EXpole", "height_m": "x"}, 1)
    assert "invalid_height_m" in errs


def test_record_to_intake_row_span():
    rec = CaptureRecord(
        id="r",
        session_id="s",
        record_type="span",
        fields={
            "from_pole_id": "10",
            "to_pole_id": "20",
            "conductor_type": "ACSR",
            "conductor_size": "185",
            "phases": 3,
            "remarks": "x",
        },
        photos=[],
        gnss_data={"latitude": 54.0, "longitude": -2.9},
        timestamp="t",
    )
    row = record_to_intake_row(rec)
    assert row["from_pole_id"] == "10"
    assert row["to_pole_id"] == "20"
    assert "latitude" in row


def test_add_record_rejects_closed_session(fc_root):
    create_project(fc_root, "C", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = create_session(pid, "").id
    mark_session_imported(pid, sid, "F001")
    with pytest.raises(ValueError, match="session_closed"):
        add_record(
            pid,
            sid,
            "pole",
            {"point_id": "1", "record_type": "EXpole"},
            {},
            [("a.jpg", b"x")],
        )


def test_list_sessions_order(fc_root):
    create_project(fc_root, "L", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    create_session(pid, "a")
    create_session(pid, "b")
    assert len(list_sessions(pid)) == 2


def test_validate_pole_missing_record_type():
    assert "missing_record_type" in validate_pole_payload({"point_id": "1"}, 1)


def test_record_to_intake_expole_mapping():
    rec = CaptureRecord(
        id="x",
        session_id="s",
        record_type="pole",
        fields={"point_id": "1", "record_type": "EXpole", "height_m": 8},
        photos=[],
        gnss_data={},
        timestamp="t",
    )
    row = record_to_intake_row(rec)
    assert row["structure_type"] == "EXpole"


def test_capture_record_photos_written(fc_root):
    create_project(fc_root, "Ph", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = create_session(pid, "").id
    add_record(
        pid,
        sid,
        "pole",
        {"point_id": "Z", "record_type": "EXpole"},
        {},
        [("shot.jpg", b"abc")],
    )
    recs = list_records(pid, sid)
    assert recs[0].photos
    rel = recs[0].photos[0]
    assert (fc_root / pid / rel).exists()


def test_session_get_by_id(fc_root):
    create_project(fc_root, "G", "")
    pid = next(p.name for p in fc_root.iterdir() if p.is_dir())
    sid = create_session(pid, "u").id
    s = get_session(pid, sid)
    assert s is not None
    assert s.surveyor == "u"
