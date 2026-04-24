from __future__ import annotations

import pandas as pd

# ---------------------------------------------------------------------------
# Issue classification patterns.
#
# Matched in order — first match wins. More specific patterns must come
# before less specific ones that share a common prefix.
# ---------------------------------------------------------------------------

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
    # --- span geometry: specific tiers first ---
    (
        "Span very short:",
        {
            "issue_code": "SPAN_VERY_SHORT",
            "severity": "warning",
            "category": "span_geometry",
            "scope": "structural",
            "confidence": "high",
            "is_observation": False,
            "recommended_action": (
                "Confirm whether duplicate capture or co-located replacement pair"
            ),
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
            "recommended_action": "Verify no duplicate entry",
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
            "recommended_action": "Verify no missing intermediate record",
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
            "recommended_action": "Check for GPS error or missing intermediate record",
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
