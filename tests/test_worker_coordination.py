"""Tests for worker coordination hardening scripts.

Tests worker_safety_check, merge_safety_check, branch_health, repo_health,
and the dirty-tree refusal added to start_task.
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import branch_health as bh  # noqa: E402
import merge_safety_check as msc  # noqa: E402
import repo_health as rh  # noqa: E402
import worker_safety_check as wsc  # noqa: E402
from start_task import _git_ai_control_dirty, refuse_if_dirty_control_files  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_run(stdout: str = "", returncode: int = 0):
    """Return a mock for subprocess.run returning fixed stdout."""
    m = MagicMock()
    m.returncode = returncode
    m.stdout = stdout
    m.stderr = ""
    return m


# ---------------------------------------------------------------------------
# worker_safety_check tests
# ---------------------------------------------------------------------------


class TestWorkerSafetyCheckWorkingTree:
    def test_clean_tree_is_ok(self):
        with patch("worker_safety_check._run", return_value=(0, "", "")):
            level, msg = wsc.check_git_working_tree()
        assert level == wsc._OK

    def test_aicontrol_dirty_is_block(self):
        dirty = " M AI_CONTROL/00_PROJECT_BOARD.md"
        with patch("worker_safety_check._run", return_value=(0, dirty, "")):
            level, msg = wsc.check_git_working_tree()
        assert level == wsc._BLOCKING
        assert "AI_CONTROL" in msg

    def test_non_aicontrol_dirty_is_warning(self):
        dirty = " M app/static/js/map-viewer.js"
        with patch("worker_safety_check._run", return_value=(0, dirty, "")):
            level, msg = wsc.check_git_working_tree()
        assert level == wsc._WARNING


class TestWorkerSafetyCheckBranchName:
    def test_matching_branch_is_ok(self):
        with patch("worker_safety_check._run", return_value=(0, "my-branch", "")):
            level, _ = wsc.check_branch_name("my-branch")
        assert level == wsc._OK

    def test_mismatched_branch_is_block(self):
        with patch("worker_safety_check._run", return_value=(0, "other-branch", "")):
            level, msg = wsc.check_branch_name("expected-branch")
        assert level == wsc._BLOCKING
        assert "expected-branch" in msg

    def test_no_expected_branch_is_warning(self):
        with patch("worker_safety_check._run", return_value=(0, "some-branch", "")):
            level, _ = wsc.check_branch_name(None)
        assert level == wsc._WARNING


class TestWorkerSafetyCheckAIControlSlot:
    def test_free_slot_is_ok(self, tmp_path):
        with patch("worker_safety_check.AI_CONTROL_DIR", tmp_path):
            level, _ = wsc.check_aicontrol_slot_free("99")
        assert level == wsc._OK

    def test_occupied_slot_is_block(self, tmp_path):
        (tmp_path / "43_SOME_DOC.md").touch()
        with patch("worker_safety_check.AI_CONTROL_DIR", tmp_path):
            level, msg = wsc.check_aicontrol_slot_free("43")
        assert level == wsc._BLOCKING
        assert "43_SOME_DOC.md" in msg

    def test_no_slot_requested_is_ok(self):
        level, _ = wsc.check_aicontrol_slot_free(None)
        assert level == wsc._OK


class TestWorkerSafetyCheckMapViewer:
    def test_no_diff_when_guard_active_is_ok(self):
        with patch("worker_safety_check._run", return_value=(0, "", "")):
            level, _ = wsc.check_map_viewer_untouched(True)
        assert level == wsc._OK

    def test_diff_when_guard_active_is_block(self):
        diff = "+some changed line\n-removed line\n"
        with patch("worker_safety_check._run", return_value=(0, diff, "")):
            level, msg = wsc.check_map_viewer_untouched(True)
        assert level == wsc._BLOCKING

    def test_guard_not_requested_is_ok(self):
        level, _ = wsc.check_map_viewer_untouched(False)
        assert level == wsc._OK


class TestWorkerSafetyCheckRunAll:
    def test_clean_working_tree_check_passes(self):
        with patch("worker_safety_check._run", return_value=(0, "", "")):
            results = wsc.run_checks(
                expected_branch=None,
                expected_task=None,
                aicontrol_slot=None,
                forbid_map_viewer=False,
                checks=["git_working_tree"],
            )
        assert wsc.print_report(results) == 0

    def test_block_returns_one(self):
        results = [{"check": "x", "level": wsc._BLOCKING, "message": "fail"}]
        assert wsc.print_report(results) == 1

    def test_warn_only_returns_two(self):
        results = [{"check": "x", "level": wsc._WARNING, "message": "warn"}]
        assert wsc.print_report(results) == 2


class TestWorkerSafetyCheckParallelTask:
    def test_matching_task_is_ok(self, tmp_path):
        board = (
            "# Board\n"
            "<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->\n"
            "- Task: My Task\n"
            "- Owner: claude-code\n"
            "<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->\n"
        )
        board_path = tmp_path / "00_PROJECT_BOARD.md"
        board_path.write_text(board)
        with patch("worker_safety_check.PROJECT_BOARD_PATH", board_path):
            level, _ = wsc.check_no_parallel_active_task("My Task")
        assert level == wsc._OK

    def test_different_task_is_block(self, tmp_path):
        board = (
            "# Board\n"
            "<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->\n"
            "- Task: Other Task\n"
            "- Owner: codex\n"
            "<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->\n"
        )
        board_path = tmp_path / "00_PROJECT_BOARD.md"
        board_path.write_text(board)
        with patch("worker_safety_check.PROJECT_BOARD_PATH", board_path):
            level, msg = wsc.check_no_parallel_active_task("My Task")
        assert level == wsc._BLOCKING
        assert "Other Task" in msg


# ---------------------------------------------------------------------------
# merge_safety_check tests
# ---------------------------------------------------------------------------


class TestMergeSafetyCheckBranchExists:
    def test_existing_branch_is_ok(self):
        with patch("merge_safety_check._run", return_value=(0, "", "")):
            level, _ = msc.check_branch_exists("some-branch")
        assert level == msc._OK

    def test_missing_branch_is_block(self):
        with patch("merge_safety_check._run", return_value=(1, "", "error")):
            level, _ = msc.check_branch_exists("ghost-branch")
        assert level == msc._BLOCKING


class TestMergeSafetyCheckCommitCounts:
    def test_zero_behind_ok(self):
        with patch("merge_safety_check._run", return_value=(0, "0\t5", "")):
            level, msg, data = msc.check_commit_counts("my-branch")
        assert level == msc._OK
        assert data["behind"] == 0

    def test_identical_is_warning(self):
        with patch("merge_safety_check._run", return_value=(0, "0\t0", "")):
            level, _, _ = msc.check_commit_counts("my-branch")
        assert level == msc._WARNING

    def test_very_far_behind_is_block(self):
        with patch("merge_safety_check._run", return_value=(0, "51\t3", "")):
            level, msg, _ = msc.check_commit_counts("my-branch")
        assert level == msc._BLOCKING
        assert "51" in msg


class TestMergeSafetyCheckAlreadyMerged:
    def test_not_merged_is_ok(self):
        with patch("merge_safety_check._run", return_value=(0, "other-branch\n", "")):
            level, _ = msc.check_branch_merged_status("my-branch")
        assert level == msc._OK

    def test_already_merged_is_warning(self):
        with patch("merge_safety_check._run", return_value=(0, "my-branch\nmaster\n", "")):
            level, msg = msc.check_branch_merged_status("my-branch")
        assert level == msc._WARNING
        assert "already merged" in msg


class TestMergeSafetyCheckAIControlNumbering:
    def test_no_changes_is_ok(self):
        with patch("merge_safety_check._run", return_value=(0, "", "")):
            level, _ = msc.check_aicontrol_numbering("branch")
        assert level == msc._OK

    def test_collision_is_block(self, tmp_path):
        (tmp_path / "22_EXISTING.md").touch()
        diff_output = "AI_CONTROL/22_NEW_DOC.md\napp/some_file.py\n"
        with (
            patch("merge_safety_check._run", return_value=(0, diff_output, "")),
            patch("merge_safety_check.REPO_ROOT", tmp_path),
        ):
            ai_dir = tmp_path / "AI_CONTROL"
            ai_dir.mkdir()
            (ai_dir / "22_EXISTING.md").touch()
            with patch("merge_safety_check.REPO_ROOT", tmp_path):
                level, msg = msc.check_aicontrol_numbering("branch")
        assert level == msc._BLOCKING
        assert "22" in msg

    def test_no_collision_non_numeric_prefix_is_ok(self, tmp_path):
        diff_output = "AI_CONTROL/AUD_NEW_DOC.md\n"
        with patch("merge_safety_check._run", return_value=(0, diff_output, "")):
            level, _ = msc.check_aicontrol_numbering("branch")
        assert level == msc._OK


class TestMergeSafetyCheckMapViewerRegression:
    def test_equal_guards_is_ok(self):
        content = "hasValue(x)\nhasValue(y)\n"
        with patch("merge_safety_check._run", return_value=(0, content, "")):
            level, _ = msc.check_map_viewer_regression("branch")
        assert level == msc._OK

    def test_fewer_guards_in_branch_is_block(self):
        def side_effect(args):
            if "master:app" in args[-1]:
                return 0, "hasValue(a)\nhasValue(b)\nhasValue(c)\n", ""
            return 0, "hasValue(a)\n", ""

        with patch("merge_safety_check._run", side_effect=side_effect):
            level, msg = msc.check_map_viewer_regression("branch")
        assert level == msc._BLOCKING
        assert "regress" in msg.lower()


# ---------------------------------------------------------------------------
# branch_health tests
# ---------------------------------------------------------------------------


class TestBranchHealthListAllBranches:
    def test_plus_prefix_stripped(self):
        # git branch -a outputs "+ branch-name" for worktree-checked-out branches
        raw = "  master\n* current-branch\n+ codex/c2f-review-focus-issue-filtering\n"
        with patch("branch_health._run", return_value=(0, raw, "")):
            branches = bh.list_all_branches()
        assert "codex/c2f-review-focus-issue-filtering" in branches
        assert "+ codex/c2f-review-focus-issue-filtering" not in branches

    def test_star_prefix_stripped(self):
        raw = "* main\n  feature/abc\n"
        with patch("branch_health._run", return_value=(0, raw, "")):
            branches = bh.list_all_branches()
        assert "main" in branches
        assert "* main" not in branches


class TestBranchHealthClassification:
    def test_known_delete_now_branch(self):
        with (
            patch("branch_health._run", return_value=(0, "", "")),
            patch("branch_health.is_merged", return_value=True),
            patch("branch_health.get_commit_counts", return_value=(0, 0)),
            patch("branch_health.get_last_commit_date", return_value="2026-05-01"),
        ):
            info = bh.classify_branch("codex/c2d-span-validity")
        assert info.bucket == bh.BUCKET_DELETE_NOW

    def test_unknown_merged_branch_gets_delete_after_confirm(self):
        with (
            patch("branch_health.is_merged", return_value=True),
            patch("branch_health.get_commit_counts", return_value=(0, 0)),
            patch("branch_health.get_last_commit_date", return_value="2026-05-01"),
        ):
            info = bh.classify_branch("some/new-branch-not-in-catalogue")
        assert info.bucket == bh.BUCKET_DELETE_AFTER_CONFIRM

    def test_large_unmerged_unknown_branch_gets_manual_inspection(self):
        with (
            patch("branch_health.is_merged", return_value=False),
            patch("branch_health.get_commit_counts", return_value=(5, 35)),
            patch("branch_health.get_last_commit_date", return_value="2026-04-01"),
        ):
            info = bh.classify_branch("mystery/giant-branch")
        assert info.bucket == bh.BUCKET_MANUAL_INSPECTION

    def test_cherry_pick_branch_has_high_risk(self):
        with (
            patch("branch_health.is_merged", return_value=False),
            patch("branch_health.get_commit_counts", return_value=(10, 5)),
            patch("branch_health.get_last_commit_date", return_value="2026-05-01"),
        ):
            info = bh.classify_branch("claude-code/c2e2-support-suite")
        assert info.bucket == bh.BUCKET_CHERRY_PICK_ONLY
        assert info.risk == "high"

    def test_master_is_do_not_touch(self):
        info = bh.classify_branch("master")
        assert info.bucket == bh.BUCKET_DO_NOT_TOUCH


# ---------------------------------------------------------------------------
# repo_health tests
# ---------------------------------------------------------------------------


class TestRepoHealthRequiredFiles:
    def test_all_files_present_is_ok(self, tmp_path):
        for f in rh._REQUIRED_CONTROL_FILES:
            (tmp_path / f).touch()
        with patch("repo_health.AI_CONTROL_DIR", tmp_path):
            level, _ = rh.check_required_control_files()
        assert level == rh._OK

    def test_missing_file_is_critical(self, tmp_path):
        # Write all but one
        for f in rh._REQUIRED_CONTROL_FILES[:-1]:
            (tmp_path / f).touch()
        with patch("repo_health.AI_CONTROL_DIR", tmp_path):
            level, msg = rh.check_required_control_files()
        assert level == rh._CRITICAL
        assert rh._REQUIRED_CONTROL_FILES[-1] in msg


class TestRepoHealthSupersededFiles:
    def test_no_superseded_is_ok(self, tmp_path):
        with patch("repo_health.AI_CONTROL_DIR", tmp_path):
            level, _ = rh.check_superseded_files()
        assert level == rh._OK

    def test_superseded_file_without_header_is_warning(self, tmp_path):
        # File exists but has no SUPERSEDED header — should warn
        (tmp_path / rh._SUPERSEDED_FILES[0]).write_text("# Old doc\nsome content\n")
        with patch("repo_health.AI_CONTROL_DIR", tmp_path):
            level, msg = rh.check_superseded_files()
        assert level == rh._WARNING
        assert "header" in msg.lower()

    def test_superseded_file_with_header_is_ok(self, tmp_path):
        # File exists and has a SUPERSEDED header — should pass
        fname = rh._SUPERSEDED_FILES[0]
        (tmp_path / fname).write_text(
            "> **SUPERSEDED — Do not use as source of truth.**\n# Old doc\n"
        )
        with patch("repo_health.AI_CONTROL_DIR", tmp_path):
            level, msg = rh.check_superseded_files()
        assert level == rh._OK


class TestRepoHealthNumberingCollisions:
    def test_no_collisions_is_ok(self, tmp_path):
        (tmp_path / "01_ALPHA.md").touch()
        (tmp_path / "02_BETA.md").touch()
        with patch("repo_health.AI_CONTROL_DIR", tmp_path):
            level, _ = rh.check_aicontrol_numbering_collisions()
        assert level == rh._OK

    def test_collision_is_warning(self, tmp_path):
        (tmp_path / "01_ALPHA.md").touch()
        (tmp_path / "01_BETA.md").touch()
        with patch("repo_health.AI_CONTROL_DIR", tmp_path):
            level, msg = rh.check_aicontrol_numbering_collisions()
        assert level == rh._WARNING
        assert "01" in msg


class TestRepoHealthActiveTaskConsistency:
    def test_board_and_handoff_agree_is_ok(self, tmp_path):
        board = (
            "<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->\n"
            "- Branch: `feature/abc`\n"
            "<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->\n"
        )
        handoff = (
            "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->\n"
            "- Branch: `feature/abc`\n"
            "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->\n"
        )
        (tmp_path / "00_PROJECT_BOARD.md").write_text(board)
        (tmp_path / "05_HANDOFF.md").write_text(handoff)
        with patch("repo_health.AI_CONTROL_DIR", tmp_path):
            level, _ = rh.check_active_task_consistency()
        assert level == rh._OK

    def test_board_and_handoff_disagree_is_critical(self, tmp_path):
        board = (
            "<!-- PROJECT_CONTROL:ACTIVE_TASK_START -->\n"
            "- Branch: `feature/abc`\n"
            "<!-- PROJECT_CONTROL:ACTIVE_TASK_END -->\n"
        )
        handoff = (
            "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_START -->\n"
            "- Branch: `feature/xyz`\n"
            "<!-- PROJECT_CONTROL:HANDOFF_ACTIVE_END -->\n"
        )
        (tmp_path / "00_PROJECT_BOARD.md").write_text(board)
        (tmp_path / "05_HANDOFF.md").write_text(handoff)
        with patch("repo_health.AI_CONTROL_DIR", tmp_path):
            level, msg = rh.check_active_task_consistency()
        assert level == rh._CRITICAL
        assert "abc" in msg and "xyz" in msg


class TestRepoHealthBranchPrefix:
    def test_valid_codex_prefix_is_ok(self):
        with patch("repo_health._run", return_value=(0, "codex/my-feature", "")):
            level, _ = rh.check_branch_is_prefixed()
        assert level == rh._OK

    def test_valid_claude_code_prefix_is_ok(self):
        with patch("repo_health._run", return_value=(0, "claude-code/hardening", "")):
            level, _ = rh.check_branch_is_prefixed()
        assert level == rh._OK

    def test_no_prefix_is_warning(self):
        with patch("repo_health._run", return_value=(0, "my-unprefixed-branch", "")):
            level, msg = rh.check_branch_is_prefixed()
        assert level == rh._WARNING
        assert "prefix" in msg.lower()


class TestRepoHealthExitCodes:
    def test_critical_exits_one(self):
        results = [{"check": "x", "level": rh._CRITICAL, "message": "bad"}]
        assert rh.print_report(results) == 1

    def test_warning_only_exits_two(self):
        results = [{"check": "x", "level": rh._WARNING, "message": "warn"}]
        assert rh.print_report(results) == 2

    def test_all_ok_exits_zero(self):
        results = [{"check": "x", "level": rh._OK, "message": "fine"}]
        assert rh.print_report(results) == 0


# ---------------------------------------------------------------------------
# start_task dirty-tree refusal tests
# ---------------------------------------------------------------------------


class TestStartTaskDirtyTreeRefusal:
    def test_clean_tree_passes(self):
        with patch(
            "start_task._git_ai_control_dirty",
            return_value=[],
        ):
            refuse_if_dirty_control_files()  # should not raise

    def test_dirty_aicontrol_raises_systemexit(self):
        dirty = [" M AI_CONTROL/00_PROJECT_BOARD.md"]
        with (
            patch("start_task._git_ai_control_dirty", return_value=dirty),
            pytest.raises(SystemExit) as exc_info,
        ):
            refuse_if_dirty_control_files()
        assert exc_info.value.code == 1

    def test_git_aicontrol_dirty_returns_only_ai_control_lines(self):
        stdout = " M app/file.py\n M AI_CONTROL/05_HANDOFF.md\n?? scripts/new.py\n"
        with patch(
            "subprocess.run",
            return_value=_mock_run(stdout=stdout),
        ):
            dirty = _git_ai_control_dirty()
        assert len(dirty) == 1
        assert "AI_CONTROL" in dirty[0]
