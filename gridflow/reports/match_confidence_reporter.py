"""Match confidence analysis report for Stage 5A pilot output packs."""

from datetime import datetime
from typing import Any, List

from gridflow.merge.models import MergedPole


class MatchConfidenceReporter:
    """Generate baseline-to-field match confidence analysis."""

    def generate(
        self, merged_poles: List[MergedPole], job_context: dict[str, Any] | None = None
    ) -> str:
        """Return Markdown report generated only from MergedPole records."""
        ctx = job_context or {}
        job_id = ctx.get("job_id", "Unknown Job")
        baseline = ctx.get("baseline_file", "baseline.csv")
        field = ctx.get("field_folder", "field_evidence")
        timestamp = ctx.get("run_timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        poles = list(merged_poles)
        total = len(poles)
        groups = {
            "HIGH": [p for p in poles if p.match_confidence == "HIGH"],
            "MEDIUM": [p for p in poles if p.match_confidence == "MEDIUM"],
            "LOW": [p for p in poles if p.match_confidence == "LOW"],
            "UNMATCHED": [p for p in poles if p.match_confidence == "UNMATCHED"],
        }
        lines = [
            f"# Match Confidence Analysis - {job_id}",
            "",
            f"**Date:** {timestamp}",
            f"**Baseline:** {baseline}",
            f"**Field Evidence:** {field}",
            "",
        ]

        lines.extend(
            self._confidence_section(
                "HIGH Confidence Matches",
                groups["HIGH"],
                total,
                "Support identity is trusted from the available merged record. No identity review is normally required.",
                [
                    "Support numbers matched strongly between baseline and field evidence",
                    "No identity verification flag raised",
                    "No conflict flag requires identity downgrade",
                ],
            )
        )
        lines.extend(
            self._confidence_section(
                "MEDIUM Confidence Matches",
                groups["MEDIUM"],
                total,
                "Generally acceptable for workflow tracking, but manual review is recommended before design reliance.",
                [
                    "Support number may use variant spelling or format",
                    "Field evidence may contain a no-popup or route-context uncertainty",
                    "Minor discrepancy may require reviewer confirmation",
                ],
            )
        )
        lines.extend(
            self._confidence_section(
                "LOW Confidence Matches",
                groups["LOW"],
                total,
                "ACTION REQUIRED: manually review before design proceeds.",
                [
                    "Support number interpretation may be weak",
                    "Field evidence may be incomplete",
                    "Conflict flags or identity uncertainty may be present",
                ],
                action=True,
            )
        )

        norm_rows = []
        for pole in poles:
            normalized = self._normalize(pole.support_no)
            norm_rows.append((pole.support_no, normalized, pole.match_confidence))

        lines.extend(["## Support Number Normalization", ""])
        if any(original != normalized for original, normalized, _ in norm_rows):
            lines.extend(
                [
                    "| Support No | Normalized | Match Result |",
                    "| --- | --- | --- |",
                ]
            )
            for original, normalized, confidence in norm_rows:
                lines.append(f"| {original} | {normalized} | {confidence} |")
        else:
            lines.append(
                "No support number variants detected. All baseline support "
                "numbers matched field evidence exactly."
            )

        lines.extend(
            [
                "",
                "## Unmatched Records",
                "",
                f"**Unmatched records:** {len(groups['UNMATCHED'])}",
                "",
            ]
        )
        if groups["UNMATCHED"]:
            lines.append(f"**Poles:** {self._pole_list(groups['UNMATCHED'])}")
            lines.append("")
        else:
            lines.append("All supplied merged poles have a match confidence other than UNMATCHED.")
            lines.append("")

        lines.extend(
            [
                "## Recommendation",
                "",
                self._recommendation(groups, total),
                "",
                "Reviewer instructions:",
                "",
                "1. Review all LOW confidence matches before design reliance.",
                "2. Review MEDIUM confidence matches where identity affects design scope.",
                "3. Confirm support number variants against the DNO asset register.",
                "4. Re-run GridFlow if corrected evidence or DNO identity data is received.",
                "",
                "---",
                "*Report generated by GridFlow Stage 5A.2*",
            ]
        )
        return "\n".join(lines)

    def _confidence_section(
        self,
        title: str,
        poles: list[MergedPole],
        total: int,
        interpretation: str,
        criteria: list[str],
        action: bool = False,
    ) -> list[str]:
        icon = self._confidence_icon(title)
        lines = [
            f"## {icon} {title}",
            "",
            f"**Count:** {len(poles)} {self._noun(len(poles), 'match', 'matches')} ({self._pct(len(poles), total)})",
            "",
            f"**Poles:** {self._pole_list(poles)}",
            "",
            "**Match criteria:**",
        ]
        lines.extend(f"- {item}" for item in criteria)
        lines.extend(["", f"**Interpretation:** {interpretation}", ""])
        if action and poles:
            lines.extend(
                [
                    "**Risk if not reviewed:** Wrong pole specified for design or construction, asset register mismatch, and safety incidents.",
                    "",
                ]
            )
        return lines

    @staticmethod
    def _confidence_icon(title: str) -> str:
        if title.startswith("HIGH"):
            return "✅"
        if title.startswith("MEDIUM"):
            return "⚠️"
        if title.startswith("LOW"):
            return "❌"
        return "ℹ️"

    @staticmethod
    def _pole_list(poles: list[MergedPole]) -> str:
        return ", ".join(p.support_no for p in poles) if poles else "None"

    @staticmethod
    def _pct(count: int, total: int) -> str:
        return "0%" if total == 0 else f"{count / total * 100:.0f}%"

    @staticmethod
    def _noun(count: int, singular: str, plural: str | None = None) -> str:
        return singular if count == 1 else (plural or f"{singular}s")

    @staticmethod
    def _normalize(support_no: str) -> str:
        return "".join(ch for ch in support_no.upper().replace("-", "_").split() if ch)

    @staticmethod
    def _recommendation(groups: dict[str, list[MergedPole]], total: int) -> str:
        if total == 0:
            return "No merged poles were supplied, so match quality cannot be assessed."
        if groups["UNMATCHED"]:
            return (
                "Match Quality Assessment: REVIEW REQUIRED. Unmatched records "
                "must be resolved against baseline and field evidence before design reliance."
            )
        low_ratio = len(groups["LOW"]) / total
        high_ratio = len(groups["HIGH"]) / total
        if low_ratio > 0.3:
            return (
                "Match Quality Assessment: REVIEW REQUIRED. More than 30% of "
                "matches are LOW confidence, so manual identity review is urgent."
            )
        if low_ratio > 0:
            return (
                "Match Quality Assessment: MIXED. LOW confidence matches must be "
                "reviewed before design reliance, but DNO data requests can proceed in parallel."
            )
        if high_ratio >= 0.8:
            return "Match Quality Assessment: STRONG. Most matches are HIGH confidence."
        return "Match Quality Assessment: ACCEPTABLE WITH REVIEW. Review MEDIUM confidence matches."
