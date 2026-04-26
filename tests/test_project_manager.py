"""Tests for app/project_manager.py — project data layer."""

from __future__ import annotations

import json

from app.project_manager import (
    add_file_slot,
    create_project,
    list_projects,
    load_project,
    next_file_id,
    next_project_id,
    refresh_project_summary,
    suggest_project_name,
)

# ---------------------------------------------------------------------------
# next_project_id
# ---------------------------------------------------------------------------


def test_next_project_id_empty_dir(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    assert next_project_id(root) == "P001"


def test_next_project_id_missing_dir(tmp_path):
    root = tmp_path / "projects"
    assert next_project_id(root) == "P001"


def test_next_project_id_increments(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    (root / "P001").mkdir()
    (root / "P002").mkdir()
    assert next_project_id(root) == "P003"


def test_next_project_id_skips_non_project_dirs(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    (root / "P001").mkdir()
    (root / "some_other_dir").mkdir()
    assert next_project_id(root) == "P002"


# ---------------------------------------------------------------------------
# next_file_id
# ---------------------------------------------------------------------------


def test_next_file_id_no_files_dir(tmp_path):
    project_dir = tmp_path / "P001"
    project_dir.mkdir()
    assert next_file_id(project_dir) == "F001"


def test_next_file_id_increments(tmp_path):
    project_dir = tmp_path / "P001"
    files_dir = project_dir / "files"
    files_dir.mkdir(parents=True)
    (files_dir / "F001").mkdir()
    (files_dir / "F002").mkdir()
    assert next_file_id(project_dir) == "F003"


# ---------------------------------------------------------------------------
# create_project
# ---------------------------------------------------------------------------


def test_create_project_returns_dict(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    project = create_project(root, "Test Project", "A description")
    assert project["project_id"] == "P001"
    assert project["name"] == "Test Project"
    assert project["description"] == "A description"
    assert project["files"] == []
    assert project["summary"]["total_files"] == 0


def test_create_project_writes_json(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    create_project(root, "My Job")
    json_path = root / "P001" / "project.json"
    assert json_path.exists()
    data = json.loads(json_path.read_text())
    assert data["project_id"] == "P001"
    assert data["name"] == "My Job"


def test_create_project_creates_files_subdir(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    create_project(root, "Test")
    assert (root / "P001" / "files").is_dir()


def test_create_project_sequential_ids(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    p1 = create_project(root, "First")
    p2 = create_project(root, "Second")
    assert p1["project_id"] == "P001"
    assert p2["project_id"] == "P002"


# ---------------------------------------------------------------------------
# load_project
# ---------------------------------------------------------------------------


def test_load_project_returns_dict(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    create_project(root, "Load Test")
    loaded = load_project(root, "P001")
    assert loaded is not None
    assert loaded["name"] == "Load Test"


def test_load_project_missing_returns_none(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    assert load_project(root, "P999") is None


# ---------------------------------------------------------------------------
# list_projects
# ---------------------------------------------------------------------------


def test_list_projects_empty(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    assert list_projects(root) == []


def test_list_projects_missing_dir(tmp_path):
    root = tmp_path / "projects"
    assert list_projects(root) == []


def test_list_projects_returns_all(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    create_project(root, "Alpha")
    create_project(root, "Beta")
    projects = list_projects(root)
    assert len(projects) == 2
    names = {p["name"] for p in projects}
    assert names == {"Alpha", "Beta"}


# ---------------------------------------------------------------------------
# add_file_slot
# ---------------------------------------------------------------------------


def test_add_file_slot_creates_dir_and_meta(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    create_project(root, "Test")
    file_id, file_dir = add_file_slot(root, "P001", "survey.csv")
    assert file_id == "F001"
    assert file_dir.is_dir()
    meta = json.loads((file_dir / "meta.json").read_text())
    assert meta["file_id"] == "F001"
    assert meta["filename"] == "survey.csv"
    assert meta["status"] == "awaiting_upload"


def test_add_file_slot_sequential(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    create_project(root, "Test")
    fid1, _ = add_file_slot(root, "P001", "a.csv")
    fid2, _ = add_file_slot(root, "P001", "b.csv")
    assert fid1 == "F001"
    assert fid2 == "F002"


# ---------------------------------------------------------------------------
# refresh_project_summary
# ---------------------------------------------------------------------------


def test_refresh_project_summary_aggregates_files(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    create_project(root, "Summary Test")

    fid1, f1_dir = add_file_slot(root, "P001", "a.csv")
    fid2, f2_dir = add_file_slot(root, "P001", "b.csv")

    # Simulate completed file metas
    for file_dir, poles, issues, rulepack in [
        (f1_dir, 50, 3, "SPEN_11kV"),
        (f2_dir, 30, 1, "NIE_11kV"),
    ]:
        meta = json.loads((file_dir / "meta.json").read_text())
        meta.update(
            {
                "status": "complete",
                "pole_count": poles,
                "issue_count": issues,
                "rulepack_id": rulepack,
                "pass_count": poles - issues,
                "warn_count": issues,
                "fail_count": 0,
            }
        )
        (file_dir / "meta.json").write_text(json.dumps(meta))

    refresh_project_summary(root, "P001")

    project = load_project(root, "P001")
    assert project["summary"]["total_files"] == 2
    assert project["summary"]["total_poles"] == 80
    assert project["summary"]["total_issues"] == 4
    assert set(project["summary"]["rulepacks_used"]) == {"SPEN_11kV", "NIE_11kV"}
    assert len(project["files"]) == 2


def test_refresh_project_summary_missing_project(tmp_path):
    root = tmp_path / "projects"
    root.mkdir()
    # Should not raise even if project doesn't exist
    refresh_project_summary(root, "P999")


# ---------------------------------------------------------------------------
# suggest_project_name
# ---------------------------------------------------------------------------


def test_suggest_project_name_underscore_three_parts():
    # 3-part underscore name: take first 2, drop trailing descriptor
    assert suggest_project_name("Gordon_Pt1_Original.csv") == "Gordon Pt1"


def test_suggest_project_name_dash_separator_stripped():
    # Trimble-style " - Descriptor" suffix removed
    assert suggest_project_name("Gordon Pt1 - Original.csv") == "Gordon Pt1"


def test_suggest_project_name_hyphens_preserved():
    # Hyphens in job numbers must not become spaces
    assert suggest_project_name("28-14 4-474.csv") == "28-14 4-474"


def test_suggest_project_name_two_part_underscore():
    # Two-part underscore name keeps both halves
    assert suggest_project_name("28-14_4-474.csv") == "28-14 4-474"


def test_suggest_project_name_empty_fallback():
    assert suggest_project_name(".csv") == "Unnamed Project"
