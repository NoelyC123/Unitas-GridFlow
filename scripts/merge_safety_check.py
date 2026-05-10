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


# ---------------------------------------------------------------------------
# Stage 4A/4B boundary checks
# ---------------------------------------------------------------------------

# Stage 4 library files — allowed to change in Stage 4A/4B branches.
_STAGE4_LIBRARY_FILES = {
    "app/structured_capture_schema.py",
    "app/structured_capture_validators.py",
    "scripts/generate_structured_capture_template.py",
    "templates/structured_capture_template.csv",
}

# Runtime files that Stage 4A/4B branches must not touch.
_STAGE4A_FORBIDDEN_RUNTIME_FILES = {
    "app/static/js/map-viewer.js",
    "app/routes/api_intake.py",
    "app/controller_intake.py",
    "app/qa_engine.py",
    "app/geometry_pipeline.py",
    "app/span_generator.py",
}

# C2E2 popup files forbidden for Stage 4A/4B.
_STAGE4A_FORBIDDEN_POPUP_FILES = {
    "app/field_validators.py",
}

# ---------------------------------------------------------------------------
# Stage 4C boundary checks
# ---------------------------------------------------------------------------

# Stage 4C files — only api_intake.py and structured_capture_models.py can be modified.
_STAGE4C_ALLOWED_FILES = {
    "app/routes/api_intake.py",
    "app/models/structured_capture_models.py",
    "scripts/merge_safety_check.py",
    "tests/test_stage4c_runtime_integration.py",
    "tests/test_stage4c_runtime_boundary.py",
    "tests/test_stage4c_completeness_truthfulness.py",
    "AI_CONTROL/56_STAGE4C_RUNTIME_INTEGRATION_ARCHITECTURE.md",
    "AI_CONTROL/57_STAGE4C_RUNTIME_BOUNDARY_RULES.md",
    "AI_CONTROL/58_STAGE4C_UI_SURFACING_PLAN.md",
    "AI_CONTROL/59_FIELD_PILOT_ACCEPTANCE_GATE.md",
    "AI_CONTROL/60_STAGE4C_RISK_DRIVEN_TEST_PLAN.md",
}

# Stage 4C forbidden files — runtime must not be modified.
_STAGE4C_FORBIDDEN_RUNTIME_FILES = {
    "app/qa_engine.py",
    "app/routes/api_qc.py",
    "app/controller_intake.py",
    "app/static/js/map-viewer.js",
    "app/dno_rules.py",
    "app/pdf_generator.py",
    "app/routes/api_export.py",
}

_STAGE4C_BRANCH_PREFIXES = ("codex/stage4c", "claude-code/stage4c", "stage4c")

# Stage 4 leakage tokens: their presence in added lines of non-library files
# signals premature integration.
_STAGE4_LEAKAGE_TOKENS = [
    "structured_capture",
    "stage4_future_capture",
    "lean_direction",
    "lean_severity",
    "pole_class",
    "pole_strength",
    "pole_material",
    "capture_source",
    "captured_by",
    "capture_date",
]

_STAGE4A_BRANCH_PREFIXES = ("codex/stage4a", "claude-code/stage4a", "stage4a")


def _is_stage4a_branch(branch: str) -> bool:
    return any(branch.lower().startswith(p) for p in _STAGE4A_BRANCH_PREFIXES)


def check_stage4a_runtime_file_boundary(branch: str) -> tuple[str, str]:
    """BLOCK if a Stage 4A branch touches forbidden runtime or popup files."""
    if not _is_stage4a_branch(branch):
        return _OK, "Not a Stage 4A branch — runtime boundary check skipped."

    _, stdout, _ = _run(["git", "diff", "--name-only", f"master...{branch}"])
    if not stdout:
        return _OK, "No changed files detected."

    changed = set(stdout.splitlines())
    all_forbidden = (changed & _STAGE4A_FORBIDDEN_RUNTIME_FILES) | (
        changed & _STAGE4A_FORBIDDEN_POPUP_FILES
    )
    if all_forbidden:
        return (
            _BLOCKING,
            "Stage 4A branch touches forbidden runtime file(s): "
            + ", ".join(sorted(all_forbidden))
            + ". Stage 4A is library-only. "
            "Forbidden: upload routes, QA engine, geometry, map renderer, popup validators.",
        )
    return _OK, "Stage 4A branch respects runtime file boundary."


def check_stage4_map_viewer_untouched(branch: str) -> tuple[str, str]:
    """BLOCK if a Stage 4A/4B branch modifies map-viewer.js at all."""
    if not _is_stage4a_branch(branch):
        return _OK, "Not a Stage 4A branch — map-viewer boundary guard skipped."

    _, stdout, _ = _run(["git", "diff", "--name-only", f"master...{branch}"])
    changed = set(stdout.splitlines()) if stdout else set()

    if "app/static/js/map-viewer.js" in changed:
        return (
            _BLOCKING,
            "Stage 4A branch modifies app/static/js/map-viewer.js. "
            "map-viewer.js must not be touched before Stage 4D. "
            "Stage 4A is library-only.",
        )
    return _OK, "map-viewer.js is untouched in this Stage 4A branch."


def check_stage4a_leakage_in_runtime_diff(branch: str) -> tuple[str, str]:
    """WARN if Stage 4 leakage tokens appear in added lines of non-library files."""
    if not _is_stage4a_branch(branch):
        return _OK, "Not a Stage 4A branch — leakage token scan skipped."

    _, diff_output, _ = _run(["git", "diff", f"master...{branch}"])
    if not diff_output:
        return _OK, "Empty diff — no leakage risk."

    leakage_hits: list[str] = []
    current_file = ""
    for line in diff_output.splitlines():
        if line.startswith("diff --git"):
            parts = line.split(" b/")
            current_file = parts[-1] if parts else ""
        elif line.startswith("+") and not line.startswith("+++"):
            if current_file and any(current_file.startswith(lf) for lf in _STAGE4_LIBRARY_FILES):
                continue
            for token in _STAGE4_LEAKAGE_TOKENS:
                if token in line:
                    leakage_hits.append(f"{current_file}: {line[:80].strip()!r}")
                    break

    if leakage_hits:
        preview = leakage_hits[:5]
        return (
            _WARNING,
            f"Stage 4 leakage token(s) in non-library diff ({len(leakage_hits)} hit(s)). "
            f"First 5: {preview}. Verify Stage 4 is not wiring into runtime surfaces.",
        )
    return _OK, "No Stage 4 leakage tokens found outside library files."


def check_stage4a_popup_test_coverage(branch: str) -> tuple[str, str]:
    """WARN if field_reference.py changed without matching C2E2 popup test changes."""
    _, stdout, _ = _run(["git", "diff", "--name-only", f"master...{branch}"])
    if not stdout:
        return _OK, "No changed files — popup test coverage check skipped."

    changed = set(stdout.splitlines())
    field_ref_changed = "app/field_reference.py" in changed
    popup_test_changed = any(
        "test_c2e2_popup" in f or "test_structured_capture" in f for f in changed
    )

    if field_ref_changed and not popup_test_changed:
        return (
            _WARNING,
            "app/field_reference.py changed but no C2E2 popup or structured capture "
            "tests were updated. Add tests to tests/test_c2e2_popup_fields.py or "
            "tests/test_c2e2_popup_rendering.py to cover the change.",
        )
    return _OK, "Popup test coverage check passed."


def _is_stage4c_branch(branch: str) -> bool:
    return any(branch.lower().startswith(p) for p in _STAGE4C_BRANCH_PREFIXES)


def check_stage4c_runtime_file_boundary(branch: str) -> tuple[str, str]:
    """BLOCK if a Stage 4C branch touches forbidden runtime files."""
    if not _is_stage4c_branch(branch):
        return _OK, "Not a Stage 4C branch — runtime boundary check skipped."

    _, stdout, _ = _run(["git", "diff", "--name-only", f"master...{branch}"])
    if not stdout:
        return _OK, "No changed files detected."

    changed = set(stdout.splitlines())
    forbidden_touched = changed & _STAGE4C_FORBIDDEN_RUNTIME_FILES

    if forbidden_touched:
        return (
            _BLOCKING,
            "Stage 4C branch touches forbidden runtime file(s): "
            + ", ".join(sorted(forbidden_touched))
            + ". Forbidden: qa_engine, api_qc, map-viewer, dno_rules, pdf_generator, export. "
            "See AI_CONTROL/57_STAGE4C_RUNTIME_BOUNDARY_RULES.md.",
        )
    return _OK, "Stage 4C branch respects runtime file boundary."


def check_stage4c_has_feature_flag(branch: str) -> tuple[str, str]:
    """WARN if Stage 4C branch modifies api_intake.py but no feature flag check found."""
    if not _is_stage4c_branch(branch):
        return _OK, "Not a Stage 4C branch — feature flag check skipped."

    _, stdout, _ = _run(["git", "diff", "--name-only", f"master...{branch}"])
    if not stdout or "app/routes/api_intake.py" not in stdout:
        return _OK, "api_intake.py not modified — feature flag check skipped."

    _, diff_output, _ = _run(["git", "diff", f"master...{branch}", "app/routes/api_intake.py"])
    if not diff_output:
        return _OK, "No changes to api_intake.py."

    has_stage4c_flag_check = (
        "FEATURE_STAGE4C_INTAKE_ENABLED" in diff_output
        or "feature_stage4c_intake" in diff_output
        or "stage4c_enabled" in diff_output
    )

    if not has_stage4c_flag_check:
        return (
            _WARNING,
            "api_intake.py modified but no feature flag check found. "
            "Stage 4C intake should be gated behind FEATURE_STAGE4C_INTAKE_ENABLED. "
            "See AI_CONTROL/57_STAGE4C_RUNTIME_BOUNDARY_RULES.md.",
        )
    return _OK, "api_intake.py contains Stage 4C feature flag check."


def check_stage4c_no_stage4_imports_in_forbidden(branch: str) -> tuple[str, str]:
    """BLOCK if forbidden files contain imports from structured_capture modules."""
    if not _is_stage4c_branch(branch):
        return _OK, "Not a Stage 4C branch — import scan skipped."

    _, diff_output, _ = _run(["git", "diff", f"master...{branch}"])
    if not diff_output:
        return _OK, "Empty diff — no import risk."

    violations: list[str] = []
    current_file = ""
    for line in diff_output.splitlines():
        if line.startswith("diff --git"):
            parts = line.split(" b/")
            current_file = parts[-1] if parts else ""
        elif line.startswith("+") and not line.startswith("+++"):
            if current_file and current_file in _STAGE4C_FORBIDDEN_RUNTIME_FILES:
                if "structured_capture" in line or "JobStructuredCaptureRecord" in line:
                    violations.append(f"{current_file}: {line[:80].strip()!r}")

    if violations:
        preview = violations[:3]
        return (
            _BLOCKING,
            f"Forbidden file(s) contain Stage 4C imports ({len(violations)} hit(s)). "
            f"First 3: {preview}. "
            "Stage 4 data must not leak into qa_engine, map-viewer, pdf_generator, etc. "
            "See AI_CONTROL/57_STAGE4C_RUNTIME_BOUNDARY_RULES.md.",
        )
    return _OK, "No Stage 4C imports detected in forbidden files."


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

    # Stage 4A boundary checks (only fire for Stage 4A branches)
    level, msg = check_stage4a_runtime_file_boundary(branch)
    record("stage4a_runtime_boundary", level, msg)

    level, msg = check_stage4_map_viewer_untouched(branch)
    record("stage4a_map_viewer_boundary", level, msg)

    level, msg = check_stage4a_leakage_in_runtime_diff(branch)
    record("stage4a_leakage_tokens", level, msg)

    level, msg = check_stage4a_popup_test_coverage(branch)
    record("stage4a_popup_test_coverage", level, msg)

    # Stage 4C boundary checks (only fire for Stage 4C branches)
    level, msg = check_stage4c_runtime_file_boundary(branch)
    record("stage4c_runtime_boundary", level, msg)

    level, msg = check_stage4c_has_feature_flag(branch)
    record("stage4c_feature_flag", level, msg)

    level, msg = check_stage4c_no_stage4_imports_in_forbidden(branch)
    record("stage4c_import_boundary", level, msg)

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
