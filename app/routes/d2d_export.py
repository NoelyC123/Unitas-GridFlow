from __future__ import annotations

import csv
import io
import json
from datetime import datetime, timezone
from pathlib import Path

from flask import Blueprint, Response

from app.review_manager import apply_pairing_overrides, load_review

d2d_export_bp = Blueprint("d2d_export", __name__)

_JOBS_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "jobs"
_PROJECTS_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "projects"

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


def _unavailable(reason: str = "Design chain export is not available for this job.") -> Response:
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


def _load_seq_from_path(seq_path: Path) -> dict | None:
    if not seq_path.exists():
        return None
    try:
        seq = json.loads(seq_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if seq.get("status") != "ok" or not seq.get("chain"):
        return None
    return seq


def _write_section_summary(buf: io.StringIO, sections: list[dict]) -> None:
    """Write a compact section summary block into the CSV header area."""
    buf.write("#\n")
    buf.write(f"# Section summary: {len(sections)} section(s)\n")
    for sec in sections:
        sid = sec.get("section_id", "?")
        start = sec.get("start_seq", "?")
        end = sec.get("end_seq", "?")
        count = sec.get("pole_count", "?")
        boundary = sec.get("boundary_point_id")
        overlap = sec.get("overlap_with_next_section", False)
        boundary_note = f" | boundary: point {boundary}" if boundary else ""
        overlap_note = f" | overlaps section {sid + 1}" if overlap else ""
        buf.write(
            f"#   Section {sid}: seq {start}–{end} | {count} poles{boundary_note}{overlap_note}\n"
        )
    buf.write("#\n")


def _render_chain_export(seq: dict, job_id: str, reviewed_label: str | None = None) -> Response:
    cfg = seq.get("config_used") or {}
    chain = seq.get("chain") or []
    matched_expoles = seq.get("matched_expoles") or []
    unmatched_expoles = seq.get("unmatched_expoles") or []
    context_features = seq.get("context_features") or []
    detached_records = seq.get("detached_records") or []
    sections = seq.get("sections") or []
    summary = seq.get("summary") or {}

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    angle_thr = cfg.get("angle_split_threshold_deg", "—")
    gap_thr = cfg.get("gap_split_threshold_m", "—")
    expole_thr = cfg.get("expole_match_threshold_m", "—")
    status_label = reviewed_label or "provisional"

    buf = io.StringIO()
    buf.write(f"# Unitas GridFlow — Design Chain Export ({status_label})\n")
    buf.write(
        "# Proposed poles in route sequence order."
        " EXpole references and context features listed separately.\n"
    )
    buf.write("# For the original file-order audit use the Raw Working Audit export.\n")
    if reviewed_label:
        buf.write(f"# {reviewed_label}.\n")
    else:
        buf.write(
            "# NOT verified PoleCAD import format — provisional output for designer review only.\n"
        )
    buf.write(
        f"# Job: {job_id} | Generated: {timestamp}"
        f" | Thresholds: provisional"
        f" (angle={angle_thr}deg, gap={gap_thr}m, EXpole match={expole_thr}m)\n"
    )
    conf_warn = summary.get("confidence_warning")
    if conf_warn:
        buf.write(f"# {conf_warn}\n")

    if sections:
        _write_section_summary(buf, sections)
    else:
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
    buf.write("# Matched EXpoles (replacement references — see Replaces columns in main chain)\n")
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
    buf.write(
        "# Unmatched EXpoles"
        " (no proposed pole within matching threshold — verify against field notes)\n"
    )
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
    buf.write("# Context Features (survey observations — not part of the structural pole chain)\n")
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
        buf.write("# --- Detached / Reference Records ---\n")
        buf.write(
            "# These records are retained for traceability"
            " but are NOT part of the main design chain.\n"
        )
        buf.write(
            "# They do not influence sequencing, spans, section membership or design numbering.\n"
        )
        buf.write(
            '# Reason codes: "remark: not required" = survey remark excluded them'
            ' | "large spatial gap from main route" = located far from main route.\n'
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

    filename = f"{job_id}_design_chain.csv"
    return Response(
        buf.getvalue(),
        status=200,
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@d2d_export_bp.get("/export/<job_id>")
def d2d_export(job_id: str) -> Response:
    seq = _load_seq(job_id)
    if seq is None:
        return _unavailable()
    return _render_chain_export(seq, job_id)


def _render_interleaved_export(
    seq: dict, job_id: str, reviewed_label: str | None = None
) -> Response:
    cfg = seq.get("config_used") or {}
    interleaved_view = seq.get("interleaved_view") or []
    sections = seq.get("sections") or []
    summary = seq.get("summary") or {}

    if not interleaved_view:
        return _unavailable("Interleaved view is not available for this job.")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    angle_thr = cfg.get("angle_split_threshold_deg", "—")
    gap_thr = cfg.get("gap_split_threshold_m", "—")
    expole_thr = cfg.get("expole_match_threshold_m", "—")
    section_count = summary.get("section_count", "—")
    total_detached = summary.get("total_detached", 0)
    status_label = reviewed_label or "provisional"

    buf = io.StringIO()
    buf.write(f"# Unitas GridFlow — Raw Working Audit ({status_label})\n")
    buf.write(
        "# All records in original file order:"
        " proposed poles, existing poles, and context features inline.\n"
    )
    buf.write("# Section markers and Role column are added — original file order is preserved.\n")
    buf.write("# This secondary audit view preserves the old manual working-file context.\n")
    if reviewed_label:
        buf.write(f"# {reviewed_label}.\n")
    else:
        buf.write(
            "# NOT verified PoleCAD import format — provisional output for designer review only.\n"
        )
    buf.write(
        f"# Job: {job_id} | Generated: {timestamp}"
        f" | Sections: {section_count}"
        f" | Detached records excluded: {total_detached}"
        f" | Thresholds: provisional"
        f" (angle={angle_thr}deg, gap={gap_thr}m, EXpole match={expole_thr}m)\n"
    )
    conf_warn = summary.get("confidence_warning")
    if conf_warn:
        buf.write(f"# {conf_warn}\n")

    if sections:
        _write_section_summary(buf, sections)
    else:
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

    filename = f"{job_id}_raw_working_audit.csv"
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
    return _render_interleaved_export(seq, job_id)


# ---------------------------------------------------------------------------
# Project-file variants — delegate to the same rendering logic
# ---------------------------------------------------------------------------


@d2d_export_bp.get("/export/project/<project_id>/<file_id>")
def d2d_export_project(project_id: str, file_id: str) -> Response:
    file_dir = _PROJECTS_ROOT / project_id / "files" / file_id
    seq = _load_seq_from_path(file_dir / "sequenced_route.json")
    if seq is None:
        return _unavailable()
    review = load_review(file_dir)
    seq = apply_pairing_overrides(seq, review)
    reviewed_label = (
        f"Designer Reviewed — {review['reviewed_at']}"
        if review and review.get("review_status") == "reviewed"
        else None
    )
    safe_id = f"{project_id}_{file_id}"
    return _render_chain_export(seq, safe_id, reviewed_label=reviewed_label)


@d2d_export_bp.get("/interleaved/project/<project_id>/<file_id>")
def d2d_interleaved_project(project_id: str, file_id: str) -> Response:
    file_dir = _PROJECTS_ROOT / project_id / "files" / file_id
    seq = _load_seq_from_path(file_dir / "sequenced_route.json")
    if seq is None:
        return _unavailable()
    review = load_review(file_dir)
    seq = apply_pairing_overrides(seq, review)
    reviewed_label = (
        f"Designer Reviewed — {review['reviewed_at']}"
        if review and review.get("review_status") == "reviewed"
        else None
    )
    safe_id = f"{project_id}_{file_id}"
    return _render_interleaved_export(seq, safe_id, reviewed_label=reviewed_label)
