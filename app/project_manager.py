from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def next_project_id(projects_root: Path) -> str:
    if not projects_root.exists():
        return "P001"
    nums = []
    for d in projects_root.iterdir():
        if d.is_dir() and d.name.startswith("P") and d.name[1:].isdigit():
            nums.append(int(d.name[1:]))
    return f"P{max(nums, default=0) + 1:03d}"


def next_file_id(project_dir: Path) -> str:
    files_dir = project_dir / "files"
    if not files_dir.exists():
        return "F001"
    nums = []
    for d in files_dir.iterdir():
        if d.is_dir() and d.name.startswith("F") and d.name[1:].isdigit():
            nums.append(int(d.name[1:]))
    return f"F{max(nums, default=0) + 1:03d}"


def create_project(projects_root: Path, name: str, description: str = "") -> dict:
    project_id = next_project_id(projects_root)
    project_dir = projects_root / project_id
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "files").mkdir(exist_ok=True)
    now = _now_iso()
    project = {
        "project_id": project_id,
        "name": name.strip(),
        "description": description.strip(),
        "created": now,
        "updated": now,
        "files": [],
        "summary": {
            "total_files": 0,
            "total_poles": 0,
            "total_issues": 0,
            "rulepacks_used": [],
        },
    }
    (project_dir / "project.json").write_text(
        json.dumps(project, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return project


def build_intake_metadata(
    survey_day_label: str = "",
    uploaded_by: str = "",
    surveyor_note: str = "",
    office_feedback: str = "",
) -> dict:
    """Build the small Stage 3A intake block stored in file meta.json."""
    return {
        "survey_day_label": survey_day_label.strip(),
        "uploaded_by": uploaded_by.strip(),
        "surveyor_note": surveyor_note.strip(),
        "office_feedback": office_feedback.strip(),
    }


def derive_intake_status(file_status: str, review_status: str = "not_reviewed") -> str:
    """Return the office-facing intake status for a project file."""
    status = (file_status or "").lower()
    if review_status == "reviewed":
        return "reviewed"
    if status == "complete":
        return "needs_review"
    if status in {"error", "failed"}:
        return "needs_attention"
    if status in {"processing", "uploaded", "awaiting_upload", "pending"}:
        return status
    return "pending"


def load_project(projects_root: Path, project_id: str) -> dict | None:
    path = projects_root / project_id / "project.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def save_project(project_dir: Path, project: dict) -> None:
    path = project_dir / "project.json"
    path.write_text(json.dumps(project, indent=2, ensure_ascii=False), encoding="utf-8")


def list_projects(projects_root: Path) -> list[dict]:
    if not projects_root.exists():
        return []
    result = []
    for p in sorted(projects_root.glob("*/project.json")):
        try:
            result.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            pass
    return result


def add_file_slot(
    projects_root: Path,
    project_id: str,
    filename: str,
    intake: dict | None = None,
) -> tuple[str, Path]:
    """Reserve the next file slot in a project. Returns (file_id, file_dir)."""
    project_dir = projects_root / project_id
    file_id = next_file_id(project_dir)
    file_dir = project_dir / "files" / file_id
    file_dir.mkdir(parents=True, exist_ok=True)
    meta: dict = {
        "project_id": project_id,
        "file_id": file_id,
        "filename": filename,
        "status": "awaiting_upload",
        "uploaded": _now_iso(),
        "intake": build_intake_metadata(**(intake or {})),
    }
    (file_dir / "meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return file_id, file_dir


def update_file_intake_feedback(
    projects_root: Path,
    project_id: str,
    file_id: str,
    office_feedback: str,
) -> dict | None:
    """Update the office feedback note for one project file."""
    file_dir = projects_root / project_id / "files" / file_id
    meta_path = file_dir / "meta.json"
    if not meta_path.exists():
        return None
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return None

    existing = meta.get("intake") or {}
    meta["intake"] = build_intake_metadata(
        survey_day_label=str(existing.get("survey_day_label", "")),
        uploaded_by=str(existing.get("uploaded_by", "")),
        surveyor_note=str(existing.get("surveyor_note", "")),
        office_feedback=office_feedback,
    )
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    refresh_project_summary(projects_root, project_id)
    return meta["intake"]


def refresh_project_summary(projects_root: Path, project_id: str) -> None:
    """Re-read all file meta.json files and update project.json summary."""
    project_dir = projects_root / project_id
    project_path = project_dir / "project.json"
    if not project_path.exists():
        return

    try:
        project = json.loads(project_path.read_text(encoding="utf-8"))
    except Exception:
        return

    files_dir = project_dir / "files"
    file_entries: list[dict] = []
    total_poles = 0
    total_issues = 0
    rulepacks: set[str] = set()

    if files_dir.exists():
        for file_dir in sorted(files_dir.iterdir()):
            if not file_dir.is_dir():
                continue
            meta_path = file_dir / "meta.json"
            if not meta_path.exists():
                continue
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                continue

            pole_count = int(meta.get("pole_count") or 0)
            issue_count = int(meta.get("issue_count") or 0)
            total_poles += pole_count
            total_issues += issue_count
            if meta.get("rulepack_id"):
                rulepacks.add(meta["rulepack_id"])
            review_status = "not_reviewed"
            review_path = file_dir / "review.json"
            if review_path.exists():
                try:
                    review = json.loads(review_path.read_text(encoding="utf-8"))
                    review_status = review.get("review_status", "not_reviewed")
                except Exception:
                    review_status = "not_reviewed"
            intake = meta.get("intake") or {}
            file_status = meta.get("status", "unknown")

            file_entries.append(
                {
                    "file_id": meta.get("file_id", file_dir.name),
                    "filename": meta.get("filename", ""),
                    "uploaded": meta.get("uploaded", ""),
                    "status": file_status,
                    "intake_status": derive_intake_status(file_status, review_status),
                    "review_status": review_status,
                    "intake": build_intake_metadata(
                        survey_day_label=str(intake.get("survey_day_label", "")),
                        uploaded_by=str(intake.get("uploaded_by", "")),
                        surveyor_note=str(intake.get("surveyor_note", "")),
                        office_feedback=str(intake.get("office_feedback", "")),
                    ),
                    "rulepack_id": meta.get("rulepack_id", ""),
                    "pole_count": pole_count,
                    "issue_count": issue_count,
                    "pass_count": int(meta.get("pass_count") or 0),
                    "warn_count": int(meta.get("warn_count") or 0),
                    "fail_count": int(meta.get("fail_count") or 0),
                    "sequence_summary": meta.get("sequence_summary") or {},
                }
            )

    project["files"] = file_entries
    project["updated"] = _now_iso()
    project["summary"] = {
        "total_files": len(file_entries),
        "total_poles": total_poles,
        "total_issues": total_issues,
        "rulepacks_used": sorted(rulepacks),
    }
    project_path.write_text(json.dumps(project, indent=2, ensure_ascii=False), encoding="utf-8")


def suggest_project_name(filename: str) -> str:
    """Derive a human-readable project name from a raw CSV filename.

    Rules (in order):
    1. Strip last file extension (rsplit so dotfiles like ".csv" give empty stem).
    2. If " - " appears, take only the part before it — strips Trimble-style
       variant suffixes like "Gordon Pt1 - Original".
    3. If the stem uses underscores with no spaces (e.g. "Gordon_Pt1_Original"),
       take only the first two underscore-separated components to drop trailing
       descriptors.  A two-component name (e.g. "28-14_4-474") keeps both halves.
    4. Replace remaining underscores with spaces.
    5. Do NOT convert hyphens — job numbers like "28-14" and "4-474" are meaningful.
    """
    bare = filename.rsplit(".", 1)[0] if "." in filename else filename

    # Strip " - Descriptor" variant suffix
    if " - " in bare:
        bare = bare.split(" - ", 1)[0]

    # Underscore-separated name with no spaces: drop trailing descriptor if 3+ parts
    if "_" in bare and " " not in bare:
        parts = bare.split("_")
        bare = " ".join(parts[:2]) if len(parts) >= 3 else bare.replace("_", " ")
    else:
        bare = bare.replace("_", " ")

    name = " ".join(bare.split())
    return name or "Unnamed Project"
