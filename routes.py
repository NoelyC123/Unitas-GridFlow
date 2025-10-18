import os
import shutil
import zipfile
from flask import Blueprint, render_template, request, redirect, flash, url_for, send_file
import pandas as pd
import geopandas as gpd
from werkzeug.utils import secure_filename

from qa_engine import run_qa_checks
from dno_rules import DNO_RULES

main = Blueprint("main", __name__)

UPLOAD_FOLDER = "uploads"
GIS_FOLDER = "temp_gis"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GIS_FOLDER, exist_ok=True)

@main.route("/")
def home():
    return render_template("index.html")

@main.route("/upload_csv", methods=["POST"])
def upload_csv():
    file = request.files.get("csv_file")
    if file and file.filename.endswith(".csv"):
        filepath = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(filepath)

        try:
            df = pd.read_csv(filepath)
            results = run_qa_checks(df, DNO_RULES)
            results_html = results.to_html(classes="table", index=False)
            return render_template("results.html", results_html=results_html)
        except Exception as e:
            flash(f"Error processing file: {str(e)}")
            return redirect(url_for("main.home"))
    else:
        flash("Please upload a valid CSV file.")
        return redirect(url_for("main.home"))

@main.route("/upload_gis", methods=["POST"])
def upload_gis():
    file = request.files.get("gis_file")
    if file and file.filename.endswith(".zip"):
        zip_path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
        file.save(zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(GIS_FOLDER)

        return redirect(url_for("main.map_preview"))
    else:
        flash("Please upload a valid .zip shapefile.")
        return redirect(url_for("main.home"))

@main.route("/map_preview")
def map_preview():
    points = []

    try:
        for fname in os.listdir(GIS_FOLDER):
            if fname.endswith(".shp"):
                gdf = gpd.read_file(os.path.join(GIS_FOLDER, fname))
                for _, row in gdf.iterrows():
                    points.append({
                        "lat": row.geometry.y,
                        "lon": row.geometry.x,
                        "id": row.get("id", "N/A"),
                        "status": row.get("status", "Unknown")
                    })
    except Exception as e:
        flash(f"Error loading shapefile: {str(e)}")

    return render_template("map.html", geojson_points=points)

@main.route("/export_dxf")
def export_dxf():
    dxf_path = os.path.join(GIS_FOLDER, "exported.dxf")
    os.makedirs(GIS_FOLDER, exist_ok=True)

    # Mock DXF content
    with open(dxf_path, "w") as f:
        f.write("0\nSECTION\n2\nHEADER\n0\nENDSEC\n0\nEOF\n")

    return send_file(dxf_path, as_attachment=True)
