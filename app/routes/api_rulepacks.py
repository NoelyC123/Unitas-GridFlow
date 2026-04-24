from __future__ import annotations

from flask import Blueprint, jsonify

from app.dno_rules import RULEPACKS

api_rulepacks_bp = Blueprint("api_rulepacks", __name__)

# Exclude DEFAULT — it is an internal fallback, not a user-selectable rulepack.
_SUPPORTED = {k: v for k, v in RULEPACKS.items() if k != "DEFAULT"}


def _summarize_rulepack(rulepack_id: str, rules: list[dict]) -> dict:
    """Derive a truthful, auditable summary from the actual rule list."""
    check_types: dict[str, int] = {}
    height_range: dict | None = None
    lat_bounds: dict | None = None
    lon_bounds: dict | None = None

    for rule in rules:
        check = rule.get("check", "unknown")
        check_types[check] = check_types.get(check, 0) + 1

        if check == "range":
            field = rule.get("field")
            if field == "height":
                height_range = {"min_m": rule.get("min"), "max_m": rule.get("max")}
            elif field == "lat":
                lat_bounds = {"min": rule.get("min"), "max": rule.get("max")}
            elif field == "lon":
                lon_bounds = {"min": rule.get("min"), "max": rule.get("max")}

    coord_bounds = None
    if lat_bounds or lon_bounds:
        coord_bounds = {"lat": lat_bounds, "lon": lon_bounds}

    return {
        "rulepack_id": rulepack_id,
        "total_checks": len(rules),
        "check_types": check_types,
        "height_range_m": height_range,
        "coordinate_bounds": coord_bounds,
    }


@api_rulepacks_bp.get("/")
def list_rulepacks():
    """List all currently supported rulepack IDs."""
    return jsonify({"rulepacks": sorted(_SUPPORTED.keys())})


@api_rulepacks_bp.get("/<rulepack_id>")
def get_rulepack(rulepack_id: str):
    """Return truthful metadata for a supported rulepack, or 404."""
    if rulepack_id not in RULEPACKS:
        return jsonify({"error": f"Rulepack not found: {rulepack_id}"}), 404
    return jsonify(_summarize_rulepack(rulepack_id, RULEPACKS[rulepack_id]))
