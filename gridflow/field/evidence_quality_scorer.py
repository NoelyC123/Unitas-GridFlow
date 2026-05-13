"""
Evidence quality scoring for field poles.

Assigns HIGH/MEDIUM/LOW quality based on photo count,
screenshot presence, notes, and popup availability.
"""

import logging

from gridflow.field.models import FieldDataset, FieldPole

logger = logging.getLogger(__name__)


class EvidenceQualityScorer:
    """Score field evidence quality and identity confidence."""

    def score(self, pole: FieldPole) -> str:
        """
        Determine evidence quality for a single pole.

        HIGH:
            3+ photos AND 1+ screenshot AND notes present AND popup yes

        MEDIUM:
            3+ photos AND 1+ screenshot AND notes present AND popup uncertain

        LOW:
            < 3 photos OR (0 screenshots AND no notes) OR UNKNOWN_SUPPORT flag
        """
        has_photos = pole.field_photo_count >= 3
        has_screenshots = pole.map_screenshot_count >= 1
        has_notes = pole.notes_present
        popup_yes = pole.map_popup_present == "yes"
        unknown_support = "UNKNOWN_SUPPORT" in pole.special_flags

        if unknown_support:
            return "LOW"

        if has_photos and has_screenshots and has_notes and popup_yes:
            return "HIGH"

        if has_photos and has_screenshots and has_notes and not popup_yes:
            return "MEDIUM"

        return "LOW"

    def score_identity_confidence(self, pole: FieldPole) -> str:
        """
        Score identity confidence based on notes and flags.

        Separate from evidence quality — specifically about identification.
        """
        if "UNKNOWN_SUPPORT" in pole.special_flags:
            return "LOW"

        # Parsed notes with support_no match → HIGH
        notes_support = pole.parsed_notes.get("support_no")
        if notes_support and notes_support.strip():
            return pole.evidence_quality  # Inherits from evidence quality

        return "MEDIUM" if pole.evidence_quality in ("HIGH", "MEDIUM") else "LOW"

    def score_dataset(self, dataset: FieldDataset) -> FieldDataset:
        """
        Apply scoring to all poles and recalculate summary.

        Args:
            dataset: FieldDataset to score

        Returns:
            Updated dataset with evidence_quality and identity_confidence set
        """
        for pole in dataset.poles:
            pole.evidence_quality = self.score(pole)
            pole.identity_confidence = self.score_identity_confidence(pole)

        # Recalculate summary
        high = sum(1 for p in dataset.poles if p.evidence_quality == "HIGH")
        medium = sum(1 for p in dataset.poles if p.evidence_quality == "MEDIUM")
        low = sum(1 for p in dataset.poles if p.evidence_quality == "LOW")

        dataset.evidence_summary.update(
            {
                "high": high,
                "medium": medium,
                "low": low,
            }
        )

        logger.info(
            "Scored %d poles: %d HIGH, %d MEDIUM, %d LOW",
            len(dataset.poles),
            high,
            medium,
            low,
        )
        return dataset
