from __future__ import annotations

import json
from pathlib import Path

from flask import Blueprint, jsonify, request

from app.review_manager import (
    build_review,
    delete_review,
    enrich_overrides_with_distances,
    load_review,
    save_review,
)

api_review_bp = Blueprint("api_review", __name__)

_PROJECTS_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "projects"


def _file_dir(project_id: str, file_id: str) -> Path:
    return _PROJECTS_ROOT / project_id / "files" / file_id


def _load_seq(file_dir: Path) -> dict | None:
    seq_path = file_dir / "sequenced_route.json"
    if not seq_path.exists():
        return None
    try:
        return json.loads(seq_path.read_text(encoding="utf-8"))
    except Exception:
        return None


@api_review_bp.get("/project/<project_id>/file/<file_id>/review")
def get_review(project_id: str, file_id: str):
    fd = _file_dir(project_id, file_id)
    if not fd.exists():
        return jsonify({"ok": False, "error": "File slot not found"}), 404
    review = load_review(fd)
    if review is None:
        return jsonify({"ok": True, "review_status": "not_reviewed", "pairing_overrides": []})
    return jsonify({"ok": True, **review})


@api_review_bp.post("/project/<project_id>/file/<file_id>/review")
def save_review_route(project_id: str, file_id: str):
    fd = _file_dir(project_id, file_id)
    if not fd.exists():
        return jsonify({"ok": False, "error": "File slot not found"}), 404

    data = request.get_json(silent=True) or {}
    review_status = str(data.get("review_status", "not_reviewed"))
    review_notes = str(data.get("review_notes", ""))
    raw_overrides: list[dict] = data.get("pairing_overrides") or []

    if review_status not in ("reviewed", "not_reviewed"):
        return jsonify({"ok": False, "error": "Invalid review_status"}), 400

    # Enrich overrides with server-calculated distances
    seq = _load_seq(fd)
    if seq and raw_overrides:
        raw_overrides = enrich_overrides_with_distances(raw_overrides, seq)

    existing = load_review(fd)
    review = build_review(
        file_id=file_id,
        review_status=review_status,
        review_notes=review_notes,
        pairing_overrides=raw_overrides,
        existing_review=existing,
    )
    save_review(fd, review)
    return jsonify({"ok": True, "review_status": review_status})


@api_review_bp.delete("/project/<project_id>/file/<file_id>/review")
def reset_review(project_id: str, file_id: str):
    fd = _file_dir(project_id, file_id)
    if not fd.exists():
        return jsonify({"ok": False, "error": "File slot not found"}), 404
    deleted = delete_review(fd)
    return jsonify({"ok": True, "deleted": deleted})
