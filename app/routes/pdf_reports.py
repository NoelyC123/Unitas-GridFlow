from __future__ import annotations

import ast
import csv
import io
import json
from pathlib import Path

from flask import Blueprint, abort, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.review_manager import load_review

pdf_reports_bp = Blueprint("pdf_reports", __name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"
PROJECTS_ROOT = PROJECT_ROOT / "uploads" / "projects"


def _job_dir(job_id: str) -> Path:
    return JOBS_ROOT / job_id


def _load_meta_from_dir(job_dir: Path) -> dict:
    path = job_dir / "meta.json"
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _load_issues_from_dir(job_dir: Path) -> list[dict]:
    path = job_dir / "issues.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _load_meta(job_id: str) -> dict:
    return _load_meta_from_dir(_job_dir(job_id))


def _load_issues(job_id: str) -> list[dict]:
    return _load_issues_from_dir(_job_dir(job_id))


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


def _build_review_context(review: dict | None) -> dict:
    if not review:
        return {
            "status": "Not Reviewed",
            "detail": "Designer review has not been completed for this project file.",
            "notes": "",
            "override_count": 0,
        }

    is_reviewed = review.get("review_status") == "reviewed"
    reviewed_at = str(review.get("reviewed_at") or "").strip()
    status = "Designer Reviewed" if is_reviewed else "Not Reviewed"
    detail = (
        f"Reviewed at {reviewed_at}."
        if is_reviewed and reviewed_at
        else "Designer review has not been completed for this project file."
    )
    return {
        "status": status,
        "detail": detail,
        "notes": str(review.get("review_notes") or "").strip(),
        "override_count": len(review.get("pairing_overrides") or []),
    }


def _draw_review_context(
    pdf: canvas.Canvas,
    review_context: dict | None,
    left: float,
    y: float,
    line_gap: float,
) -> float:
    if review_context is None:
        return y

    _draw_line(pdf, "Designer Review Status", left, y, font="Helvetica-Bold", size=12)
    y -= 8 * mm
    _draw_line(pdf, f"Status: {review_context['status']}", left, y, font="Helvetica-Bold", size=10)
    y -= line_gap
    _draw_line(pdf, str(review_context["detail"])[:110], left, y, size=9)
    y -= line_gap
    _draw_line(
        pdf,
        f"Pairing override count: {review_context['override_count']}",
        left,
        y,
        size=9,
    )
    y -= line_gap

    notes = str(review_context.get("notes") or "").strip()
    if notes:
        _draw_line(pdf, f"Review notes: {notes[:100]}", left, y, size=9)
        y -= line_gap

    return y - 4 * mm


def _parse_issue_row(row_text: object) -> dict:
    if isinstance(row_text, dict):
        return row_text
    if row_text is None:
        return {}
    text = str(row_text).strip()
    if not text:
        return {}
    try:
        parsed = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _issue_record_ref(row: dict) -> str:
    for key in ("pole_id", "asset_id", "point_id", "id", "asset_ref"):
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    row_index = row.get("__row_index__")
    if isinstance(row_index, int):
        return f"row {row_index + 1}"
    return "record"


def _issue_coordinates(row: dict) -> str:
    easting = row.get("easting")
    northing = row.get("northing")
    if easting not in (None, "") and northing not in (None, ""):
        return f"E/N {easting}, {northing}"

    lat = row.get("lat")
    lon = row.get("lon")
    if lat not in (None, "") and lon not in (None, ""):
        try:
            return f"{float(lat):.5f}, {float(lon):.5f}"
        except (TypeError, ValueError):
            return f"{lat}, {lon}"

    return "not captured"


def _issue_status_label(severity: str, issue_text: str = "") -> str:
    sev = severity.strip().upper()
    if sev == "FAIL":
        return "Design Blocker"
    if sev == "WARN":
        return "Review Required"
    lower = issue_text.lower()
    if "out of range" in lower or "coordinate mismatch" in lower or "duplicate" in lower:
        return "Design Blocker"
    if (
        "missing required field" in lower
        or "height likely estimated" in lower
        or "span" in lower
        or "replacement pair" in lower
        or "angle structure with no stay" in lower
    ):
        return "Review Required"
    return "Review Item"


def _issue_guidance(issue_text: str) -> tuple[str, str]:
    lower = issue_text.lower()

    if "missing required field" in lower and "material" in lower:
        return (
            "Structural material evidence is missing from the digital file.",
            "Confirm material from field notes, plan markups, or resurvey.",
        )
    if "missing required field" in lower and "height" in lower:
        return (
            "Pole height evidence is missing, limiting clearance and loading checks.",
            "Confirm height before relying on design calculations.",
        )
    if "missing required field" in lower:
        return (
            "Required survey evidence is missing from the record.",
            "Fill the missing field from trusted source evidence.",
        )
    if "coordinate mismatch" in lower:
        return (
            "Grid and latitude/longitude evidence disagree.",
            "Verify the coordinate source before design use.",
        )
    if "duplicate" in lower:
        return (
            "Duplicate identity or position evidence may confuse the design chain.",
            "Resolve duplicate records before handoff.",
        )
    if "span" in lower:
        return (
            "Span geometry needs review against the intended route sequence.",
            "Check the route order and adjacent pole positions.",
        )
    if "replacement pair" in lower:
        return (
            "Existing/proposed pole relationship is inferred, not designer confirmed.",
            "Verify the intended replacement pairing.",
        )
    if "angle structure with no stay" in lower:
        return (
            "Angle pole has no digital stay evidence.",
            "Check whether stay evidence is missing from the survey.",
        )

    return (
        "Issue needs review before this record is treated as design-ready.",
        "Review the source data and supporting field evidence.",
    )


def _build_design_review_item(issue: dict) -> dict:
    issue_text = str(issue.get("Issue", "Unknown issue")).strip() or "Unknown issue"
    row = _parse_issue_row(issue.get("Row"))
    consequence, action = _issue_guidance(issue_text)
    return {
        "record_ref": _issue_record_ref(row),
        "coordinates": _issue_coordinates(row),
        "status": _issue_status_label(str(issue.get("Severity", "")), issue_text),
        "issue": issue_text,
        "consequence": consequence,
        "action": action,
    }


def _wrap_text(
    pdf: canvas.Canvas,
    text: str,
    max_width: float,
    font: str,
    size: int,
    max_lines: int,
) -> list[str]:
    words = str(text).split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if pdf.stringWidth(candidate, font, size) <= max_width:
            current = candidate
            continue
        if current:
            lines.append(current)
        current = word
        if len(lines) >= max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(current)
    if len(lines) == max_lines and len(" ".join(words)) > len(" ".join(lines)):
        lines[-1] = lines[-1].rstrip(".") + "..."
    return lines or [""]


def _draw_wrapped_lines(
    pdf: canvas.Canvas,
    lines: list[str],
    x: float,
    y: float,
    font: str = "Helvetica",
    size: int = 7,
) -> None:
    pdf.setFont(font, size)
    cursor_y = y
    for line in lines:
        pdf.drawString(x, cursor_y, line)
        cursor_y -= 3.6 * mm


def _draw_design_review_table_header(
    pdf: canvas.Canvas,
    left: float,
    y: float,
    col_widths: list[float],
) -> None:
    headers = ["Record", "Coordinates", "Status", "Issue / consequence / action"]
    header_h = 7 * mm
    pdf.setFillColor(colors.HexColor("#111827"))
    pdf.rect(left, y - header_h + 1.5 * mm, sum(col_widths), header_h, fill=True, stroke=False)
    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 7)
    x = left + 2 * mm
    for header, col_w in zip(headers, col_widths, strict=False):
        pdf.drawString(x, y - 3.5 * mm, header)
        x += col_w
    pdf.setFillColor(colors.black)


def _draw_design_review_items_table(
    pdf: canvas.Canvas,
    issues: list[dict],
    left: float,
    y: float,
    top: float,
    line_gap: float,
) -> float:
    _draw_line(pdf, "Design Review Items", left, y, font="Helvetica-Bold", size=12)
    y -= 8 * mm

    if not issues:
        _draw_line(pdf, "No issues.csv found for this job, or no issues were recorded.", left, y)
        return y - line_gap

    bottom = 25 * mm
    max_rows = 25
    col_widths = [23 * mm, 36 * mm, 28 * mm, 87 * mm]
    table_width = sum(col_widths)

    def start_new_page() -> float:
        pdf.showPage()
        new_y = top
        _draw_line(
            pdf,
            "Unitas GridFlow - QA Report (continued)",
            left,
            new_y,
            font="Helvetica-Bold",
            size=14,
        )
        return new_y - 10 * mm

    _draw_design_review_table_header(pdf, left, y, col_widths)
    y -= 8 * mm

    for item in [_build_design_review_item(issue) for issue in issues[:max_rows]]:
        record_lines = _wrap_text(
            pdf, item["record_ref"], col_widths[0] - 4 * mm, "Helvetica", 7, 2
        )
        coord_lines = _wrap_text(
            pdf, item["coordinates"], col_widths[1] - 4 * mm, "Helvetica", 7, 2
        )
        status_lines = _wrap_text(
            pdf, item["status"], col_widths[2] - 4 * mm, "Helvetica-Bold", 7, 2
        )
        detail_lines = []
        for label, key in (
            ("Issue", "issue"),
            ("Consequence", "consequence"),
            ("Action", "action"),
        ):
            detail_lines.extend(
                _wrap_text(
                    pdf,
                    f"{label}: {item[key]}",
                    col_widths[3] - 4 * mm,
                    "Helvetica",
                    7,
                    2,
                )
            )

        row_line_count = max(
            len(record_lines), len(coord_lines), len(status_lines), len(detail_lines)
        )
        row_h = max(17 * mm, (row_line_count * 3.6 * mm) + 5 * mm)
        if y - row_h < bottom:
            y = start_new_page()
            _draw_design_review_table_header(pdf, left, y, col_widths)
            y -= 8 * mm

        pdf.setStrokeColor(colors.HexColor("#cbd5e1"))
        pdf.rect(left, y - row_h + 2 * mm, table_width, row_h, fill=False, stroke=True)
        x = left
        for col_w in col_widths[:-1]:
            x += col_w
            pdf.line(x, y + 2 * mm, x, y - row_h + 2 * mm)

        x = left + 2 * mm
        text_y = y - 3 * mm
        _draw_wrapped_lines(pdf, record_lines, x, text_y)
        x += col_widths[0]
        _draw_wrapped_lines(pdf, coord_lines, x + 2 * mm, text_y)
        x += col_widths[1]
        _draw_wrapped_lines(pdf, status_lines, x + 2 * mm, text_y, font="Helvetica-Bold")
        x += col_widths[2]
        _draw_wrapped_lines(pdf, detail_lines, x + 2 * mm, text_y)

        y -= row_h

    if len(issues) > max_rows:
        if y < bottom:
            y = start_new_page()
        _draw_line(
            pdf,
            f"... {len(issues) - max_rows} more design review item(s) not shown.",
            left,
            y,
        )
        y -= line_gap

    pdf.setStrokeColor(colors.black)
    return y


def _generate_qa_pdf(job_dir: Path, display_id: str, review_context: dict | None = None):
    if not job_dir.exists():
        abort(404)

    meta = _load_meta_from_dir(job_dir)
    issues = _load_issues_from_dir(job_dir)
    job_id = display_id  # used for labels only

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

    y = _draw_review_context(pdf, review_context, left, y, line_gap)

    circuit_summary = meta.get("circuit_summary") or {}
    if circuit_summary.get("summary_text"):
        _draw_line(pdf, "Circuit Summary", left, y, font="Helvetica-Bold", size=12)
        y -= 8 * mm
        _draw_line(pdf, str(circuit_summary["summary_text"])[:110], left, y, size=10)
        y -= line_gap
        y -= 4 * mm

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

    evidence_gates = meta.get("evidence_gates") or []
    if evidence_gates:
        _draw_line(pdf, "Evidence Gates", left, y, font="Helvetica-Bold", size=12)
        y -= 8 * mm
        for gate in evidence_gates:
            label = str(gate.get("label", ""))
            status = str(gate.get("status", ""))
            explanation = str(gate.get("explanation", "")).strip()
            _draw_line(pdf, f"  {label}: {status}", left, y, font="Helvetica-Bold", size=9)
            y -= line_gap
            if explanation:
                _draw_line(pdf, f"    {explanation[:108]}", left, y, size=8)
                y -= line_gap
            if y < 30 * mm:
                pdf.showPage()
                y = top
        y -= 4 * mm

    top_design_risks = meta.get("top_design_risks") or []
    if top_design_risks:
        _draw_line(pdf, "Top Design Risks", left, y, font="Helvetica-Bold", size=12)
        y -= 8 * mm
        for risk in top_design_risks:
            title = str(risk.get("title", ""))
            count = risk.get("count", 0)
            impact = str(risk.get("designer_impact", ""))
            sev_prefix = (
                "[Design Blocker] " if risk.get("severity") == "FAIL" else "[Review Required] "
            )
            _draw_line(
                pdf, f"{sev_prefix}{title} ({count})", left, y, font="Helvetica-Bold", size=10
            )
            y -= line_gap
            _draw_line(pdf, f"  {impact[:110]}", left, y, size=9)
            y -= line_gap
            if y < 30 * mm:
                pdf.showPage()
                y = top
        y -= 4 * mm

    recommended_actions = meta.get("recommended_actions") or []
    if recommended_actions:
        _draw_line(pdf, "Recommended Actions", left, y, font="Helvetica-Bold", size=12)
        y -= 8 * mm
        for item in recommended_actions:
            action_text = str(item.get("action", "")).strip()
            sev = str(item.get("severity", "warning"))
            prefix = "[!] " if sev == "critical" else "[ ] "
            _draw_line(pdf, f"  {prefix}{action_text[:105]}", left, y, size=9)
            y -= line_gap
            if y < 30 * mm:
                pdf.showPage()
                y = top
        y -= 4 * mm

    replacement_narratives = meta.get("replacement_narratives") or []
    if replacement_narratives:
        _draw_line(pdf, "Replacement Pairs", left, y, font="Helvetica-Bold", size=12)
        y -= 8 * mm
        for narrative in replacement_narratives:
            _draw_line(pdf, f"  {str(narrative)[:110]}", left, y, size=9)
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

    y = _draw_design_review_items_table(pdf, issues, left, y, top, line_gap)

    y -= 6 * mm
    _draw_line(pdf, "Generated by Unitas GridFlow.", left, y, size=9)

    # Technical Appendix — full issue detail including raw Row data.
    pdf.showPage()
    y = top

    _draw_line(
        pdf,
        "Unitas GridFlow — Technical Appendix: Issue Detail",
        left,
        y,
        font="Helvetica-Bold",
        size=14,
    )
    y -= 10 * mm

    if not issues:
        _draw_line(pdf, "No issues to show.", left, y, size=10)
    else:
        for idx, issue in enumerate(issues, start=1):
            issue_text = str(issue.get("Issue", "Unknown issue")).strip()
            row_text = str(issue.get("Row", "")).strip()
            sev = str(issue.get("Severity", "")).strip().upper()
            sev_prefix = "[Review Required] " if sev == "WARN" else ""

            _draw_line(pdf, f"{idx}. {sev_prefix}{issue_text}", left, y)
            y -= line_gap

            if row_text:
                trimmed = row_text[:130]
                _draw_line(pdf, f"   Row: {trimmed}", left, y, size=8)
                y -= line_gap

            if y < 25 * mm:
                pdf.showPage()
                y = top
                _draw_line(
                    pdf,
                    "Unitas GridFlow — Technical Appendix (continued)",
                    left,
                    y,
                    font="Helvetica-Bold",
                    size=12,
                )
                y -= 10 * mm

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/pdf",
        as_attachment=False,
        download_name=f"{display_id}_unitas_gridflow_qa_report.pdf",
    )


@pdf_reports_bp.get("/qa/<job_id>")
def qa_pdf(job_id: str):
    return _generate_qa_pdf(_job_dir(job_id), job_id)


@pdf_reports_bp.get("/qa/project/<project_id>/<file_id>")
def qa_pdf_project(project_id: str, file_id: str):
    file_dir = PROJECTS_ROOT / project_id / "files" / file_id
    return _generate_qa_pdf(
        file_dir,
        f"{project_id}_{file_id}",
        review_context=_build_review_context(load_review(file_dir)),
    )
