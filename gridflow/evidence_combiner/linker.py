"""Formal pole-to-ENWL linking for Stage 6C.

This module evaluates linking methods conservatively and does not alter
design-readiness or any verification flags.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from gridflow.evidence_combiner.combiner import combine_pole_evidence


@dataclass
class LinkingResult:
    """Formal linking outcome for one pole folder."""

    pole_id: str
    support_no: str | None
    pole_fid: str | None
    linking_method: str
    confidence: str
    matched_enwl_fid: str | None
    evidence_source: str
    manual_confirmation_required: bool
    distance_m: float | None
    notes: str
    matched_methods: list[str]
    direct_equipment_fids: list[str]
    matched_support_no: str | None = None
    matched_spn: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def link_pole(
    survey_root: str | Path, pole_folder_name: str, trace_path: str | Path
) -> LinkingResult:
    """Link one pole using Stage 6C priority rules."""
    combined = combine_pole_evidence(survey_root, pole_folder_name, trace_path)
    return _link_from_combined(combined)


def link_survey(survey_root: str | Path, trace_path: str | Path) -> list[LinkingResult]:
    """Link all pole folders in a survey root."""
    survey_root = Path(survey_root)
    pole_root = survey_root / "enwl_enrichment_clean"
    if not pole_root.exists():
        raise FileNotFoundError(f"Survey evidence folder not found: {pole_root}")

    pole_folders = sorted(
        [path.name for path in pole_root.iterdir() if path.is_dir() and "_SUPPORT_" in path.name],
        key=_pole_sort_key,
    )
    return [link_pole(survey_root, pole, trace_path) for pole in pole_folders]


def _link_from_combined(combined: dict[str, Any]) -> LinkingResult:
    support_no = combined.get("support_no")
    pole_fid = combined.get("pole_fid")
    spn = combined.get("spn")

    matched_methods: list[str] = []
    notes_parts: list[str] = []
    distance_m: float | None = None

    direct_equipment = combined.get("direct_equipment_records", [])
    direct_equipment_fids = [record.get("fid") for record in direct_equipment if record.get("fid")]

    # 1) fid_polestructure match -> HIGH
    has_fid_polestructure_match = any(
        record.get("fid_polestructure") == pole_fid and pole_fid is not None
        for record in direct_equipment
    )
    if has_fid_polestructure_match:
        matched_methods.append("fid_polestructure")
        notes_parts.append("Direct equipment fid_polestructure matches pole_fid.")

    # 2) support_no match -> MEDIUM
    if support_no and pole_fid:
        matched_methods.append("support_no")
        notes_parts.append("Support number present with confirmed ENWL pole FID in notes.")

    # 3) SPN match -> MEDIUM
    if spn and pole_fid:
        matched_methods.append("spn")
        notes_parts.append("SPN present with confirmed ENWL pole FID in notes.")

    # 4) GPS proximity (<20m) -> LOW / manual required if no stronger method
    proximity_distances = []
    for bucket in ("route_conductor_evidence", "nearby_context"):
        for record in combined.get(bucket, []):
            d = record.get("distance_m")
            if isinstance(d, (int, float)):
                proximity_distances.append(float(d))
    if proximity_distances:
        candidate_distance = min(proximity_distances)
        if candidate_distance < 20.0:
            matched_methods.append("gps_proximity")
            distance_m = round(candidate_distance, 2)
            notes_parts.append("GPS proximity candidate under 20m.")

    if "fid_polestructure" in matched_methods:
        linking_method = "fid_polestructure"
        confidence = "HIGH"
        manual = False
    elif "support_no" in matched_methods:
        linking_method = "support_no"
        confidence = "MEDIUM"
        manual = False
    elif "spn" in matched_methods:
        linking_method = "spn"
        confidence = "MEDIUM"
        manual = False
    elif "gps_proximity" in matched_methods:
        linking_method = "gps_proximity"
        confidence = "LOW"
        manual = True
    else:
        linking_method = "manual"
        confidence = "NONE"
        manual = True
        notes_parts.append("No formal linking method matched; manual confirmation required.")

    return LinkingResult(
        pole_id=combined.get("pole_id") or "",
        support_no=support_no,
        pole_fid=pole_fid,
        linking_method=linking_method,
        confidence=confidence,
        matched_enwl_fid=pole_fid,
        evidence_source="pole_notes+trace_geojson",
        manual_confirmation_required=manual,
        distance_m=distance_m if linking_method == "gps_proximity" else None,
        notes=" ".join(notes_parts).strip(),
        matched_methods=matched_methods,
        direct_equipment_fids=direct_equipment_fids,
        matched_support_no=support_no if "support_no" in matched_methods else None,
        matched_spn=spn if "spn" in matched_methods else None,
    )


def _pole_sort_key(pole_id: str) -> tuple[int, str]:
    prefix = pole_id.split("_", 1)[0]
    return (int(prefix) if prefix.isdigit() else 999, pole_id)
