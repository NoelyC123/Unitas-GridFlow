# app/routes/jobs_page.py
from flask import Blueprint, render_template

jobs_bp = Blueprint("jobs_page", __name__)


@jobs_bp.get("/")
def jobs_home():
    return render_template("jobs.html")