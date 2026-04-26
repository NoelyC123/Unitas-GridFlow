from __future__ import annotations

from flask import Blueprint, render_template

projects_page_bp = Blueprint("projects_page", __name__)


@projects_page_bp.get("/projects/")
def projects_home():
    return render_template("projects.html")


@projects_page_bp.get("/project/<project_id>")
def project_detail(project_id: str):
    return render_template("project.html", project_id=project_id)
