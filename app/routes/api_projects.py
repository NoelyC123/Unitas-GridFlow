from __future__ import annotations

import json
from pathlib import Path

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.project_manager import (
    add_file_slot,
    create_project,
    list_projects,
    load_project,
    refresh_project_summary,
    suggest_project_name,
)
from app.routes.api_intake import process_job

api_projects_bp = Blueprint("api_projects", __name__)

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_PROJECTS_ROOT = _PROJECT_ROOT / "uploads" / "projects"


def _ensure_projects_root() -> Path:
    _PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)
    return _PROJECTS_ROOT


@api_projects_bp.get("/projects/")
def list_all_projects():
    projects = list_projects(_ensure_projects_root())
    return jsonify({"projects": projects})


@api_projects_bp.get("/projects/<project_id>")
def get_project(project_id: str):
    project = load_project(_ensure_projects_root(), project_id)
    if project is None:
        return jsonify({"ok": False, "error": "Project not found"}), 404
    return jsonify(project)


@api_projects_bp.post("/project/presign")
def project_presign():
    """Create (or extend) a project and return an upload URL for the file.

    Body fields:
      filename     (required) — the CSV filename
      project_name (optional) — human label; auto-suggested from filename if omitted
      description  (optional)
      project_id   (optional) — if provided, add to this existing project
    """
    data = request.get_json(silent=True) or {}

    raw_filename = str(data.get("filename", "")).strip()
    if not raw_filename:
        return jsonify({"ok": False, "error": "Missing filename"}), 400

    filename = secure_filename(raw_filename)
    if not filename:
        return jsonify({"ok": False, "error": "Invalid filename"}), 400

    projects_root = _ensure_projects_root()
    project_id = str(data.get("project_id", "")).strip()

    if project_id:
        project = load_project(projects_root, project_id)
        if project is None:
            return jsonify({"ok": False, "error": f"Project {project_id} not found"}), 404
    else:
        name = str(data.get("project_name", "")).strip() or suggest_project_name(raw_filename)
        description = str(data.get("description", "")).strip()
        project = create_project(projects_root, name, description)
        project_id = project["project_id"]

    file_id, file_dir = add_file_slot(projects_root, project_id, filename)
    upload_url = f"/api/upload/project/{project_id}/{file_id}/{filename}"

    return jsonify(
        {
            "ok": True,
            "upload_type": "single",
            "url": upload_url,
            "headers": {"Content-Type": "text/csv"},
            "project_id": project_id,
            "file_id": file_id,
            "finalize_url": f"/api/project/{project_id}/file/{file_id}/import",
            "status_url": f"/api/project/{project_id}/file/{file_id}/status",
            "project_url": f"/project/{project_id}",
        }
    )


@api_projects_bp.put("/upload/project/<project_id>/<file_id>/<filename>")
def upload_project_file(project_id: str, file_id: str, filename: str):
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({"ok": False, "error": "Invalid filename"}), 400

    file_dir = _PROJECTS_ROOT / project_id / "files" / file_id
    if not file_dir.exists():
        return jsonify({"ok": False, "error": "File slot not found"}), 404

    body = request.get_data()
    if not body:
        return jsonify({"ok": False, "error": "No upload body received"}), 400

    destination = file_dir / safe_name
    destination.write_bytes(body)

    meta_path = file_dir / "meta.json"
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        meta = {}
    meta.update(
        {
            "status": "uploaded",
            "filename": safe_name,
            "uploaded_path": str(destination),
            "uploaded_size": len(body),
        }
    )
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    return ("", 200)


@api_projects_bp.post("/project/<project_id>/file/<file_id>/import")
def project_file_import(project_id: str, file_id: str):
    file_dir = _PROJECTS_ROOT / project_id / "files" / file_id
    if not file_dir.exists():
        return jsonify({"ok": False, "error": "File slot not found"}), 404

    data = request.get_json(silent=True) or {}
    explicit_dno = data.get("dno")

    display_id = f"{project_id}/{file_id}"
    result = process_job(file_dir, display_id, explicit_dno)

    refresh_project_summary(_PROJECTS_ROOT, project_id)

    if not result["ok"]:
        return jsonify({"ok": False, "error": result["error"]}), 500

    return jsonify(
        {
            "ok": True,
            "project_id": project_id,
            "file_id": file_id,
            **{
                k: result[k]
                for k in (
                    "file_type",
                    "auto_normalized",
                    "rulepack_id",
                    "rulepack_inferred",
                    "issue_count",
                )
                if k in result
            },
        }
    )


@api_projects_bp.get("/project/<project_id>/file/<file_id>/status")
def project_file_status(project_id: str, file_id: str):
    meta_path = _PROJECTS_ROOT / project_id / "files" / file_id / "meta.json"
    if not meta_path.exists():
        return jsonify({"project_id": project_id, "file_id": file_id, "status": "pending"})
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        return jsonify(meta)
    except Exception:
        return jsonify({"project_id": project_id, "file_id": file_id, "status": "error"}), 500
