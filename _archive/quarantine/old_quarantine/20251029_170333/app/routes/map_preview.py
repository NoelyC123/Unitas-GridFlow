from flask import Blueprint, jsonify
map_preview_bp = Blueprint("map_preview", __name__)
@map_preview_bp.get("/data/<job_id>")
def map_data(job_id):
    return jsonify({"type":"FeatureCollection","features":[],"metadata":{"job_id":job_id,"rulepack_id":"SPEN_11kV","auto_normalized":False,"pole_count":0,"span_count":0,"pass_count":0,"warn_count":0,"fail_count":0}})
