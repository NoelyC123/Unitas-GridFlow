#!/usr/bin/env python3
"""Pre-merge safety check for GridFlow branches.

Run this before writing a merge spec or before merging any branch into master.
Outputs a report suitable for inclusion in the merge commit message.

Exit codes:
  0  Safe to merge.
  1  Blocking issues — do NOT merge without resolving.
  2  Warnings — review before merging.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
_BLOCKING = "BLOCK"
_WARNING = "WARN"
_OK = "OK"

# High-blast-radius files: merge conflicts here are most dangerous.
_SENSITIVE_FILES = [
    "app/static/js/map-viewer.js",
    "AI_CONTROL/00_PROJECT_BOARD.md",
    "AI_CONTROL/05_HANDOFF.md",
    "AI_CONTROL/03_WORKER_LOG.md",
]


def _run(args: list[str]) -> tuple[int, str, str]:
    try:
        r = subprocess.run(
            args,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except OSError as exc:
        return 1, "", str(exc)


def check_branch_exists(branch: str) -> tuple[str, str]:
    rc, _, _ = _run(["git", "rev-parse", "--verify", branch])
    if rc != 0:
        return _BLOCKING, f"Branch `{branch}` does not exist."
    return _OK, f"Branch `{branch}` exists."


def check_commit_counts(branch: str, base: str = "master") -> tuple[str, str, dict]:
    _, stdout, _ = _run(["git", "rev-list", "--left-right", "--count", f"{base}...{branch}"])
    if not stdout or "\t" not in stdout:
        return _WARNING, f"Cannot compute commit counts between {base} and {branch}.", {}
    behind, ahead = stdout.split("\t", 1)
    try:
        b = int(behind.strip())
        a = int(ahead.strip())
    except ValueError:
        return _WARNING, "Cannot parse commit counts.", {}
    data = {"base": base, "branch": branch, "behind": b, "ahead": a}
    if b == 0 and a == 0:
        return _WARNING, f"`{branch}` is identical to `{base}` — nothing to merge.", data
    if b > 50:
        return (
            _BLOCKING,
            f"`{branch}` is {b} commits behind `{base}` and {a} ahead. "
            "Rebase first; a direct merge is high-risk.",
            data,
        )
    msg = f"`{branch}` is {b} behind / {a} ahead of `{base}`."
    level = _WARNING if b > 10 else _OK
    return level, msg, data


def check_sensitive_file_conflicts(branch: str, base: str = "master") -> tuple[str, str]:
    """Detect if sensitive files differ on both sides (potential semantic conflict)."""
    conflicts = []
    for path in _SENSITIVE_FILES:
        _, base_diff, _ = _run(["git", "diff", base, "--", path])
        _, branch_diff, _ = _run(["git", "diff", branch, "--", path])
        base_changed = bool(base_diff and base_diff.strip())
        branch_changed = bool(branch_diff and branch_diff.strip())
        if base_changed and branch_changed:
            conflicts.append(path)
    if conflicts:
        return (
            _WARNING,
            f"Sensitive file(s) changed on both sides: {conflicts}. "
            "Semantic review required — do not use mechanical 'keep branch side'.",
        )
    return _OK, "No sensitive files changed on both sides."


def check_map_viewer_regression(branch: str, base: str = "master") -> tuple[str, str]:
    """Detect if the branch has *fewer* truthfulness-related lines than base in map-viewer.js."""
    _, base_content, _ = _run(["git", "show", f"{base}:app/static/js/map-viewer.js"])
    _, branch_content, _ = _run(["git", "show", f"{branch}:app/static/js/map-viewer.js"])
    if not base_content or not branch_content:
        return _OK, "Cannot compare map-viewer.js (file missing on one side)."
    # Count hasValue() calls as a proxy for truthfulness guards
    base_guards = base_content.count("hasValue(")
    branch_guards = branch_content.count("hasValue(")
    if branch_guards < base_guards:
        return (
            _BLOCKING,
            f"Branch has {branch_guards} hasValue() guards in map-viewer.js vs "
            f"{base_guards} on {base}. This may regress popup truthfulness. "
            "Semantic review required.",
        )
    return _OK, f"map-viewer.js has {branch_guards} hasValue() guards (base: {base_guards})."


def check_branch_merged_status(branch: str, base: str = "master") -> tuple[str, str]:
    """Detect if the branch is already merged into base."""
    _, stdout, _ = _run(["git", "branch", "--merged", base])
    merged = [ln.strip().lstrip("* ") for ln in stdout.splitlines()]
    if branch in merged:
        return (
            _WARNING,
            f"`{branch}` is already merged into `{base}`. "
            "A second merge will be a no-op or may introduce confusion.",
        )
    return _OK, f"`{branch}` is not yet merged into `{base}`."


def check_aicontrol_numbering(branch: str) -> tuple[str, str]:
    """Detect AI_CONTROL numbering collisions introduced by the branch."""
    _, stdout, _ = _run(["git", "diff", "--name-only", f"master...{branch}"])
    if not stdout:
        return _OK, "No files differ between master and branch."
    new_docs = [p for p in stdout.splitlines() if p.startswith("AI_CONTROL/") and p.endswith(".md")]
    if not new_docs:
        return _OK, "No AI_CONTROL docs changed."

    ai_dir = REPO_ROOT / "AI_CONTROL"
    collisions = []
    for doc_path in new_docs:
        fname = Path(doc_path).name
        prefix = fname.split("_")[0] if "_" in fname else ""
        if prefix.isdigit():
            existing = list(ai_dir.glob(f"{prefix}_*.md"))
            if existing and not any(e.name == fname for e in existing):
                collisions.append(f"{doc_path} collides with {[e.name for e in existing]}")

    if collisions:
        return (
            _BLOCKING,
            "AI_CONTROL numbering collision(s) detected:\n  "
            + "\n  ".join(collisions)
            + "\nRename using namespace prefix (PCS_/PRD_/DOM_/STG_/AUD_).",
        )
    return _OK, f"No AI_CONTROL numbering collisions in {len(new_docs)} doc(s)."


def run_checks(branch: str, base: str = "master") -> list[dict[str, str]]:
    results: list[dict[str, str]] = []

    def record(name: str, level: str, message: str) -> None:
        results.append({"check": name, "level": level, "message": message})

    level, msg = check_branch_exists(branch)
    record("branch_exists", level, msg)
    if level == _BLOCKING:
        return results

    level, msg, counts = check_commit_counts(branch, base)
    record("commit_counts", level, msg)

    level, msg = check_sensitive_file_conflicts(branch, base)
    record("sensitive_file_conflicts", level, msg)

    level, msg = check_map_viewer_regression(branch, base)
    record("map_viewer_regression", level, msg)

    level, msg = check_branch_merged_status(branch, base)
    record("already_merged", level, msg)

    level, msg = check_aicontrol_numbering(branch)
    record("aicontrol_numbering", level, msg)

    return results


def print_report(
    results: list[dict[str, str]],
    branch: str,
    base: str,
    *,
    as_json: bool = False,
) -> int:
    if as_json:
        print(json.dumps({"branch": branch, "base": base, "checks": results}, indent=2))
    else:
        print(f"GridFlow Merge Safety Check: `{branch}` → `{base}`")
        print("=" * 50)
        for r in results:
            icon = {"OK": "✓", "WARN": "⚠", "BLOCK": "✗"}.get(r["level"], "?")
            print(f"  {icon} [{r['level']:5}] {r['check']}: {r['message']}")
        print("=" * 50)

    blocked = [r for r in results if r["level"] == _BLOCKING]
    warned = [r for r in results if r["level"] == _WARNING]
    if blocked:
        if not as_json:
            print(f"RESULT: BLOCKED ({len(blocked)} issue(s)). Do NOT merge.")
        return 1
    if warned:
        if not as_json:
            print(f"RESULT: WARNINGS ({len(warned)}). Review before merging.")
        return 2
    if not as_json:
        print("RESULT: SAFE TO MERGE.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("branch", help="Branch to check for mergeability into base.")
    p.add_argument("--base", default="master", help="Base branch (default: master).")
    p.add_argument("--json", action="store_true", dest="as_json")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results = run_checks(args.branch, args.base)
    return print_report(results, args.branch, args.base, as_json=args.as_json)


if __name__ == "__main__":
    sys.exit(main())
