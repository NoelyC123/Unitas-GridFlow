from __future__ import annotations

import pandas as pd

from app.qa_engine import run_qa_checks


def test_required_treats_blank_string_as_missing() -> None:
    df = pd.DataFrame(
        [
            {"material": "Wood"},
            {"material": ""},
        ]
    )

    rules = [{"check": "required", "field": "material"}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert issues.iloc[0]["Issue"] == "Missing required field: material"


def test_required_treats_whitespace_only_string_as_missing() -> None:
    df = pd.DataFrame(
        [
            {"location": "Dalton Road Junction"},
            {"location": "   "},
        ]
    )

    rules = [{"check": "required", "field": "location"}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert issues.iloc[0]["Issue"] == "Missing required field: location"


def test_range_ignores_non_numeric_values_instead_of_failing_them() -> None:
    df = pd.DataFrame(
        [
            {"height": 11.0},
            {"height": "not-a-number"},
            {"height": 28.0},
        ]
    )

    rules = [{"check": "range", "field": "height", "min": 10, "max": 25}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert issues.iloc[0]["Issue"] == "height out of range (10-25)"
    assert issues.iloc[0]["Row"]["height"] == 28.0


def test_allowed_values_flags_invalid_material() -> None:
    df = pd.DataFrame(
        [
            {"material": "Wood"},
            {"material": "Plastic"},
        ]
    )

    rules = [
        {
            "check": "allowed_values",
            "field": "material",
            "values": ["Wood", "Steel", "Concrete", "Composite"],
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert issues.iloc[0]["Issue"] == "Invalid value for 'material': Plastic"


def test_allowed_values_ignores_blank_values_when_required_is_separate() -> None:
    df = pd.DataFrame(
        [
            {"material": ""},
            {"material": "Wood"},
        ]
    )

    rules = [
        {
            "check": "allowed_values",
            "field": "material",
            "values": ["Wood", "Steel", "Concrete", "Composite"],
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 0


def test_nie_11kv_rulepack_is_registered() -> None:
    """NIE_11kV must be registered in RULEPACKS as a non-empty rule list."""
    from app.dno_rules import RULEPACKS

    assert "NIE_11kV" in RULEPACKS
    assert isinstance(RULEPACKS["NIE_11kV"], list)
    assert len(RULEPACKS["NIE_11kV"]) > 0


def test_nie_11kv_rulepack_passes_valid_nie_pole() -> None:
    """A realistic valid NIE pole in Northern Ireland (Belfast) should produce no issues.

    Uses Belfast centre (approx 54.597, -5.930) with OSGB coords derived from
    pyproj: E=146246, N=529526. Tolerance 100m.
    """
    from app.dno_rules import RULEPACKS

    df = pd.DataFrame(
        [
            {
                "pole_id": "NIE-BEL-0001",
                "height": 10.0,
                "material": "Wood",
                "structure_type": "Wood Pole",
                "location": "Belfast Substation Approach",
                "lat": 54.597,
                "lon": -5.930,
                "easting": 146246,
                "northing": 529526,
            }
        ]
    )

    issues = run_qa_checks(df, RULEPACKS["NIE_11kV"])

    assert len(issues) == 0


def test_ssen_11kv_rulepack_is_registered() -> None:
    """SSEN_11kV must be registered in RULEPACKS as a non-empty rule list."""
    from app.dno_rules import RULEPACKS

    assert "SSEN_11kV" in RULEPACKS
    assert isinstance(RULEPACKS["SSEN_11kV"], list)
    assert len(RULEPACKS["SSEN_11kV"]) > 0


def test_ssen_11kv_rulepack_passes_valid_ssen_pole() -> None:
    """A realistic valid SSEN pole in SHEPD (Inverness) should produce no issues.

    Uses Inverness centre (approx 57.477, -4.225) with OSGB coords derived from
    pyproj to match within the 100m coord_consistency tolerance.
    """
    from app.dno_rules import RULEPACKS

    df = pd.DataFrame(
        [
            {
                "pole_id": "SSEN-INV-0001",
                "height": 11.0,
                "material": "Wood",
                "structure_type": "Wood Pole",
                "location": "Inverness Substation Approach",
                "lat": 57.477,
                "lon": -4.225,
                "easting": 266679,
                "northing": 845157,
            }
        ]
    )

    issues = run_qa_checks(df, RULEPACKS["SSEN_11kV"])

    assert len(issues) == 0


def test_missing_column_still_returns_issue() -> None:
    df = pd.DataFrame([{"pole_id": "P-1001"}])

    rules = [{"check": "required", "field": "material"}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert issues.iloc[0]["Issue"] == "Missing column: material"


def test_regex_flags_invalid_format() -> None:
    df = pd.DataFrame([{"pole_id": "P-1001"}, {"pole_id": "P 1002"}])
    rules = [{"check": "regex", "field": "pole_id", "pattern": r"^[A-Za-z0-9_-]+$"}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert issues.iloc[0]["Issue"] == "Invalid format for 'pole_id': P 1002"


def test_paired_required_flags_half_coordinates() -> None:
    df = pd.DataFrame(
        [
            {"lat": 54.5, "lon": -3.0},
            {"lat": 54.5, "lon": None},
            {"lat": None, "lon": -3.0},
            {"lat": None, "lon": None},
        ]
    )
    rules = [{"check": "paired_required", "fields": ["lat", "lon"]}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 2
    assert "Missing required paired field(s)" in issues.iloc[0]["Issue"]


def test_dependent_allowed_values_flags_inconsistent_material() -> None:
    df = pd.DataFrame(
        [
            {"structure_type": "Wood Pole", "material": "Wood"},
            {"structure_type": "Wood Pole", "material": "Steel"},
        ]
    )
    rules = [
        {
            "check": "dependent_allowed_values",
            "if_field": "structure_type",
            "then_field": "material",
            "mapping": {"Wood Pole": ["Wood"]},
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert (
        issues.iloc[0]["Issue"] == "Inconsistent 'material' for 'structure_type=Wood Pole': Steel"
    )


def test_coord_consistency_flags_mismatched_coordinates() -> None:
    """lat/lon pointing to Glasgow but easting/northing pointing to London."""
    df = pd.DataFrame(
        [
            {
                "lat": 55.861,
                "lon": -4.251,
                "easting": 530000,  # London area
                "northing": 180000,  # London area
            }
        ]
    )
    rules = [
        {
            "check": "coord_consistency",
            "lat_field": "lat",
            "lon_field": "lon",
            "easting_field": "easting",
            "northing_field": "northing",
            "tolerance_m": 100,
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert "Coordinate mismatch" in issues.iloc[0]["Issue"]


def test_coord_consistency_passes_matching_coordinates() -> None:
    """Glasgow lat/lon with matching OSGB easting/northing — should produce no issues.

    Reference values derived from pyproj EPSG:4326 -> EPSG:27700 transform:
    lat=55.861, lon=-4.251 -> E=259214, N=665382
    """
    df = pd.DataFrame(
        [
            {
                "lat": 55.861,
                "lon": -4.251,
                "easting": 259214,
                "northing": 665382,
            }
        ]
    )
    rules = [
        {
            "check": "coord_consistency",
            "lat_field": "lat",
            "lon_field": "lon",
            "easting_field": "easting",
            "northing_field": "northing",
            "tolerance_m": 100,
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 0


def test_enwl_11kv_rulepack_is_registered() -> None:
    """ENWL_11kV must be registered in RULEPACKS as a non-empty rule list."""
    from app.dno_rules import RULEPACKS

    assert "ENWL_11kV" in RULEPACKS
    assert isinstance(RULEPACKS["ENWL_11kV"], list)
    assert len(RULEPACKS["ENWL_11kV"]) > 0


def test_enwl_11kv_rulepack_passes_valid_enwl_pole() -> None:
    """A valid ENWL pole in Greater Manchester should produce no issues.

    Manchester Piccadilly area (53.4808, -2.2426). OSGB coords derived from
    pyproj EPSG:4326 -> EPSG:27700: E=383997, N=398258. Tolerance 100m.
    """
    from app.dno_rules import RULEPACKS

    df = pd.DataFrame(
        [
            {
                "pole_id": "ENWL-MAN-0001",
                "height": 10.0,
                "material": "Wood",
                "structure_type": "Wood Pole",
                "location": "Manchester Piccadilly Approach",
                "lat": 53.4808,
                "lon": -2.2426,
                "easting": 383997,
                "northing": 398258,
            }
        ]
    )

    issues = run_qa_checks(df, RULEPACKS["ENWL_11kV"])

    assert len(issues) == 0


def test_unique_pair_flags_duplicate_coordinates() -> None:
    df = pd.DataFrame(
        [
            {"pole_id": "P-001", "lat": 54.5, "lon": -3.0},
            {"pole_id": "P-002", "lat": 54.5, "lon": -3.0},
        ]
    )
    rules = [{"check": "unique_pair", "fields": ["lat", "lon"]}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert "Duplicate pair" in issues.iloc[0]["Issue"]


def test_unique_pair_passes_unique_coordinates() -> None:
    df = pd.DataFrame(
        [
            {"pole_id": "P-001", "lat": 54.5, "lon": -3.0},
            {"pole_id": "P-002", "lat": 54.6, "lon": -3.1},
        ]
    )
    rules = [{"check": "unique_pair", "fields": ["lat", "lon"]}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 0


def test_span_distance_flags_poles_too_close() -> None:
    # 0.0001 degree lat ≈ 11.1m — below min_m=50, in the 8–min_m borderline tier
    df = pd.DataFrame(
        [
            {"pole_id": "P-001", "lat": 54.5000, "lon": -3.0000},
            {"pole_id": "P-002", "lat": 54.5001, "lon": -3.0000},
        ]
    )
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 50,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert "Span borderline short" in issues.iloc[0]["Issue"]
    assert issues.iloc[0].get("Severity") == "WARN"


def test_coord_consistency_skips_for_non_osgb_grid_crs() -> None:
    """coord_consistency must produce no issues when _grid_crs is a non-OSGB CRS.

    TM65 easting/northing (Strabane area) with WGS84 lat/lon derived from them.
    Comparing OSGB27700-projected lat/lon against TM65 easting/northing values
    would produce a ~27 km apparent mismatch on every pole — a false positive.
    """
    df = pd.DataFrame(
        [
            {
                "lat": 54.827,
                "lon": -7.378,
                "easting": 242186.0,
                "northing": 402362.0,
                "_grid_crs": "EPSG:29900",
            }
        ]
    )
    rules = [
        {
            "check": "coord_consistency",
            "lat_field": "lat",
            "lon_field": "lon",
            "easting_field": "easting",
            "northing_field": "northing",
            "tolerance_m": 100,
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 0


def test_coord_consistency_still_runs_for_explicit_osgb27700_grid_crs() -> None:
    """coord_consistency must still catch mismatches when _grid_crs is EPSG:27700.

    Glasgow lat/lon paired with London easting/northing — clear mismatch that
    must be flagged even when _grid_crs is explicitly set to EPSG:27700.
    """
    df = pd.DataFrame(
        [
            {
                "lat": 55.861,
                "lon": -4.251,
                "easting": 530000,
                "northing": 180000,
                "_grid_crs": "EPSG:27700",
            }
        ]
    )
    rules = [
        {
            "check": "coord_consistency",
            "lat_field": "lat",
            "lon_field": "lon",
            "easting_field": "easting",
            "northing_field": "northing",
            "tolerance_m": 100,
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1
    assert "Coordinate mismatch" in issues.iloc[0]["Issue"]


def test_span_distance_passes_normal_span() -> None:
    # 0.001 degree lat ≈ 111m — within 10–500m range
    df = pd.DataFrame(
        [
            {"pole_id": "P-001", "lat": 54.5000, "lon": -3.0000},
            {"pole_id": "P-002", "lat": 54.5010, "lon": -3.0000},
        ]
    )
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 10,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 0


def test_span_distance_skips_context_feature_codes() -> None:
    """Hedge adjacent to a Pol must not trigger a false 'span too short' issue.

    Pol at 54.5200, Hedge at 54.52002 (~2m away), Pol at 54.5207 (~78m from first).
    Without the context filter: Pol→Hedge = 2m < min_m=10 → false positive.
    With the filter: Hedge is skipped, Pol→Pol = 78m → no issue.
    """
    df = pd.DataFrame(
        [
            {"pole_id": "1", "lat": 54.5200, "lon": -3.0000, "structure_type": "Pol"},
            {"pole_id": "H", "lat": 54.52002, "lon": -3.0000, "structure_type": "Hedge"},
            {"pole_id": "2", "lat": 54.5207, "lon": -3.0000, "structure_type": "Pol"},
        ]
    )
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 10,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 0, f"Unexpected span issues: {issues['Issue'].tolist()}"


def test_span_distance_context_feature_bridges_span_to_next_structural_record() -> None:
    """Span between two Pols bridging over a Hedge must still be checked for max distance.

    Pol at 54.5200, Hedge at 54.5300 (skipped), Pol at 54.5310.
    Pol-to-Pol span (bridging Hedge) ≈ 1221m > max_m=500 → must be flagged.
    """
    df = pd.DataFrame(
        [
            {"pole_id": "1", "lat": 54.5200, "lon": -3.0000, "structure_type": "Pol"},
            {"pole_id": "H", "lat": 54.5300, "lon": -3.0000, "structure_type": "Hedge"},
            {"pole_id": "2", "lat": 54.5310, "lon": -3.0000, "structure_type": "Pol"},
        ]
    )
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 10,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)

    span_long = [i for i in issues["Issue"].tolist() if "Span too long" in i]
    assert len(span_long) == 1, f"Expected one span-too-long issue, got: {issues['Issue'].tolist()}"


def test_structural_only_range_skips_context_features() -> None:
    """structural_only: True on a range rule must not fire for Hedge/Tree rows.

    Hedge has height=2 (below min=7). With structural_only it must produce zero issues.
    Pol has height=26 (above max=25). With structural_only it must still be flagged.
    """
    df = pd.DataFrame(
        [
            {"structure_type": "Hedge", "height": 2.0},
            {"structure_type": "Pol", "height": 26.0},
        ]
    )
    rules = [{"check": "range", "field": "height", "min": 7, "max": 25, "structural_only": True}]

    issues = run_qa_checks(df, rules)

    issue_texts = issues["Issue"].tolist()
    hedge_issues = [t for t in issue_texts if "height" in t.lower()]
    assert len(hedge_issues) == 1, (
        f"Expected exactly one height issue (for Pol), got: {hedge_issues}"
    )
    pol_issues = [i for i in issues.to_dict("records") if "out of range" in i["Issue"]]
    assert len(pol_issues) == 1


def test_structural_only_required_skips_context_features() -> None:
    """structural_only: True on a required rule must not fire for Hedge rows missing height.

    Hedge with no height set must not trigger 'Missing required field: height'.
    Pol with no height set must still be flagged.
    """
    df = pd.DataFrame(
        [
            {"structure_type": "Hedge", "height": None},
            {"structure_type": "Pol", "height": None},
        ]
    )
    rules = [{"check": "required", "field": "height", "structural_only": True}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 1, (
        f"Expected one missing-height issue (for Pol), got: {issues['Issue'].tolist()}"
    )
    assert "Missing required field: height" in issues.iloc[0]["Issue"]


def test_deduplication_collapses_same_logical_issue_per_row() -> None:
    """Two height range rules for the same row must produce only one issue after dedup.

    BASE_RULES has height range (7-25); SPEN adds (7-20). A pole with height=22
    passes the (7-25) rule but fails (7-20). A pole with height=26 fails both.
    After deduplication, each pole should show at most one height-out-of-range issue.
    """
    df = pd.DataFrame(
        [
            {"__row_index__": 0, "structure_type": "Pol", "height": 26.0},
        ]
    )
    rules = [
        {"check": "range", "field": "height", "min": 7, "max": 25, "structural_only": True},
        {"check": "range", "field": "height", "min": 7, "max": 20, "structural_only": True},
    ]

    issues = run_qa_checks(df, rules)

    height_issues = [t for t in issues["Issue"].tolist() if "height out of range" in t]
    assert len(height_issues) == 1, (
        f"Expected deduplication to collapse to 1 height issue, got: {height_issues}"
    )


def test_anchor_row_excluded_from_required_check() -> None:
    """Anchor rows must never trigger QA issues, even when required fields are absent.

    A row with _record_role='anchor' and no height must produce no issue.
    A row with _record_role='structural' and no height must still be flagged.
    """
    df = pd.DataFrame(
        [
            {"_record_role": "anchor", "pole_id": "GB_Kelso", "height": None},
            {"_record_role": "structural", "pole_id": "1", "height": None},
        ]
    )
    rules = [{"check": "required", "field": "height", "structural_only": False}]

    issues = run_qa_checks(df, rules)

    issue_texts = issues["Issue"].tolist()
    assert len(issues) == 1, f"Expected exactly one issue (structural row), got: {issue_texts}"
    assert "Missing required field: height" in issue_texts[0]


def test_span_distance_resets_chain_at_anchor_row() -> None:
    """An anchor row between two structural poles must break the span chain.

    Without the anchor, a Pol at 54.52 and a Pol at 54.60 (≈8.9km) would fire
    span_too_long. With an anchor row in between the chain resets at the anchor,
    so no span issue is raised for the second Pol.
    """
    df = pd.DataFrame(
        [
            {
                "_record_role": "structural",
                "pole_id": "1",
                "lat": 54.5200,
                "lon": -3.0,
                "structure_type": "Pol",
            },
            {
                "_record_role": "anchor",
                "pole_id": "GB_Kelso",
                "lat": 55.6000,
                "lon": -2.5,
                "structure_type": None,
            },
            {
                "_record_role": "structural",
                "pole_id": "2",
                "lat": 54.6000,
                "lon": -3.0,
                "structure_type": "Pol",
            },
        ]
    )
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 10,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 0, (
        f"Expected no span issues after anchor chain reset, got {len(issues)} issue(s)"
    )


def test_gate_track_stream_no_height_range_fail() -> None:
    """Gate, Track and Stream with below-minimum heights must not produce FAIL issues.

    These feature codes were added to _CONTEXT_FEATURE_CODES in Batch 9.
    With structural_only=True, none of them should trigger a height range issue.
    A Pol with the same low height must still be flagged.
    """
    df = pd.DataFrame(
        [
            {"structure_type": "Gate", "height": 1.5},
            {"structure_type": "Track", "height": 0.0},
            {"structure_type": "Stream", "height": 0.5},
            {"structure_type": "Pol", "height": 3.0},
        ]
    )
    rules = [{"check": "range", "field": "height", "min": 7, "max": 25, "structural_only": True}]

    issues = run_qa_checks(df, rules)

    issue_texts = issues["Issue"].tolist()
    assert len(issues) == 1, f"Expected one issue (Pol only), got: {issue_texts}"
    row = issues.iloc[0]["Row"]
    assert row.get("structure_type") == "Pol", (
        f"Expected the flagged row to be Pol, got: {row.get('structure_type')}"
    )


def test_replacement_cluster_detection() -> None:
    """EXpole + structural Pol within min distance must emit WARN, not FAIL.

    Surveyors place PRpole 2–5m from EXpole for replacement jobs. This short
    offset must not trigger a false 'span too short' FAIL. A WARN with
    'Replacement pair detected' must appear instead, with Severity='WARN'.
    """
    df = pd.DataFrame(
        [
            {
                "pole_id": "EX-1",
                "lat": 54.5200,
                "lon": -3.0000,
                "structure_type": "EXpole",
            },
            {
                # 0.00003 deg lat ≈ 3.3m — EXpole → Pol replacement pair
                "pole_id": "PR-1",
                "lat": 54.52003,
                "lon": -3.0000,
                "structure_type": "Pol",
            },
        ]
    )
    df["__row_index__"] = df.index
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 10,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist()

    span_fails = [t for t in issue_texts if "Span too short" in t]
    assert len(span_fails) == 0, f"Unexpected FAIL for replacement pair: {span_fails}"

    warn_issues = [t for t in issue_texts if "Replacement pair detected" in t]
    assert len(warn_issues) == 1, f"Expected one replacement pair WARN, got: {issue_texts}"

    assert "Severity" in issues.columns
    sev = issues[issues["Issue"].str.contains("Replacement pair")]["Severity"].iloc[0]
    assert sev == "WARN", f"Expected Severity='WARN', got: {sev}"


def test_span_suppression_does_not_apply_to_pol_pol() -> None:
    """Two Pol records within min distance must emit a span WARN (not a replacement WARN).

    Replacement-pair suppression fires only when exactly one record is EXpole.
    Pol→Pol at close distance is a genuine data concern and must emit a span
    tier WARN — not a replacement pair WARN.
    """
    df = pd.DataFrame(
        [
            {
                "pole_id": "1",
                "lat": 54.5200,
                "lon": -3.0000,
                "structure_type": "Pol",
            },
            {
                # 0.00003 deg lat ≈ 3.3m — Pol → Pol, not a replacement pair
                "pole_id": "2",
                "lat": 54.52003,
                "lon": -3.0000,
                "structure_type": "Pol",
            },
        ]
    )
    df["__row_index__"] = df.index
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 10,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist()

    # 3.3m sits in the 3–8m tier → "Span unusually short"
    span_issues = [t for t in issue_texts if "Span unusually short" in t]
    assert len(span_issues) == 1, f"Expected span WARN for Pol→Pol short span, got: {issue_texts}"
    assert issues.iloc[0].get("Severity") == "WARN"

    warn_issues = [t for t in issue_texts if "Replacement pair" in t]
    assert len(warn_issues) == 0, f"Unexpected replacement pair WARN for Pol→Pol: {warn_issues}"


def test_span_distance_message_shows_one_decimal_precision() -> None:
    """Span issue text must show distances to 1 decimal place.

    0.00003 deg lat ≈ 3.3m sits in the 3–8m tier → 'Span unusually short'.
    The distance value must contain a decimal point so the actual measured
    value is unambiguous to the designer.
    """
    df = pd.DataFrame(
        [
            {"pole_id": "1", "lat": 54.5200, "lon": -3.0000},
            # 0.00003 deg lat ≈ 3.3m — in the 3–8m unusual tier
            {"pole_id": "2", "lat": 54.52003, "lon": -3.0000},
        ]
    )
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 10,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)

    span_issues = [i for i in issues["Issue"].tolist() if "Span unusually short" in i]
    assert len(span_issues) == 1
    # Message must contain a decimal point for the distance value
    assert "." in span_issues[0], (
        f"Expected decimal precision in span message, got: {span_issues[0]}"
    )


def test_angle_no_stay_emits_warn() -> None:
    """An Angle record with no stay-evidence record nearby must emit a WARN.

    A Pol at 100m distance is not stay evidence. The Angle has no stay in
    its remarks either. Exactly one WARN must be emitted, Severity='WARN'.
    """
    df = pd.DataFrame(
        [
            {
                "pole_id": "A-1",
                "lat": 54.5200,
                "lon": -3.0000,
                "structure_type": "Angle",
                "location": None,
            },
            {
                # 0.001 deg lat ≈ 111m away — not stay evidence
                "pole_id": "P-1",
                "lat": 54.5210,
                "lon": -3.0000,
                "structure_type": "Pol",
                "location": None,
            },
        ]
    )
    df["__row_index__"] = df.index
    rules = [
        {
            "check": "angle_stay",
            "lat_field": "lat",
            "lon_field": "lon",
            "proximity_m": 30,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist()

    warn_issues = [t for t in issue_texts if "Angle structure with no stay" in t]
    assert len(warn_issues) == 1, f"Expected one angle/stay WARN, got: {issue_texts}"
    assert "Severity" in issues.columns
    sev = issues[issues["Issue"].str.contains("Angle structure with no stay")]["Severity"].iloc[0]
    assert sev == "WARN", f"Expected Severity='WARN', got: {sev}"


def test_angle_with_stay_within_proximity_no_warn() -> None:
    """An Angle record with a Stay record within proximity_m must produce no issues.

    Stay at 20m (well inside the 30m threshold) satisfies the check.
    """
    df = pd.DataFrame(
        [
            {
                "pole_id": "A-1",
                "lat": 54.5200,
                "lon": -3.0000,
                "structure_type": "Angle",
                "location": None,
            },
            {
                # 0.00018 deg lat ≈ 20m — within 30m proximity
                "pole_id": "S-1",
                "lat": 54.52018,
                "lon": -3.0000,
                "structure_type": "Stay",
                "location": None,
            },
        ]
    )
    df["__row_index__"] = df.index
    rules = [
        {
            "check": "angle_stay",
            "lat_field": "lat",
            "lon_field": "lon",
            "proximity_m": 30,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist() if "Issue" in issues.columns else []

    warn_issues = [t for t in issue_texts if "Angle structure with no stay" in t]
    assert len(warn_issues) == 0, f"Unexpected WARN with stay in proximity: {issue_texts}"


def test_angle_with_stay_beyond_proximity_emits_warn() -> None:
    """Stay record beyond proximity_m must not satisfy the angle/stay check.

    Stay at 60m (beyond the 30m threshold) is too far — WARN must be emitted.
    """
    df = pd.DataFrame(
        [
            {
                "pole_id": "A-1",
                "lat": 54.5200,
                "lon": -3.0000,
                "structure_type": "Angle",
                "location": None,
            },
            {
                # 0.0006 deg lat ≈ 67m — outside 30m proximity
                "pole_id": "S-1",
                "lat": 54.5206,
                "lon": -3.0000,
                "structure_type": "Stay",
                "location": None,
            },
        ]
    )
    df["__row_index__"] = df.index
    rules = [
        {
            "check": "angle_stay",
            "lat_field": "lat",
            "lon_field": "lon",
            "proximity_m": 30,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist()

    warn_issues = [t for t in issue_texts if "Angle structure with no stay" in t]
    assert len(warn_issues) == 1, f"Expected WARN when stay is beyond proximity, got: {issue_texts}"


def test_angle_stay_remarks_evidence_suppresses_warn() -> None:
    """Stay mention in the angle record's own remarks must suppress the WARN.

    If no stay-code record exists but the angle pole's location/remarks
    contains 'stay', that secondary evidence is sufficient to pass the check.
    """
    df = pd.DataFrame(
        [
            {
                "pole_id": "A-1",
                "lat": 54.5200,
                "lon": -3.0000,
                "structure_type": "Angle",
                "location": "stay installed 3m west",
            },
        ]
    )
    df["__row_index__"] = df.index
    rules = [
        {
            "check": "angle_stay",
            "lat_field": "lat",
            "lon_field": "lon",
            "proximity_m": 30,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist() if "Issue" in issues.columns else []

    warn_issues = [t for t in issue_texts if "Angle structure with no stay" in t]
    assert len(warn_issues) == 0, f"Expected no WARN when remarks mention stay, got: {issue_texts}"


def test_angle_stay_no_issue_for_pol_only_file() -> None:
    """Files with no Angle records must produce no angle_stay issues.

    The check silently skips when _ANGLE_CODES finds no matches.
    """
    df = pd.DataFrame(
        [
            {"pole_id": "1", "lat": 54.5200, "lon": -3.0000, "structure_type": "Pol"},
            {"pole_id": "2", "lat": 54.5210, "lon": -3.0000, "structure_type": "Pol"},
        ]
    )
    df["__row_index__"] = df.index
    rules = [
        {
            "check": "angle_stay",
            "lat_field": "lat",
            "lon_field": "lon",
            "proximity_m": 30,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist() if "Issue" in issues.columns else []

    warn_issues = [t for t in issue_texts if "Angle structure" in t]
    assert len(warn_issues) == 0, f"Unexpected angle_stay issues for Pol-only file: {issue_texts}"


# ---------------------------------------------------------------------------
# Batch 13: span tier tests
# ---------------------------------------------------------------------------


def test_short_span_very_close_emits_warn_very_short_tier() -> None:
    """Span < 3m must emit WARN with 'Span very short' message.

    0.00002 deg lat ≈ 2.2m — in the sub-3m tier.
    """
    df = pd.DataFrame(
        [
            {"pole_id": "1", "lat": 54.5200, "lon": -3.0000},
            {"pole_id": "2", "lat": 54.52002, "lon": -3.0000},
        ]
    )
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 10,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist()

    very_short = [t for t in issue_texts if "Span very short" in t]
    assert len(very_short) == 1, f"Expected 'Span very short' WARN, got: {issue_texts}"
    assert issues.iloc[0].get("Severity") == "WARN"


def test_short_span_unusual_tier_emits_warn() -> None:
    """Span 3–8m must emit WARN with 'Span unusually short' message.

    0.00005 deg lat ≈ 5.6m — in the 3–8m tier.
    """
    df = pd.DataFrame(
        [
            {"pole_id": "1", "lat": 54.5200, "lon": -3.0000},
            {"pole_id": "2", "lat": 54.52005, "lon": -3.0000},
        ]
    )
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 10,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist()

    unusual = [t for t in issue_texts if "Span unusually short" in t]
    assert len(unusual) == 1, f"Expected 'Span unusually short' WARN, got: {issue_texts}"
    assert issues.iloc[0].get("Severity") == "WARN"


def test_short_span_borderline_tier_emits_warn() -> None:
    """Span 8–min_m must emit WARN with 'Span borderline short' message.

    0.00008 deg lat ≈ 8.9m with min_m=10 — in the 8–10m borderline tier.
    """
    df = pd.DataFrame(
        [
            {"pole_id": "1", "lat": 54.5200, "lon": -3.0000},
            {"pole_id": "2", "lat": 54.52008, "lon": -3.0000},
        ]
    )
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 10,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist()

    borderline = [t for t in issue_texts if "Span borderline short" in t]
    assert len(borderline) == 1, f"Expected 'Span borderline short' WARN, got: {issue_texts}"
    assert issues.iloc[0].get("Severity") == "WARN"


# ---------------------------------------------------------------------------
# Batch 13: EXpole height downgrade tests
# ---------------------------------------------------------------------------


def test_expole_height_below_min_emits_warn() -> None:
    """EXpole with height below the minimum must emit WARN, not a hard FAIL.

    EXpole heights are often estimated or not properly captured in the field.
    height=5.0 with min=7 should produce 'Height likely estimated / not captured'.
    """
    df = pd.DataFrame(
        [
            {
                "pole_id": "EX-1",
                "structure_type": "EXpole",
                "height": 5.0,
            }
        ]
    )
    rules = [
        {
            "check": "range",
            "field": "height",
            "min": 7,
            "max": 25,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist()

    assert len(issues) == 1, f"Expected exactly one issue, got: {issue_texts}"
    assert "Height likely estimated" in issue_texts[0], f"Unexpected message: {issue_texts[0]}"
    assert issues.iloc[0].get("Severity") == "WARN"


def test_expole_height_above_max_remains_range_fail() -> None:
    """EXpole with height above the maximum must still emit a standard range issue.

    The downgrade only applies when height is below the minimum. An EXpole with
    an unusually high height value is a genuine data concern.
    """
    df = pd.DataFrame(
        [
            {
                "pole_id": "EX-1",
                "structure_type": "EXpole",
                "height": 30.0,
            }
        ]
    )
    rules = [
        {
            "check": "range",
            "field": "height",
            "min": 7,
            "max": 25,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist()

    assert len(issues) == 1, f"Expected one range issue, got: {issue_texts}"
    assert "out of range" in issue_texts[0], (
        f"Expected standard range message, got: {issue_texts[0]}"
    )


def test_non_expole_height_below_min_remains_range_issue() -> None:
    """A regular Pol with height below the minimum must not receive the EXpole downgrade.

    Only EXpole records get the 'Height likely estimated' WARN. A Pol with
    height=5.0 must still emit the standard 'height out of range' message.
    """
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-1",
                "structure_type": "Pol",
                "height": 5.0,
            }
        ]
    )
    rules = [
        {
            "check": "range",
            "field": "height",
            "min": 7,
            "max": 25,
        }
    ]

    issues = run_qa_checks(df, rules)
    issue_texts = issues["Issue"].tolist()

    assert len(issues) == 1, f"Expected one range issue, got: {issue_texts}"
    assert "out of range" in issue_texts[0], (
        f"Expected standard range message, got: {issue_texts[0]}"
    )
    assert "EXpole" not in issue_texts[0]


# ---------------------------------------------------------------------------
# Phase 3A — context codes and span threshold
# ---------------------------------------------------------------------------


def test_btxing_does_not_trigger_height_required_structural_only() -> None:
    """BTxing records must not raise a height-required FAIL when structural_only=True.

    BTxing is a crossing height measurement, not a structural pole. The
    structural_only gate must skip it even if height is absent.
    """
    df = pd.DataFrame(
        [
            {"pole_id": "1", "structure_type": "BTxing", "height": None},
            {"pole_id": "2", "structure_type": "Pol", "height": 10.0},
        ]
    )
    rules = [{"check": "required", "field": "height", "structural_only": True}]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 0, (
        f"BTxing must not trigger height-required; got: {issues.to_dict('records')}"
    )


def test_lvxing_excluded_from_span_distance_bridges_to_next_structural() -> None:
    """LVxing between two Pols must be skipped — span bridges directly to next Pol.

    Pol→LVxing is ~5m (skipped). LVxing→Pol is ~800m (bridged).
    Pol-to-Pol span ≈ 805m > max_m=500 → must be flagged as 'Span too long'.
    """
    df = pd.DataFrame(
        [
            {"pole_id": "1", "lat": 54.5200, "lon": -3.0000, "structure_type": "Pol"},
            {"pole_id": "X", "lat": 54.5200, "lon": -2.9999, "structure_type": "LVxing"},
            {"pole_id": "2", "lat": 54.5272, "lon": -3.0000, "structure_type": "Pol"},
        ]
    )
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 5,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)

    long_spans = [i for i in issues["Issue"].tolist() if "Span too long" in i]
    assert len(long_spans) == 1, (
        f"Expected one 'Span too long' from bridged LVxing; got: {issues['Issue'].tolist()}"
    )


def test_span_distance_7m_does_not_trigger_with_min_m_5() -> None:
    """A 7m pole span must produce no issue when min_m=5.

    Phase 3A reduced the threshold from 10m to 5m. A span of ~7m was previously
    flagged as 'borderline short'; it must now pass cleanly.
    """
    # At lat≈54.5, 1 degree lat ≈ 111,320m → 7m ≈ 6.29e-5 degrees.
    df = pd.DataFrame(
        [
            {"pole_id": "1", "lat": 54.5200000, "lon": -3.0000, "structure_type": "Pol"},
            {"pole_id": "2", "lat": 54.5200629, "lon": -3.0000, "structure_type": "Pol"},
        ]
    )
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 5,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)

    assert len(issues) == 0, (
        f"7m span must not trigger with min_m=5; got: {issues.to_dict('records')}"
    )


def test_span_distance_2m_still_triggers_very_short_with_min_m_5() -> None:
    """A 2m pole span must still produce a 'Span very short' WARN when min_m=5.

    The 'very short' tier fires for dist<3m regardless of min_m. Reducing the
    outer gate to 5m must not suppress sub-3m spans.
    """
    # At lat≈54.5, 2m ≈ 1.80e-5 degrees lat.
    df = pd.DataFrame(
        [
            {"pole_id": "1", "lat": 54.5200000, "lon": -3.0000, "structure_type": "Pol"},
            {"pole_id": "2", "lat": 54.5200180, "lon": -3.0000, "structure_type": "Pol"},
        ]
    )
    rules = [
        {
            "check": "span_distance",
            "lat_field": "lat",
            "lon_field": "lon",
            "min_m": 5,
            "max_m": 500,
        }
    ]

    issues = run_qa_checks(df, rules)

    very_short = [i for i in issues["Issue"].tolist() if "Span very short" in i]
    assert len(very_short) == 1, (
        f"Expected 'Span very short' for 2m span; got: {issues['Issue'].tolist()}"
    )
