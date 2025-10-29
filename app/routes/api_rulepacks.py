from flask import Blueprint, jsonify
api_rulepacks_bp = Blueprint("api_rulepacks", __name__)
@api_rulepacks_bp.get("/<rulepack_id>")
def get_rulepack(rulepack_id):
    return jsonify({"rulepack_id": rulepack_id, "dno":"SPEN","thresholds":{},"enums":{},"layers":{}})
