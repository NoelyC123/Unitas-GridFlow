"""Map Overlay Route — Stage 5C baseline vs field dual-layer map."""

from __future__ import annotations

import json
import logging
import math
from pathlib import Path

from flask import Blueprint, jsonify, render_template

logger = logging.getLogger(__name__)

map_overlay_bp = Blueprint("map_overlay", __name__, url_prefix="/map")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_ROOT = PROJECT_ROOT / "uploads" / "jobs"

_CONFIDENCE_COLORS = {
    "HIGH": "#10b981",
    "MEDIUM": "#f59e0b",
    "LOW": "#ef4444",
}


def _get_lat_lng(record: dict) -> tuple[float | None, float | None]:
    """Extract lat/lng from a record, handling nested gps dict."""
    lat = record.get("latitude") or record.get("lat") or (record.get("gps") or {}).get("latitude")
    lng = (
        record.get("longitude")
        or record.get("lng")
        or record.get("lon")
        or (record.get("gps") or {}).get("longitude")
    )
    try:
        return float(lat) if lat is not None else None, float(lng) if lng is not None else None
    except (TypeError, ValueError):
        return None, None


def _haversine_approx_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Fast flat-earth distance in metres — sufficient for pole offset checks."""
    dlat = (lat2 - lat1) * 111_000
    dlng = (lng2 - lng1) * 111_000 * math.cos(math.radians(lat1))
    return round(math.sqrt(dlat**2 + dlng**2), 1)


def _build_baseline_features(baseline_data: list) -> list[dict]:
    features = []
    for pole in baseline_data:
        lat, lng = _get_lat_lng(pole)
        if lat is None or lng is None:
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lng, lat]},
                "properties": {
                    "support_number": pole.get("support_number", "Unknown"),
                    "layer": "baseline",
                    "voltage": pole.get("voltage", ""),
                    "pole_type": pole.get("pole_type", ""),
                    "source": "DNO Baseline",
                },
            }
        )
    return features


def _build_field_features(field_data: list) -> list[dict]:
    features = []
    for pole in field_data:
        lat, lng = _get_lat_lng(pole)
        if lat is None or lng is None:
            continue
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lng, lat]},
                "properties": {
                    "support_number": pole.get("support_number", "Unknown"),
                    "layer": "field",
                    "evidence_quality": pole.get("evidence_quality", ""),
                    "special_flags": pole.get("special_flags", []),
                    "source": "Field Survey",
                },
            }
        )
    return features


def _build_match_lines(
    register_entries: list,
    baseline_by_sn: dict[str, list],
    field_by_sn: dict[str, list],
) -> list[dict]:
    lines = []
    for entry in register_entries:
        baseline_sn = entry.get("baseline_support_number") or entry.get("support_number")
        field_sn = entry.get("field_support_number") or entry.get("support_number")
        confidence = entry.get("match_confidence", "LOW")

        b_coords = baseline_by_sn.get(baseline_sn)
        f_coords = field_by_sn.get(field_sn)

        if b_coords is None or f_coords is None:
            continue

        distance_m = _haversine_approx_m(b_coords[1], b_coords[0], f_coords[1], f_coords[0])

        lines.append(
            {
                "type": "Feature",
                "geometry": {"type": "LineString", "coordinates": [b_coords, f_coords]},
                "properties": {
                    "support_number": baseline_sn,
                    "match_confidence": confidence,
                    "color": _CONFIDENCE_COLORS.get(confidence, "#6b7280"),
                    "distance_m": distance_m,
                    "conflict_flags": entry.get("conflict_flags", {}),
                    "verification_flags": entry.get("verification_flags", {}),
                },
            }
        )
    return lines


@map_overlay_bp.route("/overlay/<job_id>")
def overlay_view(job_id: str):
    """Render the overlay map view."""
    return render_template(
        "map_overlay.html",
        job_id=job_id,
        page_title=f"Overlay Map — {job_id}",
    )


@map_overlay_bp.route("/overlay/data/<job_id>")
def overlay_data(job_id: str):
    """Return JSON for dual-layer overlay map."""
    job_dir = JOBS_ROOT / job_id
    match_register_path = job_dir / "03_match_register.json"

    if not match_register_path.exists():
        return jsonify({"error": f"Job not found: {job_id}"}), 404

    try:
        match_register = json.loads(match_register_path.read_text(encoding="utf-8"))
        baseline_data = json.loads(
            (job_dir / "01_baseline_dataset.json").read_text(encoding="utf-8")
        )
        field_data = json.loads((job_dir / "02_field_dataset.json").read_text(encoding="utf-8"))
        merged_data = json.loads((job_dir / "04_merged_dataset.json").read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        logger.error("Overlay file missing for job %s: %s", job_id, exc)
        return jsonify({"error": str(exc)}), 404
    except Exception as exc:
        logger.error("Overlay load error for job %s: %s", job_id, exc)
        return jsonify({"error": str(exc)}), 500

    baseline_poles = _build_baseline_features(baseline_data)
    field_poles = _build_field_features(field_data)

    baseline_by_sn = {
        f["properties"]["support_number"]: f["geometry"]["coordinates"] for f in baseline_poles
    }
    field_by_sn: dict[str, list] = {}
    for pole in field_data:
        sn = pole.get("support_number")
        lat, lng = _get_lat_lng(pole)
        if sn and lat is not None and lng is not None:
            field_by_sn[sn] = [lng, lat]

    register_entries = (
        match_register if isinstance(match_register, list) else match_register.get("entries", [])
    )
    match_lines = _build_match_lines(register_entries, baseline_by_sn, field_by_sn)

    design_status = {
        m["support_number"]: {
            "design_ready": m.get("design_ready", False),
            "verification_flags": m.get("verification_flags", {}),
        }
        for m in merged_data
        if m.get("support_number")
    }

    confidences = [ml["properties"]["match_confidence"] for ml in match_lines]
    return jsonify(
        {
            "job_id": job_id,
            "baseline_poles": baseline_poles,
            "field_poles": field_poles,
            "match_lines": match_lines,
            "design_status": design_status,
            "statistics": {
                "total_baseline": len(baseline_poles),
                "total_field": len(field_poles),
                "total_matched": len(match_lines),
                "high_confidence": confidences.count("HIGH"),
                "medium_confidence": confidences.count("MEDIUM"),
                "low_confidence": confidences.count("LOW"),
            },
        }
    )
