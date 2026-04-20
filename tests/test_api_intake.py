from __future__ import annotations

import json

import pandas as pd

from app.routes.api_intake import (
    _build_feature_collection,
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
