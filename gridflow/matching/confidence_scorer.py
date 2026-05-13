"""
Confidence scoring for matched baseline-to-field pole pairs.

Scores each MatchResult based on evidence quality, special flags,
and potential data conflicts.
"""

import logging
from typing import Optional

from gridflow.baseline.models import BaselinePole
from gridflow.field.models import FieldPole
from gridflow.matching.models import MatchRegister, MatchResult

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    """Score and enrich MatchResult objects with confidence and conflicts."""

    def score(
        self,
        match_result: MatchResult,
        baseline_pole: BaselinePole,
        field_pole: Optional[FieldPole],
    ) -> MatchResult:
        """
        Assign confidence and detect conflicts for a single match.

        HIGH: EXACT + field HIGH evidence + no conflict flags
        MEDIUM: EXACT + (MEDIUM evidence OR VARIANT_SUPPORT_NO OR NO_POLE_POPUP)
        LOW: not EXACT OR field LOW evidence
        UNMATCHED: no field pole found
        """
        if match_result.match_type == "UNMATCHED" or field_pole is None:
            match_result.match_confidence = "UNMATCHED"
            match_result.review_required = True
            return match_result

        reasons = list(match_result.confidence_reasons)
        conflicts = list(match_result.conflict_flags)

        # Detect conflicts
        self._detect_conflicts(match_result, baseline_pole, field_pole, conflicts)
        match_result.conflict_flags = conflicts

        has_variant = "VARIANT_SUPPORT_NO" in (field_pole.special_flags or [])
        no_popup = "NO_POLE_POPUP" in (field_pole.special_flags or [])
        is_exact = match_result.match_type == "EXACT"
        ev_quality = field_pole.evidence_quality

        if is_exact and ev_quality == "HIGH" and not conflicts:
            confidence = "HIGH"
        elif is_exact and (ev_quality == "MEDIUM" or has_variant or no_popup):
            confidence = "MEDIUM"
            if has_variant:
                reasons.append("VARIANT_SUPPORT_NO")
            if no_popup:
                reasons.append("NO_POLE_POPUP")
        else:
            confidence = "LOW"

        match_result.match_confidence = confidence
        match_result.confidence_reasons = reasons
        match_result.review_required = confidence in ("LOW", "MEDIUM") or bool(conflicts)
        return match_result

    def score_register(
        self,
        register: MatchRegister,
        baseline,
        field,
    ) -> MatchRegister:
        """Apply scoring to all entries and recompute statistics."""
        b_by_id = {p.pole_id: p for p in baseline.poles}
        f_by_folder = {p.folder_name: p for p in field.poles}

        for entry in register.entries:
            bp = b_by_id.get(entry.baseline_pole_id or "")
            fp = f_by_folder.get(entry.field_folder or "")

            if bp is None:
                continue

            # Build minimal MatchResult to score
            mr = MatchResult(
                baseline_pole_id=entry.baseline_pole_id or "",
                baseline_support_no=entry.support_no,
                field_folder=entry.field_folder,
                field_support_no=fp.support_no if fp else None,
                match_type=entry.match_type,
                conflict_flags=entry.conflict_flags,
            )
            scored = self.score(mr, bp, fp)
            entry.match_confidence = scored.match_confidence
            entry.conflict_flags = scored.conflict_flags
            entry.review_required = scored.review_required

        register.compute_stats()
        return register

    @staticmethod
    def _detect_conflicts(
        match_result: MatchResult,
        baseline_pole: BaselinePole,
        field_pole: FieldPole,
        conflicts: list[str],
    ) -> None:
        """Detect data conflicts between baseline and field."""
        # Support number conflict: parsed notes differ from baseline
        notes_support = (field_pole.parsed_notes or {}).get("support_no")
        if notes_support and notes_support.strip():
            # Compare only numeric portions
            import re

            b_digits = re.sub(r"[^0-9]", "", baseline_pole.support_no or "")
            n_digits = re.sub(r"[^0-9]", "", notes_support.strip())
            if b_digits and n_digits and b_digits != n_digits:
                conflicts.append("SUPPORT_NO_CONFLICT")

        # Voltage conflict: field notes vs baseline voltage
        notes_voltage = (field_pole.parsed_notes or {}).get("voltage")
        if notes_voltage and baseline_pole.voltage_level:
            bl_voltage = str(
                baseline_pole.voltage_level.value
                if hasattr(baseline_pole.voltage_level, "value")
                else baseline_pole.voltage_level
            ).upper()
            nv = notes_voltage.strip().upper()
            if (
                bl_voltage not in ("UNKNOWN",)
                and nv not in ("", "UNKNOWN")
                and bl_voltage not in nv
                and nv not in bl_voltage
            ):
                conflicts.append("VOLTAGE_CONFLICT")
