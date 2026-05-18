"""Secure local photo serving for pilot field evidence."""

from __future__ import annotations

import logging
import re
from pathlib import Path

from flask import Blueprint, abort, current_app, send_from_directory

logger = logging.getLogger(__name__)

photos_bp = Blueprint("photos", __name__)

_SURVEY_RE = re.compile(r"^[\w\-]+$")
_POLE_RE = re.compile(r"^[\w\-]+$")
_FILENAME_RE = re.compile(r"^[\w\-]+\.(jpg|jpeg|png|JPG|JPEG|PNG)$")


def _log_404(message: str) -> None:
    logger.warning("Photo 404: %s", message)


@photos_bp.get("/api/photos/<survey_id>/<pole_id>/<filename>")
def serve_photo(survey_id: str, pole_id: str, filename: str):
    root = current_app.config.get("REAL_PILOT_DATA_ROOT", "")
    if not root:
        _log_404("REAL_PILOT_DATA_ROOT not configured")
        abort(404)

    if not _SURVEY_RE.match(survey_id):
        _log_404(f"invalid survey_id={survey_id!r}")
        abort(404)
    if not _POLE_RE.match(pole_id):
        _log_404(f"invalid pole_id={pole_id!r}")
        abort(404)
    if not _FILENAME_RE.match(filename):
        _log_404(f"invalid filename={filename!r}")
        abort(404)

    root_path = Path(root).resolve()
    photo_dir = (
        root_path / survey_id / "enwl_enrichment_clean" / pole_id / "field_photos"
    ).resolve()

    if not photo_dir.is_relative_to(root_path):
        _log_404(f"path escaped root for survey_id={survey_id!r} pole_id={pole_id!r}")
        abort(404)

    photo_path = (photo_dir / filename).resolve()
    if not photo_path.is_relative_to(root_path):
        _log_404(f"file path escaped root for filename={filename!r}")
        abort(404)

    if not photo_dir.exists():
        _log_404(f"photo_dir missing: {photo_dir}")
        abort(404)
    if not photo_path.exists() or not photo_path.is_file():
        _log_404(f"photo missing: {photo_path}")
        abort(404)

    return send_from_directory(str(photo_dir), filename)
