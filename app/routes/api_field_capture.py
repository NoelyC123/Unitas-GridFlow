"""Stage 4 — field capture API (sessions, records, import to Stage 1)."""

from __future__ import annotations

import json
from pathlib import Path

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from app.field_capture import (
    PROJECTS_ROOT,
    FieldCaptureSession,
    add_record,
    create_session,
    get_session,
    list_records,
    list_sessions,
    mark_session_imported,
    session_to_csv_text,
    validate_context_payload,
    validate_pole_payload,
    validate_span_payload,
)
from app.project_manager import add_file_slot, load_project, refresh_project_summary
from app.routes.api_intake import process_job

api_field_capture_bp = Blueprint("api_field_capture", __name__)


def _projects_root() -> Path:
    PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)
    return PROJECTS_ROOT


def _parse_payload_multipart() -> tuple[str, str, dict, dict, list]:
    """Return session_id, record_kind, fields, gnss, list of (filename, bytes)."""
    session_id = (request.form.get("session_id") or "").strip()
    record_kind = (request.form.get("record_kind") or request.form.get("record_type") or "").strip()
    fields_raw = request.form.get("fields") or request.form.get("payload") or "{}"
    gnss_raw = request.form.get("gnss") or "{}"
    try:
        fields = json.loads(fields_raw)
    except json.JSONDecodeError:
        fields = {}
    try:
        gnss = json.loads(gnss_raw)
    except json.JSONDecodeError:
        gnss = {}
    if not isinstance(fields, dict):
        fields = {}
    if not isinstance(gnss, dict):
        gnss = {}

    uploads: list[tuple[str, bytes]] = []
    for fname in ("photos", "photo", "file"):
        for f in request.files.getlist(fname):
            if f and f.filename:
                uploads.append((f.filename, f.read()))

    return session_id, record_kind, fields, gnss, uploads


def _parse_payload_json() -> tuple[str, str, dict, dict, list[tuple[str, bytes]]]:
    body = request.get_json(silent=True) or {}
    session_id = str(body.get("session_id") or "").strip()
    record_kind = str(body.get("record_kind") or body.get("record_type") or "").strip()
    fields = body.get("fields") if isinstance(body.get("fields"), dict) else {}
    gnss = body.get("gnss") if isinstance(body.get("gnss"), dict) else {}
    return session_id, record_kind, fields, gnss, []


@api_field_capture_bp.post("/session")
def api_create_session():
    data = request.get_json(silent=True) or {}
    job_id = str(data.get("job_id") or data.get("project_id") or "").strip()
    surveyor = str(data.get("surveyor") or "").strip()
    if not job_id:
        return jsonify({"ok": False, "error": "job_id required"}), 400
    if load_project(_projects_root(), job_id) is None:
        return jsonify({"ok": False, "error": "project not found"}), 404
    session = create_session(job_id, surveyor)
    return jsonify(
        {
            "ok": True,
            "session_id": session.id,
            "job_id": session.job_id,
            "surveyor": session.surveyor,
            "start_time": session.start_time,
        }
    )


@api_field_capture_bp.post("/record")
def api_post_record():
    uploads: list[tuple[str, bytes]]
    if request.content_type and "multipart/form-data" in request.content_type:
        session_id, record_kind, fields, gnss, uploads = _parse_payload_multipart()
    else:
        session_id, record_kind, fields, gnss, uploads = _parse_payload_json()

    if not session_id:
        return jsonify({"ok": False, "error": "session_id required"}), 400
    if record_kind not in {"pole", "span", "context"}:
        return jsonify({"ok": False, "error": "invalid record_kind"}), 400

    session = get_session_for_any_job(session_id)
    if session is None:
        return jsonify({"ok": False, "error": "session not found"}), 404
    job_id = session.job_id

    if record_kind == "pole":
        errs = validate_pole_payload(fields, len(uploads))
        if errs:
            return jsonify({"ok": False, "error": "validation", "details": errs}), 400
    elif record_kind == "span":
        errs = validate_span_payload(fields)
        if errs:
            return jsonify({"ok": False, "error": "validation", "details": errs}), 400
    else:
        errs = validate_context_payload(fields)
        if errs:
            return jsonify({"ok": False, "error": "validation", "details": errs}), 400

    try:
        rec = add_record(job_id, session_id, record_kind, fields, gnss, uploads)
    except ValueError as e:
        code = str(e)
        if code == "session_not_found":
            return jsonify({"ok": False, "error": "session not found"}), 404
        if code == "session_closed":
            return jsonify({"ok": False, "error": "session closed"}), 400
        raise

    return jsonify(
        {
            "ok": True,
            "record_id": rec.id,
            "session_id": session_id,
            "photos": rec.photos,
            "timestamp": rec.timestamp,
        }
    )


def get_session_for_any_job(session_id: str) -> FieldCaptureSession | None:
    """Find session by id by scanning project databases (PoC scale)."""
    root = _projects_root()
    if not root.exists():
        return None
    for child in root.iterdir():
        if not child.is_dir():
            continue
        job_id = child.name
        s = get_session(job_id, session_id)
        if s is not None:
            return s
    return None


def resolve_job_for_session(session_id: str) -> str | None:
    sess = get_session_for_any_job(session_id)
    return sess.job_id if sess else None


@api_field_capture_bp.get("/sessions/<job_id>")
def api_list_sessions(job_id: str):
    if load_project(_projects_root(), job_id) is None:
        return jsonify({"ok": False, "error": "project not found"}), 404
    sessions = list_sessions(job_id)
    return jsonify(
        {
            "ok": True,
            "job_id": job_id,
            "sessions": [
                {
                    "id": s.id,
                    "surveyor": s.surveyor,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "record_count": s.record_count,
                    "status": s.status,
                    "imported_file_id": s.imported_file_id,
                }
                for s in sessions
            ],
        }
    )


@api_field_capture_bp.get("/session/<session_id>/records")
def api_list_session_records(session_id: str):
    job_id = request.args.get("job_id", "").strip()
    if not job_id:
        job_id = resolve_job_for_session(session_id) or ""
    if not job_id:
        return jsonify({"ok": False, "error": "job_id query required for new sessions"}), 400
    recs = list_records(job_id, session_id)
    return jsonify(
        {
            "ok": True,
            "records": [
                {
                    "id": r.id,
                    "record_type": r.record_type,
                    "fields": r.fields,
                    "photos": r.photos,
                    "gnss_data": r.gnss_data,
                    "timestamp": r.timestamp,
                }
                for r in recs
            ],
        }
    )


@api_field_capture_bp.post("/import/<session_id>")
def api_import_session(session_id: str):
    job_id = str(
        request.args.get("job_id", "").strip()
        or (request.get_json(silent=True) or {}).get("job_id")
        or ""
    ).strip()
    if not job_id:
        job_id = resolve_job_for_session(session_id) or ""
    if not job_id:
        return jsonify({"ok": False, "error": "job_id required"}), 400

    if load_project(_projects_root(), job_id) is None:
        return jsonify({"ok": False, "error": "project not found"}), 404

    session = get_session(job_id, session_id)
    if session is None:
        return jsonify({"ok": False, "error": "session not found"}), 404

    csv_text = session_to_csv_text(job_id, session_id)
    if not csv_text.strip():
        return jsonify({"ok": False, "error": "no records to export"}), 400

    data = request.get_json(silent=True) or {}
    explicit_dno = data.get("dno")
    surveyor_note = str(data.get("surveyor_note") or "Stage 4 field capture import").strip()

    filename = secure_filename(f"field_capture_{session_id[:8]}.csv") or "field_capture.csv"
    file_id, file_dir = add_file_slot(
        _projects_root(),
        job_id,
        filename,
        intake={
            "survey_day_label": "Field capture",
            "uploaded_by": session.surveyor or "field_capture",
            "surveyor_note": surveyor_note,
        },
    )
    csv_path = file_dir / filename
    csv_path.write_text(csv_text, encoding="utf-8")

    meta_path = file_dir / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta.update(
        {
            "status": "uploaded",
            "filename": filename,
            "uploaded_path": str(csv_path.resolve()),
            "source": "field_capture",
            "field_capture_session_id": session_id,
        }
    )
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    display_id = f"{job_id}/{file_id}"
    result = process_job(file_dir, display_id, explicit_dno)
    refresh_project_summary(_projects_root(), job_id)

    if not result.get("ok"):
        return jsonify({"ok": False, "error": result.get("error"), "file_id": file_id}), 500

    mark_session_imported(job_id, session_id, file_id)

    return jsonify(
        {
            "ok": True,
            "project_id": job_id,
            "file_id": file_id,
            "session_id": session_id,
            **{
                k: result[k]
                for k in ("issue_count", "rulepack_id", "file_type", "auto_normalized")
                if k in result
            },
        }
    )
