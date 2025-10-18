# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, send_file, flash
import os
import pandas as pd
import geopandas as gpd
from werkzeug.utils import secure_filename
from app.qa_engine import run_qa_checks
from app.dno_rules import DNO_RULES

main = Blueprint("main", __name__)

UPLOAD_FOLDER = "uploads"
GIS_FOLDER = "temp_gis"

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files.get("csv_file")
    if file and file.filename:
        try:
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(filepath)
            df = pd.read_csv(filepath)
            results = run_qa_checks(df, DNO_RULES)
            results_html = results.to_html(classes="table")
            return render_template("results.html", results=results_html)
        except Exception as e:
            flash(f"Error processing CSV: {str(e)}")
            return redirect(url_for("main.home"))
    flash("CSV upload failed or no file selected.")
    return redirect(url_for("main.home"))

@main.route("/upload_gis", methods=["POST"])
def upload_gis():
    file = request.files.get("gis_file")
    if file and file.filename.endswith(".zip"):
        try:
            os.makedirs(GIS_FOLDER, exist_ok=True)
            filepath = os.path.join(GIS_FOLDER, secure_filename(file.filename))
            file.save(filepath)
            os.system(f"unzip -o {filepath} -d {GIS_FOLDER}")
            shapefiles = [f for f in os.listdir(GIS_FOLDER) if f.endswith(".shp")]
            if shapefiles:
                gdf = gpd.read_file(os.path.join(GIS_FOLDER, shapefiles[0]))
                gdf_html = gdf.head().to_html(classes="table")
                return render_template("gis_preview.html", gdf=gdf_html)
        except Exception as e:
            flash(f"Error with GIS upload: {str(e)}")
    flash("GIS upload failed.")
    return redirect(url_for("main.home"))

@main.route("/map_preview")
def map_preview():
    return render_template("map.html")

@main.route("/export_dxf")
def export_dxf():
    os.makedirs(GIS_FOLDER, exist_ok=True)
    dxf_path = os.path.join(GIS_FOLDER, "exported.dxf")
    with open(dxf_path, "w") as f:
        f.write("0\nSECTION\n2\nHEADER\n0\nENDSEC\n0\nEOF")
    return send_file(dxf_path, as_attachment=True)