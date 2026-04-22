from flask import Blueprint, jsonify
api_jobs_bp = Blueprint("api_jobs", __name__)
@api_jobs_bp.get("/")
def list_jobs():
    return jsonify({"jobs":[]})
