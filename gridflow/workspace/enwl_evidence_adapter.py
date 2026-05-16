"""Stage 6B workspace adapter for ENWL trace and pole evidence.

Bridges the evidence combiner and trace parser to the workspace view layer.
Deliberately conservative: never modifies design_ready, conductor_spec_missing,
or any verification flags.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from gridflow.enwl_trace.parser import (
    DIRECT_EQUIPMENT_LINKED_TO_POLE,
    NEARBY_CONTEXT_ONLY,
    ROUTE_SPAN_EVIDENCE,
    ENWLEvidenceFeature,
    ENWLTraceParser,
)

CONDUCTOR_CAUTION = (
    "This conductor evidence describes the route context only. "
    "It has not been proven to apply to this specific pole or span. "
    "Do not use to clear design-readiness blockers."
)

PROVENANCE_LABEL = "From ENWL Network Asset Viewer trace"

_FID_PATTERNS = [
    re.compile(r"Pole FID:\s*(\d+)", re.IGNORECASE),
    re.compile(r"ENWL pole FID:\s*(\d+)", re.IGNORECASE),
    re.compile(r"ENWL FID:\s*(\d+)", re.IGNORECASE),
]


@dataclass
class ENWLTraceSummary:
    """Job-level trace evidence summary for the workspace overview."""

    available: bool
    trace_file_count: int = 0
    trace_file_names: list[str] = field(default_factory=list)
    total_features: int = 0
    conductor_count: int = 0
    direct_equipment_count: int = 0
    nearby_context_count: int = 0
    poles_with_direct_equipment: int = 0
    error: str | None = None


@dataclass
class ENWLPoleEvidence:
    """Per-pole ENWL evidence record for the workspace pole detail view."""

    available: bool
    pole_fid: str | None = None
    spn: str | None = None
    pole_type: str | None = None
    pole_class: str | None = None
    support_diameter: str | None = None
    direct_equipment: list[dict[str, Any]] = field(default_factory=list)
    conductors: list[dict[str, Any]] = field(default_factory=list)
    nearby_context: list[dict[str, Any]] = field(default_factory=list)
    identity_quality: str = "LOW"
    equipment_quality: str = "NONE"
    conductor_quality: str = "NONE"
    dno_badge: str = "RED"
    caution: str = CONDUCTOR_CAUTION
    provenance: str = PROVENANCE_LABEL
    error: str | None = None


def extract_enwl_fid(notes_content: str | None) -> str | None:
    """Extract ENWL pole FID from raw notes text using known label patterns."""
    if not notes_content:
        return None
    for pattern in _FID_PATTERNS:
        match = pattern.search(notes_content)
        if match:
            return match.group(1)
    return None


def load_enwl_trace_summary(job_dir: Path) -> ENWLTraceSummary:
    """Return a job-level ENWL trace evidence summary.

    Parses all *.geojson files under {job_dir}/enwl_trace/ and counts
    features by relationship category. Does not infer per-pole links.
    Returns ENWLTraceSummary(available=False) when no trace folder exists.
    """
    trace_dir = Path(job_dir) / "enwl_trace"
    if not trace_dir.exists():
        return ENWLTraceSummary(available=False)

    trace_files = sorted(trace_dir.glob("*.geojson"))
    if not trace_files:
        return ENWLTraceSummary(available=False)

    parser = ENWLTraceParser()
    total = conductor_count = equipment_count = nearby_count = 0
    pole_fids: set[str] = set()

    try:
        for path in trace_files:
            ds = parser.parse_file(path)
            total += ds.feature_count
            conductor_count += len(ds.by_relationship(ROUTE_SPAN_EVIDENCE))
            for feat in ds.by_relationship(DIRECT_EQUIPMENT_LINKED_TO_POLE):
                equipment_count += 1
                if feat.fid_polestructure:
                    pole_fids.add(feat.fid_polestructure)
            nearby_count += len(ds.by_relationship(NEARBY_CONTEXT_ONLY))

        return ENWLTraceSummary(
            available=True,
            trace_file_count=len(trace_files),
            trace_file_names=[f.name for f in trace_files],
            total_features=total,
            conductor_count=conductor_count,
            direct_equipment_count=equipment_count,
            nearby_context_count=nearby_count,
            poles_with_direct_equipment=len(pole_fids),
        )
    except Exception as exc:
        return ENWLTraceSummary(available=False, error=str(exc))


def load_enwl_pole_evidence(
    job_dir: Path,
    pole_folder_name: str | None,
    notes_content: str | None,
) -> ENWLPoleEvidence:
    """Load per-pole ENWL evidence.

    Tries two modes in order:
    1. Full combiner: if {job_dir}/enwl_enrichment_clean/{pole_folder_name} exists,
       uses EvidenceCombiner to join pole notes with each trace file.
    2. Trace-only: parses trace files and filters direct equipment by pole FID
       extracted from notes_content.

    Returns ENWLPoleEvidence(available=False) if no enwl_trace/ folder or no
    GeoJSON files are found. Never raises — errors are captured in .error.
    """
    trace_dir = Path(job_dir) / "enwl_trace"
    if not trace_dir.exists():
        return ENWLPoleEvidence(available=False)

    trace_files = sorted(trace_dir.glob("*.geojson"))
    if not trace_files:
        return ENWLPoleEvidence(available=False)

    if pole_folder_name:
        enrichment_path = Path(job_dir) / "enwl_enrichment_clean" / pole_folder_name
        if enrichment_path.exists():
            try:
                return _combine_full(job_dir, pole_folder_name, trace_files[0])
            except Exception as exc:
                return ENWLPoleEvidence(available=False, error=str(exc))

    return _combine_trace_only(trace_files, notes_content)


def _combine_full(
    job_dir: Path,
    pole_folder_name: str,
    trace_path: Path,
) -> ENWLPoleEvidence:
    """Use EvidenceCombiner for full per-pole linked evidence."""
    from gridflow.evidence_combiner import EvidenceCombiner

    record = EvidenceCombiner().combine(job_dir, pole_folder_name, trace_path)
    qs = record.get("evidence_quality_summary", {})

    return ENWLPoleEvidence(
        available=True,
        pole_fid=record.get("pole_fid"),
        spn=record.get("spn"),
        pole_type=record.get("pole_type"),
        pole_class=record.get("pole_class"),
        support_diameter=record.get("support_diameter"),
        direct_equipment=record.get("direct_equipment_records", []),
        conductors=record.get("route_conductor_evidence", []),
        nearby_context=record.get("nearby_context", []),
        identity_quality=qs.get("pole_identity", "LOW"),
        equipment_quality=qs.get("direct_equipment", "NONE"),
        conductor_quality=qs.get("route_conductor", "NONE"),
        dno_badge=_badge(qs),
    )


def _combine_trace_only(
    trace_files: list[Path],
    notes_content: str | None,
) -> ENWLPoleEvidence:
    """Route-level evidence from trace; filter direct equipment by notes pole FID."""
    pole_fid = extract_enwl_fid(notes_content)

    parser = ENWLTraceParser()
    direct_equipment: list[dict[str, Any]] = []
    conductors: list[dict[str, Any]] = []
    nearby: list[dict[str, Any]] = []

    try:
        for path in trace_files:
            ds = parser.parse_file(path)
            for feat in ds.by_relationship(DIRECT_EQUIPMENT_LINKED_TO_POLE):
                if pole_fid and feat.fid_polestructure == pole_fid:
                    direct_equipment.append(_feat_dict(feat))
            for feat in ds.by_relationship(ROUTE_SPAN_EVIDENCE):
                conductors.append(_feat_dict(feat))
            for feat in ds.by_relationship(NEARBY_CONTEXT_ONLY):
                nearby.append(_feat_dict(feat))
    except Exception as exc:
        return ENWLPoleEvidence(available=False, error=str(exc))

    identity_quality = "HIGH" if pole_fid else "LOW"
    equipment_quality = "HIGH" if direct_equipment else "NONE"
    conductor_quality = "ROUTE_ONLY" if conductors else "NONE"

    return ENWLPoleEvidence(
        available=True,
        pole_fid=pole_fid,
        direct_equipment=direct_equipment,
        conductors=conductors,
        nearby_context=nearby,
        identity_quality=identity_quality,
        equipment_quality=equipment_quality,
        conductor_quality=conductor_quality,
        dno_badge=_badge(
            {"pole_identity": identity_quality, "direct_equipment": equipment_quality}
        ),
    )


def _feat_dict(feat: ENWLEvidenceFeature) -> dict[str, Any]:
    return {
        "fid": feat.feature_id,
        "feature_type": feat.feature_type,
        "voltage": feat.voltage,
        "material": feat.material,
        "cable_size": feat.cable_size,
        "text_map": feat.text_map,
        "rated_current": feat.rated_current,
        "fid_polestructure": feat.fid_polestructure,
        "spn": feat.spn,
        "relationship": feat.relationship,
    }


def _badge(quality_summary: dict[str, Any]) -> str:
    """Return GREEN / AMBER based on per-pole evidence quality.

    GREEN: confirmed pole identity AND direct equipment linked via fid_polestructure.
    AMBER: pole identity confirmed but no direct equipment link yet.
    """
    if quality_summary.get("direct_equipment") == "HIGH":
        return "GREEN"
    return "AMBER"
