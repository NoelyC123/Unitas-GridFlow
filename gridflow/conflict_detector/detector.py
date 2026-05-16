"""Stage 6D read-only conflict detection across field, ENWL, and trace evidence."""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from gridflow.enwl_trace import DIRECT_POLE_IDENTITY, parse_geojson_file
from gridflow.evidence_combiner.combiner import combine_pole_evidence


@dataclass
class ConflictResult:
    pole_id: str
    conflict_type: str
    severity: str
    field_value: str | None
    enwl_value: str | None
    trace_value: str | None
    description: str
    recommended_action: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ConflictDetector:
    """Detect conservative evidence conflicts without changing any readiness logic."""

    def detect_survey(
        self, survey_root: str | Path, trace_path: str | Path
    ) -> dict[str, list[ConflictResult]]:
        survey_root = Path(survey_root)
        pole_root = survey_root / "enwl_enrichment_clean"
        if not pole_root.exists():
            raise FileNotFoundError(f"Survey evidence folder not found: {pole_root}")

        poles = sorted(
            [p.name for p in pole_root.iterdir() if p.is_dir() and "_SUPPORT_" in p.name],
            key=_pole_sort_key,
        )
        return {pole: self.detect_pole(survey_root, pole, trace_path) for pole in poles}

    def detect_pole(
        self, survey_root: str | Path, pole_folder_name: str, trace_path: str | Path
    ) -> list[ConflictResult]:
        combined = combine_pole_evidence(survey_root, pole_folder_name, trace_path)
        dataset = parse_geojson_file(trace_path)
        notes_text = _load_notes_text(survey_root, pole_folder_name)

        support_no = combined.get("support_no")
        pole_fid = combined.get("pole_fid")
        spn = combined.get("spn")
        field_coords = combined.get("coordinates") or {}
        conflicts: list[ConflictResult] = []

        pole_feature = _match_pole_feature(dataset.features, support_no, pole_fid, spn)
        enwl_support = pole_feature.support_no if pole_feature else None
        enwl_pole_type = pole_feature.pole_type if pole_feature else None
        enwl_coords = _feature_coordinates(pole_feature.geometry if pole_feature else None)

        field_support_visible = _extract_field_visible_support(notes_text)
        field_pole_type = _extract_field_pole_type(notes_text)
        field_equipment_present = _field_equipment_present(notes_text, combined)
        field_no_equipment = _field_no_equipment(notes_text)

        direct_pole_linked_equipment = [
            record
            for record in combined.get("direct_equipment_records", [])
            if pole_fid and record.get("fid_polestructure") == pole_fid
        ]

        # A) Pole type mismatch
        if field_pole_type and enwl_pole_type and _norm(field_pole_type) != _norm(enwl_pole_type):
            conflicts.append(
                ConflictResult(
                    pole_id=pole_folder_name,
                    conflict_type="pole_type_mismatch",
                    severity="WARNING",
                    field_value=field_pole_type,
                    enwl_value=enwl_pole_type,
                    trace_value=pole_feature.feature_id if pole_feature else None,
                    description="Field-observed pole type differs from ENWL pole record.",
                    recommended_action="Verify using field photos and ENWL asset popup.",
                )
            )

        # B) Equipment mismatch
        if direct_pole_linked_equipment and field_no_equipment:
            conflicts.append(
                ConflictResult(
                    pole_id=pole_folder_name,
                    conflict_type="equipment_mismatch",
                    severity="CRITICAL",
                    field_value="No equipment observed",
                    enwl_value="Equipment records present",
                    trace_value=", ".join(
                        str(record.get("fid"))
                        for record in direct_pole_linked_equipment
                        if record.get("fid")
                    ),
                    description="ENWL links equipment to this pole but field notes indicate none observed.",
                    recommended_action="Re-check pole photos and confirm equipment state with DNO.",
                )
            )
        if field_equipment_present and not direct_pole_linked_equipment:
            conflicts.append(
                ConflictResult(
                    pole_id=pole_folder_name,
                    conflict_type="equipment_mismatch",
                    severity="CRITICAL",
                    field_value="Equipment observed in field notes",
                    enwl_value="No direct equipment link via fid_polestructure",
                    trace_value=None,
                    description="Field evidence indicates equipment but ENWL has no direct equipment link for this pole.",
                    recommended_action="Confirm pole identity and request DNO equipment linkage check.",
                )
            )

        # C) Coordinate mismatch >50m
        if field_coords and enwl_coords:
            dist = _haversine_m(
                float(field_coords["latitude"]),
                float(field_coords["longitude"]),
                enwl_coords[0],
                enwl_coords[1],
            )
            if dist > 50.0:
                conflicts.append(
                    ConflictResult(
                        pole_id=pole_folder_name,
                        conflict_type="coordinate_mismatch",
                        severity="WARNING",
                        field_value=f"{field_coords['latitude']},{field_coords['longitude']}",
                        enwl_value=f"{enwl_coords[0]},{enwl_coords[1]}",
                        trace_value=f"{dist:.1f}m",
                        description="Field GPS and ENWL pole coordinates differ by more than 50m.",
                        recommended_action="Verify pole match and GPS capture; check route context.",
                    )
                )

        # D) Support number mismatch (field-visible vs ENWL)
        if (
            field_support_visible
            and enwl_support
            and _norm(field_support_visible) != _norm(enwl_support)
        ):
            conflicts.append(
                ConflictResult(
                    pole_id=pole_folder_name,
                    conflict_type="support_no_mismatch",
                    severity="CRITICAL",
                    field_value=field_support_visible,
                    enwl_value=enwl_support,
                    trace_value=pole_feature.feature_id if pole_feature else None,
                    description="Visible field support number differs from ENWL support number.",
                    recommended_action="Stop and verify pole identity before design use.",
                )
            )

        # E) Missing evidence gaps
        trace_has_conductor_spec = any(
            (f.material or f.cable_size or f.text_map)
            for f in dataset.features
            if "conductor" in (f.feature_type or "").lower()
        )
        notes_has_conductor_observation = _notes_have_conductor_observation(notes_text)
        if trace_has_conductor_spec and not notes_has_conductor_observation:
            conflicts.append(
                ConflictResult(
                    pole_id=pole_folder_name,
                    conflict_type="missing_field_evidence",
                    severity="INFO",
                    field_value="No conductor observation in notes",
                    enwl_value="Conductor route/spec records present",
                    trace_value=None,
                    description="ENWL has conductor evidence but field notes do not record conductor observations.",
                    recommended_action="Add field conductor observation notes where available.",
                )
            )

        if field_equipment_present and not direct_pole_linked_equipment:
            conflicts.append(
                ConflictResult(
                    pole_id=pole_folder_name,
                    conflict_type="missing_enwl_evidence",
                    severity="INFO",
                    field_value="Field equipment observation present",
                    enwl_value="No matching ENWL equipment record",
                    trace_value=None,
                    description="Field notes mention equipment but no ENWL direct equipment link was found.",
                    recommended_action="Request DNO record confirmation or update for equipment linkage.",
                )
            )

        return conflicts


def _load_notes_text(survey_root: str | Path, pole_folder_name: str) -> str:
    path = (
        Path(survey_root) / "enwl_enrichment_clean" / pole_folder_name / "notes" / "pole_notes.md"
    )
    return path.read_text(encoding="utf-8")


def _match_pole_feature(features, support_no: str | None, pole_fid: str | None, spn: str | None):
    pole_features = [f for f in features if f.relationship == DIRECT_POLE_IDENTITY]
    if pole_fid:
        match = next((f for f in pole_features if f.feature_id == pole_fid), None)
        if match:
            return match
    if support_no:
        match = next((f for f in pole_features if _norm(f.support_no) == _norm(support_no)), None)
        if match:
            return match
    if spn:
        match = next((f for f in pole_features if _norm(f.spn) == _norm(spn)), None)
        if match:
            return match
    return pole_features[0] if pole_features else None


def _feature_coordinates(geometry: dict[str, Any] | None) -> tuple[float, float] | None:
    if not geometry:
        return None
    coords = geometry.get("coordinates")
    if geometry.get("type") == "Point" and isinstance(coords, list) and len(coords) >= 2:
        lon, lat = coords[0], coords[1]
        return float(lat), float(lon)
    return None


def _extract_field_visible_support(text: str) -> str | None:
    patterns = (
        r"(?:field\s+visible\s+plate|visible\s+plate|field\s+support\s+number)\s*:\s*([A-Za-z0-9]+)",
        r"support\s+plate\s*:\s*([A-Za-z0-9]+)",
    )
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _extract_field_pole_type(text: str) -> str | None:
    patterns = (
        r"(?:field\s+pole\s+type|field\s+type|observed\s+pole\s+type)\s*:\s*([^\n]+)",
        r"field\s+observation.*?type\s*:\s*([^\n]+)",
    )
    for p in patterns:
        m = re.search(p, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None


def _field_equipment_present(text: str, combined: dict[str, Any]) -> bool:
    if any(
        "pole_notes" in str(record.get("source", ""))
        for record in combined.get("direct_equipment_records", [])
    ):
        return True
    patterns = (
        r"transformer\s*:\s*(yes|present)",
        r"switch\s*:\s*(yes|present)",
        r"equipment\s*:\s*(yes|present)",
    )
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)


def _field_no_equipment(text: str) -> bool:
    patterns = (
        r"no\s+equipment\s+observed",
        r"equipment\s*:\s*(none|no)",
        r"transformer\s*:\s*no",
        r"switch\s*:\s*no",
    )
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)


def _notes_have_conductor_observation(text: str) -> bool:
    return bool(re.search(r"conductor|text_map|cable_size|material", text, flags=re.IGNORECASE))


def _norm(value: str | None) -> str:
    if value is None:
        return ""
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def _pole_sort_key(pole_id: str) -> tuple[int, str]:
    prefix = pole_id.split("_", 1)[0]
    return (int(prefix) if prefix.isdigit() else 999, pole_id)


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
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return radius_m * c
