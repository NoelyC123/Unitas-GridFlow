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
    "Section_Split_Candidate",
    "Section_ID",
    "Section_Boundary",
    "Design_Pole_No",
    "Section_Seq_No",
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
    "Matched_Design_Pole_No",
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

_DETACHED_HEADERS = [
    "Point_ID",
    "Feature_Code",
    "Easting",
    "Northing",
    "Remark",
    "Detach_Reason",
]

_INTERLEAVED_HEADERS = [
    "Point_ID",
    "Feature_Code",
    "Easting",
    "Northing",
    "Height",
    "Remark",
    "Role",
    "Section_ID",
    "Section_Boundary",
    "Design_Pole_No",
    "Section_Seq_No",
    "Matched_Proposed_ID",
    "Matched_Design_Pole_No",
]


def _unavailable(reason: str = "D2D export is not available for this job.") -> Response:
    return Response(reason, status=404, mimetype="text/plain")


def _load_seq(job_id: str) -> dict | None:
    seq_path = _JOBS_ROOT / job_id / "sequenced_route.json"
    if not seq_path.exists():
        return None
    try:
        seq = json.loads(seq_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if seq.get("status") != "ok" or not seq.get("chain"):
        return None
    return seq


@d2d_export_bp.get("/export/<job_id>")
def d2d_export(job_id: str) -> Response:
    seq = _load_seq(job_id)
    if seq is None:
        return _unavailable()

    cfg = seq.get("config_used") or {}
    chain = seq.get("chain") or []
    matched_expoles = seq.get("matched_expoles") or []
    unmatched_expoles = seq.get("unmatched_expoles") or []
    context_features = seq.get("context_features") or []
    detached_records = seq.get("detached_records") or []
    summary = seq.get("summary") or {}

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    angle_thr = cfg.get("angle_split_threshold_deg", "—")
    gap_thr = cfg.get("gap_split_threshold_m", "—")
    expole_thr = cfg.get("expole_match_threshold_m", "—")

    buf = io.StringIO()
    buf.write("# Unitas GridFlow — Provisional D2D Candidate Export (Clean Chain View)\n")
    buf.write("# NOT verified PoleCAD import format — for designer review only\n")
    buf.write(
        f"# Job: {job_id} | Generated: {timestamp}"
        f" | Thresholds: provisional"
        f" (angle={angle_thr}deg, gap={gap_thr}m, EXpole match={expole_thr}m)\n"
    )
    conf_warn = summary.get("confidence_warning")
    if conf_warn:
        buf.write(f"# {conf_warn}\n")
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
                r.get("section_split_candidate"),
                r.get("section_id"),
                r.get("section_boundary"),
                r.get("design_pole_number"),
                r.get("section_sequence_number"),
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
                r.get("matched_design_pole_number"),
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
                r.get("matched_design_pole_number"),
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

    if detached_records:
        buf.write("\n")
        buf.write(
            "# Detached / Reference Points"
            " (excluded from chain — not required or large spatial gap)\n"
        )
        writer.writerow(_DETACHED_HEADERS)
        for r in detached_records:
            writer.writerow(
                [
                    r.get("point_id"),
                    r.get("feature_code"),
                    r.get("easting"),
                    r.get("northing"),
                    r.get("remark"),
                    r.get("detach_reason"),
                ]
            )

    filename = f"{job_id}_d2d_candidate.csv"
    return Response(
        buf.getvalue(),
        status=200,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@d2d_export_bp.get("/interleaved/<job_id>")
def d2d_interleaved(job_id: str) -> Response:
    seq = _load_seq(job_id)
    if seq is None:
        return _unavailable()

    cfg = seq.get("config_used") or {}
    interleaved_view = seq.get("interleaved_view") or []
    summary = seq.get("summary") or {}

    if not interleaved_view:
        return _unavailable("Interleaved view is not available for this job.")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    angle_thr = cfg.get("angle_split_threshold_deg", "—")
    gap_thr = cfg.get("gap_split_threshold_m", "—")
    expole_thr = cfg.get("expole_match_threshold_m", "—")
    section_count = summary.get("section_count", "—")
    total_detached = summary.get("total_detached", 0)

    buf = io.StringIO()
    buf.write("# Unitas GridFlow — Provisional D2D Working View (Interleaved)\n")
    buf.write("# All records in original file order — proposed, existing, context inline\n")
    buf.write("# NOT verified PoleCAD import format — for designer review only\n")
    buf.write(
        f"# Job: {job_id} | Generated: {timestamp}"
        f" | Sections: {section_count}"
        f" | Detached: {total_detached}"
        f" | Thresholds: provisional"
        f" (angle={angle_thr}deg, gap={gap_thr}m, EXpole match={expole_thr}m)\n"
    )
    conf_warn = summary.get("confidence_warning")
    if conf_warn:
        buf.write(f"# {conf_warn}\n")
    buf.write("\n")

    writer = csv.writer(buf)
    writer.writerow(_INTERLEAVED_HEADERS)

    for r in interleaved_view:
        writer.writerow(
            [
                r.get("point_id"),
                r.get("feature_code"),
                r.get("easting"),
                r.get("northing"),
                r.get("height"),
                r.get("remark"),
                r.get("role"),
                r.get("section_id"),
                r.get("section_boundary"),
                r.get("design_pole_number"),
                r.get("section_sequence_number"),
                r.get("matched_proposed_id"),
                r.get("matched_design_pole_number"),
            ]
        )

    filename = f"{job_id}_d2d_working_view.csv"
    return Response(
        buf.getvalue(),
        status=200,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
