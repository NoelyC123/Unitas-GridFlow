"""
Support number matching between baseline and field evidence.

Tries exact match, then variant normalization (stripping letter suffixes
and common prefixes) before marking as UNMATCHED.
"""

import logging
import re
from typing import Optional

from gridflow.baseline.models import BaselineDataset
from gridflow.field.models import FieldDataset
from gridflow.matching.models import MatchResult

logger = logging.getLogger(__name__)

# Prefixes to strip during normalization
STRIP_PREFIXES = ("SP", "EN", "WP", "NO", "YK")


class SupportNumberMatcher:
    """
    Match baseline poles to field evidence poles via support numbers.
    """

    def match(
        self,
        baseline_dataset: BaselineDataset,
        field_dataset: FieldDataset,
    ) -> list[MatchResult]:
        """
        Match all baseline poles to field evidence.

        Strategy:
          1. Exact normalized support number match
          2. Strip variant suffix and retry (903201A → 903201)
          3. Mark unmatched

        Args:
            baseline_dataset: Parsed baseline dataset
            field_dataset: Scanned field evidence dataset

        Returns:
            List of MatchResult, one per baseline pole
        """
        # Build field lookup: normalized_support_no → FieldPole
        field_by_normalized: dict[str, object] = {}
        for fp in field_dataset.poles:
            key = self._normalize(fp.support_no)
            field_by_normalized[key] = fp

        results = []
        matched_field_keys: set[str] = set()

        for bp in baseline_dataset.poles:
            b_key = self._normalize(bp.support_no or "")

            result = self._try_match(bp, field_by_normalized, b_key)

            if result.match_type != "UNMATCHED":
                matched_field_keys.add(self._normalize(result.field_support_no or ""))

            results.append(result)

        # Log unmatched field poles
        for fp in field_dataset.poles:
            if self._normalize(fp.support_no) not in matched_field_keys:
                logger.debug("Unmatched field pole: %s", fp.support_no)

        matched = sum(1 for r in results if r.match_type != "UNMATCHED")
        logger.info(
            "Matched %d/%d baseline poles to field evidence",
            matched,
            len(baseline_dataset.poles),
        )
        return results

    def _try_match(
        self,
        baseline_pole,
        field_by_normalized: dict,
        b_key: str,
    ) -> MatchResult:
        """Attempt exact and then variant match for one baseline pole."""
        # Attempt 1: exact normalized match
        if b_key in field_by_normalized:
            fp = field_by_normalized[b_key]
            return MatchResult(
                baseline_pole_id=baseline_pole.pole_id,
                baseline_support_no=baseline_pole.support_no or "",
                field_folder=fp.folder_name,
                field_support_no=fp.support_no,
                match_type="EXACT",
            )

        # Attempt 2: strip trailing letter suffix (903201A → 903201)
        stripped = re.sub(r"[A-Z]+$", "", b_key)
        if stripped != b_key and stripped in field_by_normalized:
            fp = field_by_normalized[stripped]
            return MatchResult(
                baseline_pole_id=baseline_pole.pole_id,
                baseline_support_no=baseline_pole.support_no or "",
                field_folder=fp.folder_name,
                field_support_no=fp.support_no,
                match_type="EXACT",
                confidence_reasons=["VARIANT_SUFFIX_STRIPPED"],
            )

        return MatchResult(
            baseline_pole_id=baseline_pole.pole_id,
            baseline_support_no=baseline_pole.support_no or "",
            match_type="UNMATCHED",
            match_confidence="UNMATCHED",
        )

    def match_single(self, baseline_support_no: str, field_support_no: str) -> bool:
        """Return True if two support numbers refer to the same pole."""
        b = self._normalize(baseline_support_no)
        f = self._normalize(field_support_no)
        if b == f:
            return True
        # Check if one is a variant of the other
        stripped_b = re.sub(r"[A-Z]+$", "", b)
        stripped_f = re.sub(r"[A-Z]+$", "", f)
        return stripped_b == stripped_f and bool(stripped_b)

    @staticmethod
    def _normalize(support_no: Optional[str]) -> str:
        """Normalize support number: strip spaces, uppercase, remove prefixes."""
        if not support_no:
            return ""
        s = support_no.strip().upper()
        for prefix in STRIP_PREFIXES:
            if s.startswith(prefix) and len(s) > len(prefix):
                candidate = s[len(prefix) :]
                if candidate[:1].isdigit():
                    s = candidate
                    break
        return s
