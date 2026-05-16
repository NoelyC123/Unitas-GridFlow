"""Conservative parser for ENWL trace GeoJSON evidence.

Stage 6A uses this module to preserve provenance and classify ENWL evidence
relationships. It deliberately does not infer design readiness or clear
verification flags such as conductor specification.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DIRECT_POLE_IDENTITY = "direct_pole_identity"
DIRECT_EQUIPMENT_LINKED_TO_POLE = "direct_equipment_linked_to_pole"
ROUTE_SPAN_EVIDENCE = "route_span_evidence"
NEARBY_CONTEXT_ONLY = "nearby_context_only"
UNCERTAIN = "uncertain"

RELATIONSHIP_CATEGORIES = {
    DIRECT_POLE_IDENTITY,
    DIRECT_EQUIPMENT_LINKED_TO_POLE,
    ROUTE_SPAN_EVIDENCE,
    NEARBY_CONTEXT_ONLY,
    UNCERTAIN,
}

EXTRACTED_FIELDS = (
    "voltage",
    "nominal_voltage",
    "material",
    "cable_size",
    "text_map",
    "support_no",
    "spn",
    "pole_type",
    "pole_class",
    "support_diameter",
    "rated_current",
    "fid_polestructure",
)


@dataclass(frozen=True)
class ENWLEvidenceFeature:
    """Single ENWL GeoJSON feature with normalized provenance fields."""

    feature_id: str | None
    layer_name: str | None
    feature_type: str | None
    geometry: dict[str, Any] | None
    relationship: str
    voltage: str | None = None
    nominal_voltage: str | None = None
    material: str | None = None
    cable_size: str | None = None
    text_map: str | None = None
    support_no: str | None = None
    spn: str | None = None
    pole_type: str | None = None
    pole_class: str | None = None
    support_diameter: str | None = None
    rated_current: str | None = None
    fid_polestructure: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    raw_properties: dict[str, Any] = field(default_factory=dict)

    def is_direct_equipment_link(self) -> bool:
        """Return true when this feature explicitly links equipment to a pole FID."""
        return self.relationship == DIRECT_EQUIPMENT_LINKED_TO_POLE

    def is_route_span_evidence(self) -> bool:
        """Return true when this feature is route/span evidence, not per-pole proof."""
        return self.relationship == ROUTE_SPAN_EVIDENCE


@dataclass(frozen=True)
class ENWLTraceDataset:
    """Parsed ENWL trace FeatureCollection."""

    source_path: str | None
    feature_count: int
    features: list[ENWLEvidenceFeature]

    def by_relationship(self, relationship: str) -> list[ENWLEvidenceFeature]:
        """Return features with the requested relationship classification."""
        if relationship not in RELATIONSHIP_CATEGORIES:
            raise ValueError(f"Unknown ENWL relationship category: {relationship}")
        return [feature for feature in self.features if feature.relationship == relationship]


class ENWLTraceParser:
    """Parse ENWL GeoJSON FeatureCollections into conservative evidence records."""

    def parse_file(self, path: str | Path) -> ENWLTraceDataset:
        """Parse an ENWL trace GeoJSON file from disk."""
        trace_path = Path(path)
        with trace_path.open(encoding="utf-8") as handle:
            data = json.load(handle)
        return self.parse_geojson(data, source_path=str(trace_path))

    def parse_geojson(
        self,
        data: dict[str, Any],
        source_path: str | None = None,
    ) -> ENWLTraceDataset:
        """Parse a GeoJSON FeatureCollection dictionary."""
        if data.get("type") != "FeatureCollection":
            raise ValueError("ENWL trace parser expects a GeoJSON FeatureCollection")

        features = [
            self.parse_feature(feature)
            for feature in data.get("features", [])
            if isinstance(feature, dict)
        ]
        return ENWLTraceDataset(
            source_path=source_path,
            feature_count=len(features),
            features=features,
        )

    def parse_feature(self, feature: dict[str, Any]) -> ENWLEvidenceFeature:
        """Parse one GeoJSON feature into a normalized evidence feature."""
        properties = feature.get("properties") or {}
        if not isinstance(properties, dict):
            properties = {}

        geometry = feature.get("geometry")
        if not isinstance(geometry, dict):
            geometry = None

        feature_type = _clean(_first(properties, "feature_type", "type", "asset_type"))
        layer_name = _clean(_first(properties, "layer", "layer_name", "feature_type", "geom_type"))
        relationship = self.classify_feature(properties, geometry)
        extracted = {
            field_name: _clean(_first(properties, field_name)) for field_name in EXTRACTED_FIELDS
        }

        return ENWLEvidenceFeature(
            feature_id=_clean(
                _first(properties, "FID", "fid", "id", "ogc_fid") or feature.get("id")
            ),
            layer_name=layer_name,
            feature_type=feature_type,
            geometry=geometry,
            relationship=relationship,
            metadata=dict(properties),
            raw_properties=dict(properties),
            **extracted,
        )

    def classify_feature(
        self,
        properties: dict[str, Any],
        geometry: dict[str, Any] | None = None,
    ) -> str:
        """Classify a feature without inferring design readiness.

        Conductors and line geometries remain route/span evidence unless a
        future explicit span-linking field is implemented and tested.
        """
        feature_type = (
            _clean(_first(properties, "feature_type", "type", "asset_type")) or ""
        ).lower()
        geom_type = ((geometry or {}).get("type") or "").lower()

        if _is_pole_identity_record(feature_type, properties):
            return DIRECT_POLE_IDENTITY

        if _is_conductor_or_route_record(feature_type, geom_type, properties):
            return ROUTE_SPAN_EVIDENCE

        if _has_value(_first(properties, "fid_polestructure")):
            return DIRECT_EQUIPMENT_LINKED_TO_POLE

        if _is_nearby_context_record(feature_type, properties):
            return NEARBY_CONTEXT_ONLY

        return UNCERTAIN


def parse_geojson_file(path: str | Path) -> ENWLTraceDataset:
    """Convenience wrapper for parsing an ENWL trace GeoJSON file."""
    return ENWLTraceParser().parse_file(path)


def parse_geojson(data: dict[str, Any], source_path: str | None = None) -> ENWLTraceDataset:
    """Convenience wrapper for parsing an ENWL trace FeatureCollection."""
    return ENWLTraceParser().parse_geojson(data, source_path=source_path)


def _first(properties: dict[str, Any], *keys: str) -> Any:
    """Return the first property value matching any case-insensitive key."""
    if not properties:
        return None

    lowered = {str(key).lower(): key for key in properties}
    for key in keys:
        actual_key = lowered.get(key.lower())
        if actual_key is not None:
            return properties.get(actual_key)
    return None


def _clean(value: Any) -> str | None:
    """Normalize common ENWL null placeholders while preserving raw metadata."""
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null", "n/a", "not defined"}:
        return None
    return text


def _has_value(value: Any) -> bool:
    return _clean(value) is not None


def _is_pole_identity_record(feature_type: str, properties: dict[str, Any]) -> bool:
    if any(token in feature_type for token in ("pole", "support")):
        return True
    has_identity = _has_value(_first(properties, "support_no", "spn"))
    has_pole_attributes = any(
        _has_value(_first(properties, key))
        for key in ("pole_type", "pole_class", "support_diameter")
    )
    return has_identity and has_pole_attributes


def _is_conductor_or_route_record(
    feature_type: str,
    geom_type: str,
    properties: dict[str, Any],
) -> bool:
    if any(token in feature_type for token in ("conductor", "cable", "line", "trace")):
        return True
    if geom_type in {"linestring", "multilinestring"}:
        return True
    return any(
        _has_value(_first(properties, key)) for key in ("text_map", "cable_size", "material")
    )


def _is_nearby_context_record(feature_type: str, properties: dict[str, Any]) -> bool:
    context_tokens = (
        "sleeve",
        "joint",
        "termination",
        "service",
        "transformer",
        "switch",
        "way",
        "fuse",
        "link",
        "plant",
    )
    if any(token in feature_type for token in context_tokens):
        return True
    return any(
        _has_value(_first(properties, key))
        for key in ("sleeve_type", "joint_class", "switch_name", "way_type", "transformer_type")
    )
