from __future__ import annotations

import math
import re

import pandas as pd
from pyproj import Transformer

_OSGB_TRANSFORMER = Transformer.from_crs("EPSG:4326", "EPSG:27700", always_xy=True)


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

    for rule in rules:
        check = rule.get("check")
        field = rule.get("field")

        # --- checks that don't use a single `field` key ---

        if check == "paired_required":
            fields = rule.get("fields") or []
            missing_columns = [name for name in fields if name not in df.columns]
            if missing_columns:
                for missing in missing_columns:
                    issues.append({"Issue": f"Missing column: {missing}", "Row": {}})
                continue

            if len(fields) < 2:
                issues.append({"Issue": "Invalid paired_required rule: need 2+ fields", "Row": {}})
                continue

            for _, row in df.iterrows():
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
            missing_cols = [c for c in (if_field, then_field) if not c or c not in df.columns]
            if missing_cols:
                for missing in missing_cols:
                    issues.append({"Issue": f"Missing column: {missing}", "Row": {}})
                continue

            mapping = rule.get("mapping") or {}

            for _, row in df.iterrows():
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
            if "_grid_crs" in df.columns:
                detected_crs = df["_grid_crs"].dropna()
                if len(detected_crs) and str(detected_crs.iloc[0]) != "EPSG:27700":
                    continue

            lat_field = rule.get("lat_field", "lat")
            lon_field = rule.get("lon_field", "lon")
            easting_field = rule.get("easting_field", "easting")
            northing_field = rule.get("northing_field", "northing")
            tolerance_m = rule.get("tolerance_m", 100)

            required_cols = [lat_field, lon_field, easting_field, northing_field]
            missing_cols = [c for c in required_cols if c not in df.columns]
            if missing_cols:
                for mc in missing_cols:
                    issues.append({"Issue": f"Missing column: {mc}", "Row": {}})
                continue

            transformer = _OSGB_TRANSFORMER

            for _, row in df.iterrows():
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
            missing_columns = [name for name in fields if name not in df.columns]
            if missing_columns:
                for missing in missing_columns:
                    issues.append({"Issue": f"Missing column: {missing}", "Row": {}})
                continue

            if len(fields) < 2:
                issues.append({"Issue": "Invalid unique_pair rule: need 2+ fields", "Row": {}})
                continue

            all_present = ~df[fields].apply(_is_missing_value).any(axis=1)
            df_present = df[all_present]

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
            lat_field = rule.get("lat_field", "lat")
            lon_field = rule.get("lon_field", "lon")
            min_m = rule.get("min_m", 10)
            max_m = rule.get("max_m", 500)

            required_cols = [lat_field, lon_field]
            missing_cols = [c for c in required_cols if c not in df.columns]
            if missing_cols:
                for mc in missing_cols:
                    issues.append({"Issue": f"Missing column: {mc}", "Row": {}})
                continue

            transformer = _OSGB_TRANSFORMER

            prev_e = prev_n = None
            for _, row in df.iterrows():
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
                                    f"Span too short: {dist:.0f}m between consecutive poles "
                                    f"(min {min_m}m) — possible duplicate entry"
                                ),
                                "Row": row.to_dict(),
                            }
                        )
                    elif dist > max_m:
                        issues.append(
                            {
                                "Issue": (
                                    f"Span too long: {dist:.0f}m between consecutive poles "
                                    f"(max {max_m}m) — possible GPS error or missing pole"
                                ),
                                "Row": row.to_dict(),
                            }
                        )
                prev_e, prev_n = e, n

        # --- checks that use a single `field` key ---

        elif field not in df.columns:
            issues.append({"Issue": f"Missing column: {field}", "Row": {}})

        elif check == "unique":
            duplicate_mask = df[field].duplicated(keep="first")
            duplicates = df.loc[duplicate_mask, field].tolist()

            for dup in duplicates:
                rows = df[df[field] == dup].to_dict(orient="records")
                for row in rows:
                    issues.append({"Issue": f"Duplicate value in '{field}': {dup}", "Row": row})

        elif check == "range":
            min_val = rule.get("min", float("-inf"))
            max_val = rule.get("max", float("inf"))

            numeric_series = pd.to_numeric(df[field], errors="coerce")
            out_of_range = df[
                numeric_series.notna() & ((numeric_series < min_val) | (numeric_series > max_val))
            ]

            for _, row in out_of_range.iterrows():
                issues.append(
                    {
                        "Issue": f"{field} out of range ({min_val}-{max_val})",
                        "Row": row.to_dict(),
                    }
                )

        elif check == "required":
            missing = df[_is_missing_value(df[field])]

            for _, row in missing.iterrows():
                issues.append({"Issue": f"Missing required field: {field}", "Row": row.to_dict()})

        elif check == "allowed_values":
            allowed = rule.get("values", [])

            invalid = df[~_is_missing_value(df[field]) & ~df[field].isin(allowed)]

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
            series = df[field]
            non_missing = df[~_is_missing_value(series)]

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

    return pd.DataFrame(issues)
