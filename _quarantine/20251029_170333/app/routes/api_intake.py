from flask import Blueprint, jsonify, request
api_intake_bp = Blueprint("api_intake", __name__)
@api_intake_bp.post("/import/<job_short>")
def finalize(job_short):
    data = request.get_json(silent=True) or {}
    return jsonify({"ok": True, "job_id": f"J{job_short}", "keys": data.get("keys", [])})
