"""Stage 3B integration tests — review overlay round-trip via HTTP."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

import pytest

from app import create_app
from app.routes import api_review, d2d_export, review_page

_SEQ = {
    "status": "ok",
    "config_used": {
        "angle_split_threshold_deg": 30,
        "gap_split_threshold_m": 50,
        "expole_match_threshold_m": 10,
    },
    "chain": [
        {
            "seq": 1,
            "point_id": "10",
            "feature_code": "PRpole",
            "easting": 100.0,
            "northing": 200.0,
            "lat": 54.0,
            "lon": -6.0,
            "height": 10.0,
            "span_to_next_m": 60.0,
            "deviation_angle_deg": 0.0,
            "replaces_point_id": "20",
            "replaces_distance_m": 1.5,
            "candidate_section_break": False,
            "section_split_candidate": False,
            "section_id": 1,
            "section_boundary": False,
            "design_pole_number": "Pol 1",
            "section_sequence_number": 1,
            "sequence_confidence": "high",
            "remark": "",
        },
        {
            "seq": 2,
            "point_id": "11",
            "feature_code": "PRpole",
            "easting": 160.0,
            "northing": 200.0,
            "lat": 54.0,
            "lon": -6.01,
            "height": 10.0,
            "span_to_next_m": None,
            "deviation_angle_deg": None,
            "replaces_point_id": None,
            "replaces_distance_m": None,
            "candidate_section_break": False,
            "section_split_candidate": False,
            "section_id": 1,
            "section_boundary": False,
            "design_pole_number": "Pol 2",
            "section_sequence_number": 2,
            "sequence_confidence": "high",
            "remark": "",
        },
    ],
    "matched_expoles": [
        {
            "point_id": "20",
            "feature_code": "EXpole",
            "easting": 101.5,
            "northing": 200.0,
            "height": 9.0,
            "matched_to_proposed_id": "10",
            "matched_design_pole_number": "Pol 1",
            "distance_m": 1.5,
        }
    ],
    "unmatched_expoles": [],
    "context_features": [],
    "detached_records": [],
    "sections": [{"section_id": 1, "start_seq": 1, "end_seq": 2, "pole_count": 2}],
    "interleaved_view": [
        {
            "point_id": "20",
            "feature_code": "EXpole",
            "easting": 101.5,
            "northing": 200.0,
            "height": 9.0,
            "remark": "",
            "role": "expole",
            "section_id": 1,
            "section_boundary": False,
            "design_pole_number": None,
            "section_sequence_number": None,
            "matched_proposed_id": "10",
            "matched_design_pole_number": "Pol 1",
        }
    ],
    "summary": {"total_poles": 2, "section_count": 1, "total_detached": 0},
}


@pytest.fixture()
def client_and_root(tmp_path, monkeypatch):
    projects_root = tmp_path / "projects"
    projects_root.mkdir()
    monkeypatch.setattr(api_review, "_PROJECTS_ROOT", projects_root)
    monkeypatch.setattr(review_page, "_PROJECTS_ROOT", projects_root)
    monkeypatch.setattr(d2d_export, "_PROJECTS_ROOT", projects_root)
    app = create_app()
    with app.test_client() as client:
        yield client, projects_root


def _make_file_slot(root: Path, project_id: str, file_id: str) -> Path:
    file_dir = root / project_id / "files" / file_id
    file_dir.mkdir(parents=True)
    (file_dir / "sequenced_route.json").write_text(json.dumps(_SEQ), encoding="utf-8")
    (file_dir / "meta.json").write_text(
        json.dumps({"file_id": file_id, "original_filename": "test.csv"}),
        encoding="utf-8",
    )
    return file_dir


def _csv_rows_without_comments(csv_text: str) -> list[list[str]]:
    body = "\n".join(line for line in csv_text.splitlines() if not line.startswith("#"))
    return list(csv.reader(io.StringIO(body)))


# ── 1. Creating review.json ──────────────────────────────────────────────────


def test_create_review(client_and_root):
    client, root = client_and_root
    _make_file_slot(root, "P001", "F001")
    resp = client.post(
        "/api/project/P001/file/F001/review",
        json={"review_status": "reviewed", "review_notes": "all good", "pairing_overrides": []},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ok"] is True
    review_path = root / "P001" / "files" / "F001" / "review.json"
    assert review_path.exists()
    review = json.loads(review_path.read_text())
    assert review["review_status"] == "reviewed"
    assert review["review_notes"] == "all good"


# ── 2. Saving a pairing override ─────────────────────────────────────────────


def test_save_pairing_override(client_and_root):
    client, root = client_and_root
    _make_file_slot(root, "P001", "F001")
    override = {
        "expole_point_id": "20",
        "original_matched_to": "10",
        "reviewed_matched_to": "11",
    }
    resp = client.post(
        "/api/project/P001/file/F001/review",
        json={"review_status": "reviewed", "review_notes": "", "pairing_overrides": [override]},
    )
    assert resp.status_code == 200
    review_path = root / "P001" / "files" / "F001" / "review.json"
    review = json.loads(review_path.read_text())
    assert len(review["pairing_overrides"]) == 1
    saved_ov = review["pairing_overrides"][0]
    assert saved_ov["expole_point_id"] == "20"
    assert saved_ov["reviewed_matched_to"] == "11"
    assert "reviewed_distance_m" in saved_ov


# ── 3. Marking EXpole unmatched ──────────────────────────────────────────────


def test_mark_expole_unmatched(client_and_root):
    client, root = client_and_root
    _make_file_slot(root, "P001", "F001")
    override = {
        "expole_point_id": "20",
        "original_matched_to": "10",
        "reviewed_matched_to": None,
    }
    resp = client.post(
        "/api/project/P001/file/F001/review",
        json={"review_status": "reviewed", "review_notes": "", "pairing_overrides": [override]},
    )
    assert resp.status_code == 200
    # Export should show EXpole 20 in unmatched section
    resp2 = client.get("/d2d/export/project/P001/F001")
    assert resp2.status_code == 200
    csv_text = resp2.data.decode()
    # The Unmatched EXpoles section should contain point 20
    unmatched_section = csv_text.split("Unmatched EXpoles", 1)
    assert len(unmatched_section) == 2
    assert "20" in unmatched_section[1]


def test_review_page_shows_review_summary_and_boundary_note(client_and_root):
    client, root = client_and_root
    _make_file_slot(root, "P001", "F001")

    response = client.get("/review/project/P001/F001")

    assert response.status_code == 200
    html = response.data.decode()
    assert "Review summary" in html
    assert "route sequence records" in html
    assert "auto-matched existing poles" in html
    assert "unmatched existing poles" in html
    assert "reviewed pairing changes" in html
    assert "Auto-matches are proximity signals only" in html
    assert "Existing/Proposed Pole Match Review" in html
    assert "Likely Existing-to-Proposed Pole Matches" in html
    assert "Do not confirm based on distance alone" in html
    assert "Field Maps attributes where available" in html
    assert "Reviewer-confirmed relationship" in html
    assert "No proposed replacement / unmatched" in html
    assert "Confirm suggested match:" in html
    assert "Choose different proposed pole:" in html
    assert "Pairing Review Status" in html
    assert "Pairings reviewed" in html
    assert (
        "Final design handoff sign-off should happen only after Review, Map, "
        "PDF, Design Route Sequence, and Working View" in html
    )
    assert "Reset to automatic matches" in html


# ── 4. Reviewed export header ────────────────────────────────────────────────


def test_export_header_reviewed(client_and_root):
    client, root = client_and_root
    _make_file_slot(root, "P001", "F001")
    client.post(
        "/api/project/P001/file/F001/review",
        json={"review_status": "reviewed", "review_notes": "", "pairing_overrides": []},
    )
    resp = client.get("/d2d/export/project/P001/F001")
    assert resp.status_code == 200
    csv_text = resp.data.decode()
    assert "Design Route Sequence Export" in csv_text.splitlines()[0]
    assert "Designer Reviewed" in csv_text
    assert "provisional" not in csv_text.lower().split("\n")[0]
    assert "P001_F001_design_chain.csv" in resp.headers["Content-Disposition"]


# ── 5. Provisional export header before review ───────────────────────────────


def test_export_header_provisional(client_and_root):
    client, root = client_and_root
    _make_file_slot(root, "P001", "F001")
    resp = client.get("/d2d/export/project/P001/F001")
    assert resp.status_code == 200
    csv_text = resp.data.decode()
    assert "Design Route Sequence Export" in csv_text.splitlines()[0]
    assert "provisional" in csv_text.lower()
    assert "Designer Reviewed" not in csv_text
    assert "P001_F001_design_chain.csv" in resp.headers["Content-Disposition"]


def test_design_chain_export_includes_evidence_quality_columns(client_and_root):
    client, root = client_and_root
    _make_file_slot(root, "P001", "F001")

    resp = client.get("/d2d/export/project/P001/F001")

    assert resp.status_code == 200
    rows = _csv_rows_without_comments(resp.data.decode())
    header = rows[0]
    first_chain_row = rows[1]
    row = dict(zip(header, first_chain_row, strict=False))

    assert "Position_Evidence" in header
    assert "Height_Evidence" in header
    assert "Notes_Evidence" in header
    assert "Replacement_Evidence" in header
    assert "Evidence_Gaps" in header
    assert row["Position_Evidence"] == "Surveyed grid + map coordinates"
    assert row["Height_Evidence"] == "Captured"
    assert row["Notes_Evidence"] == "Missing"
    assert row["Replacement_Evidence"] == "Inferred nearby EXpole (1.5m)"
    assert "replacement proximity inferred" in row["Evidence_Gaps"]


# ── 6. Reviewed route-sequence export uses override ──────────────────────────


def test_export_uses_override(client_and_root):
    client, root = client_and_root
    _make_file_slot(root, "P001", "F001")
    override = {
        "expole_point_id": "20",
        "original_matched_to": "10",
        "reviewed_matched_to": "11",
    }
    client.post(
        "/api/project/P001/file/F001/review",
        json={"review_status": "reviewed", "review_notes": "", "pairing_overrides": [override]},
    )
    resp = client.get("/d2d/export/project/P001/F001")
    assert resp.status_code == 200
    csv_text = resp.data.decode()
    # Chain row for point 11 should now reference EXpole 20 as its replacement
    lines = [line for line in csv_text.splitlines() if line.startswith("2,11,")]
    assert lines, "No chain row found for point 11"
    assert "20" in lines[0]


# ── 7. sequenced_route.json unchanged after override ─────────────────────────


def test_original_seq_preserved(client_and_root):
    client, root = client_and_root
    file_dir = _make_file_slot(root, "P001", "F001")
    original_seq = (file_dir / "sequenced_route.json").read_text()
    override = {
        "expole_point_id": "20",
        "original_matched_to": "10",
        "reviewed_matched_to": "11",
    }
    client.post(
        "/api/project/P001/file/F001/review",
        json={"review_status": "reviewed", "review_notes": "", "pairing_overrides": [override]},
    )
    current_seq = (file_dir / "sequenced_route.json").read_text()
    assert current_seq == original_seq


# ── 8. Reset review removes review.json ──────────────────────────────────────


def test_reset_review(client_and_root):
    client, root = client_and_root
    _make_file_slot(root, "P001", "F001")
    client.post(
        "/api/project/P001/file/F001/review",
        json={"review_status": "reviewed", "review_notes": "", "pairing_overrides": []},
    )
    review_path = root / "P001" / "files" / "F001" / "review.json"
    assert review_path.exists()
    resp = client.delete("/api/project/P001/file/F001/review")
    assert resp.status_code == 200
    assert resp.get_json()["ok"] is True
    assert not review_path.exists()
    # Export should revert to provisional
    resp2 = client.get("/d2d/export/project/P001/F001")
    assert "provisional" in resp2.data.decode().lower()


# ── 9. Existing exports work without review.json ─────────────────────────────


def test_exports_work_without_review(client_and_root):
    client, root = client_and_root
    _make_file_slot(root, "P001", "F001")
    resp_chain = client.get("/d2d/export/project/P001/F001")
    assert resp_chain.status_code == 200
    assert b"Point_ID" in resp_chain.data
    assert b"Design Route Sequence Export" in resp_chain.data
    resp_interleaved = client.get("/d2d/interleaved/project/P001/F001")
    assert resp_interleaved.status_code == 200
    assert b"Point_ID" in resp_interleaved.data
    assert b"Raw Working Audit" in resp_interleaved.data
    assert b"Position_Evidence" in resp_interleaved.data
    assert b"Evidence_Gaps" in resp_interleaved.data
    assert "P001_F001_raw_working_audit.csv" in resp_interleaved.headers["Content-Disposition"]
