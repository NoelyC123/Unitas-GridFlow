from __future__ import annotations

import json

import pandas as pd

from app.routes.api_intake import (
    _build_feature_collection,
    _build_replacement_narratives,
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
                "height_method": "measured_rtk",
                "material": "Wood",
                "pole_specification": "11m Medium Pole",
                "grade": "Class 9 Medium",
                "pole_condition": "Fair",
                "lean_direction": "west",
                "defects": "rot at base",
                "line_voltage": "11kV",
                "conductor": "AAC",
                "mounted_equipment": "Transformer",
                "surveyed_by": "J. Smith",
                "capture_date": "2026-04-30",
                "position_accuracy": "RTK",
                "data_source": "field observed",
                "survey_method": "rtk",
                "attached_assets": "streetlight",
                "photo_refs": "pole-1.jpg;top-1.jpg",
                "install_year": "1998",
                "feeder_id": "CIR-11-04",
                "has_stay": "yes",
                "stay_spec": "storm stay",
                "stay_direction": "245",
                "stay_arrangement": "single stay",
                "anchor_type": "screw anchor",
                "parent_pole_id": "P-1001",
                "angle_deviation": 32.5,
                "required_action": "verify stay",
                "access_notes": "private lane",
                "measured_clearance": "5.4m",
                "route_offset_m": 3.2,
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
    assert normalized_df.loc[0, "height_source"] == "measured_rtk"
    assert normalized_df.loc[0, "material"] == "Wood"
    assert normalized_df.loc[0, "specification"] == "11m Medium Pole"
    assert normalized_df.loc[0, "pole_class"] == "Class 9 Medium"
    assert normalized_df.loc[0, "condition"] == "Fair"
    assert normalized_df.loc[0, "lean_direction"] == "west"
    assert normalized_df.loc[0, "defect_type"] == "rot at base"
    assert normalized_df.loc[0, "voltage"] == "11kV"
    assert normalized_df.loc[0, "conductor_type"] == "AAC"
    assert normalized_df.loc[0, "equipment"] == "Transformer"
    assert normalized_df.loc[0, "surveyor"] == "J. Smith"
    assert normalized_df.loc[0, "survey_date"] == "2026-04-30"
    assert normalized_df.loc[0, "gnss_accuracy"] == "RTK"
    assert normalized_df.loc[0, "source_confidence"] == "field observed"
    assert normalized_df.loc[0, "capture_method"] == "rtk"
    assert normalized_df.loc[0, "third_party_attachments"] == "streetlight"
    assert normalized_df.loc[0, "photo_links"] == "pole-1.jpg;top-1.jpg"
    assert normalized_df.loc[0, "year_installed"] == "1998"
    assert normalized_df.loc[0, "circuit_id"] == "CIR-11-04"
    assert normalized_df.loc[0, "stay_present"] == "yes"
    assert normalized_df.loc[0, "stay_type"] == "storm stay"
    assert normalized_df.loc[0, "stay_bearing"] == "245"
    assert normalized_df.loc[0, "stay_configuration"] == "single stay"
    assert normalized_df.loc[0, "anchor_details"] == "screw anchor"
    assert normalized_df.loc[0, "linked_pole_id"] == "P-1001"
    assert normalized_df.loc[0, "route_deviation_deg"] == 32.5
    assert normalized_df.loc[0, "action_required"] == "verify stay"
    assert normalized_df.loc[0, "access_constraint"] == "private lane"
    assert normalized_df.loc[0, "clearance_measured"] == "5.4m"
    assert normalized_df.loc[0, "distance_from_route_m"] == 3.2
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


def test_build_feature_collection_includes_c2_2_popup_display_fields() -> None:
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-1001",
                "location": "Dalton Road Junction",
                "material": "Wood",
                "height": 11.0,
                "height_source": "measured",
                "pole_class": "Class 9 Medium",
                "condition": "Fair",
                "lean_direction": "west",
                "lean_severity": "minor",
                "defect_type": "rot at base",
                "foundation_type": "direct buried",
                "voltage": "11kV",
                "conductor_type": "AAC 7/3.75",
                "phase_count": "3-phase",
                "equipment": "Transformer;Fuse",
                "equipment_rating": "50kVA",
                "surveyor": "J. Smith",
                "survey_date": "2026-04-30",
                "gnss_accuracy": "RTK +/-0.02m",
                "photo_links": "full.jpg;top.jpg",
                "year_installed": "1998",
                "circuit_id": "CIR-11-04",
                "stay_present": "yes",
                "stay_type": "storm stay",
                "stay_bearing": "245",
                "stay_configuration": "single stay",
                "anchor_details": "screw anchor",
                "linked_pole_id": "P-1001",
                "route_deviation_deg": 32.5,
                "action_required": "verify stay",
                "access_constraint": "private lane",
                "clearance_measured": "5.4m",
                "distance_from_route_m": 3.2,
                "structure_type": "EXpole",
                "easting": 352841,
                "northing": 503122,
                "elevation": 127.3,
                "lat": 54.5210,
                "lon": -3.0140,
                "__row_index__": 0,
            },
            {
                "pole_id": "P-1002",
                "location": "Next pole",
                "material": "Wood",
                "height": 11.0,
                "height_source": "measured",
                "structure_type": "Pol",
                "easting": 352900,
                "northing": 503200,
                "elevation": 127.0,
                "lat": 54.5220,
                "lon": -3.0130,
                "__row_index__": 1,
            },
        ]
    )
    issues_df = pd.DataFrame(columns=["Issue", "Row"])

    sequence_payload = {
        "status": "ok",
        "chain": [
            {
                "point_id": "P-1001",
                "lat": 54.5210,
                "lon": -3.0140,
                "span_to_next_m": 120.0,
                "design_pole_number": 1,
            },
            {
                "point_id": "P-1002",
                "lat": 54.5220,
                "lon": -3.0130,
                "design_pole_number": 2,
            },
        ],
    }

    feature_collection = _build_feature_collection(
        df=df,
        issues_df=issues_df,
        job_id="J_TEST",
        rulepack_id="SPEN_11kV",
        sequence_payload=sequence_payload,
    )

    props = feature_collection["features"][0]["properties"]
    assert props["pole_class"] == "Class 9 Medium"
    assert props["condition"] == "Fair"
    assert props["lean_direction"] == "west"
    assert props["defect_type"] == "rot at base"
    assert props["voltage"] == "11kV"
    assert props["conductor_type"] == "AAC 7/3.75"
    assert props["equipment"] == ["Transformer", "Fuse"]
    assert props["equipment_rating"] == "50kVA"
    assert props["surveyor"] == "J. Smith"
    assert props["survey_date"] == "2026-04-30"
    assert props["gnss_accuracy"] == "RTK +/-0.02m"
    assert props["photo_links"] == ["full.jpg", "top.jpg"]
    assert props["photo_count"] == 2
    assert props["elevation"] == 127.3
    assert props["source_confidence"] == "raw survey export"
    assert props["height_confidence"]["level"] == "medium-high"
    assert props["height_confidence"]["status"] == "ok"
    assert props["year_installed"] == "1998"
    assert props["circuit_id"] == "CIR-11-04"
    assert props["stay_present"] == "yes"
    assert props["stay_type"] == "storm stay"
    assert props["stay_bearing"] == "245"
    assert props["stay_configuration"] == "single stay"
    assert props["anchor_details"] == "screw anchor"
    assert props["linked_pole_id"] == "P-1001"
    assert props["route_deviation_deg"] == 32.5
    assert props["action_required"] == "verify stay"
    assert props["access_constraint"] == "private lane"
    assert props["clearance_measured"] == "5.4m"
    assert props["distance_from_route_m"] == 3.2
    assert props["equipment_kva"] == 50.0
    assert props["equipment_kva_label"] == "50 kVA"
    assert props["connectivity_parent_pole"] == "P-1001"
    assert props["gnss_accuracy_summary"]
    assert len(feature_collection["span_features"]) == 1
    spanp = feature_collection["span_features"][0]["properties"]
    assert spanp["from_point_id"] == "P-1001"
    assert spanp["to_point_id"] == "P-1002"
    assert spanp.get("voltage_detail", {}).get("label")
    assert "voltage_detail" not in props
    assert "cable_features" in feature_collection
    assert isinstance(feature_collection["cable_features"], list)


def test_build_feature_collection_adds_source_confidence_detail() -> None:
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-LEGACY",
                "location": "Legacy record",
                "structure_type": "EXpole",
                "height": 10.5,
                "height_source": "legacy_data",
                "source_confidence": "legacy map data",
                "lat": 54.5210,
                "lon": -3.0140,
                "__row_index__": 0,
            }
        ]
    )
    issues_df = pd.DataFrame(columns=["Issue", "Row"])

    feature_collection = _build_feature_collection(
        df=df,
        issues_df=issues_df,
        job_id="J_TEST",
        rulepack_id="SPEN_11kV",
    )

    detail = feature_collection["features"][0]["properties"]["source_confidence_detail"]
    assert detail["provenance"] == "legacy_map_data"
    assert detail["confidence"] == "low"
    assert detail["geometry_trust"] == "unverified"
    assert "Field verification required before design" in detail["warnings"]


def test_build_feature_collection_adds_attachment_detail() -> None:
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-ATT",
                "location": "Pole with streetlight",
                "structure_type": "EXpole",
                "height": 10.5,
                "height_source": "measured_rtk",
                "third_party_attachments": "streetlight",
                "lat": 54.5210,
                "lon": -3.0140,
                "__row_index__": 0,
            }
        ]
    )
    issues_df = pd.DataFrame(columns=["Issue", "Row"])

    feature_collection = _build_feature_collection(
        df=df,
        issues_df=issues_df,
        job_id="J_TEST",
        rulepack_id="SPEN_11kV",
    )

    detail = feature_collection["features"][0]["properties"]["attachments_detail"]
    assert detail["has_attachments"] is True
    assert detail["attachment_count"] == 1
    assert detail["attachment_types"] == ["streetlight"]
    assert detail["coordination_required"] is True


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


def test_build_feature_collection_bt_expole_gets_third_party_fields() -> None:
    df = pd.DataFrame(
        [
            {
                "pole_id": "72",
                "structure_type": "EXpole",
                "height": 6.5,
                "material": "Wood",
                "location": "bt pole",
                "_record_role": "third_party",
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
    assert props["record_role"] == "third_party"
    assert props["asset_intent"] == "third_party_not_network"
    assert props["lifecycle_state"] is None
    assert props["primary_type"] == "third_party_infrastructure"
    assert props["infrastructure_owner"] == "telecoms"
    assert props["popup_type_label"] == "Third-Party Telecoms Pole (BT/Openreach)"
    assert props["is_structural_pole"] is False
    assert props["is_electric_network"] is False


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
                "specification": "11m Medium Pole",
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
    assert props["specification"] == "11m Medium Pole"


def test_build_feature_collection_adds_lifecycle_links_for_replacement_pair() -> None:
    df = pd.DataFrame(
        [
            {
                "pole_id": "48",
                "structure_type": "EXpole",
                "height": 10.0,
                "material": "Wood",
                "lat": 54.5200,
                "lon": -3.0000,
                "__row_index__": 0,
            },
            {
                "pole_id": "49",
                "structure_type": "Pol",
                "height": None,
                "material": None,
                "lat": 54.5201,
                "lon": -3.0001,
                "__row_index__": 1,
            },
        ]
    )
    issues_df = pd.DataFrame(
        [
            {
                "Issue": "Replacement pair detected (EX → PR, 3.3m offset)",
                "Row": {"pole_id": "49", "__row_index__": 1},
                "Severity": "WARN",
            }
        ]
    )

    fc = _build_feature_collection(
        df=df, issues_df=issues_df, job_id="J_TEST", rulepack_id="SPEN_11kV"
    )

    existing_props = fc["features"][0]["properties"]
    proposed_props = fc["features"][1]["properties"]
    assert existing_props["lifecycle_state"] == "Existing Pole being Replaced (Recovered)"
    assert existing_props["being_replaced_by"] == "49"
    assert proposed_props["lifecycle_state"] == "Proposed Replacement Pole"
    assert proposed_props["replacing"] == "48"
    assert proposed_props["match_offset_m"] == 3.3


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
                    "⚠️ Angle pole — stay evidence not captured."
                    " Check field notes, photos or plan evidence."
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
    assert "stay evidence not captured" in props["warn_texts"][0]
    assert props["stay_evidence_status"] == "missing"
    assert props["issue_count"] == 0  # WARN, not FAIL


def test_build_feature_collection_shows_captured_stay_evidence_for_angle() -> None:
    df = pd.DataFrame(
        [
            {
                "pole_id": "A-1",
                "structure_type": "Angle",
                "lat": 54.5200,
                "lon": -3.0000,
                "__row_index__": 0,
            },
            {
                "pole_id": "ST-1",
                "structure_type": "Stay",
                "lat": 54.52005,
                "lon": -3.0000,
                "_record_role": "anchor",
                "__row_index__": 1,
            },
        ]
    )
    issues_df = pd.DataFrame(columns=["Issue", "Row"])

    fc = _build_feature_collection(
        df=df, issues_df=issues_df, job_id="J_TEST", rulepack_id="SPEN_11kV"
    )

    angle_props = fc["features"][0]["properties"]
    stay_props = fc["features"][1]["properties"]
    assert angle_props["stay_evidence_status"] == "captured"
    assert angle_props["stay_types"] == ["Stay"]
    assert stay_props["structure_type"] == "Stay"


# ---------------------------------------------------------------------------
# Batch 15: _build_replacement_narratives
# ---------------------------------------------------------------------------


def test_build_replacement_narratives_returns_readable_text_for_pair() -> None:
    """EXpole→Pol pair must produce a narrative including both IDs and the offset."""
    df = pd.DataFrame(
        [
            {
                "pole_id": "EX-1",
                "structure_type": "EXpole",
                "_record_role": "structural",
                "__row_index__": 0,
                "lat": 54.52,
                "lon": -3.01,
            },
            {
                "pole_id": "PR-2",
                "structure_type": "Pol",
                "_record_role": "structural",
                "__row_index__": 1,
                "lat": 54.5201,
                "lon": -3.0098,
            },
        ]
    )
    issues_df = pd.DataFrame(
        [
            {
                "Issue": "Replacement pair detected (EX → PR, 3.2m offset)",
                "Row": {"pole_id": "PR-2", "__row_index__": 1},
                "Severity": "WARN",
            }
        ]
    )

    narratives = _build_replacement_narratives(df, issues_df)

    assert len(narratives) == 1
    assert "EX-1" in narratives[0]
    assert "PR-2" in narratives[0]
    assert "3.2m" in narratives[0]


def test_build_replacement_narratives_same_position_wording() -> None:
    """Offset < 0.5m must use 'at the same surveyed position' wording."""
    df = pd.DataFrame(
        [
            {
                "pole_id": "EX-10",
                "structure_type": "EXpole",
                "_record_role": "structural",
                "__row_index__": 0,
            },
            {
                "pole_id": "PR-11",
                "structure_type": "Pol",
                "_record_role": "structural",
                "__row_index__": 1,
            },
        ]
    )
    issues_df = pd.DataFrame(
        [
            {
                "Issue": "Replacement pair detected (EX → PR, 0.0m offset)",
                "Row": {"pole_id": "PR-11", "__row_index__": 1},
                "Severity": "WARN",
            }
        ]
    )

    narratives = _build_replacement_narratives(df, issues_df)

    assert len(narratives) == 1
    assert "same surveyed position" in narratives[0]


def test_build_replacement_narratives_returns_empty_for_no_pairs() -> None:
    """No replacement-pair WARNs must return an empty list."""
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-1",
                "structure_type": "Pol",
                "_record_role": "structural",
                "__row_index__": 0,
            }
        ]
    )
    issues_df = pd.DataFrame(columns=["Issue", "Row", "Severity"])

    narratives = _build_replacement_narratives(df, issues_df)

    assert narratives == []
