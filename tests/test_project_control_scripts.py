from __future__ import annotations

import importlib
import re
from pathlib import Path

from scripts import log_validation_run, log_worker_update, start_task


def _configure_paths(tmp_path: Path, monkeypatch) -> None:
    control = tmp_path / "AI_CONTROL"
    monkeypatch.setattr(start_task, "AI_CONTROL_DIR", control)
    monkeypatch.setattr(start_task, "PROJECT_BOARD_PATH", control / "00_PROJECT_BOARD.md")
    monkeypatch.setattr(start_task, "WORKER_LOG_PATH", control / "03_WORKER_LOG.md")
    monkeypatch.setattr(start_task, "HANDOFF_PATH", control / "05_HANDOFF.md")
    monkeypatch.setattr(log_worker_update, "AI_CONTROL_DIR", control)
    monkeypatch.setattr(log_worker_update, "WORKER_LOG_PATH", control / "03_WORKER_LOG.md")
    monkeypatch.setattr(log_validation_run, "AI_CONTROL_DIR", control)
    monkeypatch.setattr(log_validation_run, "VALIDATION_LOG_PATH", control / "04_VALIDATION_LOG.md")
    monkeypatch.setattr(log_validation_run, "WORKER_LOG_PATH", control / "03_WORKER_LOG.md")


def _seed_marked_files(tmp_path: Path) -> None:
    control = tmp_path / "AI_CONTROL"
    control.mkdir(parents=True, exist_ok=True)
    (control / "00_PROJECT_BOARD.md").write_text(
        "# Board\n\n"
        "<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->\nold\n"
        "<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->\n\noutside board\n",
        encoding="utf-8",
    )
    (control / "05_HANDOFF.md").write_text(
        "# Handoff\n\n"
        "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->\nold\n"
        "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->\n\noutside handoff\n",
        encoding="utf-8",
    )


def test_start_task_appends_worker_log_entry(tmp_path, monkeypatch) -> None:
    _configure_paths(tmp_path, monkeypatch)
    _seed_marked_files(tmp_path)

    result = start_task.main(
        [
            "--task",
            "Project Control Center Foundation",
            "--owner",
            "codex",
            "--branch",
            "codex/project-control-center-foundation",
        ]
    )

    log = (tmp_path / "AI_CONTROL" / "03_WORKER_LOG.md").read_text(encoding="utf-8")
    assert result == 0
    assert "Project Control Center Foundation" in log
    assert "codex/project-control-center-foundation" in log
    assert "Worker: codex" in log
    assert re.search(r"### \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", log)


def test_start_task_updates_handoff_active_task_section(tmp_path, monkeypatch) -> None:
    _configure_paths(tmp_path, monkeypatch)
    _seed_marked_files(tmp_path)

    start_task.main(
        [
            "--task",
            "Control Layer",
            "--owner",
            "codex",
            "--branch",
            "codex/control",
            "--status",
            "in_progress",
            "--summary",
            "Create control files",
        ]
    )

    handoff = (tmp_path / "AI_CONTROL" / "05_HANDOFF.md").read_text(encoding="utf-8")
    board = (tmp_path / "AI_CONTROL" / "00_PROJECT_BOARD.md").read_text(encoding="utf-8")
    assert "Task: Control Layer" in handoff
    assert "Branch: `codex/control`" in handoff
    assert "outside handoff" in handoff
    assert "Create control files" in board
    assert "outside board" in board


def test_log_worker_update_appends_without_overwriting(tmp_path, monkeypatch) -> None:
    _configure_paths(tmp_path, monkeypatch)
    control = tmp_path / "AI_CONTROL"
    control.mkdir(parents=True)
    (control / "03_WORKER_LOG.md").write_text("existing entry\n", encoding="utf-8")

    log_worker_update.main(
        [
            "--worker",
            "cursor",
            "--branch",
            "codex/control",
            "--summary",
            "Added docs",
            "--files",
            "README_PROJECT_CONTROL.md",
            "--validation",
            "pytest pending",
        ]
    )

    log = (control / "03_WORKER_LOG.md").read_text(encoding="utf-8")
    assert log.startswith("existing entry")
    assert "Worker: cursor" in log
    assert "Added docs" in log
    assert "README_PROJECT_CONTROL.md" in log


def test_log_validation_run_appends_validation_log_entry(tmp_path, monkeypatch) -> None:
    _configure_paths(tmp_path, monkeypatch)

    log_validation_run.main(
        [
            "--branch",
            "codex/control",
            "--status",
            "pass",
            "--command",
            "pytest -v",
        ]
    )

    validation = (tmp_path / "AI_CONTROL" / "04_VALIDATION_LOG.md").read_text(encoding="utf-8")
    worker = (tmp_path / "AI_CONTROL" / "03_WORKER_LOG.md").read_text(encoding="utf-8")
    assert "Branch: `codex/control`" in validation
    assert "Command run: `pytest -v`" in validation
    assert "Verdict: pass" in validation
    assert "Recorded validation run" in worker


def test_log_validation_run_records_jobs_and_report_path(tmp_path, monkeypatch) -> None:
    _configure_paths(tmp_path, monkeypatch)

    log_validation_run.main(
        [
            "--branch",
            "codex/control",
            "--commit",
            "abc123",
            "--status",
            "pass",
            "--jobs",
            "P008/F001",
            "P010",
            "--command",
            "pytest -v && pre-commit run --all-files",
            "--report",
            "validation_runs/20260509_192248/validation_report.md",
            "--failures",
            "[]",
        ]
    )

    validation = (tmp_path / "AI_CONTROL" / "04_VALIDATION_LOG.md").read_text(encoding="utf-8")
    assert "`P008/F001`, `P010`" in validation
    assert "`validation_runs/20260509_192248/validation_report.md`" in validation
    assert "failures.json status: []" in validation
    assert "Commit: `abc123`" in validation


def test_scripts_handle_missing_optional_args(tmp_path, monkeypatch) -> None:
    _configure_paths(tmp_path, monkeypatch)

    log_worker_update.main(
        ["--worker", "codex", "--branch", "codex/control", "--summary", "Short update"]
    )
    log_validation_run.main(
        ["--branch", "codex/control", "--status", "pass", "--command", "pytest"]
    )

    log = (tmp_path / "AI_CONTROL" / "03_WORKER_LOG.md").read_text(encoding="utf-8")
    validation = (tmp_path / "AI_CONTROL" / "04_VALIDATION_LOG.md").read_text(encoding="utf-8")
    assert "Files changed: n/a" in log
    assert "Validation state: not run" in log
    assert "Jobs tested: n/a" in validation
    assert "validation_runs report path: `n/a`" in validation


def test_start_task_appends_section_when_markers_are_missing(tmp_path, monkeypatch) -> None:
    _configure_paths(tmp_path, monkeypatch)
    control = tmp_path / "AI_CONTROL"
    control.mkdir(parents=True, exist_ok=True)
    (control / "00_PROJECT_BOARD.md").write_text("# Board\n\nno markers yet\n", encoding="utf-8")
    (control / "05_HANDOFF.md").write_text("# Handoff\n\nno markers yet\n", encoding="utf-8")

    start_task.main(
        [
            "--task",
            "Recovery Task",
            "--owner",
            "codex",
            "--branch",
            "codex/recovery",
            "--summary",
            "Re-seed markers after manual edit",
        ]
    )

    board = (control / "00_PROJECT_BOARD.md").read_text(encoding="utf-8")
    handoff = (control / "05_HANDOFF.md").read_text(encoding="utf-8")
    assert "no markers yet" in board
    assert "no markers yet" in handoff
    assert "<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->" in board
    assert "<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->" in board
    assert "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->" in handoff
    assert "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->" in handoff
    assert "Task: Recovery Task" in board
    assert "Task: Recovery Task" in handoff


def test_modules_expose_main_functions() -> None:
    for module_name in [
        "scripts.start_task",
        "scripts.log_worker_update",
        "scripts.log_validation_run",
    ]:
        module = importlib.import_module(module_name)
        assert callable(module.main)
