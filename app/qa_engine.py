from __future__ import annotations

import math
import re

import pandas as pd
from pyproj import Transformer

from app.electrical_schema import row_suggests_hv_overhead, row_suggests_transformer_equipment

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
        "Pline",
        "pline",
        "PLINE",
        # Crossing height measurements and environmental observations.
        # Per OHL survey standard section 8.8 — not structural poles.
        "11xing",
        "11XING",
        "33xing",
        "33XING",
        "110xing",
        "110XING",
        "BTxing",
        "btxing",
        "BTXING",
        "HVxing",
        "hvxing",
        "HVXING",
        "LVxing",
        "lvxing",
        "LVXING",
        "Road",
        "road",
        "ROAD",
        "Ignore",
        "ignore",
        "IGNORE",
    }
)

# EXpole codes — existing poles being replaced. Detected in span_distance to
# suppress false 'span too short' FAILs for EX→PR replacement pairs.
_EXPOLE_CODES: frozenset[str] = frozenset({"EXpole", "expole", "EXPOLE"})

# Angle/deviation structure codes — structures that typically require a stay.
_ANGLE_CODES: frozenset[str] = frozenset({"Angle", "angle", "ANGLE"})

# Structure codes that constitute stay evidence when found near an angle record.
# Also covers "Stay pole" (a combined angle+stay structure).
_STAY_EVIDENCE_CODES: frozenset[str] = frozenset(
    {
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


def infer_display_network_fields(
    row: "pd.Series | dict",
    rulepack_id: str | None = None,
) -> dict[str, object]:
    """Infer non-authoritative display context for map popups.

    This is not QA logic and must not create compliance conclusions. It only
    fills display scaffolding where the current survey export lacks richer
    structured fields that Stage 4 capture can populate later.
    """
    st = str(row.get("structure_type") or "").lower()
    rulepack = str(rulepack_id or "")
    inferred_voltage = None
    if "11" in st:
        inferred_voltage = "11kV"
    elif "33" in st:
        inferred_voltage = "33kV"
    elif "lv" in st:
        inferred_voltage = "LV"
    elif "11kv" in rulepack.lower() or "11kv" in rulepack.replace("_", "").lower():
        inferred_voltage = "11kV"

    return {
        "voltage": row.get("voltage") or row.get("line_voltage") or inferred_voltage,
        "conductor_type": row.get("conductor_type") or row.get("conductor"),
        "conductor_size": row.get("conductor_size") or row.get("wire_size"),
        "cable_type": row.get("cable_type") or row.get("ug_cable_type"),
        "route_type": row.get("route_type") or row.get("line_route"),
        "phase_count": row.get("phase_count") or row.get("phases"),
        "equipment": row.get("equipment") or row.get("mounted_equipment"),
        "equipment_rating": row.get("equipment_rating") or row.get("rating"),
        "source_confidence": row.get("source_confidence") or "raw survey export",
    }


def _text_value(row: "pd.Series | dict", field: str) -> str:
    value = row.get(field) if hasattr(row, "get") else None
    if _is_missing_scalar(value):
        return ""
    return str(value).strip()


def _is_third_party_record(row: "pd.Series | dict") -> bool:
    primary_type = _text_value(row, "primary_type").lower()
    record_role = (
        _text_value(row, "_record_role").lower() or _text_value(row, "record_role").lower()
    )
    asset_intent = _text_value(row, "asset_intent").lower()
    return (
        primary_type == "third_party_infrastructure"
        or record_role == "third_party"
        or asset_intent == "third_party_not_network"
    )


def _is_existing_pole_record(row: "pd.Series | dict") -> bool:
    if _is_third_party_record(row):
        return False
    structure_type = _text_value(row, "structure_type").lower()
    asset_intent = _text_value(row, "asset_intent").lower()
    lifecycle_state = _text_value(row, "lifecycle_state").lower()
    return (
        "expole" in structure_type
        or "existing" in asset_intent
        or "existing pole" in lifecycle_state
    )


def classify_height_confidence(record: "pd.Series | dict") -> dict[str, str]:
    """Describe whether a height value is reliable enough for design use."""

    height = record.get("height") if hasattr(record, "get") else None
    height_source = _text_value(record, "height_source").lower().replace(" ", "_")
    source_confidence = _text_value(record, "source_confidence").lower()
    is_existing = _is_existing_pole_record(record)

    if _is_missing_scalar(height):
        if is_existing:
            return {
                "level": "missing",
                "status": "blocker",
                "warning": "Measured height missing - clearance check impossible",
            }
        return {
            "level": "not_applicable",
            "status": "info",
            "warning": "Proposed pole specification required (design decision)",
        }

    if not height_source or height_source == "not_captured":
        if "legacy" in source_confidence or "drawing" in source_confidence:
            warning = (
                "Height from legacy data - field verification required before "
                "clearance calculations"
            )
        else:
            warning = (
                "Height source not recorded - verify measurement method before relying on value"
            )
        return {"level": "low", "status": "warning", "warning": warning}

    if any(token in height_source for token in ("rtk", "ppk", "survey_grade")):
        return {"level": "high", "status": "ok", "warning": ""}

    if "measured" in height_source and "gnss" in height_source:
        return {
            "level": "medium",
            "status": "ok",
            "warning": "Standalone GNSS measurement - adequate for design",
        }

    if any(token in height_source for token in ("measured", "tape", "rangefinder")):
        return {"level": "medium-high", "status": "ok", "warning": ""}

    if any(token in height_source for token in ("estimated", "visual")):
        return {
            "level": "low",
            "status": "warning",
            "warning": "Height estimated - field measurement required for clearance calculations",
        }

    if any(token in height_source for token in ("plan", "drawing", "legacy")):
        return {
            "level": "low",
            "status": "warning",
            "warning": "Height from plan/drawing - field verification required",
        }

    return {
        "level": "unknown",
        "status": "review",
        "warning": "Height source unknown - verify before use in design",
    }


def classify_source_confidence(record: "pd.Series | dict") -> dict[str, object]:
    """Classify survey-record provenance and geometry trust for display."""

    source = (
        _text_value(record, "source_confidence").lower()
        or _text_value(record, "data_source").lower()
    )
    capture_method = _text_value(record, "capture_method").lower()

    if "field" in source and ("rtk" in capture_method or "ppk" in capture_method):
        return {
            "provenance": "field_observed_rtk",
            "confidence": "high",
            "geometry_trust": "survey_grade",
            "warnings": [],
            "designer_note": "Field survey with RTK GNSS - geometry is survey-grade",
        }

    if "field" in source and "gnss" in capture_method:
        return {
            "provenance": "field_observed_gnss",
            "confidence": "medium-high",
            "geometry_trust": "mapping_grade",
            "warnings": ["Standalone GNSS - adequate for design"],
            "designer_note": "Field survey with standalone GNSS",
        }

    if "field" in source or "observed" in source:
        return {
            "provenance": "field_observed",
            "confidence": "medium",
            "geometry_trust": "field_verified",
            "warnings": ["Capture method not specified - assume mapping-grade accuracy"],
            "designer_note": "Field survey (method not specified)",
        }

    if "gis" in source or "dno" in source:
        return {
            "provenance": "dno_gis_import",
            "confidence": "medium",
            "geometry_trust": "gis_inherited",
            "warnings": ["Imported from DNO GIS - verify critical attributes before design"],
            "designer_note": (
                "DNO GIS import - position likely reliable, attributes may be outdated"
            ),
        }

    if "legacy" in source or "map data" in source:
        return {
            "provenance": "legacy_map_data",
            "confidence": "low",
            "geometry_trust": "unverified",
            "warnings": [
                "LEGACY MAP DATA - NOT FIELD VERIFIED",
                "Geometry and attributes from historical records",
                "Field verification required before design",
            ],
            "designer_note": "Legacy map data - field verification required",
        }

    if "drawing" in source or "plan" in source or "digitised" in source:
        return {
            "provenance": "digitised_from_drawing",
            "confidence": "low",
            "geometry_trust": "indicative",
            "warnings": ["Digitised from plan/drawing - field verification required"],
            "designer_note": "Digitised from drawing - not field-verified",
        }

    if "proposed" in source or "design" in source:
        return {
            "provenance": "proposed_by_design",
            "confidence": "n/a",
            "geometry_trust": "design_intent",
            "warnings": ["Proposed design location - not survey data"],
            "designer_note": "Design proposal - not field-verified",
        }

    if "inferred" in source or "calculated" in source:
        return {
            "provenance": "inferred",
            "confidence": "low",
            "geometry_trust": "estimated",
            "warnings": ["Inferred/calculated position - field verification recommended"],
            "designer_note": "Inferred position - verify if critical",
        }

    return {
        "provenance": "unknown",
        "confidence": "low",
        "geometry_trust": "unverified",
        "warnings": ["DATA SOURCE UNKNOWN - reliability cannot be determined"],
        "designer_note": "Source unclear — treated as unverified; field validation required",
    }


def parse_attachments(record: "pd.Series | dict") -> dict[str, object]:
    """Detect third-party attachments that create coordination dependencies."""

    attachments_text = " ".join(
        _text_value(record, key).lower()
        for key in (
            "third_party_attachments",
            "attachments",
            "third_party",
            "attached_assets",
            "pole_attachments",
            "remarks",
            "location",
            "name",
        )
    )
    attachments: list[dict[str, str]] = []

    def add_once(
        attachment_type: str,
        owner: str,
        impact: str,
        icon: str,
        keywords: tuple[str, ...],
    ) -> None:
        if attachment_type in {item["type"] for item in attachments}:
            return
        if any(keyword in attachments_text for keyword in keywords):
            attachments.append(
                {
                    "type": attachment_type,
                    "owner": owner,
                    "impact": impact,
                    "icon": icon,
                }
            )

    add_once(
        "telecoms",
        "BT/Openreach/Virgin",
        "Wayleave coordination may be required",
        "TEL",
        ("bt", "openreach", "virgin", "telecom", "fibre", "fiber", "copper"),
    )
    add_once(
        "streetlight",
        "Local Authority",
        "LA coordination required if pole replacement planned",
        "SL",
        ("streetlight", "street light", "lamp", "lighting"),
    )
    add_once(
        "customer_service",
        "Customer",
        "Customer notification required",
        "CS",
        ("customer", "service", "private supply", "house service"),
    )
    add_once(
        "signage",
        "Various",
        "Relocate/replace signage if pole removed",
        "SIGN",
        ("sign", "signage", "notice", "warning plate"),
    )
    add_once(
        "cctv",
        "LA/Private",
        "Security equipment coordination required",
        "CCTV",
        ("cctv", "camera", "security"),
    )

    return {
        "has_attachments": bool(attachments),
        "attachment_count": len(attachments),
        "attachment_types": [attachment["type"] for attachment in attachments],
        "attachment_list": attachments,
        "coordination_required": bool(attachments),
    }


def _is_context_row(row: "pd.Series", has_structure_type: bool) -> bool:
    """Return True when this row represents a non-structural contextual feature."""
    if row.get("_record_role") in {"context", "third_party"}:
        return True
    if not has_structure_type:
        return False
    st = row.get("structure_type")
    return isinstance(st, str) and st in _CONTEXT_FEATURE_CODES


def _is_replacement_pair(prev_st: str | None, curr_st: str | None) -> bool:
    """Return True when prev and curr form an EXpole ↔ structural replacement pair.

    Exactly one of the two structure_type values must be an EXpole code.
    This covers EX→PR and PR→EX orderings (XOR logic).
    """
    if not isinstance(prev_st, str) or not isinstance(curr_st, str):
        return False
    return (prev_st in _EXPOLE_CODES) != (curr_st in _EXPOLE_CODES)


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
    if series.dtype == "object" or pd.api.types.is_string_dtype(series):
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

        elif check == "conductor_hv_overhead":
            for _, row in qc.iterrows():
                if not _is_existing_pole_record(row):
                    continue
                if not row_suggests_hv_overhead(row):
                    continue
                conductor_val = row.get("conductor_type") or row.get("conductor")
                if not _is_missing_scalar(conductor_val):
                    continue
                issues.append(
                    {
                        "Issue": ("Overhead conductor type not recorded — specify for HV design"),
                        "Row": row.to_dict(),
                        "Severity": "WARN",
                    }
                )

        elif check == "equipment_expected_transformer":
            for _, row in qc.iterrows():
                if _is_third_party_record(row):
                    continue
                role = str(row.get("_record_role") or "").lower()
                if role in ("context", "anchor"):
                    continue
                if not _is_existing_pole_record(row):
                    continue
                if not row_suggests_transformer_equipment(row):
                    continue
                ev = row.get("equipment") or row.get("mounted_equipment")
                if not _is_missing_scalar(ev):
                    continue
                issues.append(
                    {
                        "Issue": (
                            "Transformer or kVA equipment implied — mounted equipment not recorded"
                        ),
                        "Row": row.to_dict(),
                        "Severity": "WARN",
                    }
                )

        elif check == "connectivity_span_endpoints":
            cols = qc.columns
            has_from = "from_support_id" in cols
            has_to = "to_support_id" in cols
            if has_from or has_to:
                for _, row in qc.iterrows():
                    if _is_third_party_record(row):
                        continue
                    role = str(row.get("_record_role") or "").lower()
                    if role in ("context", "anchor"):
                        continue
                    f = row.get("from_support_id")
                    t = row.get("to_support_id")
                    f_pres = not _is_missing_scalar(f)
                    t_pres = not _is_missing_scalar(t)
                    if not f_pres and not t_pres:
                        continue
                    if f_pres ^ t_pres:
                        issues.append(
                            {
                                "Issue": (
                                    "Span connectivity incomplete — record both from and to "
                                    "support identifiers"
                                ),
                                "Row": row.to_dict(),
                                "Severity": "WARN",
                            }
                        )

        elif check == "connectivity_reference_ids":
            cols = qc.columns
            if "from_support_id" in cols or "to_support_id" in cols:
                pid_set: set[str] = set()
                for _, r in df.iterrows():
                    p = r.get("pole_id")
                    if not _is_missing_scalar(p):
                        pid_set.add(str(p).strip())
                for _, row in qc.iterrows():
                    if _is_third_party_record(row):
                        continue
                    for fld in ("from_support_id", "to_support_id"):
                        if fld not in cols:
                            continue
                        v = row.get(fld)
                        if _is_missing_scalar(v):
                            continue
                        vs = str(v).strip()
                        if vs not in pid_set:
                            issues.append(
                                {
                                    "Issue": (
                                        f"Support reference '{vs}' not found on job pole list"
                                    ),
                                    "Row": row.to_dict(),
                                    "Severity": "WARN",
                                }
                            )

        elif check == "connectivity_stay_parent":
            cols = qc.columns
            has_linked = "linked_pole_id" in cols
            has_parent = "parent_support_id" in cols
            if has_linked or has_parent:
                for _, row in qc.iterrows():
                    if _is_third_party_record(row):
                        continue
                    if str(row.get("_record_role") or "").lower() == "anchor":
                        continue
                    st = str(row.get("structure_type") or "").strip()
                    if st not in _STAY_EVIDENCE_CODES:
                        continue
                    parent = row.get("parent_support_id") if has_parent else None
                    linked = row.get("linked_pole_id") if has_linked else None
                    if not _is_missing_scalar(parent) or not _is_missing_scalar(linked):
                        continue
                    issues.append(
                        {
                            "Issue": "Stay structure has no parent pole identifier",
                            "Row": row.to_dict(),
                            "Severity": "WARN",
                        }
                    )

        elif check == "survey_metadata_advisory":
            cols = qc.columns
            if "surveyor" in cols and "survey_date" in cols:
                for _, row in qc.iterrows():
                    if _is_third_party_record(row):
                        continue
                    role = str(row.get("_record_role") or "").lower()
                    if role in ("context", "anchor"):
                        continue
                    if not _is_missing_scalar(row.get("surveyor")):
                        continue
                    if not _is_missing_scalar(row.get("survey_date")):
                        continue
                    issues.append(
                        {
                            "Issue": (
                                "Survey metadata incomplete (surveyor, survey date) — "
                                "adds audit value for design handoff"
                            ),
                            "Row": row.to_dict(),
                            "Severity": "INFO",
                        }
                    )

        elif check == "height_source_existing":
            height_source_field = rule.get("height_source_field", "height_source")
            height_field = rule.get("height_field", "height")

            for _, row in qc.iterrows():
                if not _is_existing_pole_record(row):
                    continue
                height = row.get(height_field)
                height_source = row.get(height_source_field)

                if _is_missing_scalar(height):
                    issues.append(
                        {
                            "Issue": "Measured height missing - clearance check impossible",
                            "Row": row.to_dict(),
                            "Severity": "FAIL",
                        }
                    )
                    continue

                if (
                    _is_missing_scalar(height_source)
                    or _text_value(row, height_source_field).lower() == "not captured"
                ):
                    issues.append(
                        {
                            "Issue": "Height source not recorded - verify measurement method",
                            "Row": row.to_dict(),
                            "Severity": "WARN",
                        }
                    )
                    continue

                source_text = _text_value(row, height_source_field).lower()
                if any(
                    token in source_text for token in ("legacy", "plan", "drawing", "estimated")
                ):
                    issues.append(
                        {
                            "Issue": f"Height from {height_source} - field verification required",
                            "Row": row.to_dict(),
                            "Severity": "WARN",
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
            short_anomaly_m = max(float(min_m), 10.0)

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
            prev_st: str | None = None
            for _, row in qc.iterrows():
                # Anchor rows are at unrelated reference locations — reset chain.
                if has_record_role and row.get("_record_role") == "anchor":
                    prev_e = prev_n = None
                    prev_st = None
                    continue
                # Context rows bridge the span — skip without resetting chain.
                if _is_context_row(row, has_structure_type):
                    continue

                lat = row.get(lat_field)
                lon = row.get(lon_field)
                if any(_is_missing_scalar(v) for v in (lat, lon)):
                    prev_e = prev_n = None
                    prev_st = None
                    continue
                try:
                    e, n = transformer.transform(float(lon), float(lat))
                except Exception:
                    prev_e = prev_n = None
                    prev_st = None
                    continue

                _st_raw = row.get("structure_type") if has_structure_type else None
                curr_st = str(_st_raw) if isinstance(_st_raw, str) else None

                if prev_e is not None:
                    dist = math.sqrt((e - prev_e) ** 2 + (n - prev_n) ** 2)
                    if dist < short_anomaly_m:
                        if _is_replacement_pair(prev_st, curr_st):
                            issues.append(
                                {
                                    "Issue": (
                                        f"Replacement pair detected (EX → PR, {dist:.1f}m offset)"
                                    ),
                                    "Row": row.to_dict(),
                                    "Severity": "WARN",
                                }
                            )
                        else:
                            msg = (
                                f"Probable duplicate pole or GPS bounce: {dist:.1f}m span"
                                " between consecutive poles"
                            )
                            issues.append(
                                {
                                    "Issue": msg,
                                    "Row": row.to_dict(),
                                    "Severity": "FAIL",
                                }
                            )
                    elif dist > max_m:
                        issues.append(
                            {
                                "Issue": (
                                    f"Probable missing intermediate pole: {dist:.1f}m span"
                                    f" between consecutive poles (max {max_m}m)"
                                ),
                                "Row": row.to_dict(),
                                "Severity": "WARN",
                            }
                        )
                prev_e, prev_n = e, n
                prev_st = curr_st

        elif check == "angle_stay":
            # For each Angle record, check whether any stay-evidence record
            # is within proximity_m. If none found (and no stay mention in
            # the angle record's own remarks), emit a cautious WARN.
            lat_field = rule.get("lat_field", "lat")
            lon_field = rule.get("lon_field", "lon")
            proximity_m = rule.get("proximity_m", 20)

            if "structure_type" not in qc.columns:
                continue
            if lat_field not in qc.columns or lon_field not in qc.columns:
                continue

            transformer = _OSGB_TRANSFORMER
            angle_records: list[tuple] = []  # (row, e, n)
            stay_positions: list[tuple] = []  # (e, n)

            for _, row in qc.iterrows():
                st = row.get("structure_type")
                if not isinstance(st, str):
                    continue
                lat = row.get(lat_field)
                lon = row.get(lon_field)
                if _is_missing_scalar(lat) or _is_missing_scalar(lon):
                    continue
                try:
                    e, n = transformer.transform(float(lon), float(lat))
                except Exception:
                    continue
                if st in _ANGLE_CODES:
                    angle_records.append((row, e, n))
                elif st in _STAY_EVIDENCE_CODES:
                    stay_positions.append((e, n))

            for angle_row, ae, an in angle_records:
                has_stay = any(
                    math.sqrt((ae - se) ** 2 + (an - sn) ** 2) <= proximity_m
                    for se, sn in stay_positions
                )
                # Secondary evidence: stay mentioned in the angle record's own remarks.
                if not has_stay:
                    loc = angle_row.get("location", "")
                    if isinstance(loc, str) and "stay" in loc.lower():
                        has_stay = True
                if not has_stay:
                    issues.append(
                        {
                            "Issue": (
                                "⚠️ Angle pole — stay evidence not captured."
                                " Check field notes, photos or plan evidence."
                            ),
                            "Row": angle_row.to_dict(),
                            "Severity": "WARN",
                        }
                    )

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
                height_val = pd.to_numeric(row.get(field), errors="coerce")
                if (
                    field == "height"
                    and row.get("structure_type") in _EXPOLE_CODES
                    and not pd.isna(height_val)
                    and height_val < min_val
                ):
                    issues.append(
                        {
                            "Issue": "Height likely estimated / not captured (EXpole)",
                            "Row": row.to_dict(),
                            "Severity": "WARN",
                        }
                    )
                else:
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
