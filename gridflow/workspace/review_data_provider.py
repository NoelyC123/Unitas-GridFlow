"""
Review Data Provider

Loads and filters merged pole data for the workspace UI.
Uses MergedPole field names from gridflow.merge.models (not the spec stub).
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from gridflow.merge.models import MergedPole

logger = logging.getLogger(__name__)


def _evidence_quality(pole: MergedPole) -> str:
    """Derive evidence quality from MergedPole field data."""
    if pole.field_photo_count >= 3 and pole.notes_content:
        return "MEDIUM" if "NO_POLE_POPUP" in pole.special_flags else "HIGH"
    return "LOW"


def _has_any_verification_flag(pole: MergedPole) -> bool:
    """Return True if any verification flag is set on the pole."""
    return (
        pole.voltage_verification_required
        or pole.conductor_verification_required
        or pole.pole_class_verification_required
        or pole.condition_verification_required
        or pole.identity_verification_required
        or pole.equipment_conflict_flag
    )


class ReviewDataProvider:
    """Provides filtered data access for the review workspace."""

    def __init__(self, job_dir: Path):
        """
        Args:
            job_dir: Path to pipeline run directory containing 04_merged_dataset.json
        """
        self.job_dir = Path(job_dir)
        self.merged_dataset_path = self.job_dir / "04_merged_dataset.json"
        self._poles: Optional[List[MergedPole]] = None

    def load_job(self) -> Dict:
        """
        Load merged poles from disk.

        Returns:
            Dict with job metadata and pole count

        Raises:
            FileNotFoundError: If 04_merged_dataset.json is missing
        """
        if not self.merged_dataset_path.exists():
            raise FileNotFoundError(f"Merged dataset not found: {self.merged_dataset_path}")

        with open(self.merged_dataset_path, encoding="utf-8") as f:
            data = json.load(f)

        # MergedDataset.model_dump() produces {"poles": [...], ...metadata...}
        raw_poles = data.get("poles", [])
        self._poles = [MergedPole(**p) for p in raw_poles]

        logger.info("Loaded %d poles from %s", len(self._poles), self.merged_dataset_path)

        return {
            "job_dir": str(self.job_dir),
            "pole_count": len(self._poles),
            "loaded": True,
        }

    def get_poles(self, filters: Optional[Dict] = None) -> List[MergedPole]:
        """
        Return poles, optionally filtered.

        Supported filter keys:
            design_ready (bool)
            evidence_quality (str: HIGH/MEDIUM/LOW)
            match_confidence (str: HIGH/MEDIUM/LOW/UNMATCHED)
            has_flags (bool)
        """
        if self._poles is None:
            self.load_job()

        poles = list(self._poles)

        if not filters:
            return poles

        if "design_ready" in filters:
            poles = [p for p in poles if p.design_ready == filters["design_ready"]]

        if "evidence_quality" in filters:
            wanted = filters["evidence_quality"]
            poles = [p for p in poles if _evidence_quality(p) == wanted]

        if "match_confidence" in filters:
            poles = [p for p in poles if p.match_confidence == filters["match_confidence"]]

        if "has_flags" in filters and filters["has_flags"]:
            poles = [p for p in poles if _has_any_verification_flag(p)]

        return poles

    def get_pole_details(self, support_no: str) -> Optional[MergedPole]:
        """
        Return a single pole by support number, or None if not found.
        """
        if self._poles is None:
            self.load_job()

        for pole in self._poles:
            if pole.support_no == support_no:
                return pole
        return None

    def get_statistics(self) -> Dict:
        """Return summary counts for the statistics panel."""
        if self._poles is None:
            self.load_job()

        eq_counts: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
        mc_counts: Dict[str, int] = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNMATCHED": 0}

        for pole in self._poles:
            eq = _evidence_quality(pole)
            if eq in eq_counts:
                eq_counts[eq] += 1

            mc = pole.match_confidence
            if mc in mc_counts:
                mc_counts[mc] += 1

        return {
            "total_poles": len(self._poles),
            "design_ready": sum(1 for p in self._poles if p.design_ready),
            "design_blocked": sum(1 for p in self._poles if p.design_blocked),
            "poles_with_flags": sum(1 for p in self._poles if _has_any_verification_flag(p)),
            "evidence_quality": eq_counts,
            "match_confidence": mc_counts,
        }
