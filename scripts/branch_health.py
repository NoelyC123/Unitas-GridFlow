#!/usr/bin/env python3
"""Branch health and retirement candidate report for GridFlow.

Classifies all local and remote branches into action buckets following
the protocol in AI_CONTROL/38_BRANCH_RETIREMENT_PLAN.md.

This is a read-only reporting tool — it does not delete or rename branches.

Exit codes:
  0  Report generated.
  1  Error (git unavailable or repo not found).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Buckets from AI_CONTROL/38_BRANCH_RETIREMENT_PLAN.md
BUCKET_DELETE_NOW = "DELETE_NOW"
BUCKET_DELETE_AFTER_CONFIRM = "DELETE_AFTER_CONFIRM"
BUCKET_KEEP_AS_REFERENCE = "KEEP_AS_REFERENCE"
BUCKET_DO_NOT_TOUCH = "DO_NOT_TOUCH"
BUCKET_MANUAL_INSPECTION = "MANUAL_INSPECTION"
BUCKET_CHERRY_PICK_ONLY = "CHERRY_PICK_ONLY"
BUCKET_ACTIVE = "ACTIVE"
BUCKET_UNKNOWN = "UNKNOWN"

# Branches that are explicitly preserved
_PROTECTED = {"master", "origin/master"}

# Buckets from the retirement plan (branch name -> bucket, reason)
_KNOWN: dict[str, tuple[str, str]] = {
    "claude-code/backend-robustness-validation": (
        BUCKET_DELETE_NOW,
        "Merged; backend helpers landed in master",
    ),
    "claude-code/stage4-structured-capture-foundation": (BUCKET_DELETE_NOW, "Tag preserves SHA"),
    "claude-code/technical-docs-field-architecture": (BUCKET_DELETE_NOW, "Tag preserves SHA"),
    "codex/c2d-2-popup-grouping-labels": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-3-popup-field-catalog": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-aa-review-workspace-package": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-ab-control-refresh": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-ab-popup-field-truthfulness": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-ac-map-workspace-usability": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-ad-validation-readiness-consolidation": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-ae-validation-plan-docs": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-geometry-trust": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-geometry-trust-validation-upgrade": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-planner-awareness-layer": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-review-workspace-integration": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-route-highlight-layer": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-span-clustering": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-span-validity": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-ux-truthfulness": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-x-popup-system": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-y-popup-renderer": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "codex/c2d-z-map-review-polish": (BUCKET_DELETE_NOW, "Old C2D iteration"),
    "c2d-1-field-inventory-alias-mapping": (BUCKET_DELETE_NOW, "Old C2D; no-prefix legacy name"),
    "codex/c2e2-map-navigation-followups": (BUCKET_DELETE_NOW, "Branch tip = master HEAD"),
    "codex/c2f-review-focus-issue-filtering": (BUCKET_DELETE_NOW, "Tag preserves SHA"),
    "codex/c2g-lifecycle-replacement-visualization": (BUCKET_DELETE_NOW, "Tag preserves SHA"),
    "codex/stage4-structured-capture-integration-plan": (
        BUCKET_DELETE_AFTER_CONFIRM,
        "Confirm no unpublished planning content",
    ),
    "claude-code/c2e2-support-suite": (
        BUCKET_CHERRY_PICK_ONLY,
        "Master is stricter; mechanical merge would regress truthfulness",
    ),
    "claude-code/stage4-structured-capture-technical-audit": (
        BUCKET_CHERRY_PICK_ONLY,
        "AI_CONTROL doc numbers collide with master",
    ),
    "codex/c2d-duplicate-detection": (BUCKET_MANUAL_INSPECTION, "44 commits ahead, never merged"),
    "codex/c2d-geom-pipeline": (
        BUCKET_MANUAL_INSPECTION,
        "44 commits ahead, predates merged geometry work",
    ),
    "codex/c2d-struct-inference": (
        BUCKET_MANUAL_INSPECTION,
        "37 commits ahead, touches map-viewer.js",
    ),
    "backup/pre-cleanup-20260422-0943": (
        BUCKET_DELETE_AFTER_CONFIRM,
        "Pre-cleanup snapshot; superseded",
    ),
    "backup/pre-control-audit-20260422-0946": (
        BUCKET_DELETE_AFTER_CONFIRM,
        "Pre-control-audit snapshot; superseded",
    ),
    "control/c2e2-finalise-from-master": (BUCKET_DELETE_AFTER_CONFIRM, "Tip already merged"),
    "codex/gridflow-control-center-v1": (BUCKET_DO_NOT_TOUCH, "Active codex branch"),
}


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


def list_all_branches() -> list[str]:
    _, stdout, _ = _run(["git", "branch", "-a"])
    branches = []
    for line in stdout.splitlines():
        name = line.strip().lstrip("*+ ").removeprefix("remotes/")
        if " -> " in name:
            continue
        if name:
            branches.append(name)
    return sorted(set(branches))


def is_merged(branch: str, base: str = "master") -> bool:
    _, stdout, _ = _run(["git", "branch", "--merged", base])
    merged = {ln.strip().lstrip("* ") for ln in stdout.splitlines()}
    return branch in merged


def get_commit_counts(branch: str, base: str = "master") -> tuple[int, int]:
    _, stdout, _ = _run(["git", "rev-list", "--left-right", "--count", f"{base}...{branch}"])
    if not stdout or "\t" not in stdout:
        return 0, 0
    behind, ahead = stdout.split("\t", 1)
    try:
        return int(behind.strip()), int(ahead.strip())
    except ValueError:
        return 0, 0


def get_last_commit_date(branch: str) -> str:
    _, stdout, _ = _run(["git", "log", "-1", "--format=%ci", branch])
    return stdout or "unknown"


@dataclass
class BranchInfo:
    name: str
    bucket: str = BUCKET_UNKNOWN
    reason: str = ""
    merged: bool = False
    behind: int = 0
    ahead: int = 0
    last_commit: str = ""
    is_remote_only: bool = False
    risk: str = "low"


def classify_branch(name: str, base: str = "master") -> BranchInfo:
    info = BranchInfo(name=name)
    short = name.removeprefix("origin/")

    if short in _PROTECTED or name in _PROTECTED:
        info.bucket = BUCKET_DO_NOT_TOUCH
        info.reason = "Protected base branch"
        return info

    if short in _KNOWN:
        bucket, reason = _KNOWN[short]
        info.bucket = bucket
        info.reason = reason
    elif name.startswith("origin/") and short not in _KNOWN:
        info.is_remote_only = True

    info.merged = is_merged(short, base)
    info.behind, info.ahead = get_commit_counts(short, base)
    info.last_commit = get_last_commit_date(short)

    if info.bucket == BUCKET_UNKNOWN:
        if info.merged:
            info.bucket = BUCKET_DELETE_AFTER_CONFIRM
            info.reason = "Merged into master but not catalogued in retirement plan"
        elif info.ahead > 30:
            info.bucket = BUCKET_MANUAL_INSPECTION
            info.reason = f"Large unmerged branch ({info.ahead} commits ahead)"
        elif info.ahead > 0:
            info.bucket = BUCKET_MANUAL_INSPECTION
            info.reason = "Unmerged; not in retirement plan catalogue"
        else:
            info.bucket = BUCKET_DELETE_AFTER_CONFIRM
            info.reason = "No divergent commits; likely safe to delete"

    # Risk scoring
    if info.bucket in (BUCKET_CHERRY_PICK_ONLY, BUCKET_MANUAL_INSPECTION):
        info.risk = "high"
    elif info.bucket in (BUCKET_DELETE_AFTER_CONFIRM,):
        info.risk = "medium"
    else:
        info.risk = "low"

    return info


def build_report(base: str = "master") -> dict:
    branches = list_all_branches()
    classified: list[BranchInfo] = []
    for b in branches:
        classified.append(classify_branch(b, base))

    by_bucket: dict[str, list[str]] = {}
    for info in classified:
        by_bucket.setdefault(info.bucket, []).append(info.name)

    high_risk = [i for i in classified if i.risk == "high"]
    return {
        "total_branches": len(classified),
        "by_bucket": {k: sorted(v) for k, v in sorted(by_bucket.items())},
        "high_risk": [
            {"name": i.name, "bucket": i.bucket, "reason": i.reason}
            for i in sorted(high_risk, key=lambda x: x.name)
        ],
        "details": [
            {
                "name": i.name,
                "bucket": i.bucket,
                "merged": i.merged,
                "behind": i.behind,
                "ahead": i.ahead,
                "last_commit": i.last_commit,
                "risk": i.risk,
                "reason": i.reason,
            }
            for i in classified
        ],
    }


def print_text_report(report: dict) -> None:
    print("GridFlow Branch Health Report")
    print("=" * 50)
    print(f"Total branches: {report['total_branches']}")
    print()
    print("By action bucket:")
    for bucket, names in report["by_bucket"].items():
        print(f"  {bucket}: {len(names)} branch(es)")
        for n in names:
            print(f"    - {n}")
    print()
    high_risk = report.get("high_risk", [])
    if high_risk:
        print(f"High-risk branches ({len(high_risk)}):")
        for h in high_risk:
            print(f"  ✗ {h['name']}: {h['reason']}")
    else:
        print("No high-risk branches detected.")
    print("=" * 50)
    print("NOTE: This report is read-only. Run with --json for machine-readable output.")
    print("      Use AI_CONTROL/38_BRANCH_RETIREMENT_PLAN.md for deletion procedures.")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", default="master", help="Base branch (default: master).")
    p.add_argument("--json", action="store_true", dest="as_json")
    p.add_argument(
        "--bucket",
        choices=[
            BUCKET_DELETE_NOW,
            BUCKET_DELETE_AFTER_CONFIRM,
            BUCKET_KEEP_AS_REFERENCE,
            BUCKET_DO_NOT_TOUCH,
            BUCKET_MANUAL_INSPECTION,
            BUCKET_CHERRY_PICK_ONLY,
            BUCKET_ACTIVE,
            BUCKET_UNKNOWN,
        ],
        help="Filter output to a single bucket.",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = build_report(args.base)

    if args.bucket:
        filtered = [d for d in report["details"] if d["bucket"] == args.bucket]
        if args.as_json:
            print(json.dumps(filtered, indent=2))
        else:
            print(f"Branches in bucket {args.bucket}:")
            for d in filtered:
                print(f"  {d['name']} (merged={d['merged']}, ahead={d['ahead']}): {d['reason']}")
        return 0

    if args.as_json:
        print(json.dumps(report, indent=2))
    else:
        print_text_report(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
