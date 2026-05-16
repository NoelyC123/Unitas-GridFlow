"""Tests for conservative ENWL trace GeoJSON parsing."""

import json
from pathlib import Path

import pytest

from gridflow.enwl_trace import (
    DIRECT_EQUIPMENT_LINKED_TO_POLE,
    DIRECT_POLE_IDENTITY,
    NEARBY_CONTEXT_ONLY,
    ROUTE_SPAN_EVIDENCE,
    UNCERTAIN,
    ENWLTraceParser,
    parse_geojson_file,
)


def feature(properties, geometry=None):
    return {
        "type": "Feature",
        "properties": properties,
        "geometry": geometry or {"type": "Point", "coordinates": [-2.7, 54.1]},
    }


def collection(*features):
    return {"type": "FeatureCollection", "features": list(features)}


def test_parse_geojson_feature_collection_extracts_pole_identity():
    parser = ENWLTraceParser()
    dataset = parser.parse_geojson(
        collection(
            feature(
                {
                    "FID": "16793152",
                    "feature_type": "pole_structure",
                    "support_no": "902201",
                    "spn": "61090H02201",
                    "pole_type": "Section",
                    "pole_class": "Single Wood Pole",
                    "support_diameter": "Medium",
                }
            )
        )
    )

    pole = dataset.features[0]
    assert dataset.feature_count == 1
    assert pole.feature_id == "16793152"
    assert pole.relationship == DIRECT_POLE_IDENTITY
    assert pole.support_no == "902201"
    assert pole.spn == "61090H02201"
    assert pole.pole_type == "Section"
    assert pole.pole_class == "Single Wood Pole"


def test_conductor_records_are_route_span_evidence_and_extract_specs():
    parser = ENWLTraceParser()
    dataset = parser.parse_geojson(
        collection(
            feature(
                {
                    "FID": "5940634",
                    "feature_type": "conductor_hv",
                    "voltage": "11kV",
                    "material": "Hard Drawn Copper",
                    "cable_size": "0.025in2",
                    "text_map": "3x .025 Cu 11",
                    "rated_current": "115.0",
                },
                geometry={
                    "type": "LineString",
                    "coordinates": [[-2.7, 54.1], [-2.71, 54.11]],
                },
            )
        )
    )

    conductor = dataset.features[0]
    assert conductor.relationship == ROUTE_SPAN_EVIDENCE
    assert conductor.is_route_span_evidence()
    assert conductor.material == "Hard Drawn Copper"
    assert conductor.cable_size == "0.025in2"
    assert conductor.text_map == "3x .025 Cu 11"
    assert conductor.rated_current == "115.0"


def test_fid_polestructure_creates_direct_equipment_link():
    parser = ENWLTraceParser()
    dataset = parser.parse_geojson(
        collection(
            feature(
                {
                    "FID": "20636886",
                    "feature_type": "transformer",
                    "spn": "6511294TX001",
                    "fid_polestructure": "53427080",
                    "rating_normal": "200 kVA",
                }
            )
        )
    )

    transformer = dataset.features[0]
    assert transformer.relationship == DIRECT_EQUIPMENT_LINKED_TO_POLE
    assert transformer.is_direct_equipment_link()
    assert transformer.fid_polestructure == "53427080"
    assert transformer.metadata["rating_normal"] == "200 kVA"


def test_equipment_without_fid_polestructure_is_nearby_context_only():
    parser = ENWLTraceParser()
    dataset = parser.parse_geojson(
        collection(
            feature(
                {
                    "FID": "20676288",
                    "feature_type": "way",
                    "way_type": "Support mounted fuse",
                    "spn": "6511291LC001",
                    "voltage": "415V",
                }
            )
        )
    )

    assert dataset.features[0].relationship == NEARBY_CONTEXT_ONLY


def test_sleeve_and_joint_records_are_nearby_context_only():
    parser = ENWLTraceParser()
    dataset = parser.parse_geojson(
        collection(
            feature(
                {
                    "FID": "11970605",
                    "feature_type": "sleeve_hv",
                    "sleeve_type": "Overhead Termination",
                    "joint_class": "High Voltage",
                    "voltage": "11kV",
                }
            )
        )
    )

    sleeve = dataset.features[0]
    assert sleeve.relationship == NEARBY_CONTEXT_ONLY
    assert sleeve.voltage == "11kV"


def test_missing_or_unknown_fields_do_not_crash_and_are_uncertain():
    parser = ENWLTraceParser()
    dataset = parser.parse_geojson(collection(feature({"unexpected": "value"}, geometry=None)))

    parsed = dataset.features[0]
    assert parsed.relationship == UNCERTAIN
    assert parsed.feature_id is None
    assert parsed.geometry["type"] == "Point"
    assert parsed.metadata["unexpected"] == "value"


def test_non_feature_collection_raises_value_error():
    parser = ENWLTraceParser()
    with pytest.raises(ValueError, match="FeatureCollection"):
        parser.parse_geojson({"type": "Feature", "properties": {}})


def test_by_relationship_validates_known_categories():
    parser = ENWLTraceParser()
    dataset = parser.parse_geojson(
        collection(
            feature({"feature_type": "conductor_lv", "FID": "1"}),
            feature({"feature_type": "sleeve_lv", "FID": "2"}),
        )
    )

    assert len(dataset.by_relationship(ROUTE_SPAN_EVIDENCE)) == 1
    assert len(dataset.by_relationship(NEARBY_CONTEXT_ONLY)) == 1
    with pytest.raises(ValueError, match="Unknown ENWL relationship"):
        dataset.by_relationship("design_ready")


def test_parse_geojson_file_reads_file_from_disk(tmp_path):
    path = tmp_path / "trace.geojson"
    path.write_text(
        json.dumps(collection(feature({"feature_type": "conductor_lv", "FID": "5937803"}))),
        encoding="utf-8",
    )

    dataset = parse_geojson_file(path)

    assert dataset.source_path == str(path)
    assert dataset.feature_count == 1
    assert dataset.features[0].relationship == ROUTE_SPAN_EVIDENCE


def test_real_plocal002_trace_file_classifies_observed_feature_types():
    trace_path = Path(
        "real_pilot_data/P_LOCAL_002/enwl_trace/enwl_trace_10924865_with_ratings.geojson"
    )
    if not trace_path.exists():
        pytest.skip("P_LOCAL_002 ENWL trace sample is not available")

    dataset = parse_geojson_file(trace_path)

    assert dataset.feature_count > 0
    conductors = dataset.by_relationship(ROUTE_SPAN_EVIDENCE)
    direct_equipment = dataset.by_relationship(DIRECT_EQUIPMENT_LINKED_TO_POLE)
    nearby_context = dataset.by_relationship(NEARBY_CONTEXT_ONLY)

    assert any(feature.material for feature in conductors)
    assert any(feature.cable_size for feature in conductors)
    assert any(feature.text_map for feature in conductors)
    assert all(feature.relationship == ROUTE_SPAN_EVIDENCE for feature in conductors)
    assert any(feature.fid_polestructure for feature in direct_equipment)
    assert any(feature.feature_type == "sleeve_hv" for feature in nearby_context)
