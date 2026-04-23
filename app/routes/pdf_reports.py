from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from flask import Blueprint, abort, send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

pdf_reports_bp = Blueprint("pdf_reports", __name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"


def _job_dir(job_id: str) -> Path:
    return JOBS_ROOT / job_id


def _meta_path(job_id: str) -> Path:
    return _job_dir(job_id) / "meta.json"


def _issues_path(job_id: str) -> Path:
    return _job_dir(job_id) / "issues.csv"


def _load_meta(job_id: str) -> dict:
    path = _meta_path(job_id)

    if not path.exists():
        return {}

    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_issues(job_id: str) -> list[dict]:
    path = _issues_path(job_id)

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _draw_line(
    pdf: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    font: str = "Helvetica",
    size: int = 10,
) -> None:
    pdf.setFont(font, size)
    pdf.drawString(x, y, text)


@pdf_reports_bp.get("/qa/<job_id>")
def qa_pdf(job_id: str):
    job_path = _job_dir(job_id)

    if not job_path.exists():
        abort(404)

    meta = _load_meta(job_id)
    issues = _load_issues(job_id)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    left = 18 * mm
    top = height - 18 * mm
    line_gap = 6 * mm
    y = top

    _draw_line(pdf, "Unitas GridFlow — QA Report", left, y, font="Helvetica-Bold", size=16)
    y -= 10 * mm

    _draw_line(pdf, f"Job ID: {job_id}", left, y, font="Helvetica-Bold", size=11)
    y -= line_gap
    _draw_line(pdf, f"Status: {meta.get('status', 'unknown')}", left, y)
    y -= line_gap
    _draw_line(pdf, f"Rulepack: {meta.get('rulepack_id', 'SPEN_11kV')}", left, y)
    y -= line_gap
    _draw_line(pdf, f"Auto-normalized: {meta.get('auto_normalized', False)}", left, y)
    y -= line_gap
    _draw_line(pdf, f"Record count: {meta.get('pole_count', 0)}", left, y)
    y -= line_gap
    _draw_line(pdf, f"Issue count: {meta.get('issue_count', 0)}", left, y)
    y -= 8 * mm

    design_readiness = meta.get("design_readiness") or {}
    if design_readiness:
        verdict = design_readiness.get("verdict", "")
        _draw_line(pdf, "Design Readiness", left, y, font="Helvetica-Bold", size=12)
        y -= 8 * mm
        _draw_line(pdf, f"Verdict: {verdict}", left, y, font="Helvetica-Bold", size=11)
        y -= line_gap

        for reason in design_readiness.get("reasons") or []:
            _draw_line(pdf, f"  - {str(reason)[:110]}", left, y, size=9)
            y -= line_gap
            if y < 30 * mm:
                pdf.showPage()
                y = top

        coverage = design_readiness.get("coverage") or {}
        if coverage:
            _draw_line(pdf, "Survey Coverage:", left, y)
            y -= line_gap
            for cat, rating in coverage.items():
                _draw_line(pdf, f"  {cat}: {rating}", left, y, size=9)
                y -= line_gap
                if y < 30 * mm:
                    pdf.showPage()
                    y = top

        what_supports = design_readiness.get("what_this_supports") or []
        if what_supports:
            _draw_line(pdf, "This file supports:", left, y)
            y -= line_gap
            for item in what_supports:
                _draw_line(pdf, f"  + {str(item)[:110]}", left, y, size=9)
                y -= line_gap
                if y < 30 * mm:
                    pdf.showPage()
                    y = top

        y -= 4 * mm

    completeness = meta.get("completeness") or {}
    if completeness:
        _draw_line(pdf, "Survey Completeness", left, y, font="Helvetica-Bold", size=12)
        y -= 8 * mm

        total = completeness.get("total_records", 0)
        _draw_line(pdf, f"Total records: {total}", left, y)
        y -= line_gap

        s_count = completeness.get("structural_count")
        c_count = completeness.get("context_count")
        a_count = completeness.get("anchor_count")
        if s_count is not None:
            parts = [f"{s_count} structural"]
            if c_count:
                parts.append(f"{c_count} context")
            if a_count:
                parts.append(f"{a_count} anchor")
            _draw_line(pdf, f"Composition: {', '.join(parts)}", left, y, size=9)
            y -= line_gap

        pos = completeness.get("position_status", "unknown")
        _draw_line(pdf, f"Position: {pos}", left, y)
        y -= line_gap

        crs = completeness.get("grid_crs_detected")
        if crs:
            _draw_line(pdf, f"Grid CRS: {crs}", left, y)
            y -= line_gap

        fields = completeness.get("fields") or {}
        skip_fields = {"lat", "lon", "easting", "northing"}
        coverage_fields = {k: v for k, v in fields.items() if k not in skip_fields}
        if coverage_fields:
            _draw_line(pdf, "Field coverage:", left, y)
            y -= line_gap
            for field_name, info in coverage_fields.items():
                present = info.get("present", 0)
                pct = info.get("coverage_pct", 0.0)
                _draw_line(pdf, f"  {field_name}: {present}/{total} ({pct}%)", left, y, size=9)
                y -= line_gap
                if y < 30 * mm:
                    pdf.showPage()
                    y = top

        codes = completeness.get("feature_codes_found") or []
        if codes:
            _draw_line(pdf, f"Feature codes: {', '.join(codes)}", left, y)
            y -= line_gap

        y -= 4 * mm

    _draw_line(pdf, "Issues", left, y, font="Helvetica-Bold", size=12)
    y -= 8 * mm

    if not issues:
        _draw_line(pdf, "No issues.csv found for this job, or no issues were recorded.", left, y)
        y -= line_gap
    else:
        max_rows = 20

        for idx, issue in enumerate(issues[:max_rows], start=1):
            issue_text = str(issue.get("Issue", "Unknown issue")).strip()
            row_text = str(issue.get("Row", "")).strip()

            _draw_line(pdf, f"{idx}. {issue_text}", left, y)
            y -= line_gap

            if row_text:
                trimmed = row_text[:120]
                _draw_line(pdf, f"   Row: {trimmed}", left, y, size=9)
                y -= line_gap

            if y < 25 * mm:
                pdf.showPage()
                y = top
                _draw_line(
                    pdf,
                    "Unitas GridFlow — QA Report (continued)",
                    left,
                    y,
                    font="Helvetica-Bold",
                    size=14,
                )
                y -= 10 * mm

        if len(issues) > max_rows:
            _draw_line(
                pdf,
                f"... {len(issues) - max_rows} more issue(s) not shown in this PDF.",
                left,
                y,
            )
            y -= line_gap

    y -= 6 * mm
    _draw_line(pdf, "Generated by Unitas GridFlow local MVP.", left, y, size=9)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"{job_id}_unitas_gridflow_qa_report.pdf",
    )
