"""Three-source evidence combiner for Stage 6B.

The combiner joins:

- a surveyed pole folder,
- the pole's `notes/pole_notes.md`,
- an ENWL trace GeoJSON file parsed by `gridflow.enwl_trace`.

It produces one conservative evidence record per pole. It does not change
design readiness, clear conductor flags, or infer conductor-to-pole/span
assignment from proximity.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from gridflow.enwl_trace import (
    DIRECT_EQUIPMENT_LINKED_TO_POLE,
    NEARBY_CONTEXT_ONLY,
    ROUTE_SPAN_EVIDENCE,
    ENWLEvidenceFeature,
    parse_geojson_file,
)

DESIGN_READINESS_CAUTION = (
    "This combined record is evidence provenance only. It does not mark the pole "
    "design-ready, does not clear conductor_spec_missing, and does not authorize "
    "per-pole conductor or span assignment without a proven DNO linking chain."
)

PROXIMITY_CANDIDATE_THRESHOLD_M = 50.0


@dataclass
class ParsedPoleNotes:
    """Structured fields extracted from `pole_notes.md`."""

    notes_path: str
    raw_text: str
    support_no: str | None = None
    pole_fid: str | None = None
    spn: str | None = None
    pole_type: str | None = None
    pole_class: str | None = None
    support_diameter: str | None = None
    coordinates: dict[str, Any] | None = None
    direct_equipment_records: list[dict[str, Any]] = field(default_factory=list)
    route_conductor_records: list[dict[str, Any]] = field(default_factory=list)
    nearby_context_records: list[dict[str, Any]] = field(default_factory=list)
    uncertainties: list[str] = field(default_factory=list)


class EvidenceCombiner:
    """Combine pole notes and ENWL trace features into one evidence record."""

    def combine(
        self,
        survey_root: str | Path,
        pole_folder_name: str,
        trace_path: str | Path,
    ) -> dict[str, Any]:
        """Build a combined evidence record for one pole folder."""
        survey_root = Path(survey_root)
        pole_dir = self._resolve_pole_dir(survey_root, pole_folder_name)
        notes_path = pole_dir / "notes" / "pole_notes.md"
        if not notes_path.exists():
            raise FileNotFoundError(f"Missing pole notes file: {notes_path}")

        parsed_notes = self.parse_pole_notes(notes_path)
        trace_dataset = parse_geojson_file(trace_path)

        direct_equipment = self._combine_direct_equipment(parsed_notes, trace_dataset.features)
        route_conductors = self._combine_route_conductors(parsed_notes, trace_dataset.features)
        nearby_context = self._combine_nearby_context(parsed_notes, trace_dataset.features)

        record = {
            "pole_id": pole_folder_name,
            "support_no": parsed_notes.support_no,
            "pole_fid": parsed_notes.pole_fid,
            "spn": parsed_notes.spn,
            "pole_type": parsed_notes.pole_type,
            "pole_class": parsed_notes.pole_class,
            "support_diameter": parsed_notes.support_diameter,
            "coordinates": parsed_notes.coordinates,
            "direct_equipment_records": direct_equipment,
            "route_conductor_evidence": route_conductors,
            "nearby_context": nearby_context,
            "evidence_quality_summary": self._quality_summary(
                parsed_notes,
                direct_equipment,
                route_conductors,
                nearby_context,
            ),
            "design_readiness_caution": DESIGN_READINESS_CAUTION,
            "contributing_files": {
                "survey_root": str(survey_root),
                "pole_folder": str(pole_dir),
                "pole_notes": str(notes_path),
                "trace_geojson": str(trace_path),
            },
            "uncertainties": parsed_notes.uncertainties,
        }
        return record

    def parse_pole_notes(self, notes_path: str | Path) -> ParsedPoleNotes:
        """Extract conservative evidence fields from a pole notes file."""
        path = Path(notes_path)
        text = path.read_text(encoding="utf-8")
        sections = _split_sections(text)

        parsed = ParsedPoleNotes(
            notes_path=str(path),
            raw_text=text,
            support_no=_extract_support_no(text),
            pole_fid=_find_first(
                text,
                r"(?:ENWL\s+pole\s+FID|Pole\s+FID):\s*([0-9]+)",
                r"ENWL\s+FID:\s*([0-9]+)",
                r"pole\s+FID\s+([0-9]+)",
                r"fid_polestructure\s+([0-9]+)",
            ),
            spn=_find_first(text, r"\bSPN:\s*([A-Za-z0-9]+)"),
            pole_type=_find_first(text, r"(?:Pole type|pole_type):\s*([^\n]+)"),
            pole_class=_find_first(text, r"(?:Pole class|pole_class):\s*([^\n]+)"),
            support_diameter=_find_first(
                text,
                r"(?:Support diameter|support_diameter):\s*([^\n]+)",
            ),
            coordinates=_extract_coordinates(text),
            uncertainties=_extract_uncertainties(sections),
        )

        for heading, body in sections:
            if _is_conductor_section(heading, body):
                record = _record_from_section(heading, body, str(path), "route_span_evidence", 3)
                if record.get("fid") or record.get("text_map"):
                    parsed.route_conductor_records.append(record)
            elif _is_nearby_context_section(heading, body):
                record = _record_from_section(heading, body, str(path), "nearby_context_only", 4)
                if record.get("fid") or record.get("feature_type"):
                    parsed.nearby_context_records.append(record)
            elif _is_equipment_section(heading, body):
                record = _record_from_section(
                    heading,
                    body,
                    str(path),
                    "direct_equipment_linked_to_pole",
                    2,
                )
                if record.get("fid"):
                    parsed.direct_equipment_records.append(record)

        return parsed

    def _resolve_pole_dir(self, survey_root: Path, pole_folder_name: str) -> Path:
        direct = survey_root / pole_folder_name
        if direct.exists():
            return direct

        clean = survey_root / "enwl_enrichment_clean" / pole_folder_name
        if clean.exists():
            return clean

        raise FileNotFoundError(
            f"Pole folder {pole_folder_name!r} not found under {survey_root} "
            "or enwl_enrichment_clean/"
        )

    def _combine_direct_equipment(
        self,
        notes: ParsedPoleNotes,
        trace_features: list[ENWLEvidenceFeature],
    ) -> list[dict[str, Any]]:
        records: dict[str, dict[str, Any]] = {
            str(record["fid"]): dict(record)
            for record in notes.direct_equipment_records
            if record.get("fid")
        }
        known_note_fids = set(records)

        for feature in trace_features:
            if feature.relationship != DIRECT_EQUIPMENT_LINKED_TO_POLE:
                continue

            explicit_pole_link = (
                notes.pole_fid is not None and feature.fid_polestructure == notes.pole_fid
            )
            known_equipment_fid = feature.feature_id in known_note_fids
            if not explicit_pole_link and not known_equipment_fid:
                continue

            feature_record = _record_from_feature(
                feature,
                "direct_equipment_linked_to_pole",
                2,
                "trace_geojson",
                "fid_polestructure_match" if explicit_pole_link else "known_equipment_fid_match",
            )
            _merge_record(records, feature_record)

        return list(records.values())

    def _combine_route_conductors(
        self,
        notes: ParsedPoleNotes,
        trace_features: list[ENWLEvidenceFeature],
    ) -> list[dict[str, Any]]:
        records: dict[str, dict[str, Any]] = {
            str(record["fid"]): dict(record)
            for record in notes.route_conductor_records
            if record.get("fid")
        }
        note_fids = set(records)

        for feature in trace_features:
            if feature.relationship != ROUTE_SPAN_EVIDENCE:
                continue

            exact_note_fid = feature.feature_id in note_fids
            distance_m = _distance_to_feature(notes.coordinates, feature)
            proximity_candidate = (
                distance_m is not None and distance_m <= PROXIMITY_CANDIDATE_THRESHOLD_M
            )

            if not exact_note_fid and not proximity_candidate:
                continue

            feature_record = _record_from_feature(
                feature,
                "route_span_evidence",
                3,
                "trace_geojson",
                "known_conductor_fid_match" if exact_note_fid else "proximity_candidate",
                distance_m=distance_m,
            )
            _merge_record(records, feature_record)

        return list(records.values())

    def _combine_nearby_context(
        self,
        notes: ParsedPoleNotes,
        trace_features: list[ENWLEvidenceFeature],
    ) -> list[dict[str, Any]]:
        records: dict[str, dict[str, Any]] = {
            str(record["fid"]): dict(record)
            for record in notes.nearby_context_records
            if record.get("fid")
        }

        for feature in trace_features:
            if feature.relationship != NEARBY_CONTEXT_ONLY:
                continue
            distance_m = _distance_to_feature(notes.coordinates, feature)
            if distance_m is None or distance_m > PROXIMITY_CANDIDATE_THRESHOLD_M:
                continue
            feature_record = _record_from_feature(
                feature,
                "nearby_context_only",
                4,
                "trace_geojson",
                "proximity_candidate",
                distance_m=distance_m,
            )
            _merge_record(records, feature_record)

        return list(records.values())

    def _quality_summary(
        self,
        notes: ParsedPoleNotes,
        direct_equipment: list[dict[str, Any]],
        route_conductors: list[dict[str, Any]],
        nearby_context: list[dict[str, Any]],
    ) -> dict[str, Any]:
        identity_complete = bool(notes.support_no and notes.pole_fid and notes.spn)
        return {
            "pole_identity": "HIGH" if identity_complete else "LOW",
            "direct_equipment": "HIGH" if direct_equipment else "NONE",
            "route_conductor": "ROUTE_ONLY" if route_conductors else "NONE",
            "nearby_context": "PRESENT" if nearby_context else "NONE",
            "direct_equipment_count": len(direct_equipment),
            "route_conductor_count": len(route_conductors),
            "nearby_context_count": len(nearby_context),
        }


def combine_pole_evidence(
    survey_root: str | Path,
    pole_folder_name: str,
    trace_path: str | Path,
) -> dict[str, Any]:
    """Convenience wrapper for combining one pole evidence record."""
    return EvidenceCombiner().combine(survey_root, pole_folder_name, trace_path)


def _extract_support_no(text: str) -> str | None:
    return _find_first(text, r"Support number:\s*([A-Za-z0-9]+)", r"Support\s+([A-Za-z0-9]+)")


def _extract_coordinates(text: str) -> dict[str, Any] | None:
    lat = _find_first(text, r"Latitude:\s*(-?[0-9.]+)")
    lon = _find_first(text, r"Longitude:\s*(-?[0-9.]+)")
    if lat and lon:
        return {"latitude": float(lat), "longitude": float(lon), "source": "pole_notes"}

    paired = _find_first(
        text,
        r"Coordinates from ENWL:\s*(-?[0-9.]+)\s*,\s*(-?[0-9.]+)",
        r"Map record screenshot:\s*(-?[0-9.]+)\s*,\s*(-?[0-9.]+)",
    )
    if paired:
        latitude, longitude = paired
        return {"latitude": float(latitude), "longitude": float(longitude), "source": "pole_notes"}

    return None


def _find_first(text: str, *patterns: str) -> Any:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        if len(match.groups()) == 1:
            return _clean(match.group(1))
        return tuple(_clean(group) for group in match.groups())
    return None


def _split_sections(text: str) -> list[tuple[str, str]]:
    matches = list(re.finditer(r"^#{2,4}\s+(.+)$", text, flags=re.MULTILINE))
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append((_clean(match.group(1)) or "", text[start:end].strip()))
    return sections


def _extract_uncertainties(sections: list[tuple[str, str]]) -> list[str]:
    for heading, body in sections:
        if "uncertainties" not in heading.lower():
            continue
        uncertainties = []
        for line in body.splitlines():
            if not line.strip().startswith("-"):
                continue
            value = line.strip("- ").strip()
            if value:
                uncertainties.append(value)
        return uncertainties
    return []


def _is_equipment_section(heading: str, body: str) -> bool:
    combined = f"{heading}\n{body}".lower()
    if "pole record" in heading.lower():
        return False
    if _is_conductor_section(heading, body) or _is_nearby_context_section(heading, body):
        return False
    equipment_tokens = (
        "switch",
        "transformer",
        "link",
        "fuse",
        "way",
        "isolator",
    )
    return "fid" in combined and any(token in combined for token in equipment_tokens)


def _is_conductor_section(heading: str, body: str) -> bool:
    combined = f"{heading}\n{body}".lower()
    return "conductor" in combined and "fid" in combined


def _is_nearby_context_section(heading: str, body: str) -> bool:
    combined = f"{heading}\n{body}".lower()
    direct_tokens = ("switch", "transformer", "link", "fuse", "way", "isolator")
    if "fid_polestructure" in combined and any(token in combined for token in direct_tokens):
        return False
    context_tokens = ("sleeve", "termination", "joint", "plant", "substation", "context")
    return "fid" in combined and any(token in combined for token in context_tokens)


def _record_from_section(
    heading: str,
    body: str,
    source_file: str,
    relationship: str,
    evidence_level: int,
) -> dict[str, Any]:
    fields = _parse_key_values(body)
    fid = fields.get("fid") or fields.get("feature_id")
    record_type = (
        fields.get("record_type")
        or fields.get("asset_type_title")
        or fields.get("switch_type")
        or fields.get("transformer_type")
        or fields.get("way_type")
        or heading
    )
    return {
        "fid": fid,
        "feature_type": record_type,
        "spn": fields.get("spn"),
        "fid_polestructure": fields.get("fid_polestructure") or fields.get("fid_pole_structure"),
        "voltage": fields.get("voltage"),
        "material": fields.get("material"),
        "cable_size": fields.get("cable_size"),
        "text_map": fields.get("text_map"),
        "rated_current": fields.get("rated_current"),
        "relationship": relationship,
        "evidence_level": evidence_level,
        "link_basis": "pole_notes_explicit_record",
        "source": "pole_notes",
        "source_file": source_file,
        "source_section": heading,
        "trace_match": False,
    }


def _record_from_feature(
    feature: ENWLEvidenceFeature,
    relationship: str,
    evidence_level: int,
    source: str,
    link_basis: str,
    distance_m: float | None = None,
) -> dict[str, Any]:
    return {
        "fid": feature.feature_id,
        "feature_type": feature.feature_type,
        "spn": feature.spn,
        "fid_polestructure": feature.fid_polestructure,
        "voltage": feature.voltage,
        "nominal_voltage": feature.nominal_voltage,
        "material": feature.material,
        "cable_size": feature.cable_size,
        "text_map": feature.text_map,
        "rated_current": feature.rated_current,
        "relationship": relationship,
        "evidence_level": evidence_level,
        "link_basis": link_basis,
        "source": source,
        "source_file": feature.metadata.get("_source_file"),
        "trace_match": True,
        "distance_m": round(distance_m, 2) if distance_m is not None else None,
    }


def _parse_key_values(body: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for line in body.splitlines():
        match = re.match(r"\s*-?\s*([A-Za-z][A-Za-z0-9_ /-]+):\s*(.+?)\s*$", line)
        if not match:
            continue
        key = _normalize_key(match.group(1))
        value = _clean(match.group(2))
        if value:
            fields[key] = value
    return fields


def _normalize_key(key: str) -> str:
    key = key.strip().lower()
    key = key.replace("/", " ")
    key = key.replace("-", " ")
    key = re.sub(r"\s+", "_", key)
    if key == "asset_type_title":
        return "asset_type_title"
    if key == "fid_pole_structure":
        return "fid_polestructure"
    return key


def _merge_record(records: dict[str, dict[str, Any]], incoming: dict[str, Any]) -> None:
    fid = incoming.get("fid")
    if not fid:
        return
    existing = records.get(str(fid))
    if existing is None:
        records[str(fid)] = incoming
        return

    for key, value in incoming.items():
        if value is None:
            continue
        if key == "source" and existing.get("source") != value:
            existing["source"] = "pole_notes+trace_geojson"
        elif key == "trace_match":
            existing["trace_match"] = bool(existing.get("trace_match") or value)
        elif existing.get(key) in (None, "", False):
            existing[key] = value


def _distance_to_feature(
    coordinates: dict[str, Any] | None,
    feature: ENWLEvidenceFeature,
) -> float | None:
    if not coordinates or not feature.geometry:
        return None
    lat = coordinates.get("latitude")
    lon = coordinates.get("longitude")
    if lat is None or lon is None:
        return None

    points = _geometry_points(feature.geometry)
    if not points:
        return None

    return min(_haversine_m(float(lat), float(lon), point[1], point[0]) for point in points)


def _geometry_points(geometry: dict[str, Any]) -> list[tuple[float, float]]:
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates")
    if not coords:
        return []
    if geom_type == "Point":
        return [tuple(coords)]
    if geom_type == "LineString":
        return [tuple(point) for point in coords]
    if geom_type == "MultiLineString":
        return [tuple(point) for line in coords for point in line]
    return []


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    radius_m = 6_371_000.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * radius_m * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"none", "null", "n/a", "not defined"}:
        return None
    return text


def record_to_jsonable(record: dict[str, Any]) -> dict[str, Any]:
    """Return a JSON-serializable combined evidence record."""
    return asdict(record) if dataclass_is_instance(record) else record


def dataclass_is_instance(value: Any) -> bool:
    return hasattr(value, "__dataclass_fields__")
