"""
Conflict detection between baseline and field evidence.

Detects true contradictions — not normal baseline omissions.
"""

import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Keywords indicating HV/transformer presence in field notes
HV_KEYWORDS = {"transformer", "11kv", "33kv", "hv", "high voltage"}
LV_KEYWORDS = {"lv", "low voltage", "streetlight", "service"}


class ConflictDetector:
    """Detect data conflicts between baseline and field evidence poles."""

    def detect(self, baseline_pole, field_pole) -> list[str]:
        """
        Run all conflict checks and return list of conflict flag strings.

        Args:
            baseline_pole: BaselinePole from baseline dataset
            field_pole: FieldPole from field dataset

        Returns:
            List of conflict strings e.g. ["VOLTAGE_CONFLICT"]
        """
        conflicts = []

        for check in (
            self._check_voltage_conflict,
            self._check_equipment_conflict,
            self._check_support_no_conflict,
        ):
            result = check(baseline_pole, field_pole)
            if result:
                conflicts.append(result)

        return conflicts

    @staticmethod
    def _check_voltage_conflict(baseline_pole, field_pole) -> Optional[str]:
        """Flag if baseline voltage directly contradicts field notes voltage."""
        bl_voltage = str(
            baseline_pole.voltage_level.value
            if hasattr(baseline_pole.voltage_level, "value")
            else baseline_pole.voltage_level or ""
        ).upper()

        if bl_voltage in ("UNKNOWN", ""):
            return None

        notes_voltage = (field_pole.parsed_notes or {}).get("voltage", "")
        if not notes_voltage:
            return None

        nv = notes_voltage.strip().upper()
        # Only flag when one clearly says LV and the other says HV
        if bl_voltage == "LV" and nv in ("HV", "11KV", "33KV", "EHV"):
            return "VOLTAGE_CONFLICT"
        if bl_voltage in ("HV", "EHV") and nv in ("LV", "400V"):
            return "VOLTAGE_CONFLICT"

        return None

    @staticmethod
    def _check_equipment_conflict(baseline_pole, field_pole) -> Optional[str]:
        """
        Flag if baseline type contradicts observed field equipment.

        Only flag true contradictions (e.g. baseline=POLE but
        field explicitly observes transformer).
        """
        bl_type = str(
            baseline_pole.asset_type.value
            if hasattr(baseline_pole.asset_type, "value")
            else baseline_pole.asset_type or ""
        ).upper()

        if bl_type not in ("POLE",):
            return None

        # Check equipment observed in field
        parsed = field_pole.parsed_notes or {}
        equipment = parsed.get("equipment", [])
        equipment_str = " ".join(equipment).lower() if equipment else ""

        notes_content = (field_pole.notes_content or "").lower()

        combined = equipment_str + " " + notes_content

        # Transformer contradiction: baseline is a plain POLE but field explicitly
        # confirms transformer attached (not just "transformer: No")
        has_transformer = (
            "transformer: yes" in combined
            or re.search(r"transformer[:\s]+present", combined) is not None
        )

        if has_transformer:
            return "EQUIPMENT_CONFLICT"

        return None

    @staticmethod
    def _check_support_no_conflict(baseline_pole, field_pole) -> Optional[str]:
        """
        Flag if field parsed_notes support_no contradicts baseline support_no.

        Only flag when both are present, both have digits, and they differ.
        """
        baseline_sno = baseline_pole.support_no or ""
        notes_sno = (field_pole.parsed_notes or {}).get("support_no", "")

        if not notes_sno:
            return None

        # Compare numeric portions only
        b_digits = re.sub(r"[^0-9]", "", baseline_sno)
        n_digits = re.sub(r"[^0-9]", "", str(notes_sno).strip())

        if b_digits and n_digits and b_digits != n_digits:
            return "SUPPORT_NO_CONFLICT"

        return None
