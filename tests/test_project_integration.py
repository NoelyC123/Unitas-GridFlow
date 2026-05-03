"""Integration tests for the project container system (Stage 3C).

Tests cover the full HTTP surface: presign, upload, finalize, status,
listing, and the map/PDF/design-chain project routes.  All filesystem I/O is
redirected to tmp_path via monkeypatch so the real uploads/ directory
is never touched.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app import create_app
from app.routes import api_jobs, api_projects, api_review, d2d_export, map_preview, pdf_reports

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_MOCK_CSV = "\n".join(
    [
        "asset_id,structure_type,height_m,material,location_name,easting,northing,latitude,longitude",
        "P-1001,Wood Pole,11.0,Wood,Dalton Road Junction,352841,503122,54.5210,-3.0140",
        "P-1002,Wood Pole,7.5,Wood,Back Lane Farm,352910,503088,54.5183,-3.0121",
        "P-1003,Steel Pole,28.0,Steel,Moorside Substation,352975,503200,54.5291,-3.0098",
        "P-1004,Wood Pole,12.5,,Hartley Bridge,353041,503155,54.5246,-3.0075",
        "P-1001,Wood Pole,13.0,Wood,Dalton Road Junction North,353100,503170,54.5261,-3.0052",
    ]
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _make_file_slot(projects_root: Path, project_id: str, file_id: str, filename: str) -> Path:
    """Create a minimal project + file slot on disk."""
    project_dir = projects_root / project_id
    file_dir = project_dir / "files" / file_id
    file_dir.mkdir(parents=True, exist_ok=True)

    _write_json(
        project_dir / "project.json",
        {
            "project_id": project_id,
            "name": "Test Project",
            "description": "",
            "created": "2026-01-01T00:00:00Z",
            "updated": "2026-01-01T00:00:00Z",
            "files": [],
            "summary": {
                "total_files": 0,
                "total_poles": 0,
                "total_issues": 0,
                "rulepacks_used": [],
            },
        },
    )
    _write_json(
        file_dir / "meta.json",
        {
            "project_id": project_id,
            "file_id": file_id,
            "filename": filename,
            "status": "awaiting_upload",
            "uploaded": "2026-01-01T00:00:00Z",
        },
    )
    return file_dir


# ---------------------------------------------------------------------------
# Fixture: app client + all project roots redirected to tmp_path
# ---------------------------------------------------------------------------


@pytest.fixture()
def client_and_root(tmp_path, monkeypatch):
    projects_root = tmp_path / "projects"
    projects_root.mkdir()

    monkeypatch.setattr(api_projects, "_PROJECTS_ROOT", projects_root)
    monkeypatch.setattr(api_review, "_PROJECTS_ROOT", projects_root)
    monkeypatch.setattr(map_preview, "PROJECTS_ROOT", projects_root)
    monkeypatch.setattr(pdf_reports, "PROJECTS_ROOT", projects_root)
    monkeypatch.setattr(d2d_export, "_PROJECTS_ROOT", projects_root)

    app = create_app()
    with app.test_client() as client:
        yield client, projects_root


# ---------------------------------------------------------------------------
# test_project_presign_creates_project_and_returns_urls
# ---------------------------------------------------------------------------


def test_project_presign_creates_project_and_returns_urls(client_and_root):
    client, projects_root = client_and_root

    response = client.post(
        "/api/project/presign",
        json={"filename": "Gordon_Pt1_Original.csv", "project_name": "Gordon Pt1"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert data["project_id"] == "P001"
    assert data["file_id"] == "F001"
    assert "/api/upload/project/P001/F001/" in data["url"]
    assert data["finalize_url"] == "/api/project/P001/file/F001/import"
    assert data["status_url"] == "/api/project/P001/file/F001/status"

    # project.json must exist on disk
    assert (projects_root / "P001" / "project.json").exists()
    project = json.loads((projects_root / "P001" / "project.json").read_text())
    assert project["name"] == "Gordon Pt1"


def test_project_presign_stores_intake_metadata(client_and_root):
    client, projects_root = client_and_root

    response = client.post(
        "/api/project/presign",
        json={
            "filename": "Gordon_Pt1_Original.csv",
            "project_name": "Gordon Pt1",
            "survey_day_label": "Day 1",
            "uploaded_by": "Surveyor",
            "surveyor_note": "Uploaded from van at end of day.",
        },
    )

    assert response.status_code == 200
    meta = json.loads((projects_root / "P001" / "files" / "F001" / "meta.json").read_text())
    assert meta["intake"]["survey_day_label"] == "Day 1"
    assert meta["intake"]["uploaded_by"] == "Surveyor"
    assert meta["intake"]["surveyor_note"] == "Uploaded from van at end of day."


# ---------------------------------------------------------------------------
# test_project_file_upload_endpoint_stores_file
# ---------------------------------------------------------------------------


def test_project_file_upload_endpoint_stores_file(client_and_root):
    client, projects_root = client_and_root

    file_dir = _make_file_slot(projects_root, "P001", "F001", "survey.csv")

    response = client.put(
        "/api/upload/project/P001/F001/survey.csv",
        data=_MOCK_CSV.encode(),
        content_type="text/csv",
    )

    assert response.status_code == 200
    assert (file_dir / "survey.csv").exists()
    meta = json.loads((file_dir / "meta.json").read_text())
    assert meta["status"] == "uploaded"
    assert meta["uploaded_size"] > 0


# ---------------------------------------------------------------------------
# test_project_finalize_success_path
# ---------------------------------------------------------------------------


def test_project_finalize_success_path(client_and_root, monkeypatch):
    client, projects_root = client_and_root

    file_dir = _make_file_slot(projects_root, "P001", "F001", "survey.csv")
    csv_path = file_dir / "survey.csv"
    csv_path.write_text(_MOCK_CSV, encoding="utf-8")

    # Tell meta where the uploaded file lives
    _write_json(
        file_dir / "meta.json",
        {
            "project_id": "P001",
            "file_id": "F001",
            "filename": "survey.csv",
            "status": "uploaded",
            "uploaded": "2026-01-01T00:00:00Z",
            "uploaded_path": str(csv_path),
        },
    )

    response = client.post(
        "/api/project/P001/file/F001/import",
        json={"dno": "SPEN_11kV"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert data["project_id"] == "P001"
    assert data["file_id"] == "F001"

    # project.json must be refreshed
    project = json.loads((projects_root / "P001" / "project.json").read_text())
    assert project["summary"]["total_files"] == 1
    assert project["summary"]["total_poles"] > 0


# ---------------------------------------------------------------------------
# test_project_finalize_failure_appears_in_project_overview
# ---------------------------------------------------------------------------


def test_project_finalize_failure_appears_in_project_overview(client_and_root):
    client, projects_root = client_and_root

    # File slot exists but uploaded_path is missing — process_job will error
    _make_file_slot(projects_root, "P001", "F001", "survey.csv")

    response = client.post(
        "/api/project/P001/file/F001/import",
        json={"dno": "SPEN_11kV"},
    )

    # 500 from the API because processing failed
    assert response.status_code == 500

    # project.json must still be refreshed so the file shows in the overview
    project = json.loads((projects_root / "P001" / "project.json").read_text())
    assert project["summary"]["total_files"] == 1
    file_entry = project["files"][0]
    assert file_entry["file_id"] == "F001"
    assert file_entry["status"] in ("error", "processing", "awaiting_upload")


# ---------------------------------------------------------------------------
# test_get_api_projects_returns_all_projects
# ---------------------------------------------------------------------------


def test_get_api_projects_returns_all_projects(client_and_root):
    client, projects_root = client_and_root

    for pid, name in [("P001", "Alpha"), ("P002", "Beta")]:
        project_dir = projects_root / pid
        project_dir.mkdir(parents=True, exist_ok=True)
        _write_json(
            project_dir / "project.json",
            {
                "project_id": pid,
                "name": name,
                "description": "",
                "created": "2026-01-01T00:00:00Z",
                "updated": "2026-01-01T00:00:00Z",
                "files": [],
                "summary": {
                    "total_files": 0,
                    "total_poles": 0,
                    "total_issues": 0,
                    "rulepacks_used": [],
                },
            },
        )

    response = client.get("/api/projects/")
    assert response.status_code == 200
    data = response.get_json()
    assert "projects" in data
    assert len(data["projects"]) == 2
    names = {p["name"] for p in data["projects"]}
    assert names == {"Alpha", "Beta"}


def test_projects_page_uses_scannable_card_layout(client_and_root):
    client, _projects_root = client_and_root

    response = client.get("/projects/")

    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "projects-card-list" in html
    assert "project-list-card" in html
    assert "project-meta-grid" in html
    assert "File count" in html
    assert "Last modified" in html
    assert "Processing complete" in html
    assert "Needs attention" in html
    assert "p.description" not in html
    assert "<th>Poles</th>" not in html
    assert "Applied QA Rules" not in html


def test_update_project_file_intake_feedback(client_and_root):
    client, projects_root = client_and_root

    _make_file_slot(projects_root, "P001", "F001", "survey.csv")

    response = client.post(
        "/api/project/P001/file/F001/intake",
        json={"office_feedback": "Please confirm EXpole pairing before export."},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["ok"] is True
    assert data["intake"]["office_feedback"] == "Please confirm EXpole pairing before export."

    meta = json.loads((projects_root / "P001" / "files" / "F001" / "meta.json").read_text())
    assert meta["intake"]["office_feedback"] == "Please confirm EXpole pairing before export."

    project = json.loads((projects_root / "P001" / "project.json").read_text())
    assert project["files"][0]["intake"]["office_feedback"] == (
        "Please confirm EXpole pairing before export."
    )


def test_review_save_refreshes_project_dashboard_status(client_and_root):
    client, projects_root = client_and_root

    _make_file_slot(projects_root, "P001", "F001", "survey.csv")

    response = client.post(
        "/api/project/P001/file/F001/review",
        json={"review_status": "reviewed", "review_notes": "Checked.", "pairing_overrides": []},
    )

    assert response.status_code == 200
    project = json.loads((projects_root / "P001" / "project.json").read_text())
    file_entry = project["files"][0]
    assert file_entry["review_status"] == "reviewed"
    assert file_entry["intake_status"] == "reviewed"


# ---------------------------------------------------------------------------
# test_legacy_jobs_route_still_works
# ---------------------------------------------------------------------------


def test_legacy_jobs_route_still_works(tmp_path, monkeypatch):
    jobs_root = tmp_path / "jobs"
    job_dir = jobs_root / "J10001"
    job_dir.mkdir(parents=True)

    _write_json(
        job_dir / "meta.json",
        {
            "job_id": "J10001",
            "status": "complete",
            "rulepack_id": "SPEN_11kV",
            "pole_count": 4,
            "issue_count": 1,
            "pass_count": 3,
            "warn_count": 1,
            "fail_count": 0,
            "filename": "survey.csv",
            "auto_normalized": True,
        },
    )

    monkeypatch.setattr(api_jobs, "JOBS_ROOT", jobs_root)

    app = create_app()
    client = app.test_client()

    response = client.get("/api/jobs/")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data["jobs"]) == 1
    assert data["jobs"][0]["job_id"] == "J10001"


# ---------------------------------------------------------------------------
# test_project_map_route_returns_200
# ---------------------------------------------------------------------------


def test_project_map_route_returns_200(client_and_root):
    client, projects_root = client_and_root

    _make_file_slot(projects_root, "P001", "F001", "survey.csv")

    response = client.get("/map/view/project/P001/F001")
    assert response.status_code == 200
    assert b"map" in response.data.lower()


def test_project_map_route_includes_review_focus_filters(client_and_root):
    client, projects_root = client_and_root

    _make_file_slot(projects_root, "P001", "F001", "survey.csv")

    response = client.get("/map/view/project/P001/F001")

    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Map Layers" in html
    assert "Review Focus" in html
    assert 'data-layer="existing"' in html
    assert 'data-layer="proposed"' in html
    assert 'data-layer="angle"' in html
    assert 'data-layer="stays"' in html
    assert 'data-layer="thirdparty"' in html
    assert 'data-layer="context"' in html
    assert 'data-layer="spans"' in html
    assert 'data-layer="cables"' in html
    assert "Context/Crossings" in html
    assert "Third-party infrastructure" in html
    assert 'data-focus="design-blockers"' in html
    assert 'data-focus="replacement-proximity"' in html
    assert 'data-focus="missing-height"' in html
    assert 'data-focus="missing-specification"' in html
    assert 'data-focus="angle-missing-stay"' in html
    assert 'data-focus="span-anomalies"' in html
    assert 'data-focus="span-crossing-risk"' in html
    assert 'data-focus="ug-cable-missing-spec"' in html
    assert 'data-focus="clearance-crossings"' in html
    assert 'data-focus="records-with-remarks"' in html
    assert "Replacement pairing signals" in html
    assert "Missing existing heights" in html
    assert "Proposed poles missing spec" in html
    assert "Angle poles missing stay evidence" in html
    assert "Span anomalies" in html
    assert "Span crossing / context review" in html
    assert "UG cable records missing spec" in html
    assert "Crossings needing clearance review" in html
    assert "Provisional route spans" in html
    assert "Suggested Existing/Proposed Match (map evidence only)" in html
    assert "Suggested replacement map links" in html
    assert "Asset Types (by shape)" in html
    assert "Existing pole (square)" in html
    assert "Proposed pole (circle)" in html
    assert "Angle function (A badge)" in html
    assert "Third-party infrastructure" in html
    assert "QA Status (by stroke color)" in html
    assert "popup-section-title" in html
    assert "popup-field-label" in html
    assert "Asset Lifecycle" in html
    assert "Existing Pole being Replaced (Recovered)" in html
    assert "Proposed Replacement Pole" in html
    assert "Survey Map Review" in html
    assert "Open review findings" in html
    assert "Detailed readiness, evidence, and completeness notes are collapsed" in html


def test_project_map_data_includes_design_chain_spans(client_and_root):
    client, projects_root = client_and_root

    file_dir = _make_file_slot(projects_root, "P001", "F001", "survey.csv")
    _write_json(
        file_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "features": [],
            "metadata": {"job_id": "P001/F001"},
        },
    )
    _write_json(
        file_dir / "sequenced_route.json",
        {
            "status": "ok",
            "chain": [
                {
                    "point_id": "P-1001",
                    "lat": 54.521,
                    "lon": -3.014,
                    "span_to_next_m": 75.0,
                    "section_id": "SEC-1",
                    "design_pole_number": 1,
                },
                {
                    "point_id": "P-1002",
                    "lat": 54.522,
                    "lon": -3.013,
                    "span_to_next_m": None,
                    "section_id": "SEC-1",
                    "design_pole_number": 2,
                },
            ],
        },
    )

    response = client.get("/map/data/project/P001/F001")

    assert response.status_code == 200
    data = response.get_json()
    assert data["metadata"]["design_chain_span_count"] == 1
    assert len(data.get("span_features") or []) == 1
    assert data["span_features"][0]["geometry"]["type"] == "LineString"
    assert data["design_chain_spans"] == [
        {
            "from_point_id": "P-1001",
            "to_point_id": "P-1002",
            "from_design_pole_no": 1,
            "to_design_pole_no": 2,
            "section_id": "SEC-1",
            "distance_m": 75.0,
            "coordinates": [[54.521, -3.014], [54.522, -3.013]],
        }
    ]


def test_project_map_data_backfills_c2_2_popup_display_fields(client_and_root):
    client, projects_root = client_and_root

    file_dir = _make_file_slot(projects_root, "P001", "F001", "survey.csv")
    _write_json(
        file_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-3.014, 54.521]},
                    "properties": {
                        "pole_id": "P-1001",
                        "structure_type": "EXpole",
                        "height": 9.2,
                        "voltage": "11kV",
                        "third_party_attachments": "streetlight",
                    },
                }
            ],
            "metadata": {"job_id": "P001/F001", "rulepack_id": "SPEN_11kV"},
        },
    )

    response = client.get("/map/data/project/P001/F001")

    assert response.status_code == 200
    props = response.get_json()["features"][0]["properties"]
    assert props["pole_class"] is None
    assert props["condition"] is None
    assert props.get("voltage") is None
    assert "voltage" not in props
    assert props["photo_links"] == []
    assert props["source_confidence"] == "legacy map data"
    assert props["source_confidence_detail"]["provenance"] == "legacy_map_data"
    assert props["source_confidence_detail"]["geometry_trust"] == "unverified"
    assert props["attachments_detail"]["has_attachments"] is True
    assert props["attachments_detail"]["attachment_types"] == ["streetlight"]
    assert props["height_confidence"]["level"] == "low"
    assert props["height_confidence"]["status"] == "warning"
    assert props["primary_type"] == "electric_network"
    assert props["popup_type_label"] == "Electric Network Structural Pole"
    assert props["is_structural_pole"] is True
    assert props["year_installed"] is None
    assert props["circuit_id"] is None
    assert props["stay_bearing"] is None
    assert props["action_required"] is None
    assert props["distance_from_route_m"] is None


def test_project_map_data_backfills_bt_expole_as_third_party(client_and_root):
    client, projects_root = client_and_root

    file_dir = _make_file_slot(projects_root, "P001", "F001", "survey.csv")
    _write_json(
        file_dir / "map_data.json",
        {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [-3.014, 54.521]},
                    "properties": {
                        "pole_id": "72",
                        "structure_type": "EXpole",
                        "name": "bt pole",
                        "height": 6.5,
                    },
                }
            ],
            "metadata": {"job_id": "P001/F001", "rulepack_id": "SPEN_11kV"},
        },
    )

    response = client.get("/map/data/project/P001/F001")

    assert response.status_code == 200
    props = response.get_json()["features"][0]["properties"]
    assert props["record_role"] == "third_party"
    assert props["asset_intent"] == "third_party_not_network"
    assert props["primary_type"] == "third_party_infrastructure"
    assert props["infrastructure_owner"] == "telecoms"
    assert props["popup_type_label"] == "Third-Party Telecoms Pole (BT/Openreach)"
    assert props["is_structural_pole"] is False


def test_project_detail_includes_responsive_file_card_layout(client_and_root):
    client, projects_root = client_and_root

    _make_file_slot(projects_root, "P001", "F001", "survey.csv")

    response = client.get("/project/P001")

    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "files-card-list" in html
    assert "project-file-card" in html
    assert "file-card-metrics" in html
    assert "file-action-grid" in html
    assert "Working View" in html
    assert "Review</a>" in html
    assert "Map</a>" in html
    assert "PDF</a>" in html
    assert "Suggested order: Review issues" in html
    assert "Designer reviewed" in html
    assert "review-pill" in html
    assert "Processing status only, not final design approval" in html
    assert "Complete = GridFlow has processed. Designer review still needed." in html
    assert "Survey records" in html
    assert "Survey file QA status" in html
    assert "Pass" in html
    assert "Warning" in html
    assert "Fail" in html
    assert "Pass / Warning / Fail counts" in html
    assert "QA findings" in html
    assert "Rulepack" in html
    assert "Design readiness: Provisional" in html
    assert "Raw survey intake requires office review" in html
    assert "Office feedback / intake note" in html
    assert "Survey is provisional and requires review before design export is final" in html
    assert "Complete = GridFlow has processed" in html
    assert "Design Route Sequence" in html


# ---------------------------------------------------------------------------
# test_project_pdf_route_returns_200
# ---------------------------------------------------------------------------


def test_project_pdf_route_returns_200(client_and_root):
    client, projects_root = client_and_root

    file_dir = _make_file_slot(projects_root, "P001", "F001", "survey.csv")

    _write_json(
        file_dir / "meta.json",
        {
            "project_id": "P001",
            "file_id": "F001",
            "filename": "survey.csv",
            "status": "complete",
            "uploaded": "2026-01-01T00:00:00Z",
            "rulepack_id": "SPEN_11kV",
            "pole_count": 4,
            "issue_count": 1,
        },
    )
    (file_dir / "issues.csv").write_text(
        "Issue,Row\n\"Missing material\",\"{'asset_id': 'P-1004'}\"\n",
        encoding="utf-8",
    )

    response = client.get("/pdf/qa/project/P001/F001")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")


def test_project_pdf_route_accepts_designer_review_context(client_and_root):
    client, projects_root = client_and_root

    file_dir = _make_file_slot(projects_root, "P001", "F001", "survey.csv")
    _write_json(
        file_dir / "meta.json",
        {
            "project_id": "P001",
            "file_id": "F001",
            "filename": "survey.csv",
            "status": "complete",
            "rulepack_id": "SPEN_11kV",
            "pole_count": 4,
            "issue_count": 0,
        },
    )
    _write_json(
        file_dir / "review.json",
        {
            "file_id": "F001",
            "review_status": "reviewed",
            "reviewed_at": "2026-04-28T12:00:00Z",
            "review_notes": "Checked proximity QA.",
            "pairing_overrides": [{"expole_point_id": "20", "reviewed_matched_to": "10"}],
        },
    )

    response = client.get("/pdf/qa/project/P001/F001")

    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")


# ---------------------------------------------------------------------------
# test_project_d2d_chain_route_returns_csv_when_seq_exists
# ---------------------------------------------------------------------------


def test_project_d2d_chain_route_returns_csv_when_seq_exists(client_and_root):
    client, projects_root = client_and_root

    file_dir = _make_file_slot(projects_root, "P001", "F001", "survey.csv")

    seq = {
        "status": "ok",
        "reason": "sequenced",
        "chain": [
            {
                "seq": 1,
                "point_id": "P-1001",
                "feature_code": "WP",
                "easting": 352841,
                "northing": 503122,
                "lat": 54.521,
                "lon": -3.014,
                "height": 11.0,
                "remark": "",
                "span_to_next_m": 75.0,
                "deviation_angle_deg": 0.0,
                "replaces_point_id": None,
                "replaces_distance_m": None,
                "candidate_section_break": False,
                "section_split_candidate": False,
                "section_id": "SEC-1",
                "section_boundary": "start",
                "design_pole_number": 1,
                "section_sequence_number": 1,
                "sequence_confidence": "high",
            }
        ],
        "sections": [],
        "matched_expoles": [],
        "unmatched_expoles": [],
        "context_features": [],
        "detached_records": [],
        "interleaved_view": [],
        "config_used": {},
        "summary": {},
    }
    _write_json(file_dir / "sequenced_route.json", seq)

    response = client.get("/d2d/export/project/P001/F001")
    assert response.status_code == 200
    assert "text/csv" in response.content_type
