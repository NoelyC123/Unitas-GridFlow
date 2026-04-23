from __future__ import annotations

import json

import pandas as pd

from app.routes.api_intake import (
    _build_feature_collection,
    _collect_per_row_issues,
    _normalize_dataframe,
    _postprocess_issues,
    _sanitize_issues_for_csv,
)


def test_normalize_dataframe_maps_representative_schema() -> None:
    df = pd.DataFrame(
        [
            {
                "asset_id": "P-1001",
                "structure_type": "Wood Pole",
                "height_m": 11.0,
                "material": "Wood",
                "location_name": "Dalton Road Junction",
                "easting": 352841,
                "northing": 503122,
                "latitude": 54.5210,
                "longitude": -3.0140,
            }
        ]
    )

    normalized_df, auto_normalized = _normalize_dataframe(df)

    assert auto_normalized is True
    assert "pole_id" in normalized_df.columns
    assert "height" in normalized_df.columns
    assert "location" in normalized_df.columns
    assert "lat" in normalized_df.columns
    assert "lon" in normalized_df.columns

    assert normalized_df.loc[0, "pole_id"] == "P-1001"
    assert normalized_df.loc[0, "height"] == 11.0
    assert normalized_df.loc[0, "material"] == "Wood"
    assert normalized_df.loc[0, "location"] == "Dalton Road Junction"
    assert normalized_df.loc[0, "lat"] == 54.5210
    assert normalized_df.loc[0, "lon"] == -3.0140


def test_postprocess_issues_keeps_only_later_duplicate_row() -> None:
    df = pd.DataFrame(
        [
            {"pole_id": "P-1001", "__row_index__": 0},
            {"pole_id": "P-1002", "__row_index__": 1},
            {"pole_id": "P-1001", "__row_index__": 2},
        ]
    )

    issues_df = pd.DataFrame(
        [
            {
                "Issue": "Duplicate value in 'pole_id': P-1001",
                "Row": {"pole_id": "P-1001", "__row_index__": 0},
            },
            {
                "Issue": "Duplicate value in 'pole_id': P-1001",
                "Row": {"pole_id": "P-1001", "__row_index__": 2},
            },
        ]
    )

    processed = _postprocess_issues(issues_df, df)

    assert len(processed) == 1
    assert processed.iloc[0]["Row"]["__row_index__"] == 2


def test_sanitize_issues_for_csv_replaces_nan_with_empty_string() -> None:
    issues_df = pd.DataFrame(
        [
            {
                "Issue": "Missing required field: material",
                "Row": {
                    "pole_id": "P-1004",
                    "material": float("nan"),
                    "__row_index__": 3,
                },
            }
        ]
    )

    cleaned = _sanitize_issues_for_csv(issues_df)

    assert len(cleaned) == 1
    assert cleaned.iloc[0]["Row"]["material"] == ""


def test_build_feature_collection_counts_pass_and_fail_correctly() -> None:
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-1001",
                "location": "Dalton Road Junction",
                "material": "Wood",
                "height": 11.0,
                "structure_type": "Wood Pole",
                "easting": 352841,
                "northing": 503122,
                "lat": 54.5210,
                "lon": -3.0140,
                "__row_index__": 0,
            },
            {
                "pole_id": "P-1002",
                "location": "Back Lane Farm",
                "material": "Wood",
                "height": 7.5,
                "structure_type": "Wood Pole",
                "easting": 352910,
                "northing": 503088,
                "lat": 54.5183,
                "lon": -3.0121,
                "__row_index__": 1,
            },
        ]
    )

    issues_df = pd.DataFrame(
        [
            {
                "Issue": "height out of range (10-25)",
                "Row": {"pole_id": "P-1002", "__row_index__": 1},
            }
        ]
    )

    feature_collection = _build_feature_collection(
        df=df,
        issues_df=issues_df,
        job_id="J_TEST",
        rulepack_id="SPEN_11kV",
    )

    assert feature_collection["type"] == "FeatureCollection"
    assert len(feature_collection["features"]) == 2
    assert feature_collection["metadata"]["pole_count"] == 2
    assert feature_collection["metadata"]["pass_count"] == 1
    assert feature_collection["metadata"]["fail_count"] == 1
    assert feature_collection["metadata"]["issue_count"] == 1


def test_normalize_dataframe_handles_capitalised_headers() -> None:
    # "Latitude", "Structure Type", "Asset ID" etc. — common in Excel exports
    df = pd.DataFrame(
        [
            {
                "Asset ID": "P-2001",
                "Structure Type": "Wood Pole",
                "Height M": 10.0,
                "Material": "Wood",
                "Location Name": "Test Site",
                "Easting": 352841,
                "Northing": 503122,
                "Latitude": 54.521,
                "Longitude": -3.014,
            }
        ]
    )

    normalized_df, auto_normalized = _normalize_dataframe(df)

    assert auto_normalized is True
    assert normalized_df.loc[0, "pole_id"] == "P-2001"
    assert normalized_df.loc[0, "structure_type"] == "Wood Pole"
    assert normalized_df.loc[0, "height"] == 10.0
    assert normalized_df.loc[0, "material"] == "Wood"
    assert normalized_df.loc[0, "location"] == "Test Site"
    assert normalized_df.loc[0, "lat"] == 54.521
    assert normalized_df.loc[0, "lon"] == -3.014
    assert normalized_df.loc[0, "easting"] == 352841
    assert normalized_df.loc[0, "northing"] == 503122


def test_normalize_dataframe_handles_common_aliases() -> None:
    # "long" for longitude, "mat" for material, "ht_m" for height, "pole_type"
    df = pd.DataFrame(
        [
            {
                "pole_ref": "P-3001",
                "pole_type": "Steel Pole",
                "ht_m": 12.0,
                "mat": "Steel",
                "site": "Moorside",
                "lat": 54.529,
                "long": -3.010,
                "easting": 352975,
                "northing": 503200,
            }
        ]
    )

    normalized_df, auto_normalized = _normalize_dataframe(df)

    assert auto_normalized is True
    assert normalized_df.loc[0, "pole_id"] == "P-3001"
    assert normalized_df.loc[0, "structure_type"] == "Steel Pole"
    assert normalized_df.loc[0, "height"] == 12.0
    assert normalized_df.loc[0, "material"] == "Steel"
    assert normalized_df.loc[0, "location"] == "Moorside"
    assert normalized_df.loc[0, "lon"] == -3.010


def test_normalize_dataframe_handles_osgb_aliases() -> None:
    # "os_easting" / "grid_n" — OS-prefixed and grid-prefixed OSGB variants
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-4001",
                "structure_type": "Wood Pole",
                "height": 9.0,
                "material": "Wood",
                "location": "Grid Test",
                "lat": 54.521,
                "lon": -3.014,
                "os_easting": 352841,
                "grid_n": 503122,
            }
        ]
    )

    normalized_df, auto_normalized = _normalize_dataframe(df)

    assert normalized_df.loc[0, "easting"] == 352841
    assert normalized_df.loc[0, "northing"] == 503122


def test_collect_per_row_issues_returns_count_and_texts() -> None:
    issues_df = pd.DataFrame(
        [
            {
                "Issue": "Missing required field: material",
                "Row": {"pole_id": "P-1004", "__row_index__": 3},
            },
            {
                "Issue": "height out of range (10-25)",
                "Row": {"pole_id": "P-1004", "__row_index__": 3},
            },
            {
                "Issue": "Missing required field: structure_type",
                "Row": {"pole_id": "P-1005", "__row_index__": 4},
            },
        ]
    )

    result = _collect_per_row_issues(issues_df)

    assert 3 in result
    assert result[3]["count"] == 2
    assert len(result[3]["texts"]) == 2
    assert "material" in result[3]["texts"][0]
    assert 4 in result
    assert result[4]["count"] == 1
    assert result[4]["texts"][0] == "Missing required field: structure_type"


def test_collect_per_row_issues_truncates_to_three_texts() -> None:
    issues_df = pd.DataFrame(
        [{"Issue": f"Issue {i}", "Row": {"pole_id": "P-1", "__row_index__": 0}} for i in range(5)]
    )

    result = _collect_per_row_issues(issues_df)

    assert result[0]["count"] == 5
    assert len(result[0]["texts"]) == 3


def test_build_feature_collection_includes_issue_texts() -> None:
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-1001",
                "location": "Dalton Road",
                "material": None,
                "height": 11.0,
                "structure_type": "Wood Pole",
                "easting": 352841,
                "northing": 503122,
                "lat": 54.5210,
                "lon": -3.0140,
                "__row_index__": 0,
            }
        ]
    )

    issues_df = pd.DataFrame(
        [
            {
                "Issue": "Missing required field: material",
                "Row": {"pole_id": "P-1001", "__row_index__": 0},
            }
        ]
    )

    fc = _build_feature_collection(
        df=df, issues_df=issues_df, job_id="J_TEST", rulepack_id="SPEN_11kV"
    )

    props = fc["features"][0]["properties"]
    assert "issue_texts" in props
    assert len(props["issue_texts"]) == 1
    assert "material" in props["issue_texts"][0]


def test_feature_collection_is_json_serializable_without_nan() -> None:
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-1004",
                "location": "Hartley Bridge",
                "material": None,
                "height": 12.5,
                "structure_type": "Wood Pole",
                "easting": 353041,
                "northing": 503155,
                "lat": 54.5246,
                "lon": -3.0075,
                "__row_index__": 3,
            }
        ]
    )

    issues_df = pd.DataFrame(
        [
            {
                "Issue": "Missing required field: material",
                "Row": {"pole_id": "P-1004", "__row_index__": 3},
            }
        ]
    )

    feature_collection = _build_feature_collection(
        df=df,
        issues_df=issues_df,
        job_id="J_TEST_JSON",
        rulepack_id="SPEN_11kV",
    )

    payload = json.dumps(feature_collection, allow_nan=False)
    assert isinstance(payload, str)
    assert "Hartley Bridge" in payload


# ---------------------------------------------------------------------------
# Batch 14: asset_intent labels + warn_texts in feature properties
# ---------------------------------------------------------------------------


def test_build_feature_collection_expole_gets_existing_asset_intent() -> None:
    """An EXpole record must receive asset_intent='Existing asset'.

    The label is derived from structure_type alone — no WARN issue is required.
    """
    df = pd.DataFrame(
        [
            {
                "pole_id": "EX-1",
                "structure_type": "EXpole",
                "height": None,
                "material": None,
                "location": None,
                "lat": 54.5200,
                "lon": -3.0000,
                "__row_index__": 0,
            }
        ]
    )
    issues_df = pd.DataFrame(columns=["Issue", "Row"])

    fc = _build_feature_collection(
        df=df, issues_df=issues_df, job_id="J_TEST", rulepack_id="SPEN_11kV"
    )

    props = fc["features"][0]["properties"]
    assert props["asset_intent"] == "Existing asset"


def test_build_feature_collection_replacement_pair_non_expole_gets_proposed_support() -> None:
    """Non-EXpole with replacement-pair WARN must receive asset_intent='Proposed support'.

    The WARN issue text 'Replacement pair detected' is what triggers the label.
    """
    df = pd.DataFrame(
        [
            {
                "pole_id": "PR-1",
                "structure_type": "Pol",
                "height": None,
                "material": None,
                "location": None,
                "lat": 54.5200,
                "lon": -3.0000,
                "__row_index__": 0,
            }
        ]
    )
    issues_df = pd.DataFrame(
        [
            {
                "Issue": "Replacement pair detected (EX → PR, 3.3m offset)",
                "Row": {"pole_id": "PR-1", "__row_index__": 0},
                "Severity": "WARN",
            }
        ]
    )

    fc = _build_feature_collection(
        df=df, issues_df=issues_df, job_id="J_TEST", rulepack_id="SPEN_11kV"
    )

    props = fc["features"][0]["properties"]
    assert props["asset_intent"] == "Proposed support"
    assert props["relationship"] == "replacement_pair"


def test_build_feature_collection_regular_pole_has_no_asset_intent() -> None:
    """A regular Pol with no replacement-pair issues must have asset_intent=None."""
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-1",
                "structure_type": "Pol",
                "height": 10.0,
                "material": "Wood",
                "location": "Test site",
                "lat": 54.5200,
                "lon": -3.0000,
                "__row_index__": 0,
            }
        ]
    )
    issues_df = pd.DataFrame(columns=["Issue", "Row"])

    fc = _build_feature_collection(
        df=df, issues_df=issues_df, job_id="J_TEST", rulepack_id="SPEN_11kV"
    )

    props = fc["features"][0]["properties"]
    assert props["asset_intent"] is None


def test_build_feature_collection_warn_texts_populated_in_properties() -> None:
    """WARN issues must populate warn_count and warn_texts in feature properties.

    Previously these were computed but not serialised into the GeoJSON properties,
    so angle/stay and other WARN issues were invisible in the map popup.
    """
    df = pd.DataFrame(
        [
            {
                "pole_id": "A-1",
                "structure_type": "Angle",
                "height": None,
                "material": None,
                "location": None,
                "lat": 54.5200,
                "lon": -3.0000,
                "__row_index__": 0,
            }
        ]
    )
    issues_df = pd.DataFrame(
        [
            {
                "Issue": (
                    "Angle structure with no stay evidence detected"
                    " — verify whether stay capture is missing"
                ),
                "Row": {"pole_id": "A-1", "__row_index__": 0},
                "Severity": "WARN",
            }
        ]
    )

    fc = _build_feature_collection(
        df=df, issues_df=issues_df, job_id="J_TEST", rulepack_id="SPEN_11kV"
    )

    props = fc["features"][0]["properties"]
    assert props["warn_count"] == 1
    assert len(props["warn_texts"]) == 1
    assert "Angle structure" in props["warn_texts"][0]
    assert props["issue_count"] == 0  # WARN, not FAIL
