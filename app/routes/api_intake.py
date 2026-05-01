from __future__ import annotations

import json
import math
import re
from pathlib import Path
from typing import Any

import pandas as pd
from flask import Blueprint, jsonify, request

from app.asset_classifier import classify_asset_type, get_popup_type_label
from app.controller_intake import (
    build_circuit_summary,
    build_completeness_summary,
    build_design_readiness,
    build_top_design_risks,
    classify_record_roles,
    convert_grid_to_wgs84,
    is_controller_csv,
    is_raw_controller_dump,
    parse_controller_csv,
    parse_raw_controller_dump,
)
from app.dno_rules import DNO_RULES, RULEPACKS, filter_rules_for_controller
from app.issue_model import build_evidence_gates, build_recommended_actions, enrich_issues
from app.qa_engine import classify_height_confidence, infer_display_network_fields, run_qa_checks
from app.review_manager import delete_review
from app.route_sequencer import sequence_route

# Compiled once at module level for replacement-pair offset extraction.
_REPL_OFFSET_RE = re.compile(r"([\d.]+)m offset")
_ANGLE_CODES = {"Angle", "angle", "ANGLE"}
_STAY_EVIDENCE_CODES = {
    "Stay",
    "stay",
    "STAY",
    "Staywire",
    "staywire",
    "STAYWIRE",
    "Stay wire",
    "stay wire",
    "Stay pole",
    "stay pole",
}

api_intake_bp = Blueprint("api_intake", __name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _jobs_root() -> Path:
    return _project_root() / "uploads" / "jobs"


def _job_dir(job_id: str) -> Path:
    return _jobs_root() / job_id


def _meta_path(job_id: str) -> Path:
    return _job_dir(job_id) / "meta.json"


def _read_json(path: Path, default: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        return default or {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default or {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    cleaned_payload = _sanitize_for_json(payload)
    path.write_text(
        json.dumps(cleaned_payload, indent=2, allow_nan=False),
        encoding="utf-8",
    )


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        if pd.isna(value):
            return None
        result = float(value)
        if math.isnan(result) or math.isinf(result):
            return None
        return result
    except Exception:
        return None


def _safe_value(value: Any) -> Any:
    if value is None:
        return None

    try:
        if pd.isna(value):
            return None
    except Exception:
        pass

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value

    return value


def _sanitize_for_json(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _sanitize_for_json(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_for_json(v) for v in value]
    if isinstance(value, tuple):
        return [_sanitize_for_json(v) for v in value]
    return _safe_value(value)


def _coerce_numeric_column(df: pd.DataFrame, column: str) -> None:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")


def _copy_if_missing(df: pd.DataFrame, target: str, candidates: list[str]) -> bool:
    """
    Copy the first available candidate column into `target` only if `target`
    does not already exist or is effectively empty.
    Returns True if a copy/rename happened.
    """
    target_missing = target not in df.columns or df[target].isna().all()
    if not target_missing:
        return False

    for candidate in candidates:
        if candidate in df.columns:
            df[target] = df[candidate]
            return candidate != target

    return False


def _normalize_dataframe(df: pd.DataFrame) -> tuple[pd.DataFrame, bool]:
    df = df.copy()
    normalized = False

    # Normalise column names first: strip whitespace, lowercase, spaces→underscores.
    # This handles capitalised exports ("Latitude", "Structure Type", "Asset ID")
    # before the alias mapping runs.
    original_cols = list(df.columns)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    if list(df.columns) != original_cols:
        normalized = True

    normalized |= _copy_if_missing(
        df,
        "pole_id",
        [
            "asset_id",
            "pole_id",
            "id",
            "pole_ref",
            "asset_ref",
        ],
    )
    normalized |= _copy_if_missing(
        df,
        "height",
        [
            "height_m",
            "height",
            "pole_height_m",
            "pole_height",
            "ht_m",
        ],
    )
    normalized |= _copy_if_missing(
        df,
        "height_source",
        [
            "height_source",
            "height_method",
            "measurement_method",
            "height_measurement_method",
            "height_capture_method",
        ],
    )
    normalized |= _copy_if_missing(
        df,
        "structure_type",
        [
            "structure_type",
            "pole_type",
            "type",
        ],
    )
    normalized |= _copy_if_missing(
        df,
        "material",
        [
            "material",
            "pole_material",
            "mat",
        ],
    )
    normalized |= _copy_if_missing(
        df,
        "specification",
        [
            "specification",
            "pole_specification",
            "pole_spec",
            "design_specification",
            "design_spec",
            "proposed_specification",
        ],
    )
    normalized |= _copy_if_missing(
        df,
        "pole_class",
        ["pole_class", "class", "grade", "strength_class", "pole_grade"],
    )
    normalized |= _copy_if_missing(
        df,
        "condition",
        ["condition", "pole_condition", "asset_condition"],
    )
    normalized |= _copy_if_missing(
        df,
        "lean_direction",
        ["lean_direction", "lean_dir", "lean_bearing"],
    )
    normalized |= _copy_if_missing(
        df,
        "lean_severity",
        ["lean_severity", "lean", "lean_angle"],
    )
    normalized |= _copy_if_missing(
        df,
        "defect_type",
        ["defect_type", "defects", "defect", "pole_defects"],
    )
    normalized |= _copy_if_missing(
        df,
        "foundation_type",
        ["foundation_type", "foundation", "base_type"],
    )
    normalized |= _copy_if_missing(
        df,
        "voltage",
        ["voltage", "line_voltage", "network_voltage"],
    )
    normalized |= _copy_if_missing(
        df,
        "conductor_type",
        ["conductor_type", "conductor", "conductor_size"],
    )
    normalized |= _copy_if_missing(
        df,
        "phase_count",
        ["phase_count", "phases", "phase"],
    )
    normalized |= _copy_if_missing(
        df,
        "equipment",
        ["equipment", "mounted_equipment", "pole_equipment"],
    )
    normalized |= _copy_if_missing(
        df,
        "equipment_rating",
        ["equipment_rating", "rating", "transformer_rating"],
    )
    normalized |= _copy_if_missing(
        df,
        "surveyor",
        ["surveyor", "surveyed_by", "operator", "crew"],
    )
    normalized |= _copy_if_missing(
        df,
        "survey_date",
        ["survey_date", "date_surveyed", "capture_date", "date"],
    )
    normalized |= _copy_if_missing(
        df,
        "gnss_accuracy",
        ["gnss_accuracy", "gps_accuracy", "accuracy", "position_accuracy"],
    )
    normalized |= _copy_if_missing(
        df,
        "photo_links",
        ["photo_links", "photos", "attachments", "photo_refs"],
    )
    normalized |= _copy_if_missing(
        df,
        "year_installed",
        ["year_installed", "install_year", "year", "installation_year"],
    )
    normalized |= _copy_if_missing(
        df,
        "circuit_id",
        ["circuit_id", "circuit", "feeder_id", "network_circuit"],
    )
    normalized |= _copy_if_missing(
        df,
        "stay_present",
        ["stay_present", "has_stay", "stay_captured"],
    )
    normalized |= _copy_if_missing(
        df,
        "stay_type",
        ["stay_type", "stay_types", "stay_spec"],
    )
    normalized |= _copy_if_missing(
        df,
        "stay_bearing",
        ["stay_bearing", "stay_direction", "stay_bearing_deg"],
    )
    normalized |= _copy_if_missing(
        df,
        "stay_configuration",
        ["stay_configuration", "stay_config", "stay_arrangement"],
    )
    normalized |= _copy_if_missing(
        df,
        "anchor_details",
        ["anchor_details", "anchor_type", "anchor_spec"],
    )
    normalized |= _copy_if_missing(
        df,
        "linked_pole_id",
        ["linked_pole_id", "linked_pole", "parent_pole_id"],
    )
    normalized |= _copy_if_missing(
        df,
        "route_deviation_deg",
        ["route_deviation_deg", "angle_deviation", "deviation_deg"],
    )
    normalized |= _copy_if_missing(
        df,
        "action_required",
        ["action_required", "required_action", "design_action"],
    )
    normalized |= _copy_if_missing(
        df,
        "access_constraint",
        ["access_constraint", "access_notes", "access_issue"],
    )
    normalized |= _copy_if_missing(
        df,
        "clearance_measured",
        ["clearance_measured", "clearance", "measured_clearance"],
    )
    normalized |= _copy_if_missing(
        df,
        "distance_from_route_m",
        ["distance_from_route_m", "route_offset_m", "offset_from_route_m"],
    )
    normalized |= _copy_if_missing(
        df,
        "height_source",
        ["height_source", "pole_height_source", "measurement_source"],
    )
    normalized |= _copy_if_missing(
        df,
        "elevation",
        ["elevation", "elev", "gps_elevation", "z"],
    )
    normalized |= _copy_if_missing(
        df,
        "location",
        [
            "location_name",
            "location",
            "site",
            "site_name",
            "description",
        ],
    )
    normalized |= _copy_if_missing(df, "lat", ["latitude", "lat"])
    normalized |= _copy_if_missing(df, "lon", ["longitude", "lon", "long"])
    normalized |= _copy_if_missing(
        df,
        "easting",
        [
            "easting",
            "os_easting",
            "grid_easting",
            "grid_e",
        ],
    )
    normalized |= _copy_if_missing(
        df,
        "northing",
        [
            "northing",
            "os_northing",
            "grid_northing",
            "grid_n",
        ],
    )

    _coerce_numeric_column(df, "height")
    _coerce_numeric_column(df, "lat")
    _coerce_numeric_column(df, "lon")
    _coerce_numeric_column(df, "easting")
    _coerce_numeric_column(df, "northing")
    _coerce_numeric_column(df, "elevation")
    _coerce_numeric_column(df, "route_deviation_deg")
    _coerce_numeric_column(df, "distance_from_route_m")

    return df, normalized


def _postprocess_issues(issues_df: pd.DataFrame, df: pd.DataFrame) -> pd.DataFrame:
    """
    Current qa_engine flags both the original and repeated row for duplicates.
    For this MVP step, keep duplicate issues only on the later duplicated rows,
    so the output better matches the intended behaviour:
    - first occurrence = pass
    - repeated occurrence = fail
    """
    if issues_df.empty or "Issue" not in issues_df.columns or "Row" not in issues_df.columns:
        return issues_df

    if "pole_id" not in df.columns or "__row_index__" not in df.columns:
        return issues_df

    later_duplicate_rows = set(
        df.loc[df["pole_id"].duplicated(keep="first"), "__row_index__"].tolist()
    )

    filtered_rows: list[dict[str, Any]] = []

    for _, issue_row in issues_df.iterrows():
        issue_text = str(issue_row.get("Issue", ""))
        row_payload = issue_row.get("Row", {})

        if issue_text.startswith("Duplicate value in 'pole_id'"):
            if isinstance(row_payload, dict):
                row_index = row_payload.get("__row_index__")
                if row_index in later_duplicate_rows:
                    filtered_rows.append(issue_row.to_dict())
            continue

        filtered_rows.append(issue_row.to_dict())

    if not filtered_rows:
        return pd.DataFrame(columns=issues_df.columns)

    return pd.DataFrame(filtered_rows)


def _sanitize_issues_for_csv(issues_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean NaN/None values inside issue row payloads before writing issues.csv.
    This keeps the CSV human-readable and avoids payloads like `material: nan`.
    """
    if issues_df.empty or "Row" not in issues_df.columns:
        return issues_df

    cleaned_rows: list[dict[str, Any]] = []

    for _, issue_row in issues_df.iterrows():
        row_dict = issue_row.to_dict()
        row_payload = row_dict.get("Row")

        if isinstance(row_payload, dict):
            cleaned_payload = _sanitize_for_json(row_payload)
            # For CSV readability, use empty string instead of None in row payloads.
            cleaned_payload = {
                key: ("" if value is None else value) for key, value in cleaned_payload.items()
            }
            row_dict["Row"] = cleaned_payload

        cleaned_rows.append(row_dict)

    return pd.DataFrame(cleaned_rows)


def _collect_per_row_issues(issues_df: pd.DataFrame) -> dict[int, dict[str, Any]]:
    """
    Return {row_index: {"count": int, "texts": list, "warn_count": int, "warn_texts": list}}
    for each flagged row. WARN issues (Severity="WARN") are tracked separately.
    Stores up to 3 descriptions per row per severity, truncated to 80 chars each.
    """
    result: dict[int, dict[str, Any]] = {}
    if issues_df.empty or "Row" not in issues_df.columns:
        return result
    for _, issue_row in issues_df.iterrows():
        row_payload = issue_row.get("Row")
        issue_text = str(issue_row.get("Issue", ""))
        _sev = issue_row.get("Severity", None)
        severity = str(_sev).upper() if isinstance(_sev, str) else "FAIL"
        if isinstance(row_payload, dict):
            row_index = row_payload.get("__row_index__")
            if isinstance(row_index, int):
                if row_index not in result:
                    result[row_index] = {
                        "count": 0,
                        "texts": [],
                        "warn_count": 0,
                        "warn_texts": [],
                    }
                if severity == "WARN":
                    result[row_index]["warn_count"] += 1
                    if len(result[row_index]["warn_texts"]) < 3:
                        result[row_index]["warn_texts"].append(issue_text[:80])
                else:
                    result[row_index]["count"] += 1
                    if len(result[row_index]["texts"]) < 3:
                        result[row_index]["texts"].append(issue_text[:80])
    return result


def _build_replacement_links(
    df: pd.DataFrame,
    issues_df: pd.DataFrame,
) -> dict[int, dict[str, Any]]:
    """Map replacement-pair WARN rows to both lifecycle endpoints."""

    if issues_df.empty or "Issue" not in issues_df.columns:
        return {}

    _expole_codes = {"EXpole", "expole", "EXPOLE"}
    links: dict[int, dict[str, Any]] = {}

    structural_indices: list[int] = sorted(
        int(row.get("__row_index__"))
        for _, row in df.iterrows()
        if isinstance(row.get("__row_index__"), int)
        and row.get("_record_role") not in ("context", "third_party", "anchor")
    )
    prev_of: dict[int, int] = {}
    for i in range(1, len(structural_indices)):
        prev_of[structural_indices[i]] = structural_indices[i - 1]

    row_by_index: dict[int, Any] = {
        int(row.get("__row_index__")): row
        for _, row in df.iterrows()
        if isinstance(row.get("__row_index__"), int)
    }

    for _, issue_row in issues_df.iterrows():
        issue_text = str(issue_row.get("Issue", ""))
        if "Replacement pair" not in issue_text:
            continue
        row_payload = issue_row.get("Row", {})
        if not isinstance(row_payload, dict):
            continue
        curr_idx = row_payload.get("__row_index__")
        if not isinstance(curr_idx, int):
            continue

        curr_row = row_by_index.get(curr_idx)
        prev_idx = prev_of.get(curr_idx)
        if curr_row is None or prev_idx is None:
            continue
        prev_row = row_by_index.get(prev_idx)
        if prev_row is None:
            continue

        curr_id = str(_safe_value(curr_row.get("pole_id")) or curr_idx)
        prev_id = str(_safe_value(prev_row.get("pole_id")) or prev_idx)
        curr_st = str(_safe_value(curr_row.get("structure_type")) or "")

        if curr_st in _expole_codes:
            ex_idx, pr_idx = curr_idx, prev_idx
            ex_id, pr_id = curr_id, prev_id
        else:
            ex_idx, pr_idx = prev_idx, curr_idx
            ex_id, pr_id = prev_id, curr_id

        offset_match = _REPL_OFFSET_RE.search(issue_text)
        offset_m = float(offset_match.group(1)) if offset_match else None

        links[ex_idx] = {
            "lifecycle_state": "Existing Pole being Replaced (Recovered)",
            "being_replaced_by": pr_id,
            "match_offset_m": offset_m,
            "match_role": "recovered_existing",
        }
        links[pr_idx] = {
            "lifecycle_state": "Proposed Replacement Pole",
            "replacing": ex_id,
            "match_offset_m": offset_m,
            "match_role": "proposed_replacement",
        }

    return links


def _latlon_distance_m(lat1: Any, lon1: Any, lat2: Any, lon2: Any) -> float | None:
    try:
        lat1_f = float(lat1)
        lon1_f = float(lon1)
        lat2_f = float(lat2)
        lon2_f = float(lon2)
    except (TypeError, ValueError):
        return None

    mean_lat_rad = math.radians((lat1_f + lat2_f) / 2)
    metres_per_lat = 111_320.0
    metres_per_lon = 111_320.0 * math.cos(mean_lat_rad)
    dx = (lon2_f - lon1_f) * metres_per_lon
    dy = (lat2_f - lat1_f) * metres_per_lat
    return math.sqrt(dx * dx + dy * dy)


def _build_angle_stay_evidence(
    df: pd.DataFrame,
    proximity_m: float = 20.0,
) -> dict[int, dict[str, Any]]:
    """Return stay-evidence summaries for angle records in the map payload."""

    if "structure_type" not in df.columns:
        return {}

    stay_records: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        st = str(_safe_value(row.get("structure_type")) or "")
        if st not in _STAY_EVIDENCE_CODES:
            continue
        stay_records.append(
            {
                "type": st,
                "lat": row.get("lat"),
                "lon": row.get("lon"),
            }
        )

    result: dict[int, dict[str, Any]] = {}
    for _, row in df.iterrows():
        row_index = row.get("__row_index__")
        st = str(_safe_value(row.get("structure_type")) or "")
        if not isinstance(row_index, int) or st not in _ANGLE_CODES:
            continue

        captured: list[tuple[str, float]] = []
        for stay in stay_records:
            distance_m = _latlon_distance_m(
                row.get("lat"),
                row.get("lon"),
                stay["lat"],
                stay["lon"],
            )
            if distance_m is not None and distance_m <= proximity_m:
                captured.append((stay["type"], distance_m))

        remarks = str(_safe_value(row.get("location")) or "")
        if captured:
            captured.sort(key=lambda item: item[1])
            result[row_index] = {
                "stay_evidence_status": "captured",
                "stay_types": sorted({item[0] for item in captured}),
                "nearest_stay_distance_m": round(captured[0][1], 1),
            }
        elif "stay" in remarks.lower():
            result[row_index] = {
                "stay_evidence_status": "captured",
                "stay_types": ["Stay evidence in remarks"],
                "nearest_stay_distance_m": None,
            }
        else:
            result[row_index] = {
                "stay_evidence_status": "missing",
                "stay_types": [],
                "nearest_stay_distance_m": None,
            }

    return result


def _split_display_list(value: Any) -> list[str]:
    value = _safe_value(value)
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    text = str(value).strip()
    if not text:
        return []
    return [part.strip() for part in re.split(r"[;,|]", text) if part.strip()]


def _photo_indicators(row: pd.Series) -> dict[str, Any]:
    links = _split_display_list(row.get("photo_links"))
    return {
        "photo_links": links,
        "has_full_pole_photo": bool(_safe_value(row.get("has_full_pole_photo"))) or bool(links),
        "has_pole_top_photo": bool(_safe_value(row.get("has_pole_top_photo"))),
        "has_defect_photo": bool(_safe_value(row.get("has_defect_photo"))),
        "photo_count": len(links),
    }


def _display_value(row: pd.Series, field: str) -> Any:
    return _safe_value(row.get(field))


def _build_feature_collection(
    df: pd.DataFrame,
    issues_df: pd.DataFrame,
    job_id: str,
    rulepack_id: str,
    file_type: str = "structured",
) -> dict[str, Any]:
    per_row = _collect_per_row_issues(issues_df)
    replacement_links = _build_replacement_links(df, issues_df)
    angle_stay_evidence = _build_angle_stay_evidence(df)
    features: list[dict[str, Any]] = []

    pass_count = 0
    warn_count = 0
    fail_count = 0

    for _, row in df.reset_index(drop=True).iterrows():
        # Exclude anchor rows (reference control points) from the map output.
        # They are not survey records and may be at distant unrelated locations.
        _st_for_anchor = str(_safe_value(row.get("structure_type")) or "")
        if row.get("_record_role") == "anchor" and _st_for_anchor not in _STAY_EVIDENCE_CODES:
            continue

        row_index = row.get("__row_index__")
        lat = _safe_float(row.get("lat"))
        lon = _safe_float(row.get("lon"))

        if lat is None or lon is None:
            continue

        _empty: dict[str, Any] = {
            "count": 0,
            "texts": [],
            "warn_count": 0,
            "warn_texts": [],
        }
        row_data = per_row.get(row_index, _empty) if isinstance(row_index, int) else _empty
        row_issue_count = row_data["count"]
        row_issue_texts = row_data["texts"]
        row_warn_count = row_data.get("warn_count", 0)
        row_warn_texts = row_data.get("warn_texts", [])

        if row_issue_count > 0:
            qa_status = "FAIL"
            fail_count += 1
        elif row_warn_count > 0:
            qa_status = "WARN"
            warn_count += 1
        else:
            qa_status = "PASS"
            pass_count += 1

        # Mark replacement pairs so the map popup can show a contextual note.
        is_replacement = any("Replacement pair" in t for t in row_warn_texts)

        # Derive a cautious asset-intent label from existing data only.
        # EXpole structure_type → existing asset being replaced.
        # Non-EXpole with a replacement-pair WARN → proposed support record.
        _st = str(_safe_value(row.get("structure_type")) or "")
        if _st in ("EXpole", "expole", "EXPOLE"):
            asset_intent: str | None = "Existing asset"
        elif is_replacement:
            asset_intent = "Proposed support"
        else:
            asset_intent = None

        lifecycle_link = replacement_links.get(row_index, {}) if isinstance(row_index, int) else {}
        stay_evidence = angle_stay_evidence.get(row_index, {}) if isinstance(row_index, int) else {}
        if lifecycle_link:
            lifecycle_state = lifecycle_link.get("lifecycle_state")
        elif _st in ("EXpole", "expole", "EXPOLE"):
            lifecycle_state = "Existing Pole"
        elif asset_intent == "Proposed support" or _st in (
            "PRpole",
            "prpole",
            "PRPOLE",
            "Pol",
            "pol",
            "POL",
        ):
            lifecycle_state = "Proposed Pole"
        else:
            lifecycle_state = None

        network_fields = infer_display_network_fields(row, rulepack_id)
        photo_fields = _photo_indicators(row)
        equipment_items = _split_display_list(network_fields.get("equipment"))
        classification = classify_asset_type(row)
        is_third_party = classification.get("primary_type") == "third_party_infrastructure"
        if is_third_party:
            asset_intent = "third_party_not_network"
            lifecycle_state = None
        height_confidence = classify_height_confidence(
            {
                **row.to_dict(),
                "asset_intent": asset_intent,
                "lifecycle_state": lifecycle_state,
                "primary_type": classification.get("primary_type"),
            }
        )

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lon, lat],
            },
            "properties": {
                "id": row.get(
                    "pole_id", f"row-{int(row_index) + 1 if row_index is not None else 'unknown'}"
                ),
                "name": row.get(
                    "location", f"Record {int(row_index) + 1 if row_index is not None else ''}"
                ),
                "pole_id": _safe_value(row.get("pole_id")),
                "material": _safe_value(row.get("material")),
                "specification": _safe_value(row.get("specification")),
                "height": _safe_value(row.get("height")),
                "height_source": _display_value(row, "height_source"),
                "height_confidence": height_confidence,
                "pole_class": _display_value(row, "pole_class"),
                "condition": _display_value(row, "condition"),
                "lean_direction": _display_value(row, "lean_direction"),
                "lean_severity": _display_value(row, "lean_severity"),
                "defect_type": _display_value(row, "defect_type"),
                "foundation_type": _display_value(row, "foundation_type"),
                "voltage": _safe_value(network_fields.get("voltage")),
                "conductor_type": _safe_value(network_fields.get("conductor_type")),
                "phase_count": _safe_value(network_fields.get("phase_count")),
                "equipment": equipment_items,
                "equipment_rating": _safe_value(network_fields.get("equipment_rating")),
                "surveyor": _display_value(row, "surveyor"),
                "survey_date": _display_value(row, "survey_date"),
                "gnss_accuracy": _display_value(row, "gnss_accuracy"),
                "source_confidence": _safe_value(network_fields.get("source_confidence")),
                "primary_type": _safe_value(classification.get("primary_type")),
                "infrastructure_owner": _safe_value(classification.get("infrastructure_owner")),
                "asset_subtype": _safe_value(classification.get("subtype")),
                "is_structural_pole": bool(classification.get("is_structural_pole")),
                "is_electric_network": bool(classification.get("is_electric_network")),
                "classification_confidence": _safe_value(
                    classification.get("classification_confidence")
                ),
                "classification_warnings": classification.get("warnings", []),
                "classification_basis": _safe_value(classification.get("classification_basis")),
                "popup_type_label": get_popup_type_label(classification),
                "elevation": _display_value(row, "elevation"),
                "year_installed": _display_value(row, "year_installed"),
                "circuit_id": _display_value(row, "circuit_id"),
                "stay_present": _display_value(row, "stay_present"),
                "stay_type": _display_value(row, "stay_type"),
                "stay_bearing": _display_value(row, "stay_bearing"),
                "stay_configuration": _display_value(row, "stay_configuration"),
                "anchor_details": _display_value(row, "anchor_details"),
                "linked_pole_id": _display_value(row, "linked_pole_id"),
                "route_deviation_deg": _display_value(row, "route_deviation_deg"),
                "action_required": _display_value(row, "action_required"),
                "access_constraint": _display_value(row, "access_constraint"),
                "clearance_measured": _display_value(row, "clearance_measured"),
                "distance_from_route_m": _display_value(row, "distance_from_route_m"),
                **photo_fields,
                "qa_status": qa_status,
                "structure_type": _safe_value(row.get("structure_type")),
                "easting": _safe_value(row.get("easting")),
                "northing": _safe_value(row.get("northing")),
                "issue_count": row_issue_count,
                "issue_texts": row_issue_texts,
                "warn_count": row_warn_count,
                "warn_texts": row_warn_texts,
                "record_role": _safe_value(row.get("_record_role")),
                "relationship": "replacement_pair" if is_replacement else None,
                "asset_intent": asset_intent,
                "lifecycle_state": lifecycle_state,
                "replacing": lifecycle_link.get("replacing"),
                "being_replaced_by": lifecycle_link.get("being_replaced_by"),
                "match_offset_m": lifecycle_link.get("match_offset_m"),
                "match_role": lifecycle_link.get("match_role"),
                "stay_evidence_status": stay_evidence.get("stay_evidence_status"),
                "stay_types": stay_evidence.get("stay_types", []),
                "nearest_stay_distance_m": stay_evidence.get("nearest_stay_distance_m"),
            },
        }
        features.append(feature)

    metadata = {
        "job_id": job_id,
        "rulepack_id": rulepack_id,
        "auto_normalized": False,
        "file_type": file_type,
        "pole_count": len(features),
        "pass_count": pass_count,
        "warn_count": warn_count,
        "fail_count": fail_count,
        "issue_count": len(issues_df),
    }

    return _sanitize_for_json(
        {
            "type": "FeatureCollection",
            "features": features,
            "metadata": metadata,
        }
    )


def _build_replacement_narratives(
    df: pd.DataFrame,
    issues_df: pd.DataFrame,
) -> list[str]:
    """Build readable narrative strings for each detected replacement pair.

    Each WARN row in issues_df is the second record in the pair; the function
    looks backward through structural rows to find the first, then emits text
    like 'EXpole 99 is likely being replaced by nearby proposed support 100
    (3.2m offset).'
    """
    narratives: list[str] = []
    if issues_df.empty or "Issue" not in issues_df.columns:
        return narratives

    _expole_codes = {"EXpole", "expole", "EXPOLE"}
    ex_id_counts: dict[str, int] = {}

    # Build sorted list of structural (non-context, non-anchor) row indices.
    structural_indices: list[int] = sorted(
        int(row.get("__row_index__"))
        for _, row in df.iterrows()
        if isinstance(row.get("__row_index__"), int)
        and row.get("_record_role") not in ("context", "anchor")
    )

    # Map: row_index → immediately preceding structural row_index.
    prev_of: dict[int, int] = {}
    for i in range(1, len(structural_indices)):
        prev_of[structural_indices[i]] = structural_indices[i - 1]

    row_by_index: dict[int, Any] = {
        int(row.get("__row_index__")): row
        for _, row in df.iterrows()
        if isinstance(row.get("__row_index__"), int)
    }

    for _, issue_row in issues_df.iterrows():
        issue_text = str(issue_row.get("Issue", ""))
        if "Replacement pair" not in issue_text:
            continue
        row_payload = issue_row.get("Row", {})
        if not isinstance(row_payload, dict):
            continue
        curr_idx = row_payload.get("__row_index__")
        if not isinstance(curr_idx, int):
            continue

        curr_row = row_by_index.get(curr_idx)
        prev_idx = prev_of.get(curr_idx)
        if curr_row is None or prev_idx is None:
            continue
        prev_row = row_by_index.get(prev_idx)
        if prev_row is None:
            continue

        curr_id = str(_safe_value(curr_row.get("pole_id")) or curr_idx)
        prev_id = str(_safe_value(prev_row.get("pole_id")) or prev_idx)
        curr_st = str(_safe_value(curr_row.get("structure_type")) or "")

        if curr_st in _expole_codes:
            ex_id, pr_id = curr_id, prev_id
        else:
            ex_id, pr_id = prev_id, curr_id

        offset_match = _REPL_OFFSET_RE.search(issue_text)
        if offset_match:
            offset = float(offset_match.group(1))
            loc = "at the same surveyed position" if offset < 0.5 else f"{offset:.1f}m offset"
            narrative = (
                f"EXpole {ex_id} is likely being replaced by nearby proposed"
                f" support {pr_id} ({loc})."
            )
        else:
            narrative = (
                f"EXpole {ex_id} is likely being replaced by nearby proposed support {pr_id}."
            )
        narratives.append(narrative)
        ex_id_counts[ex_id] = ex_id_counts.get(ex_id, 0) + 1

    ambiguous_ids = [eid for eid, cnt in ex_id_counts.items() if cnt > 1]
    if ambiguous_ids:
        narratives.append(
            f"Note: {len(ambiguous_ids)} existing pole(s) have multiple proposed supports nearby"
            " — verify intended pairings before design proceeds."
        )

    return narratives


def process_job(
    job_dir: Path,
    job_id: str,
    explicit_dno: str | None = None,
) -> dict[str, Any]:
    """Process a survey CSV in job_dir and return a response-ready dict.

    Writes sequenced_route.json, issues.csv, map_data.json, and updates
    meta.json in job_dir.  Returns {"ok": True, ...} or {"ok": False, "error": ...}.
    Callers must not duplicate this logic — both legacy and project finalize routes
    call this function.
    """
    delete_review(job_dir)
    meta_path = job_dir / "meta.json"
    meta = _read_json(meta_path, default={"job_id": job_id})
    requested_dno = explicit_dno or "SPEN_11kV"
    meta["job_id"] = job_id
    meta["status"] = "processing"
    meta["rulepack_id"] = requested_dno
    _write_json(meta_path, meta)

    try:
        uploaded_path = meta.get("uploaded_path")
        if not uploaded_path:
            raise FileNotFoundError("No uploaded file path recorded in meta.json")

        csv_path = Path(uploaded_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"Uploaded CSV not found: {csv_path}")

        # Peek at the first line to detect raw controller dump format before
        # calling pd.read_csv, which would treat the metadata row as column
        # headers and make format detection impossible.
        file_type = "structured"
        with csv_path.open(encoding="utf-8", errors="replace") as _fh:
            first_line = _fh.readline()

        if is_raw_controller_dump(first_line):
            df = parse_raw_controller_dump(csv_path)
            file_type = "controller"
        else:
            df = pd.read_csv(csv_path)
            if is_controller_csv(df):
                df = parse_controller_csv(df)
                file_type = "controller"

        df, auto_normalized = _normalize_dataframe(df)
        if file_type == "controller":
            auto_normalized = True

        df = convert_grid_to_wgs84(df)
        df = classify_record_roles(df)

        completeness = build_completeness_summary(df)
        design_readiness = build_design_readiness(completeness)

        # If no DNO was explicitly supplied, infer NIE_11kV from Irish Grid CRS.
        # TM65 (EPSG:29900) and ITM (EPSG:2157) both indicate Northern Ireland;
        # the default SPEN_11kV coordinate bounds would reject valid NIE poles.
        rulepack_inferred = False
        if not explicit_dno and "_grid_crs" in df.columns:
            detected_crs = df["_grid_crs"].dropna()
            if len(detected_crs) and str(detected_crs.iloc[0]) in ("EPSG:29900", "EPSG:2157"):
                requested_dno = "NIE_11kV"
                rulepack_inferred = True

        # Add row index before QA so issue rows can be mapped back onto the map output.
        df = df.reset_index(drop=True)
        df["__row_index__"] = df.index

        selected_rules = RULEPACKS.get(requested_dno) or RULEPACKS.get("DEFAULT") or DNO_RULES
        if file_type == "controller":
            selected_rules = filter_rules_for_controller(selected_rules)
        issues_df = run_qa_checks(df, selected_rules)
        issues_df = _postprocess_issues(issues_df, df)
        issues_df = enrich_issues(issues_df)
        recommended_actions = build_recommended_actions(issues_df)
        evidence_gates = build_evidence_gates(completeness, issues_df)

        # Designer summary layer — derived purely from existing completeness + issues.
        circuit_summary = build_circuit_summary(df, completeness)
        top_design_risks = build_top_design_risks(issues_df, completeness)
        replacement_narratives = _build_replacement_narratives(df, issues_df)

        # Route sequencer — produces provisional design-chain output.
        # Wrapped in its own try/except so any sequencer bug does NOT break the
        # existing upload/map/PDF flow. Errors are logged and surfaced in meta.json.
        sequence_result: dict = {}
        try:
            sequence_result = sequence_route(df)
        except Exception as _seq_exc:
            import logging

            logging.getLogger(__name__).warning(
                "route_sequencer failed for %s: %s", job_id, _seq_exc
            )
            sequence_result = {"status": "error", "reason": str(_seq_exc)}

        seq_path = job_dir / "sequenced_route.json"
        _write_json(seq_path, sequence_result)
        sequence_summary = sequence_result.get("summary") or {
            "status": sequence_result.get("status", "error"),
            "reason": sequence_result.get("reason"),
        }

        # Count replacement pairs and surface in design readiness.
        replacement_cluster_count = 0
        if not issues_df.empty and "Severity" in issues_df.columns and "Issue" in issues_df.columns:
            replacement_cluster_count = int(
                (
                    (issues_df["Severity"] == "WARN")
                    & issues_df["Issue"].str.contains("Replacement pair", na=False)
                ).sum()
            )
        if replacement_cluster_count > 0:
            if replacement_cluster_count == 1:
                repl_label = "Proposed replacement identified near existing pole"
            else:
                repl_label = (
                    f"{replacement_cluster_count} probable replacement pairs detected"
                    " — verify intended pairings"
                )
            design_readiness.setdefault("what_this_supports", []).append(repl_label)
            design_readiness["replacement_cluster_count"] = replacement_cluster_count

        # Count angle-without-stay WARNs and surface in design readiness.
        angle_no_stay_count = 0
        if not issues_df.empty and "Severity" in issues_df.columns and "Issue" in issues_df.columns:
            angle_no_stay_count = int(
                (
                    (issues_df["Severity"] == "WARN")
                    & issues_df["Issue"].str.contains("stay evidence not captured", na=False)
                ).sum()
            )
        if angle_no_stay_count > 0:
            noun = "structure" if angle_no_stay_count == 1 else "structures"
            design_readiness.setdefault("reasons", []).append(
                f"{angle_no_stay_count} angle {noun} with no stay evidence"
                f" — check field notes, photos or plan evidence"
            )
            design_readiness["angle_no_stay_count"] = angle_no_stay_count

        # Build lightweight issue_groups triage metadata (counts per risk category).
        s_fields = completeness.get("structural_fields") or completeness.get("fields") or {}
        issue_groups: dict[str, int] = {
            "span_issues": 0,
            "replacement_clusters": replacement_cluster_count,
            "missing_heights": int(s_fields.get("height", {}).get("missing", 0)),
            "angle_stay": angle_no_stay_count,
        }
        if not issues_df.empty and "Issue" in issues_df.columns:
            issue_groups["span_issues"] = int(
                issues_df["Issue"]
                .str.contains(
                    "Probable duplicate pole|Probable missing intermediate pole|"
                    "Span very short|Span unusually short|Span borderline short",
                    na=False,
                )
                .sum()
            )

        map_issues_df = issues_df.copy()
        csv_issues_df = _sanitize_issues_for_csv(issues_df)

        issues_path = job_dir / "issues.csv"
        csv_issues_df.to_csv(issues_path, index=False)

        feature_collection = _build_feature_collection(
            df, map_issues_df, job_id, requested_dno, file_type
        )
        feature_collection["metadata"]["auto_normalized"] = auto_normalized
        for _rkey in (
            "structural_count",
            "context_count",
            "third_party_count",
            "anchor_count",
        ):
            if _rkey in completeness:
                feature_collection["metadata"][_rkey] = completeness[_rkey]

        map_data_path = job_dir / "map_data.json"
        map_data_path.write_text(
            json.dumps(_sanitize_for_json(feature_collection), indent=2, allow_nan=False),
            encoding="utf-8",
        )

        meta.update(
            {
                "status": "complete",
                "rulepack_id": requested_dno,
                "rulepack_inferred": rulepack_inferred,
                "file_type": file_type,
                "auto_normalized": auto_normalized,
                "completeness": completeness,
                "design_readiness": design_readiness,
                "circuit_summary": circuit_summary,
                "top_design_risks": top_design_risks,
                "replacement_narratives": replacement_narratives,
                "recommended_actions": recommended_actions,
                "evidence_gates": evidence_gates,
                "sequence_summary": sequence_summary,
                "issue_groups": issue_groups,
                "issue_count": len(map_issues_df),
                "pole_count": completeness.get(
                    "total_records", feature_collection["metadata"]["pole_count"]
                ),
                "pass_count": feature_collection["metadata"]["pass_count"],
                "warn_count": feature_collection["metadata"]["warn_count"],
                "fail_count": feature_collection["metadata"]["fail_count"],
                "issues_csv": str(issues_path),
                "map_data_json": str(map_data_path),
            }
        )
        _write_json(meta_path, meta)

        return {
            "ok": True,
            "job_id": job_id,
            "file_type": file_type,
            "auto_normalized": auto_normalized,
            "rulepack_id": requested_dno,
            "rulepack_inferred": rulepack_inferred,
            "issue_count": len(map_issues_df),
            "completeness": completeness,
            "design_readiness": design_readiness,
        }

    except Exception as exc:
        meta.update({"status": "error", "error": str(exc)})
        _write_json(meta_path, meta)
        return {"ok": False, "job_id": job_id, "error": str(exc)}


@api_intake_bp.post("/import/<job_short>")
def finalize(job_short: str):
    bare_id = job_short[1:] if job_short.startswith("J") else job_short
    job_id = f"J{bare_id}"
    data = request.get_json(silent=True) or {}
    explicit_dno = data.get("dno")

    result = process_job(_job_dir(job_id), job_id, explicit_dno)
    if not result["ok"]:
        return jsonify({"ok": False, "job_id": job_id, "error": result["error"]}), 500
    return jsonify(result)
