from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, Response

d2d_export_bp = Blueprint("d2d_export", __name__)

_JOBS_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "jobs"

_CHAIN_HEADERS = [
    "Seq",
    "Point_ID",
    "Feature_Code",
    "Easting",
    "Northing",
    "Lat",
    "Lon",
    "Height",
    "Span_To_Next_m",
    "Deviation_Angle_deg",
    "Replaces_Point_ID",
    "Replaces_Distance_m",
    "Candidate_Section_Break",
    "Sequence_Confidence",
    "Remark",
]

_EXPOLE_HEADERS = [
    "Point_ID",
    "Feature_Code",
    "Easting",
    "Northing",
    "Height",
    "Matched_To_Proposed_ID",
    "Distance_m",
]

_CONTEXT_HEADERS = [
    "Point_ID",
    "Feature_Code",
    "Easting",
    "Northing",
    "Height",
    "Remark",
]


def _unavailable(reason: str = "D2D export is not available for this job.") -> Response:
    return Response(reason, status=404, mimetype="text/plain")


@d2d_export_bp.get("/export/<job_id>")
def d2d_export(job_id: str) -> Response:
    seq_path = _JOBS_ROOT / job_id / "sequenced_route.json"

    if not seq_path.exists():
        return _unavailable()

    try:
        seq = json.loads(seq_path.read_text(encoding="utf-8"))
    except Exception:
        return _unavailable()

    if seq.get("status") != "ok" or not seq.get("chain"):
        return _unavailable()

    cfg = seq.get("config_used") or {}
    chain = seq.get("chain") or []
    matched_expoles = seq.get("matched_expoles") or []
    unmatched_expoles = seq.get("unmatched_expoles") or []
    context_features = seq.get("context_features") or []

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    angle_thr = cfg.get("angle_split_threshold_deg", "—")
    gap_thr = cfg.get("gap_split_threshold_m", "—")
    expole_thr = cfg.get("expole_match_threshold_m", "—")

    buf = io.StringIO()

    buf.write("# Unitas GridFlow — Provisional D2D Candidate Export\n")
    buf.write("# NOT verified PoleCAD import format — for designer review only\n")
    buf.write(
        f"# Job: {job_id} | Generated: {timestamp}"
        f" | Thresholds: provisional"
        f" (angle={angle_thr}deg, gap={gap_thr}m, EXpole match={expole_thr}m)\n"
    )
    buf.write("\n")

    writer = csv.writer(buf)

    writer.writerow(_CHAIN_HEADERS)
    for r in chain:
        writer.writerow(
            [
                r.get("seq"),
                r.get("point_id"),
                r.get("feature_code"),
                r.get("easting"),
                r.get("northing"),
                r.get("lat"),
                r.get("lon"),
                r.get("height"),
                r.get("span_to_next_m"),
                r.get("deviation_angle_deg"),
                r.get("replaces_point_id"),
                r.get("replaces_distance_m"),
                r.get("candidate_section_break"),
                r.get("sequence_confidence"),
                r.get("remark"),
            ]
        )

    buf.write("\n")
    buf.write("# Matched EXpoles (replacement references)\n")
    writer.writerow(_EXPOLE_HEADERS)
    for r in matched_expoles:
        writer.writerow(
            [
                r.get("point_id"),
                r.get("feature_code"),
                r.get("easting"),
                r.get("northing"),
                r.get("height"),
                r.get("matched_to_proposed_id"),
                r.get("distance_m"),
            ]
        )

    buf.write("\n")
    buf.write("# Unmatched EXpoles (could not pair within threshold — verify in field notes)\n")
    writer.writerow(_EXPOLE_HEADERS)
    for r in unmatched_expoles:
        writer.writerow(
            [
                r.get("point_id"),
                r.get("feature_code"),
                r.get("easting"),
                r.get("northing"),
                r.get("height"),
                r.get("matched_to_proposed_id"),
                r.get("distance_m"),
            ]
        )

    buf.write("\n")
    buf.write("# Context Features (for reference only — not part of structural chain)\n")
    writer.writerow(_CONTEXT_HEADERS)
    for r in context_features:
        writer.writerow(
            [
                r.get("point_id"),
                r.get("feature_code"),
                r.get("easting"),
                r.get("northing"),
                r.get("height"),
                r.get("remark"),
            ]
        )

    filename = f"{job_id}_d2d_candidate.csv"
    return Response(
        buf.getvalue(),
        status=200,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
