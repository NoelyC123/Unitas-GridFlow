"""Stage 6E conservative design-readiness assessment."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from gridflow.conflict_detector import ConflictDetector, ConflictResult
from gridflow.evidence_combiner import combine_pole_evidence, link_pole


@dataclass
class ReadinessResult:
    pole_id: str
    support_no: str | None
    design_ready: bool
    readiness_status: str
    readiness_confidence: str
    readiness_reason: str
    readiness_blockers: list[str]
    readiness_warnings: list[str]
    evidence_basis: list[str]
    linking_confidence: str
    conflict_count: int
    critical_conflicts: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ReadinessAssessor:
    """Assess conservative design readiness from combined evidence, linking, and conflicts."""

    def __init__(self) -> None:
        self._conflict_detector = ConflictDetector()

    def assess_survey(
        self, survey_root: str | Path, trace_path: str | Path
    ) -> list[ReadinessResult]:
        survey_root = Path(survey_root)
        pole_root = survey_root / "enwl_enrichment_clean"
        if not pole_root.exists():
            raise FileNotFoundError(f"Survey evidence folder not found: {pole_root}")

        pole_folders = sorted(
            [
                path.name
                for path in pole_root.iterdir()
                if path.is_dir() and "_SUPPORT_" in path.name
            ],
            key=_pole_sort_key,
        )
        return [self.assess_pole(survey_root, pole, trace_path) for pole in pole_folders]

    def assess_pole(
        self, survey_root: str | Path, pole_folder_name: str, trace_path: str | Path
    ) -> ReadinessResult:
        combined = combine_pole_evidence(survey_root, pole_folder_name, trace_path)
        linking = link_pole(survey_root, pole_folder_name, trace_path)
        conflicts = self._conflict_detector.detect_pole(survey_root, pole_folder_name, trace_path)
        return self.assess_from_records(combined, linking, conflicts)

    def assess_from_records(
        self,
        combined: dict[str, Any],
        linking: Any,
        conflicts: list[ConflictResult],
    ) -> ReadinessResult:
        pole_id = combined.get("pole_id") or ""
        support_no = combined.get("support_no")
        blockers: list[str] = []
        warnings: list[str] = []
        critical_conflicts = sum(1 for conflict in conflicts if conflict.severity == "CRITICAL")

        notes_path = Path(combined.get("contributing_files", {}).get("pole_notes", ""))
        pole_folder = Path(combined.get("contributing_files", {}).get("pole_folder", ""))
        missing_identity = []
        for field_name in ("support_no", "pole_fid", "spn"):
            if not combined.get(field_name):
                missing_identity.append(field_name)

        if not notes_path.exists():
            blockers.append("Pole notes missing")
        photo_count = _count_images(pole_folder / "field_photos")
        if photo_count < 3:
            blockers.append("Required field photo evidence missing")

        if missing_identity:
            blockers.append(
                "Missing required identity fields: " + ", ".join(sorted(missing_identity))
            )

        if getattr(linking, "confidence", "NONE") in {"NONE", "LOW"} or getattr(
            linking, "manual_confirmation_required", True
        ):
            blockers.append(
                f"Linking confidence insufficient ({getattr(linking, 'confidence', 'NONE')})"
            )

        for conflict in conflicts:
            if conflict.severity == "CRITICAL":
                blockers.append(f"Stage 6D CRITICAL conflict: {conflict.description}")
            elif conflict.severity == "WARNING":
                warnings.append(f"Stage 6D WARNING: {conflict.description}")
            elif conflict.severity == "INFO":
                warnings.append(f"Stage 6D INFO: {conflict.description}")

        route_conductors = combined.get("route_conductor_evidence", [])
        direct_equipment = combined.get("direct_equipment_records", [])
        nearby_context = combined.get("nearby_context", [])
        has_route_conductor = bool(route_conductors)
        has_span_confirmed_conductor = any(
            record.get("span_confirmed") is True
            or record.get("link_basis") == "span_link_confirmed"
            or record.get("relationship") == "span_confirmed"
            for record in route_conductors
        )
        has_direct_equipment = bool(direct_equipment)
        route_context_ambiguous = (
            has_route_conductor
            and not has_span_confirmed_conductor
            and bool(nearby_context)
            and not has_direct_equipment
        )

        if not has_route_conductor:
            blockers.append("No conductor evidence present")
        elif not has_span_confirmed_conductor:
            warnings.append("Conductor evidence route-level only — span confirmation not proven")
            if route_context_ambiguous:
                blockers.append(
                    "Route conductor context unresolved — nearby transition/context records need manual review"
                )

        pole_class = combined.get("pole_class")
        if not pole_class:
            blockers.append("Pole class/strength rating not confirmed from ENWL or field notes")

        if getattr(linking, "linking_method", "") == "gps_proximity":
            warnings.append("GPS proximity is corroborating only — not sufficient as sole proof")

        evidence_basis = _evidence_basis(combined, linking, conflicts, photo_count)

        if (
            missing_identity
            or not notes_path.exists()
            or getattr(linking, "confidence", "NONE")
            in {
                "NONE",
                "LOW",
            }
        ):
            status = "insufficient_evidence"
            reason = "Support identity or evidence completeness is insufficient for readiness."
        elif critical_conflicts > 0 or any(
            blocker == "No conductor evidence present"
            or blocker.startswith("Required field photo evidence")
            or blocker.startswith("Pole class")
            or blocker.startswith("Route conductor context unresolved")
            for blocker in blockers
        ):
            status = "not_ready"
            reason = "Critical readiness requirements are not satisfied."
        elif has_span_confirmed_conductor:
            status = "ready"
            reason = (
                "Identity is linked, conflicts are clear, and conductor evidence is span-confirmed."
            )
        else:
            status = "review_required"
            reason = "Identity is linked, but conductor evidence remains route-level only."

        design_ready = status == "ready"
        readiness_confidence = _readiness_confidence(getattr(linking, "confidence", "NONE"), status)

        if status == "review_required":
            blockers = [b for b in blockers if b != "No conductor evidence present"]
        if status == "ready":
            blockers = []

        return ReadinessResult(
            pole_id=pole_id,
            support_no=support_no,
            design_ready=design_ready,
            readiness_status=status,
            readiness_confidence=readiness_confidence,
            readiness_reason=reason,
            readiness_blockers=blockers,
            readiness_warnings=warnings,
            evidence_basis=evidence_basis,
            linking_confidence=str(getattr(linking, "confidence", "NONE")).lower(),
            conflict_count=len(conflicts),
            critical_conflicts=critical_conflicts,
        )


def _count_images(folder: Path) -> int:
    if not folder.exists():
        return 0
    return sum(
        1
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png", ".heic", ".webp"}
    )


def _evidence_basis(
    combined: dict[str, Any], linking: Any, conflicts: list[ConflictResult], photo_count: int
) -> list[str]:
    basis = ["field_notes", "enwl_linking", "conflict_detection"]
    if photo_count >= 3:
        basis.append("field_photos")
    if combined.get("direct_equipment_records"):
        basis.append("direct_equipment_evidence")
    if combined.get("route_conductor_evidence"):
        basis.append("route_conductor_evidence")
    if combined.get("nearby_context"):
        basis.append("nearby_context")
    if getattr(linking, "linking_method", ""):
        basis.append(f"link_method:{linking.linking_method}")
    if conflicts:
        basis.append("conflicts_present")
    return basis


def _readiness_confidence(linking_confidence: str, status: str) -> str:
    normalized = (linking_confidence or "NONE").upper()
    if normalized == "HIGH" and status in {"ready", "review_required"}:
        return "high"
    if normalized == "MEDIUM" and status in {"ready", "review_required", "not_ready"}:
        return "medium"
    if normalized == "LOW":
        return "low"
    return "none"


def _pole_sort_key(pole_id: str) -> tuple[int, str]:
    prefix = pole_id.split("_", 1)[0]
    return (int(prefix) if prefix.isdigit() else 999, pole_id)
