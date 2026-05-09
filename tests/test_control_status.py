from __future__ import annotations

import importlib
import json
from pathlib import Path

from scripts import control_status


def _configure_paths(tmp_path: Path, monkeypatch) -> Path:
    control = tmp_path / "AI_CONTROL"
    monkeypatch.setattr(control_status, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(control_status, "AI_CONTROL_DIR", control)
    monkeypatch.setattr(control_status, "PROJECT_BOARD_PATH", control / "00_PROJECT_BOARD.md")
    monkeypatch.setattr(control_status, "HANDOFF_PATH", control / "05_HANDOFF.md")
    monkeypatch.setattr(control_status, "VALIDATION_LOG_PATH", control / "04_VALIDATION_LOG.md")
    monkeypatch.setattr(control_status, "WORKER_RULES_PATH", control / "06_WORKER_RULES.md")
    return control


def _seed_control_files(control: Path) -> None:
    control.mkdir(parents=True, exist_ok=True)
    (control / "00_PROJECT_BOARD.md").write_text(
        "# Board\n\n"
        "## Current stable milestone\n\n"
        "- `project-control-center-foundation-complete`\n"
        "- validation clean\n\n"
        "## Active task\n\n"
        "<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->\n"
        "- Task: Worker Bootstrap\n"
        "- Branch: `codex/bootstrap`\n"
        "- Owner: codex\n"
        "- Status: in_progress\n"
        "- Summary: Add checklists\n"
        "<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->\n",
        encoding="utf-8",
    )
    (control / "05_HANDOFF.md").write_text(
        "# Handoff\n\n"
        "## Summary\n\n"
        "- Master is stable.\n"
        "- Active branch is `codex/bootstrap`.\n"
        "- Runtime files must remain untouched.\n\n"
        "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->\n"
        "- Task: Worker Bootstrap\n"
        "- Branch: `codex/bootstrap`\n"
        "- Status: in_progress\n"
        "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->\n",
        encoding="utf-8",
    )
    (control / "04_VALIDATION_LOG.md").write_text(
        "# Validation\n\n"
        "## Validation Runs\n\n"
        "### 2026-05-09T21:00:00Z\n\n"
        "- Branch: `codex/bootstrap`\n"
        "- Command run: `pytest -v`\n"
        "- Verdict: pass\n",
        encoding="utf-8",
    )
    (control / "06_WORKER_RULES.md").write_text(
        "# Rules\n\n"
        "## Required Reading\n\n"
        "- Read `AI_CONTROL/01_CURRENT_STATE.md`.\n"
        "- Run `python3 scripts/control_status.py`.\n"
        "- Use the checklists before handoff.\n",
        encoding="utf-8",
    )


class _Result:
    def __init__(self, returncode: int, stdout: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout


def test_module_exposes_main_function() -> None:
    module = importlib.import_module("scripts.control_status")
    assert callable(module.main)


def test_text_output_includes_branch_status_task_handoff_and_validation(
    tmp_path, monkeypatch, capsys
) -> None:
    control = _configure_paths(tmp_path, monkeypatch)
    _seed_control_files(control)

    def fake_run(args, cwd, capture_output, text, check):
        if args == ["git", "branch", "--show-current"]:
            return _Result(0, "codex/bootstrap\n")
        if args == ["git", "status", "--short"]:
            return _Result(0, "")
        raise AssertionError(f"unexpected git call: {args}")

    monkeypatch.setattr(control_status.subprocess, "run", fake_run)

    result = control_status.main([])
    output = capsys.readouterr().out

    assert result == 0
    assert "Git branch: codex/bootstrap" in output
    assert "Git status: clean" in output
    assert "Active task:" in output
    assert "Handoff summary:" in output
    assert "Latest validation:" in output
    assert "Worker rules reminder:" in output


def test_json_output_is_valid_json(tmp_path, monkeypatch, capsys) -> None:
    control = _configure_paths(tmp_path, monkeypatch)
    _seed_control_files(control)

    def fake_run(args, cwd, capture_output, text, check):
        if args == ["git", "branch", "--show-current"]:
            return _Result(0, "codex/bootstrap\n")
        if args == ["git", "status", "--short"]:
            return _Result(0, " M AI_CONTROL/05_HANDOFF.md\n")
        raise AssertionError(f"unexpected git call: {args}")

    monkeypatch.setattr(control_status.subprocess, "run", fake_run)

    control_status.main(["--json"])
    payload = json.loads(capsys.readouterr().out)

    assert payload["branch"] == "codex/bootstrap"
    assert payload["active_task"]["task"] == "Worker Bootstrap"
    assert "latest_validation" in payload
    assert "warnings" in payload


def test_missing_control_files_are_handled_gracefully(tmp_path, monkeypatch, capsys) -> None:
    _configure_paths(tmp_path, monkeypatch)

    def fake_run(args, cwd, capture_output, text, check):
        if args == ["git", "branch", "--show-current"]:
            return _Result(0, "codex/bootstrap\n")
        if args == ["git", "status", "--short"]:
            return _Result(0, "")
        raise AssertionError(f"unexpected git call: {args}")

    monkeypatch.setattr(control_status.subprocess, "run", fake_run)

    result = control_status.main([])
    output = capsys.readouterr().out

    assert result == 0
    assert "missing control files" in output


def test_git_command_failure_is_handled_gracefully(tmp_path, monkeypatch, capsys) -> None:
    control = _configure_paths(tmp_path, monkeypatch)
    _seed_control_files(control)

    def fake_run(args, cwd, capture_output, text, check):
        raise FileNotFoundError("git not installed")

    monkeypatch.setattr(control_status.subprocess, "run", fake_run)

    result = control_status.main([])
    output = capsys.readouterr().out

    assert result == 0
    assert "Git branch: unknown" in output
    assert "git status unavailable" in output


def test_dirty_working_tree_warning_appears_when_git_status_is_not_clean(
    tmp_path, monkeypatch, capsys
) -> None:
    control = _configure_paths(tmp_path, monkeypatch)
    _seed_control_files(control)

    def fake_run(args, cwd, capture_output, text, check):
        if args == ["git", "branch", "--show-current"]:
            return _Result(0, "codex/bootstrap\n")
        if args == ["git", "status", "--short"]:
            return _Result(0, " M AI_CONTROL/05_HANDOFF.md\n?? scripts/control_status.py\n")
        raise AssertionError(f"unexpected git call: {args}")

    monkeypatch.setattr(control_status.subprocess, "run", fake_run)

    control_status.main([])
    output = capsys.readouterr().out

    assert "working tree is dirty" in output
    assert "Git status: M AI_CONTROL/05_HANDOFF.md; ?? scripts/control_status.py" in output


def test_script_does_not_write_files(tmp_path, monkeypatch) -> None:
    _configure_paths(tmp_path, monkeypatch)
    before = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    def fake_run(args, cwd, capture_output, text, check):
        if args == ["git", "branch", "--show-current"]:
            return _Result(0, "codex/bootstrap\n")
        if args == ["git", "status", "--short"]:
            return _Result(0, "")
        raise AssertionError(f"unexpected git call: {args}")

    monkeypatch.setattr(control_status.subprocess, "run", fake_run)

    control_status.main(["--json"])
    after = sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*"))

    assert before == after
