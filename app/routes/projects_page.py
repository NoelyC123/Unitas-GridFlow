from __future__ import annotations

from flask import Blueprint, render_template, request

projects_page_bp = Blueprint("projects_page", __name__)


@projects_page_bp.get("/projects/")
def projects_home():
    return render_template("projects.html")


@projects_page_bp.get("/project/<project_id>")
def project_detail(project_id: str):
    return render_template("project.html", project_id=project_id)


@projects_page_bp.get("/field-capture")
def field_capture_page():
    """Stage 4 — offline-friendly structured capture UI (optional ``project_id`` query)."""
    project_id = request.args.get("project_id", "").strip()
    return render_template("field_capture_form.html", project_id=project_id)
