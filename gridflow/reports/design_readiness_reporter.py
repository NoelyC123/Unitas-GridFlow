"""Design readiness summary report for Stage 5A pilot output packs."""

from collections import Counter
from datetime import datetime
from typing import List

from gridflow.merge.models import MergedPole


class DesignReadinessReporter:
    """Generate a management-level design-readiness report."""

    def generate(self, merged_poles: List[MergedPole]) -> str:
        """Return Markdown report generated only from MergedPole records."""
        poles = list(merged_poles)
        total = len(poles)
        ready = sum(1 for p in poles if p.design_ready)
        blocked = total - ready
        status = self._overall_status(total, ready, blocked)
        evidence_counts = self._evidence_quality_counts(poles)
        confidence_counts = Counter(p.match_confidence for p in poles)
        blockers = self._blocker_counts(poles)

        lines = [
            "# Design Readiness Summary - Job GridFlow Pipeline",
            "",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Overall Status:** {status}",
            "",
            "## Pole Counts",
            "",
            f"- **Total baseline poles:** {total}",
            f"- **Field evidence captured:** {total} ({self._pct(total, total)})",
            f"- **Poles matched:** {sum(1 for p in poles if p.match_confidence != 'UNMATCHED')} ({self._pct(sum(1 for p in poles if p.match_confidence != 'UNMATCHED'), total)})",
            f"- **Design-ready poles:** {ready} ({self._pct(ready, total)})",
            f"- **Design-blocked poles:** {blocked} ({self._pct(blocked, total)})",
            "",
            "## Evidence Quality Assessment",
            "",
            f"Field survey quality: **{self._quality_label(evidence_counts, total)}**",
            "",
            f"- **HIGH quality:** {evidence_counts['HIGH']} {self._noun(evidence_counts['HIGH'], 'pole')} ({self._pct(evidence_counts['HIGH'], total)})",
            f"- **MEDIUM quality:** {evidence_counts['MEDIUM']} {self._noun(evidence_counts['MEDIUM'], 'pole')} ({self._pct(evidence_counts['MEDIUM'], total)})",
            f"- **LOW quality:** {evidence_counts['LOW']} {self._noun(evidence_counts['LOW'], 'pole')} ({self._pct(evidence_counts['LOW'], total)})",
            "",
            "**Interpretation:** Evidence quality describes the field evidence package available in the merged records. It does not certify engineering design data.",
            "",
            "## Match Confidence Assessment",
            "",
            f"- **HIGH confidence:** {confidence_counts['HIGH']} {self._noun(confidence_counts['HIGH'], 'match', 'matches')} ({self._pct(confidence_counts['HIGH'], total)})",
            f"- **MEDIUM confidence:** {confidence_counts['MEDIUM']} {self._noun(confidence_counts['MEDIUM'], 'match', 'matches')} ({self._pct(confidence_counts['MEDIUM'], total)})",
            f"- **LOW confidence:** {confidence_counts['LOW']} {self._noun(confidence_counts['LOW'], 'match', 'matches')} ({self._pct(confidence_counts['LOW'], total)})",
            f"- **UNMATCHED:** {confidence_counts['UNMATCHED']} records ({self._pct(confidence_counts['UNMATCHED'], total)})",
            "",
            "**Interpretation:** Match confidence is identity confidence. HIGH confidence does not mean the pole is design-ready.",
            "",
            "## Design Blocker Analysis",
            "",
            "Why poles are blocked from design, ranked by frequency:",
            "",
        ]

        if blockers:
            for idx, (label, count, priority, impact) in enumerate(blockers, start=1):
                lines.extend(
                    [
                        f"{idx}. **{label}:** {count} poles ({self._pct(count, total)})",
                        f"   - Blocks: {impact}",
                        f"   - Priority: {priority}",
                        "",
                    ]
                )
        else:
            lines.extend(["No design blockers were raised from the available merged records.", ""])

        lines.extend(
            [
                "## Survey vs DNO Data Gap Analysis",
                "",
                "**What the field survey can support:**",
                "",
                "- Pole identity evidence and support number correlation",
                "- Field photos and notes",
                "- Visible condition and equipment observations",
                "- Access constraints and survey limitations",
                "",
                "**What still requires DNO records:**",
                "",
                "- Conductor specification",
                "- Pole class or strength rating",
                "- Certified voltage and circuit context",
                "- Historical asset records and inspection history",
                "",
                "This is the expected workflow gap. Field surveys capture observable evidence. DNO asset records provide engineering specifications.",
                "",
                "## Interpretation",
                "",
                self._interpretation(total, ready, blocked),
                "",
                "## Next Actions (Priority Order)",
                "",
                "1. Review and submit the DNO data request in Report 06.",
                "2. Manually review any MEDIUM, LOW, or UNMATCHED identity records.",
                "3. Re-run GridFlow when DNO engineering data or corrected evidence is available.",
                "4. Proceed to design preparation only for poles that clear verification blockers.",
                "",
                "---",
                "*Report generated by GridFlow Stage 5A.1*",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _overall_status(total: int, ready: int, blocked: int) -> str:
        if total == 0:
            return "NO DATA"
        if ready == total:
            return "DESIGN-READY"
        if ready > 0 and blocked > 0:
            return "PARTIALLY READY"
        return "DESIGN-BLOCKED (DNO Data Required)"

    @staticmethod
    def _pct(count: int, total: int) -> str:
        return "0%" if total == 0 else f"{count / total * 100:.0f}%"

    @staticmethod
    def _noun(count: int, singular: str, plural: str | None = None) -> str:
        return singular if count == 1 else (plural or f"{singular}s")

    @staticmethod
    def _evidence_quality_counts(poles: list[MergedPole]) -> Counter:
        counts = Counter()
        for pole in poles:
            if pole.field_photo_count >= 3 and pole.notes_content:
                quality = "MEDIUM" if "NO_POLE_POPUP" in pole.special_flags else "HIGH"
                counts[quality] += 1
            else:
                counts["LOW"] += 1
        return counts

    @staticmethod
    def _quality_label(counts: Counter, total: int) -> str:
        if total == 0:
            return "NO DATA"
        high_ratio = counts["HIGH"] / total
        if high_ratio >= 0.8:
            return "EXCELLENT"
        if high_ratio >= 0.5:
            return "GOOD"
        return "REVIEW REQUIRED"

    @staticmethod
    def _blocker_counts(poles: list[MergedPole]) -> list[tuple[str, int, str, str]]:
        specs = [
            (
                "Missing conductor specification",
                "conductor_verification_required",
                "CRITICAL",
                "span sag, clearance, and loading calculations",
            ),
            (
                "Missing pole class",
                "pole_class_verification_required",
                "CRITICAL",
                "replacement decisions, stay design, and loading assessment",
            ),
            (
                "Voltage conflicts or missing voltage",
                "voltage_or_conflict",
                "HIGH",
                "clearance calculations and safety verification",
            ),
            (
                "Identity confirmation required",
                "identity_verification_required",
                "MEDIUM",
                "asset register alignment and construction planning",
            ),
            (
                "Equipment conflicts",
                "equipment_conflict_only",
                "MEDIUM",
                "equipment assumptions and site risk planning",
            ),
            (
                "Condition verification required",
                "condition_verification_required",
                "MEDIUM",
                "condition risk review and possible re-inspection",
            ),
        ]
        rows = []
        for label, attr, priority, impact in specs:
            count = sum(1 for p in poles if DesignReadinessReporter._has_blocker(p, attr))
            if count:
                rows.append((label, count, priority, impact))
        return sorted(rows, key=lambda row: row[1], reverse=True)

    @staticmethod
    def _has_blocker(pole: MergedPole, attr: str) -> bool:
        if attr == "voltage_or_conflict":
            return pole.voltage_verification_required or "VOLTAGE_CONFLICT" in pole.conflict_flags
        if attr == "equipment_conflict_only":
            return "EQUIPMENT_CONFLICT" in pole.conflict_flags
        return bool(getattr(pole, attr, False))

    @staticmethod
    def _interpretation(total: int, ready: int, blocked: int) -> str:
        if total == 0:
            return "No merged poles were supplied, so design readiness cannot be assessed."
        if blocked and ready == 0:
            return (
                f"Status: NOT DESIGN-READY. 0/{total} poles are design-ready because "
                "DNO engineering specifications or confirmations are missing. This is "
                "not a survey failure or pipeline error; it is the expected next workflow step."
            )
        if ready == total:
            return f"Status: DESIGN-READY based on the verification flags available for all {total} poles."
        return f"Status: PARTIALLY READY. {ready}/{total} poles are ready and {blocked}/{total} remain blocked."
