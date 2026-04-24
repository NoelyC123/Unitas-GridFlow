from __future__ import annotations

import pandas as pd

# ---------------------------------------------------------------------------
# Issue classification patterns.
#
# Matched in order — first match wins. More specific patterns must come
# before less specific ones that share a common prefix.
# ---------------------------------------------------------------------------

_SPAN_ACTION = (
    "Review span anomalies — confirm whether short or long spans represent"
    " replacement pairs, duplicate captures, or missing intermediate records"
)

_ISSUE_PATTERNS: list[tuple[str, dict]] = [
    # --- replacement intent ---
    (
        "Replacement pair detected",
        {
            "issue_code": "REPL_PAIR",
            "severity": "observation",
            "category": "replacement_intent",
            "scope": "structural",
            "confidence": "high",
            "is_observation": True,
            "recommended_action": None,
        },
    ),
    # --- structural evidence ---
    (
        "Angle structure with no stay evidence",
        {
            "issue_code": "ANGLE_NO_STAY",
            "severity": "warning",
            "category": "structural_evidence",
            "scope": "structural",
            "confidence": "medium",
            "is_observation": False,
            "recommended_action": (
                "Verify whether stay capture is missing or not required for this job"
            ),
        },
    ),
    (
        "Height likely estimated / not captured (EXpole)",
        {
            "issue_code": "EXPOLE_HEIGHT_EST",
            "severity": "warning",
            "category": "structural_evidence",
            "scope": "structural",
            "confidence": "medium",
            "is_observation": False,
            "recommended_action": "Confirm actual EXpole height from field notes or plan",
        },
    ),
    # --- data completeness: specific fields first, then generic fallback ---
    (
        "Missing required field: height",
        {
            "issue_code": "MISS_HEIGHT",
            "severity": "warning",
            "category": "data_completeness",
            "scope": "structural",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": (
                "Confirm heights from field notes or plan before clearance design"
            ),
        },
    ),
    (
        "Missing required field: material",
        {
            "issue_code": "MISS_MATERIAL",
            "severity": "warning",
            "category": "structural_evidence",
            "scope": "structural",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": (
                "Confirm material from field notes or plan before structural loading calculation"
            ),
        },
    ),
    (
        "Missing required field:",
        {
            "issue_code": "MISS_FIELD",
            "severity": "warning",
            "category": "data_completeness",
            "scope": "all",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": None,
        },
    ),
    (
        "Missing required paired field",
        {
            "issue_code": "MISS_PAIRED_FIELD",
            "severity": "critical",
            "category": "coordinate_quality",
            "scope": "all",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": None,
        },
    ),
    (
        "Missing column:",
        {
            "issue_code": "MISSING_COLUMN",
            "severity": "critical",
            "category": "data_completeness",
            "scope": "all",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": None,
        },
    ),
    # --- span geometry: all tiers share one grouped action so they deduplicate naturally ---
    (
        "Span very short:",
        {
            "issue_code": "SPAN_VERY_SHORT",
            "severity": "warning",
            "category": "span_geometry",
            "scope": "structural",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": _SPAN_ACTION,
        },
    ),
    (
        "Span unusually short:",
        {
            "issue_code": "SPAN_SHORT",
            "severity": "warning",
            "category": "span_geometry",
            "scope": "structural",
            "confidence": "medium",
            "is_observation": False,
            "recommended_action": _SPAN_ACTION,
        },
    ),
    (
        "Span borderline short:",
        {
            "issue_code": "SPAN_BORDERLINE",
            "severity": "warning",
            "category": "span_geometry",
            "scope": "structural",
            "confidence": "medium",
            "is_observation": False,
            "recommended_action": _SPAN_ACTION,
        },
    ),
    (
        "Span too long:",
        {
            "issue_code": "SPAN_LONG",
            "severity": "warning",
            "category": "span_geometry",
            "scope": "structural",
            "confidence": "medium",
            "is_observation": False,
            "recommended_action": _SPAN_ACTION,
        },
    ),
    # --- coordinate quality ---
    (
        "Coordinate mismatch:",
        {
            "issue_code": "COORD_MISMATCH",
            "severity": "critical",
            "category": "coordinate_quality",
            "scope": "all",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": None,
        },
    ),
    (
        "Duplicate pair",
        {
            "issue_code": "COORD_DUPLICATE",
            "severity": "critical",
            "category": "coordinate_quality",
            "scope": "all",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": None,
        },
    ),
    # --- rulepack validation ---
    (
        "height out of range",
        {
            "issue_code": "HEIGHT_RANGE",
            "severity": "warning",
            "category": "rulepack_validation",
            "scope": "structural",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": None,
        },
    ),
    (
        "out of range",
        {
            "issue_code": "FIELD_RANGE",
            "severity": "warning",
            "category": "rulepack_validation",
            "scope": "all",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": None,
        },
    ),
    (
        "Inconsistent",
        {
            "issue_code": "INCONSISTENT_VALUE",
            "severity": "warning",
            "category": "rulepack_validation",
            "scope": "all",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": None,
        },
    ),
    (
        "Invalid value for",
        {
            "issue_code": "INVALID_VALUE",
            "severity": "warning",
            "category": "rulepack_validation",
            "scope": "all",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": None,
        },
    ),
    (
        "Invalid format for",
        {
            "issue_code": "INVALID_FORMAT",
            "severity": "warning",
            "category": "rulepack_validation",
            "scope": "all",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": None,
        },
    ),
    (
        "Duplicate value in",
        {
            "issue_code": "DUPE_ID",
            "severity": "warning",
            "category": "data_completeness",
            "scope": "all",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": None,
        },
    ),
]

_STRUCTURED_FIELDS = [
    "issue_code",
    "severity",
    "category",
    "scope",
    "confidence",
    "is_observation",
    "recommended_action",
]

_FALLBACK: dict = {
    "issue_code": "UNKNOWN",
    "severity": "warning",
    "category": "rulepack_validation",
    "scope": "all",
    "confidence": "low",
    "is_observation": False,
    "recommended_action": None,
}

_SEVERITY_ORDER: dict[str, int] = {"critical": 0, "warning": 1, "observation": 2}


def _count_issue_codes(issues_df: pd.DataFrame, codes: set[str]) -> int:
    """Count rows whose issue_code is in the given set."""
    if issues_df.empty or "issue_code" not in issues_df.columns:
        return 0
    return int(issues_df["issue_code"].isin(codes).sum())


def build_evidence_gates(completeness: dict, issues_df: pd.DataFrame) -> list[dict]:
    """Return a list of scoped design evidence gates.

    Each entry is {"label": str, "status": str, "explanation": str}.
    Status values: Strong / Partial / Weak / Missing / N/A / Blocked.
    Derived deterministically from completeness summary and enriched issues.
    """
    gates: list[dict] = []

    fields = completeness.get("fields") or {}
    s_fields = completeness.get("structural_fields") or fields
    feature_codes: list = completeness.get("feature_codes_found") or []
    structural_count = int(completeness.get("structural_count") or 0)

    # -------------------------------------------------------------------------
    # Gate 1 — Position / Mapping Evidence
    # -------------------------------------------------------------------------
    lat_pct = float((fields.get("lat") or {}).get("coverage_pct") or 0)
    east_pct = float((fields.get("easting") or {}).get("coverage_pct") or 0)
    coord_pct = max(lat_pct, east_pct)
    coord_issues = _count_issue_codes(
        issues_df, {"COORD_MISMATCH", "COORD_DUPLICATE", "MISS_PAIRED_FIELD"}
    )

    if coord_pct == 0:
        g1 = (
            "Missing",
            "No coordinate data found — map output and span calculations are not possible.",
        )
    elif coord_issues > 0 and coord_pct < 85:
        g1 = (
            "Weak",
            f"Coordinate coverage low ({coord_pct:.0f}%) with {coord_issues} quality"
            " issue(s) — map output is unreliable.",
        )
    elif coord_issues > 0:
        g1 = (
            "Partial",
            f"Coordinates mostly present ({coord_pct:.0f}%) but {coord_issues} quality"
            " issue(s) flagged — verify before relying on map output.",
        )
    elif coord_pct >= 85:
        g1 = (
            "Strong",
            f"Coordinates present for {coord_pct:.0f}% of records — map output is reliable.",
        )
    elif coord_pct >= 50:
        g1 = (
            "Partial",
            f"Coordinates present for {coord_pct:.0f}% of records — partial map output only.",
        )
    else:
        g1 = (
            "Weak",
            f"Coordinate coverage low ({coord_pct:.0f}%) — map output is limited.",
        )

    gates.append({"label": "Position / Mapping", "status": g1[0], "explanation": g1[1]})

    # -------------------------------------------------------------------------
    # Gate 2 — Structure Identity Evidence
    # -------------------------------------------------------------------------
    st_pct = float((s_fields.get("structure_type") or {}).get("coverage_pct") or 0)
    has_ex = any(c.lower() == "expole" for c in feature_codes)
    has_pr = any(c.lower() in ("pol", "prpole") for c in feature_codes)

    if st_pct == 0:
        g2 = (
            "Missing",
            "No structure type codes found — EX/proposed intent cannot be determined.",
        )
    elif st_pct >= 80 and (has_ex or has_pr):
        g2 = (
            "Strong",
            f"Structure type present for {st_pct:.0f}% of records with recognised EX/PR codes.",
        )
    elif st_pct >= 50:
        g2 = (
            "Partial",
            f"Structure type present for {st_pct:.0f}% of records"
            " — incomplete EX/PR classification.",
        )
    else:
        g2 = (
            "Weak",
            f"Structure type coverage low ({st_pct:.0f}%) — asset intent unclear.",
        )

    gates.append({"label": "Structure Identity", "status": g2[0], "explanation": g2[1]})

    # -------------------------------------------------------------------------
    # Gate 3 — Structural Specification (Height & Material)
    # -------------------------------------------------------------------------
    height_pct = float((s_fields.get("height") or {}).get("coverage_pct") or 0)
    material_pct = float((s_fields.get("material") or {}).get("coverage_pct") or 0)

    if height_pct == 0 and material_pct == 0:
        g3 = (
            "Missing",
            "No height or material data — structural loading and clearance checks not possible.",
        )
    elif height_pct >= 70 and material_pct >= 70:
        g3 = (
            "Strong",
            f"Height ({height_pct:.0f}%) and material ({material_pct:.0f}%) both well covered.",
        )
    else:
        h_part = f"height {height_pct:.0f}%" if height_pct > 0 else "height missing"
        m_part = f"material {material_pct:.0f}%" if material_pct > 0 else "material missing"
        g3 = ("Partial", f"Partial specification: {h_part}, {m_part}.")

    gates.append({"label": "Structural Specification", "status": g3[0], "explanation": g3[1]})

    # -------------------------------------------------------------------------
    # Gate 4 — Stay Evidence
    # -------------------------------------------------------------------------
    has_angle = any(c.lower() == "angle" for c in feature_codes)
    angle_no_stay = _count_issue_codes(issues_df, {"ANGLE_NO_STAY"})

    if not has_angle:
        g4 = ("N/A", "No angle structures detected — stay evidence gate not applicable.")
    elif angle_no_stay == 0:
        g4 = ("Strong", "Angle structures present with stay evidence captured.")
    else:
        noun = "structure" if angle_no_stay == 1 else "structures"
        g4 = (
            "Weak",
            f"{angle_no_stay} angle {noun} with no stay evidence — confirm from field notes.",
        )

    gates.append({"label": "Stay Evidence", "status": g4[0], "explanation": g4[1]})

    # -------------------------------------------------------------------------
    # Gate 5 — Clearance Design Evidence
    # Clearance is at most Partial — field verification is always needed.
    # -------------------------------------------------------------------------
    if height_pct == 0:
        g5 = (
            "Missing",
            "No height data — clearance design cannot proceed without pole heights.",
        )
    elif height_pct >= 70:
        g5 = (
            "Partial",
            f"Height captured for {height_pct:.0f}% of structures — clearance design is"
            " possible but field verification is recommended.",
        )
    else:
        g5 = (
            "Weak",
            f"Height coverage low ({height_pct:.0f}%) — clearance design unreliable"
            " without additional field evidence.",
        )

    gates.append({"label": "Clearance Design", "status": g5[0], "explanation": g5[1]})

    # -------------------------------------------------------------------------
    # Gate 6 — Conductor Scope Evidence
    # -------------------------------------------------------------------------
    span_issues = _count_issue_codes(
        issues_df, {"SPAN_VERY_SHORT", "SPAN_SHORT", "SPAN_BORDERLINE", "SPAN_LONG"}
    )

    if structural_count < 2:
        g6 = (
            "Missing",
            "Fewer than 2 structural records — conductor scope and span data not derivable.",
        )
    elif span_issues == 0:
        g6 = ("Strong", f"{structural_count} structural records with no span anomalies.")
    elif span_issues <= 3:
        g6 = (
            "Partial",
            f"{structural_count} structural records with {span_issues} span anomaly(ies)"
            " — review before design.",
        )
    else:
        g6 = (
            "Weak",
            f"{structural_count} structural records but {span_issues} span anomalies"
            " flagged — review field notes.",
        )

    gates.append({"label": "Conductor Scope", "status": g6[0], "explanation": g6[1]})

    # -------------------------------------------------------------------------
    # Gate 7 — Overall Design Handoff Status
    # Reads prior gate statuses directly instead of re-deriving them.
    # -------------------------------------------------------------------------
    actionable = [g1[0], g2[0], g3[0], g5[0], g6[0]]
    if g4[0] != "N/A":
        actionable.append(g4[0])

    if g1[0] in ("Missing", "Weak"):
        g7 = (
            "Blocked",
            "Position data is missing or weak — reliable map output and design cannot proceed.",
        )
    elif any(s in ("Missing", "Weak") for s in actionable):
        g7 = (
            "Partial",
            "Some evidence gaps remain — review individual gates above before design release.",
        )
    else:
        g7 = (
            "Partial",
            "Position and specification evidence is present — verify individual gates"
            " before final design release.",
        )

    gates.append({"label": "Overall Handoff Status", "status": g7[0], "explanation": g7[1]})

    return gates


def build_recommended_actions(issues_df: pd.DataFrame) -> list[dict]:
    """Return a deduplicated, severity-prioritised list of recommended designer actions.

    Each entry is {"action": str, "severity": str}.
    Order: critical → warning → observation.
    Issues with no recommended_action are skipped.
    Each unique action text appears once — first occurrence by severity order wins.
    """
    if issues_df.empty:
        return []
    if "recommended_action" not in issues_df.columns or "severity" not in issues_df.columns:
        return []

    seen: set[str] = set()
    actions: list[dict] = []

    for sev in ("critical", "warning", "observation"):
        subset = issues_df[issues_df["severity"] == sev]
        for _, row in subset.iterrows():
            action = row.get("recommended_action")
            if action is None:
                continue
            try:
                if pd.isna(action):
                    continue
            except Exception:
                pass
            action_str = str(action).strip()
            if not action_str or action_str in seen:
                continue
            seen.add(action_str)
            actions.append({"action": action_str, "severity": sev})

    return actions


def classify_issue(issue_text: str) -> dict:
    """Return structured metadata for a given issue text string.

    Matches against _ISSUE_PATTERNS in order — first match wins.
    Falls back to _FALLBACK for unrecognised patterns.
    """
    for pattern, meta in _ISSUE_PATTERNS:
        if pattern in issue_text:
            return dict(meta)
    return dict(_FALLBACK)


def enrich_issues(issues_df: pd.DataFrame) -> pd.DataFrame:
    """Add structured issue model fields to an issues DataFrame.

    Adds: issue_code, severity, category, scope, confidence,
    is_observation, recommended_action.

    The existing 'Issue' and 'Severity' columns are preserved unchanged
    so all downstream consumers that rely on them continue to work.
    """
    if issues_df.empty:
        enriched = issues_df.copy()
        for field in _STRUCTURED_FIELDS:
            if field not in enriched.columns:
                enriched[field] = pd.Series(dtype=object)
        return enriched

    new_cols: dict[str, list] = {field: [] for field in _STRUCTURED_FIELDS}

    for _, row in issues_df.iterrows():
        issue_text = str(row.get("Issue", ""))
        meta = classify_issue(issue_text)
        for field in _STRUCTURED_FIELDS:
            new_cols[field].append(meta.get(field))

    enriched = issues_df.copy()
    for field, values in new_cols.items():
        enriched[field] = values

    return enriched
