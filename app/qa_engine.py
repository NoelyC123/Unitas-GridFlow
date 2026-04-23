from __future__ import annotations

import math
import re

import pandas as pd
from pyproj import Transformer

_OSGB_TRANSFORMER = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)

# Contextual/environmental survey markers — not structural poles.
# Excluded from structural span checks and structural-only rules so that
# Gate, Hedge, Track, Stream etc never trigger height or structural FAILs.
_CONTEXT_FEATURE_CODES: frozenset[str] = frozenset(
    {
        "Hedge",
        "hedge",
        "HEDGE",
        "Tree",
        "tree",
        "TREE",
        "Wall",
        "wall",
        "WALL",
        "Fence",
        "fence",
        "FENCE",
        "Post",
        "post",
        "POST",
        "Gate",
        "gate",
        "GATE",
        "Track",
        "track",
        "TRACK",
        "Stream",
        "stream",
        "STREAM",
    }
)

# Explicit structural support records — informational, used by callers that
# need to distinguish structural from unknown feature codes.
_STRUCTURAL_FEATURE_CODES: frozenset[str] = frozenset(
    {
        "Pol",
        "pol",
        "POL",
        "Angle",
        "angle",
        "ANGLE",
        "EXpole",
        "expole",
        "EXPOLE",
        "Terminal",
        "terminal",
        "TERMINAL",
        "Stay pole",
        "Service pole",
        "Pole",
        "pole",
        "POLE",
        "Wood Pole",
        "Steel Pole",
        "Concrete Pole",
        "Composite Pole",
    }
)


def _is_context_row(row: "pd.Series", has_structure_type: bool) -> bool:
    """Return True when this row represents a non-structural contextual feature."""
    if not has_structure_type:
        return False
    st = row.get("structure_type")
    return isinstance(st, str) and st in _CONTEXT_FEATURE_CODES


def _deduplicate_issues(issues: list[dict]) -> list[dict]:
    """Collapse duplicate issues that fire for the same row with the same logical check.

    Two issues are considered duplicates when they share the same row index and the
    same issue-text prefix (text before the first opening parenthesis). This handles
    the case where BASE_RULES and a rulepack both define a height-range rule: both
    fire independently and produce messages like "height out of range (7-25)" and
    "height out of range (7-20)" for the same row — only the first should surface.
    """
    seen: set[tuple] = set()
    result: list[dict] = []
    for issue in issues:
        row_dict = issue.get("Row") or {}
        row_idx = row_dict.get("__row_index__", None)
        text = issue.get("Issue", "")
        # Normalise by stripping the parenthesised parameter suffix so that
        # "height out of range (7-25)" and "height out of range (7-20)" share a key.
        prefix = text.split(" (")[0].strip()
        key = (row_idx, prefix)
        if key in seen:
            continue
        seen.add(key)
        result.append(issue)
    return result


def _is_missing_value(series: pd.Series) -> pd.Series:
    if series.dtype == "object":
        return series.isnull() | (series.astype(str).str.strip() == "")
    return series.isnull()


def _is_missing_scalar(value: object) -> bool:
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except Exception:
        pass
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def run_qa_checks(df, rules):
    issues = []

    # Exclude anchor rows from all checks except span_distance.
    # Anchor rows (grid reference control points like GB_Kelso) must never
    # generate QA issues. span_distance receives the full df so it can detect
    # the route chain break at anchor locations.
    if "_record_role" in df.columns:
        _df_no_anchor = df[df["_record_role"] != "anchor"].copy()
    else:
        _df_no_anchor = df

    for rule in rules:
        check = rule.get("check")
        field = rule.get("field")

        # span_distance uses the full df to handle anchor-based chain breaks;
        # all other checks use the anchor-filtered view.
        qc = df if check == "span_distance" else _df_no_anchor

        # --- checks that don't use a single `field` key ---

        if check == "paired_required":
            fields = rule.get("fields") or []
            missing_columns = [name for name in fields if name not in qc.columns]
            if missing_columns:
                for missing in missing_columns:
                    issues.append({"Issue": f"Missing column: {missing}", "Row": {}})
                continue

            if len(fields) < 2:
                issues.append({"Issue": "Invalid paired_required rule: need 2+ fields", "Row": {}})
                continue

            for _, row in qc.iterrows():
                values = [row.get(name) for name in fields]
                present = [not _is_missing_scalar(v) for v in values]
                if any(present) and not all(present):
                    missing = [fields[i] for i, ok in enumerate(present) if not ok]
                    issues.append(
                        {
                            "Issue": f"Missing required paired field(s): {', '.join(missing)}",
                            "Row": row.to_dict(),
                        }
                    )

        elif check == "dependent_allowed_values":
            if_field = rule.get("if_field")
            then_field = rule.get("then_field")
            missing_cols = [c for c in (if_field, then_field) if not c or c not in qc.columns]
            if missing_cols:
                for missing in missing_cols:
                    issues.append({"Issue": f"Missing column: {missing}", "Row": {}})
                continue

            mapping = rule.get("mapping") or {}

            for _, row in qc.iterrows():
                if_value = row.get(if_field)
                then_value = row.get(then_field)
                if _is_missing_scalar(if_value) or _is_missing_scalar(then_value):
                    continue

                allowed_then = mapping.get(if_value)
                if not allowed_then:
                    continue
                if then_value not in allowed_then:
                    issues.append(
                        {
                            "Issue": (
                                f"Inconsistent '{then_field}' for '{if_field}={if_value}': "
                                f"{then_value}"
                            ),
                            "Row": row.to_dict(),
                        }
                    )

        elif check == "coord_consistency":
            # Skip when easting/northing are in a non-OSGB CRS. This check
            # reprojects lat/lon to EPSG:27700 and compares against declared
            # easting/northing; for TM65/ITM files the comparison is across
            # different coordinate spaces and always produces false positives.
            if "_grid_crs" in qc.columns:
                detected_crs = qc["_grid_crs"].dropna()
                if len(detected_crs) and str(detected_crs.iloc[0]) != "EPSG:27700":
                    continue

            lat_field = rule.get("lat_field", "lat")
            lon_field = rule.get("lon_field", "lon")
            easting_field = rule.get("easting_field", "easting")
            northing_field = rule.get("northing_field", "northing")
            tolerance_m = rule.get("tolerance_m", 100)

            required_cols = [lat_field, lon_field, easting_field, northing_field]
            missing_cols = [c for c in required_cols if c not in qc.columns]
            if missing_cols:
                for mc in missing_cols:
                    issues.append({"Issue": f"Missing column: {mc}", "Row": {}})
                continue

            transformer = _OSGB_TRANSFORMER

            for _, row in qc.iterrows():
                lat = row.get(lat_field)
                lon = row.get(lon_field)
                easting = row.get(easting_field)
                northing = row.get(northing_field)

                if any(_is_missing_scalar(v) for v in (lat, lon, easting, northing)):
                    continue

                try:
                    calc_e, calc_n = transformer.transform(float(lon), float(lat))
                except Exception:
                    issues.append(
                        {
                            "Issue": "Could not convert lat/lon to OSGB",
                            "Row": row.to_dict(),
                        }
                    )
                    continue

                dist = math.sqrt((calc_e - float(easting)) ** 2 + (calc_n - float(northing)) ** 2)
                if dist > tolerance_m:
                    issues.append(
                        {
                            "Issue": (
                                f"Coordinate mismatch: lat/lon and easting/northing "
                                f"are {dist:.0f}m apart (tolerance {tolerance_m}m)"
                            ),
                            "Row": row.to_dict(),
                        }
                    )

        elif check == "unique_pair":
            fields = rule.get("fields") or []
            missing_columns = [name for name in fields if name not in qc.columns]
            if missing_columns:
                for missing in missing_columns:
                    issues.append({"Issue": f"Missing column: {missing}", "Row": {}})
                continue

            if len(fields) < 2:
                issues.append({"Issue": "Invalid unique_pair rule: need 2+ fields", "Row": {}})
                continue

            all_present = ~qc[fields].apply(_is_missing_value).any(axis=1)
            df_present = qc[all_present]

            duplicate_mask = df_present.duplicated(subset=fields, keep="first")
            for _, row in df_present[duplicate_mask].iterrows():
                values = ", ".join(str(row[f]) for f in fields)
                issues.append(
                    {
                        "Issue": f"Duplicate pair ({', '.join(fields)}): {values}",
                        "Row": row.to_dict(),
                    }
                )

        elif check == "span_distance":
            # qc == df here (full DataFrame including anchor rows)
            lat_field = rule.get("lat_field", "lat")
            lon_field = rule.get("lon_field", "lon")
            min_m = rule.get("min_m", 10)
            max_m = rule.get("max_m", 500)

            required_cols = [lat_field, lon_field]
            missing_cols = [c for c in required_cols if c not in qc.columns]
            if missing_cols:
                for mc in missing_cols:
                    issues.append({"Issue": f"Missing column: {mc}", "Row": {}})
                continue

            transformer = _OSGB_TRANSFORMER
            has_structure_type = "structure_type" in qc.columns
            has_record_role = "_record_role" in qc.columns

            prev_e = prev_n = None
            for _, row in qc.iterrows():
                # Anchor rows are at unrelated reference locations — reset chain.
                if has_record_role and row.get("_record_role") == "anchor":
                    prev_e = prev_n = None
                    continue
                # Context rows bridge the span — skip without resetting chain.
                if _is_context_row(row, has_structure_type):
                    continue

                lat = row.get(lat_field)
                lon = row.get(lon_field)
                if any(_is_missing_scalar(v) for v in (lat, lon)):
                    prev_e = prev_n = None
                    continue
                try:
                    e, n = transformer.transform(float(lon), float(lat))
                except Exception:
                    prev_e = prev_n = None
                    continue
                if prev_e is not None:
                    dist = math.sqrt((e - prev_e) ** 2 + (n - prev_n) ** 2)
                    if dist < min_m:
                        issues.append(
                            {
                                "Issue": (
                                    f"Span too short: {dist:.0f}m between structural records "
                                    f"(min {min_m}m) — possible duplicate entry"
                                ),
                                "Row": row.to_dict(),
                            }
                        )
                    elif dist > max_m:
                        issues.append(
                            {
                                "Issue": (
                                    f"Span too long: {dist:.0f}m between structural records "
                                    f"(max {max_m}m) — possible GPS error or missing record"
                                ),
                                "Row": row.to_dict(),
                            }
                        )
                prev_e, prev_n = e, n

        # --- checks that use a single `field` key ---

        elif field not in qc.columns:
            issues.append({"Issue": f"Missing column: {field}", "Row": {}})

        elif check == "unique":
            duplicate_mask = qc[field].duplicated(keep="first")
            duplicates = qc.loc[duplicate_mask, field].tolist()

            for dup in duplicates:
                rows = qc[qc[field] == dup].to_dict(orient="records")
                for row in rows:
                    issues.append({"Issue": f"Duplicate value in '{field}': {dup}", "Row": row})

        elif check == "range":
            min_val = rule.get("min", float("-inf"))
            max_val = rule.get("max", float("inf"))
            structural_only = rule.get("structural_only", False)
            has_st = "structure_type" in qc.columns

            numeric_series = pd.to_numeric(qc[field], errors="coerce")
            out_of_range = qc[
                numeric_series.notna() & ((numeric_series < min_val) | (numeric_series > max_val))
            ]

            for _, row in out_of_range.iterrows():
                if structural_only and _is_context_row(row, has_st):
                    continue
                issues.append(
                    {
                        "Issue": f"{field} out of range ({min_val}-{max_val})",
                        "Row": row.to_dict(),
                    }
                )

        elif check == "required":
            structural_only = rule.get("structural_only", False)
            has_st = "structure_type" in qc.columns
            missing = qc[_is_missing_value(qc[field])]

            for _, row in missing.iterrows():
                if structural_only and _is_context_row(row, has_st):
                    continue
                issues.append({"Issue": f"Missing required field: {field}", "Row": row.to_dict()})

        elif check == "allowed_values":
            allowed = rule.get("values", [])

            invalid = qc[~_is_missing_value(qc[field]) & ~qc[field].isin(allowed)]

            for _, row in invalid.iterrows():
                issues.append(
                    {
                        "Issue": f"Invalid value for '{field}': {row[field]}",
                        "Row": row.to_dict(),
                    }
                )

        elif check == "regex":
            pattern = rule.get("pattern")
            if not pattern:
                issues.append({"Issue": "Invalid regex rule: missing pattern", "Row": {}})
                continue

            compiled = re.compile(pattern)
            series = qc[field]
            non_missing = qc[~_is_missing_value(series)]

            for _, row in non_missing.iterrows():
                value = row.get(field)
                if _is_missing_scalar(value):
                    continue
                if not compiled.match(str(value)):
                    issues.append(
                        {
                            "Issue": f"Invalid format for '{field}': {value}",
                            "Row": row.to_dict(),
                        }
                    )

        else:
            issues.append({"Issue": f"Unknown check type: {check}", "Row": {}})

    return pd.DataFrame(_deduplicate_issues(issues))
