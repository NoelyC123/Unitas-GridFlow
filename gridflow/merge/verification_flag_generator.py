"""
Verification flag generator for merged poles.

Applies DNO/engineering spec verification requirements based on
what is and isn't available in the merged evidence.
"""

import logging
from gridflow.merge.models import MergedPole

logger = logging.getLogger(__name__)

# Keywords that trigger condition_verification_required
SEVERE_DEFECT_KEYWORDS = {
    "severe", "rot", "crack", "split", "lean", "damage",
    "fail", "unsafe", "broken", "shattered", "subsidence",
}

DESIGNER_ACTION_TEMPLATES = {
    "voltage": "Obtain DNO-certified voltage specification",
    "conductor": "Obtain DNO conductor specification (size, type, material)",
    "pole_class": "Obtain DNO pole class and strength rating",
    "condition": "Obtain DNO re-inspection (severe defects observed in field)",
    "identity": "Confirm pole identity with DNO (match confidence < HIGH)",
    "equipment": "Resolve equipment conflict: field observation differs from baseline record",
}


class VerificationFlagGenerator:
    """Generate verification flags and designer actions for a MergedPole."""

    def generate_flags(self, merged_pole: MergedPole) -> MergedPole:
        """
        Set all verification flags on merged_pole and return updated pole.

        Also populates designer_actions, design_blocked, and design_ready.
        """
        merged_pole.voltage_verification_required = self._check_voltage_verification(merged_pole)
        merged_pole.conductor_verification_required = self._check_conductor_verification(merged_pole)
        merged_pole.pole_class_verification_required = self._check_pole_class_verification(merged_pole)
        merged_pole.condition_verification_required = self._check_condition_verification(merged_pole)
        merged_pole.identity_verification_required = self._check_identity_verification(merged_pole)
        merged_pole.equipment_conflict_flag = self._detect_equipment_conflict(merged_pole)

        blocked, ready = self._compute_design_status(merged_pole)
        merged_pole.design_blocked = blocked
        merged_pole.design_ready = ready
        merged_pole.review_required = merged_pole.match_confidence in ("MEDIUM", "LOW", "UNMATCHED")

        merged_pole.designer_actions = self._compute_designer_actions(merged_pole)

        logger.debug(
            "Flags for %s: voltage=%s conductor=%s pole_class=%s condition=%s identity=%s blocked=%s",
            merged_pole.support_no,
            merged_pole.voltage_verification_required,
            merged_pole.conductor_verification_required,
            merged_pole.pole_class_verification_required,
            merged_pole.condition_verification_required,
            merged_pole.identity_verification_required,
            merged_pole.design_blocked,
        )
        return merged_pole

    @staticmethod
    def _check_voltage_verification(pole: MergedPole) -> bool:
        """True if no authoritative baseline voltage is available."""
        if not pole.baseline_voltage:
            return True
        v = str(pole.baseline_voltage).upper().strip()
        return v in ("", "UNKNOWN", "NONE", "NULL")

    @staticmethod
    def _check_conductor_verification(_pole: MergedPole) -> bool:
        """Always True — conductor spec requires DNO data records."""
        return True

    @staticmethod
    def _check_pole_class_verification(_pole: MergedPole) -> bool:
        """Always True — pole class requires DNO data records."""
        return True

    @staticmethod
    def _check_condition_verification(pole: MergedPole) -> bool:
        """
        True if parsed defects list contains keywords indicating severe damage.

        Only checks the structured defects list — not raw notes — to avoid
        false positives from negated observations like "no rot visible".
        """
        if not pole.defects:
            return False
        defects_str = " ".join(pole.defects).lower()
        return any(kw in defects_str for kw in SEVERE_DEFECT_KEYWORDS)

    @staticmethod
    def _check_identity_verification(pole: MergedPole) -> bool:
        """True if match confidence is anything other than HIGH."""
        return pole.match_confidence != "HIGH"

    @staticmethod
    def _detect_equipment_conflict(pole: MergedPole) -> bool:
        """True if EQUIPMENT_CONFLICT or VOLTAGE_CONFLICT flagged by matcher."""
        return (
            "EQUIPMENT_CONFLICT" in pole.conflict_flags
            or "VOLTAGE_CONFLICT" in pole.conflict_flags
        )

    @staticmethod
    def _compute_design_status(pole: MergedPole) -> tuple[bool, bool]:
        """
        Compute (design_blocked, design_ready).

        design_blocked: any required verification flag is set
        design_ready: not blocked AND HIGH confidence
        """
        design_blocked = (
            pole.voltage_verification_required
            or pole.conductor_verification_required
            or pole.pole_class_verification_required
            or pole.identity_verification_required
            or pole.condition_verification_required
        )
        design_ready = not design_blocked and pole.match_confidence == "HIGH"
        return design_blocked, design_ready

    @staticmethod
    def _compute_designer_actions(pole: MergedPole) -> list[str]:
        """Build specific ordered list of actions needed before design."""
        actions = []
        if pole.voltage_verification_required:
            actions.append(DESIGNER_ACTION_TEMPLATES["voltage"])
        if pole.conductor_verification_required:
            actions.append(DESIGNER_ACTION_TEMPLATES["conductor"])
        if pole.pole_class_verification_required:
            actions.append(DESIGNER_ACTION_TEMPLATES["pole_class"])
        if pole.condition_verification_required:
            actions.append(DESIGNER_ACTION_TEMPLATES["condition"])
        if pole.identity_verification_required:
            actions.append(DESIGNER_ACTION_TEMPLATES["identity"])
        if pole.equipment_conflict_flag:
            actions.append(DESIGNER_ACTION_TEMPLATES["equipment"])
        return actions
