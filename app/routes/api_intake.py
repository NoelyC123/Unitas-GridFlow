from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd
from flask import Blueprint, jsonify, request

from app.controller_intake import (
    build_completeness_summary,
    convert_grid_to_wgs84,
    is_controller_csv,
    is_raw_controller_dump,
    parse_controller_csv,
    parse_raw_controller_dump,
)
from app.dno_rules import DNO_RULES, RULEPACKS
from app.qa_engine import run_qa_checks

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


def _infer_issue_rows(issues_df: pd.DataFrame) -> set[int]:
    flagged_rows: set[int] = set()

    if issues_df.empty or "Row" not in issues_df.columns:
        return flagged_rows

    for row_payload in issues_df["Row"].tolist():
        if isinstance(row_payload, dict):
            row_index = row_payload.get("__row_index__")
            if isinstance(row_index, int):
                flagged_rows.add(row_index)

    return flagged_rows


def _build_feature_collection(
    df: pd.DataFrame,
    issues_df: pd.DataFrame,
    job_id: str,
    rulepack_id: str,
) -> dict[str, Any]:
    flagged_rows = _infer_issue_rows(issues_df)
    features: list[dict[str, Any]] = []

    pass_count = 0
    fail_count = 0

    for _, row in df.reset_index(drop=True).iterrows():
        row_index = row.get("__row_index__")
        lat = _safe_float(row.get("lat"))
        lon = _safe_float(row.get("lon"))

        if lat is None or lon is None:
            continue

        if row_index in flagged_rows:
            qa_status = "FAIL"
            fail_count += 1
        else:
            qa_status = "PASS"
            pass_count += 1

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
                "height": _safe_value(row.get("height")),
                "qa_status": qa_status,
                "structure_type": _safe_value(row.get("structure_type")),
                "easting": _safe_value(row.get("easting")),
                "northing": _safe_value(row.get("northing")),
            },
        }
        features.append(feature)

    metadata = {
        "job_id": job_id,
        "rulepack_id": rulepack_id,
        "auto_normalized": False,
        "pole_count": len(features),
        "span_count": 0,
        "pass_count": pass_count,
        "warn_count": 0,
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


@api_intake_bp.post("/import/<job_short>")
def finalize(job_short: str):
    bare_id = job_short[1:] if job_short.startswith("J") else job_short
    job_id = f"J{bare_id}"

    data = request.get_json(silent=True) or {}
    requested_dno = data.get("dno") or "SPEN_11kV"

    job_dir = _job_dir(job_id)
    meta_path = _meta_path(job_id)

    meta = _read_json(meta_path, default={"job_id": job_id})
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

        completeness = build_completeness_summary(df)

        # Add row index before QA so issue rows can be mapped back onto the map output.
        df = df.reset_index(drop=True)
        df["__row_index__"] = df.index

        selected_rules = RULEPACKS.get(requested_dno) or RULEPACKS.get("DEFAULT") or DNO_RULES
        issues_df = run_qa_checks(df, selected_rules)
        issues_df = _postprocess_issues(issues_df, df)

        map_issues_df = issues_df.copy()
        csv_issues_df = _sanitize_issues_for_csv(issues_df)

        issues_path = job_dir / "issues.csv"
        csv_issues_df.to_csv(issues_path, index=False)

        feature_collection = _build_feature_collection(df, map_issues_df, job_id, requested_dno)
        feature_collection["metadata"]["auto_normalized"] = auto_normalized

        map_data_path = job_dir / "map_data.json"
        map_data_path.write_text(
            json.dumps(_sanitize_for_json(feature_collection), indent=2, allow_nan=False),
            encoding="utf-8",
        )

        meta.update(
            {
                "status": "complete",
                "rulepack_id": requested_dno,
                "file_type": file_type,
                "auto_normalized": auto_normalized,
                "completeness": completeness,
                "issue_count": len(map_issues_df),
                "pole_count": feature_collection["metadata"]["pole_count"],
                "span_count": feature_collection["metadata"]["span_count"],
                "pass_count": feature_collection["metadata"]["pass_count"],
                "warn_count": feature_collection["metadata"]["warn_count"],
                "fail_count": feature_collection["metadata"]["fail_count"],
                "issues_csv": str(issues_path),
                "map_data_json": str(map_data_path),
            }
        )
        _write_json(meta_path, meta)

        return jsonify(
            {
                "ok": True,
                "job_id": job_id,
                "file_type": file_type,
                "auto_normalized": auto_normalized,
                "rulepack_id": requested_dno,
                "issue_count": len(map_issues_df),
                "completeness": completeness,
            }
        )

    except Exception as exc:
        meta.update(
            {
                "status": "error",
                "error": str(exc),
            }
        )
        _write_json(meta_path, meta)
        return jsonify({"ok": False, "job_id": job_id, "error": str(exc)}), 500
