# app/routes/api_upload.py
from __future__ import annotations

import json
from pathlib import Path

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

api_upload_bp = Blueprint("api_upload", __name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOAD_ROOT = PROJECT_ROOT / "uploads"
JOBS_ROOT = UPLOAD_ROOT / "jobs"


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _job_dir(job_id: str) -> Path:
    return JOBS_ROOT / job_id


def _meta_path(job_id: str) -> Path:
    return _job_dir(job_id) / "meta.json"


def _load_meta(job_id: str) -> dict:
    path = _meta_path(job_id)
    if not path.exists():
        return {"job_id": job_id, "status": "pending"}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"job_id": job_id, "status": "error", "error": "invalid meta.json"}


def _save_meta(job_id: str, meta: dict) -> None:
    job_path = _job_dir(job_id)
    _ensure_dir(job_path)
    _meta_path(job_id).write_text(
        json.dumps(meta, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


@api_upload_bp.post("/presign")
def presign():
    data = request.get_json(silent=True) or {}

    raw_key = str(data.get("key", "")).strip()
    content_type = str(data.get("content_type", "application/octet-stream")).strip()
    multipart = bool(data.get("multipart", False))

    if not raw_key:
        return jsonify({"ok": False, "error": "Missing upload key"}), 400

    parts = Path(raw_key).parts
    job_id = None
    for part in parts:
        if part.upper().startswith("J"):
            job_id = part.upper()
            break

    if not job_id:
        return jsonify({"ok": False, "error": "Could not infer job_id from key"}), 400

    filename = secure_filename(Path(raw_key).name)
    if not filename:
        return jsonify({"ok": False, "error": "Invalid filename"}), 400

    _ensure_dir(_job_dir(job_id))

    meta = _load_meta(job_id)
    meta.update(
        {
            "job_id": job_id,
            "status": "awaiting_upload",
            "upload_key": raw_key,
            "filename": filename,
            "content_type": content_type,
            "multipart": multipart,
        }
    )
    _save_meta(job_id, meta)

    return jsonify(
        {
            "ok": True,
            "upload_type": "single",
            "url": f"/api/upload/{job_id}/{filename}",
            "headers": {"Content-Type": content_type or "application/octet-stream"},
            "job_id": job_id,
        }
    )


@api_upload_bp.put("/upload/<job_id>/<filename>")
def upload_file(job_id: str, filename: str):
    safe_name = secure_filename(filename)
    if not safe_name:
        return jsonify({"ok": False, "error": "Invalid filename"}), 400

    body = request.get_data()
    if body is None:
        return jsonify({"ok": False, "error": "No upload body received"}), 400

    job_path = _job_dir(job_id)
    _ensure_dir(job_path)

    destination = job_path / safe_name
    destination.write_bytes(body)

    meta = _load_meta(job_id)
    meta.update(
        {
            "job_id": job_id,
            "status": "uploaded",
            "filename": safe_name,
            "uploaded_path": str(destination),
            "uploaded_size": len(body),
        }
    )
    _save_meta(job_id, meta)

    return ("", 200)