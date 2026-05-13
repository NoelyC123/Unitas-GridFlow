"""
Match register builder.

Assembles MatchResult objects into a structured MatchRegister
and exports as JSON or CSV.
"""

import csv
import logging
from pathlib import Path

from gridflow.baseline.models import BaselineDataset
from gridflow.field.models import FieldDataset
from gridflow.matching.models import MatchRegister, MatchRegisterEntry, MatchResult

logger = logging.getLogger(__name__)


class RegisterBuilder:
    """Build and export MatchRegister from MatchResult list."""

    def build(
        self,
        match_results: list[MatchResult],
        baseline: BaselineDataset,
        field: FieldDataset,
    ) -> MatchRegister:
        """
        Build MatchRegister from match results and source datasets.

        Args:
            match_results: Output from SupportNumberMatcher.match()
            baseline: Source baseline dataset
            field: Source field dataset

        Returns:
            MatchRegister with entries and statistics
        """
        # Build lookup sets for unmatched tracking
        matched_field_folders = {r.field_folder for r in match_results if r.field_folder}

        entries = []

        # Add matched / unmatched baseline entries
        b_by_id = {p.pole_id: p for p in baseline.poles}
        for mr in match_results:
            entry = MatchRegisterEntry(
                support_no=mr.baseline_support_no,
                baseline_pole_id=mr.baseline_pole_id,
                field_folder=mr.field_folder,
                match_confidence=mr.match_confidence,
                match_type=mr.match_type,
                review_required=mr.review_required,
                conflict_flags=mr.conflict_flags,
            )
            entries.append(entry)

        # Add field poles not matched to any baseline
        for fp in field.poles:
            if fp.folder_name not in matched_field_folders:
                entry = MatchRegisterEntry(
                    support_no=fp.support_no,
                    field_folder=fp.folder_name,
                    match_type="EXTRA_FIELD",
                    match_confidence="UNMATCHED",
                    review_required=True,
                )
                entries.append(entry)

        unmatched_baseline = sum(1 for e in entries if e.match_type == "UNMATCHED")
        unmatched_field = sum(1 for e in entries if e.match_type == "EXTRA_FIELD")
        matched = sum(1 for e in entries if e.match_type not in ("UNMATCHED", "EXTRA_FIELD"))

        register = MatchRegister(
            baseline_total=len(baseline.poles),
            field_total=len(field.poles),
            matched=matched,
            unmatched_baseline=unmatched_baseline,
            unmatched_field=unmatched_field,
            entries=entries,
        )
        register.compute_stats()

        logger.info(
            "Register built: %d matched, %d unmatched baseline, %d extra field | rate %.1f%%",
            matched,
            unmatched_baseline,
            unmatched_field,
            register.match_rate,
        )
        return register

    def export_csv(self, register: MatchRegister, output_path: "str | Path") -> None:
        """
        Export register as CSV matching baseline_field_match_register.csv format.

        Columns: support_no, baseline_pole_id, field_folder, match_confidence,
                 match_type, identity_verified, review_required, conflict_flags
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "support_no",
            "baseline_pole_id",
            "field_folder",
            "match_confidence",
            "match_type",
            "identity_verified",
            "review_required",
            "conflict_flags",
        ]

        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for entry in register.entries:
                writer.writerow(
                    {
                        "support_no": entry.support_no,
                        "baseline_pole_id": entry.baseline_pole_id or "",
                        "field_folder": entry.field_folder or "",
                        "match_confidence": entry.match_confidence,
                        "match_type": entry.match_type,
                        "identity_verified": "yes" if entry.identity_verified else "",
                        "review_required": "yes" if entry.review_required else "no",
                        "conflict_flags": "|".join(entry.conflict_flags),
                    }
                )

        logger.info("CSV exported to %s (%d rows)", output_path, len(register.entries))
