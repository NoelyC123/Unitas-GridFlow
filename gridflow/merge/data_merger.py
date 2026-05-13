"""
Data merger combining baseline, field, and matching evidence.

Produces a MergedDataset with one MergedPole per matched record.
"""

import logging
from datetime import datetime
from typing import Optional

from gridflow.baseline.models import BaselineDataset, BaselinePole
from gridflow.field.models import FieldDataset, FieldPole
from gridflow.matching.models import MatchRegister
from gridflow.merge.models import MergedDataset, MergedPole
from gridflow.merge.verification_flag_generator import VerificationFlagGenerator

logger = logging.getLogger(__name__)


class DataMerger:
    """Merge baseline, field, and matching evidence into MergedDataset."""

    def __init__(self):
        self._flag_generator = VerificationFlagGenerator()

    def merge(
        self,
        baseline: BaselineDataset,
        field: FieldDataset,
        register: MatchRegister,
    ) -> MergedDataset:
        """
        Combine all three datasets into a unified MergedDataset.

        Args:
            baseline: Parsed baseline dataset
            field: Scanned field evidence dataset
            register: Match register from matching engine

        Returns:
            MergedDataset with verification flags and design status
        """
        logger.info(
            "Merging: %d baseline, %d field, %d register entries",
            baseline.pole_count, field.total_poles, len(register.entries),
        )

        # Build lookup indexes
        b_by_support: dict[str, BaselinePole] = {
            (p.support_no or ""): p for p in baseline.poles
        }
        f_by_folder: dict[str, FieldPole] = {
            p.folder_name: p for p in field.poles
        }

        merged_poles: list[MergedPole] = []
        matched_baseline_snos: set[str] = set()
        matched_field_folders: set[str] = set()

        for entry in register.entries:
            if entry.match_type in ("UNMATCHED", "EXTRA_FIELD"):
                continue

            bp = b_by_support.get(entry.support_no)
            fp = f_by_folder.get(entry.field_folder or "")

            if bp is None:
                logger.warning("Register entry %s: baseline pole not found", entry.support_no)
                continue

            pole = self._merge_pole(bp, fp, entry)
            pole = self._flag_generator.generate_flags(pole)
            merged_poles.append(pole)

            matched_baseline_snos.add(entry.support_no)
            if fp:
                matched_field_folders.add(fp.folder_name)

        # Collect unmatched
        unmatched_baseline = [
            {"support_no": p.support_no, "easting": p.easting, "northing": p.northing}
            for p in baseline.poles
            if (p.support_no or "") not in matched_baseline_snos
        ]
        unmatched_field = [
            {"folder_name": p.folder_name, "support_no": p.support_no}
            for p in field.poles
            if p.folder_name not in matched_field_folders
        ]

        # Summary stats
        design_ready = sum(1 for p in merged_poles if p.design_ready)
        design_blocked = sum(1 for p in merged_poles if p.design_blocked)
        review_req = sum(1 for p in merged_poles if p.review_required)
        high = sum(1 for p in merged_poles if p.match_confidence == "HIGH")
        medium = sum(1 for p in merged_poles if p.match_confidence == "MEDIUM")
        low = sum(1 for p in merged_poles if p.match_confidence == "LOW")

        dataset = MergedDataset(
            baseline_source=str(baseline.metadata.get("source_file", "")),
            field_source=field.dataset_path,
            merge_date=datetime.now().isoformat(),
            total_poles_baseline=baseline.pole_count,
            total_poles_field=field.total_poles,
            total_matched=len(merged_poles),
            total_unmatched_baseline=len(unmatched_baseline),
            total_unmatched_field=len(unmatched_field),
            design_ready_count=design_ready,
            design_blocked_count=design_blocked,
            review_required_count=review_req,
            high_confidence_count=high,
            medium_confidence_count=medium,
            low_confidence_count=low,
            poles=merged_poles,
            unmatched_baseline=unmatched_baseline,
            unmatched_field=unmatched_field,
        )

        logger.info(
            "Merge complete: %d merged, %d design_ready, %d design_blocked",
            len(merged_poles), design_ready, design_blocked,
        )
        return dataset

    def _merge_pole(
        self,
        baseline_pole: BaselinePole,
        field_pole: Optional[FieldPole],
        entry,
    ) -> MergedPole:
        """
        Combine one baseline pole with its field evidence.

        Baseline is authoritative for identity and coordinates.
        Field is authoritative for current condition.
        """
        # Baseline fields (authoritative)
        bl_voltage = str(
            baseline_pole.voltage_level.value
            if hasattr(baseline_pole.voltage_level, "value")
            else baseline_pole.voltage_level or ""
        )
        bl_asset_type = str(
            baseline_pole.asset_type.value
            if hasattr(baseline_pole.asset_type, "value")
            else baseline_pole.asset_type or ""
        )
        bl_status = str(
            baseline_pole.status.value
            if hasattr(baseline_pole.status, "value")
            else baseline_pole.status or ""
        )

        # Field condition data
        condition = {}
        photo_count = 0
        photo_paths: list[str] = []
        notes_content: Optional[str] = None
        parsed_notes: dict = {}
        special_flags: list[str] = []

        if field_pole is not None:
            condition = self._extract_condition(field_pole)
            photo_count = field_pole.field_photo_count
            photo_paths = field_pole.photo_paths or []
            notes_content = field_pole.notes_content
            parsed_notes = field_pole.parsed_notes or {}
            special_flags = field_pole.special_flags or []

        # Carry forward conflict flags from register entry
        conflict_flags = list(entry.conflict_flags or [])

        return MergedPole(
            # Identity
            support_no=baseline_pole.support_no or entry.support_no,
            pole_id=baseline_pole.pole_id,
            folder_name=entry.field_folder,
            match_confidence=entry.match_confidence,
            match_type=entry.match_type,
            # Coordinates (baseline)
            easting=baseline_pole.easting,
            northing=baseline_pole.northing,
            latitude=baseline_pole.latitude,
            longitude=baseline_pole.longitude,
            route_id=baseline_pole.route_id,
            pole_sequence=baseline_pole.pole_sequence,
            # Baseline specs
            baseline_voltage=bl_voltage if bl_voltage not in ("UNKNOWN", "") else None,
            baseline_asset_type=bl_asset_type if bl_asset_type not in ("UNKNOWN", "") else None,
            baseline_status=bl_status if bl_status not in ("UNKNOWN", "") else None,
            # Field condition
            condition_overall=condition.get("condition_overall"),
            condition_base=condition.get("condition_base"),
            condition_top=condition.get("condition_top"),
            defects=condition.get("defects", []),
            access_constraints=condition.get("access_constraints"),
            equipment_observed=condition.get("equipment_observed", []),
            warning_signs_present=condition.get("warning_signs_present"),
            stay_present=condition.get("stay_present"),
            # Field evidence
            field_photo_count=photo_count,
            photo_paths=photo_paths,
            notes_content=notes_content,
            parsed_notes=parsed_notes,
            # Flags
            special_flags=special_flags,
            conflict_flags=conflict_flags,
        )

    @staticmethod
    def _extract_condition(field_pole: FieldPole) -> dict:
        """Extract condition fields from field pole parsed notes."""
        parsed = field_pole.parsed_notes or {}

        # Condition fields
        condition_overall = parsed.get("condition")

        # Try to extract base/top from free text or equipment observations
        notes = (field_pole.notes_content or "").lower()
        condition_base = None
        condition_top = None

        for line in (field_pole.notes_content or "").splitlines():
            lower = line.lower().strip()
            if lower.startswith("base:"):
                condition_base = line.split(":", 1)[1].strip()
            elif lower.startswith("top:"):
                condition_top = line.split(":", 1)[1].strip()

        # Defects
        defects = parsed.get("defects", [])

        # Access
        access_constraints = parsed.get("access")

        # Equipment
        equipment_observed = parsed.get("equipment", [])

        # Warning signs / stay from equipment list
        equipment_str = " ".join(equipment_observed).lower()
        warning_signs_present: Optional[bool] = None
        stay_present: Optional[bool] = None

        if "warning signs: present" in equipment_str or "warning signs: yes" in equipment_str:
            warning_signs_present = True
        elif "warning signs: no" in equipment_str or "warning signs: none" in equipment_str:
            warning_signs_present = False

        if "stay: yes" in equipment_str or "stay: present" in equipment_str:
            stay_present = True
        elif "stay: no" in equipment_str or "stay: none" in equipment_str:
            stay_present = False

        return {
            "condition_overall": condition_overall,
            "condition_base": condition_base,
            "condition_top": condition_top,
            "defects": defects,
            "access_constraints": access_constraints,
            "equipment_observed": equipment_observed,
            "warning_signs_present": warning_signs_present,
            "stay_present": stay_present,
        }
