from __future__ import annotations

import json
from pathlib import Path

from flask import Blueprint, render_template

review_page_bp = Blueprint("review_page", __name__)

_PROJECTS_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "projects"


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


@review_page_bp.get("/review/project/<project_id>/<file_id>")
def review_file(project_id: str, file_id: str):
    file_dir = _PROJECTS_ROOT / project_id / "files" / file_id
    seq = _load_json(file_dir / "sequenced_route.json")
    meta = _load_json(file_dir / "meta.json")
    review = _load_json(file_dir / "review.json") or None

    chain = seq.get("chain") or []
    matched_expoles = seq.get("matched_expoles") or []
    unmatched_expoles = seq.get("unmatched_expoles") or []
    sections = seq.get("sections") or []
    summary = seq.get("summary") or {}

    # Proposed poles available for reassignment
    proposed_poles = [
        {
            "point_id": r.get("point_id"),
            "feature_code": r.get("feature_code"),
            "design_pole_number": r.get("design_pole_number"),
            "remark": r.get("remark"),
            "seq": r.get("seq"),
            "easting": r.get("easting"),
            "northing": r.get("northing"),
        }
        for r in chain
    ]

    # Build quick lookup of current overrides by EXpole point_id
    override_by_expole: dict[str, dict] = {}
    if review:
        for ov in review.get("pairing_overrides") or []:
            override_by_expole[str(ov["expole_point_id"])] = ov

    return render_template(
        "review.html",
        project_id=project_id,
        file_id=file_id,
        meta=meta,
        matched_expoles=matched_expoles,
        unmatched_expoles=unmatched_expoles,
        proposed_poles=proposed_poles,
        sections=sections,
        summary=summary,
        review=review,
        override_by_expole=override_by_expole,
    )
