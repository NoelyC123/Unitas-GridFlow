from __future__ import annotations

from pathlib import Path

import pytest

from scripts import manual_review


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_resolve_project_file_and_project_shortcut(tmp_path, monkeypatch) -> None:
    projects = tmp_path / "projects"
    file_dir = projects / "P010" / "files" / "F001"
    file_dir.mkdir(parents=True)
    _write(projects / "P010" / "project.json", '{"project_id": "P010", "name": "Gordon"}')
    monkeypatch.setattr(manual_review, "PROJECTS_ROOT", projects)

    explicit = manual_review.resolve_job_target("P010/F001")
    shortcut = manual_review.resolve_job_target("P010")

    assert explicit.view_path == "/map/view/project/P010/F001"
    assert explicit.data_path == "/map/data/project/P010/F001"
    assert shortcut.label == "P010/F001"


def test_resolve_real_job_aliases_prefer_operational_project_files(tmp_path, monkeypatch) -> None:
    projects = tmp_path / "projects"
    (projects / "P008" / "files" / "F001").mkdir(parents=True)
    (projects / "P010" / "files" / "F001").mkdir(parents=True)
    _write(projects / "P008" / "project.json", '{"project_id": "P008", "name": "Bellsprings"}')
    _write(projects / "P010" / "project.json", '{"project_id": "P010", "name": "Gordon"}')
    monkeypatch.setattr(manual_review, "PROJECTS_ROOT", projects)

    assert manual_review.resolve_job_target("Gordon").label == "P010/F001"
    assert manual_review.resolve_job_target("Bellsprings").label == "P008/F001"


def test_resolve_legacy_job(tmp_path, monkeypatch) -> None:
    jobs = tmp_path / "jobs"
    (jobs / "J12345").mkdir(parents=True)
    monkeypatch.setattr(manual_review, "JOBS_ROOT", jobs)

    target = manual_review.resolve_job_target("J12345")

    assert target.kind == "legacy_job"
    assert target.view_path == "/map/view/J12345"


def test_load_simple_yaml_checklist(tmp_path) -> None:
    checklist = tmp_path / "popup.yml"
    _write(
        checklist,
        """
name: Popup checks
checks:
  - id: popup_core
    description: Popup includes key fields.
    type: popup_text_contains
    contains:
      - Identity
      - QA
  - id: route
    type: route_highlight_active
  - id: map_shell
    type: selector_visible
    selector: "#map"
  - id: c2e2_popup
    type: c2e2_support_popup_text_contains
    contains:
      - Identity and role
  - id: focus_blockers
    type: review_focus_category_active
    category: blockers
""",
    )

    checks = manual_review.load_checklist(checklist)

    assert checks[0]["id"] == "popup_core"
    assert checks[0]["contains"] == ["Identity", "QA"]
    assert checks[1]["type"] == "route_highlight_active"
    assert checks[2]["selector"] == "#map"
    assert checks[3]["type"] == "c2e2_support_popup_text_contains"
    assert checks[4]["type"] == "review_focus_category_active"
    assert checks[4]["category"] == "blockers"


def test_load_checklist_rejects_missing_id(tmp_path) -> None:
    checklist = tmp_path / "bad.yml"
    _write(
        checklist,
        """
checks:
  - type: selector_visible
    selector: "#map"
""",
    )

    with pytest.raises(ValueError, match="id and type"):
        manual_review.load_checklist(checklist)
