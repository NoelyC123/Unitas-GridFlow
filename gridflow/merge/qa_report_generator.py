"""
QA report generator for merge engine output.

Produces a markdown report showing what a designer needs to obtain
from the DNO before design can proceed.
"""

import csv
import logging
from pathlib import Path
from gridflow.merge.models import MergedDataset, MergedPole

logger = logging.getLogger(__name__)


class QAReportGenerator:
    """Generate QA reports and CSV exports from MergedDataset."""

    def generate(self, dataset: MergedDataset) -> str:
        """
        Generate complete markdown QA report.

        Args:
            dataset: Completed MergedDataset

        Returns:
            Markdown report as string
        """
        sections = [
            self.generate_summary(dataset),
            self.generate_confidence_table(dataset),
            self.generate_verification_summary(dataset),
            self.generate_pole_table(dataset),
            self.generate_design_blockers(dataset),
            self.generate_unmatched_section(dataset),
            self.generate_action_items(dataset),
        ]
        return "\n\n".join(sections)

    def generate_summary(self, dataset: MergedDataset) -> str:
        """Executive summary section."""
        match_rate = (
            (dataset.total_matched / dataset.total_poles_baseline * 100)
            if dataset.total_poles_baseline > 0 else 0.0
        )

        lines = [
            "# GridFlow QA Report — Merge Analysis",
            "",
            "## Executive Summary",
            "",
            f"- **Baseline Source**: {dataset.baseline_source or 'N/A'}",
            f"- **Field Source**: {dataset.field_source or 'N/A'}",
            f"- **Merge Date**: {dataset.merge_date}",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| Total Poles (Baseline) | {dataset.total_poles_baseline} |",
            f"| Total Poles (Field) | {dataset.total_poles_field} |",
            f"| Matched | {dataset.total_matched} |",
            f"| Match Rate | {match_rate:.1f}% |",
            f"| Unmatched Baseline | {dataset.total_unmatched_baseline} |",
            f"| Unmatched Field | {dataset.total_unmatched_field} |",
            "",
            f"| Status | Count |",
            f"|--------|-------|",
            f"| Design Ready | {dataset.design_ready_count} |",
            f"| Design Blocked | {dataset.design_blocked_count} |",
            f"| Review Required | {dataset.review_required_count} |",
            "",
            "> **Note:** Design-blocked status is expected at this stage. "
            "DNO engineering specifications (voltage, conductor, pole class) "
            "have not yet been obtained. This report identifies exactly what "
            "is needed before design can proceed.",
        ]
        return "\n".join(lines)

    def generate_confidence_table(self, dataset: MergedDataset) -> str:
        """Match confidence distribution."""
        total = dataset.total_matched or 1
        h = dataset.high_confidence_count
        m = dataset.medium_confidence_count
        l = dataset.low_confidence_count
        u = dataset.total_poles_baseline - (h + m + l)

        lines = [
            "## Match Confidence Distribution",
            "",
            "| Confidence | Count | Percentage |",
            "|------------|-------|------------|",
            f"| HIGH | {h} | {h/total*100:.1f}% |",
            f"| MEDIUM | {m} | {m/total*100:.1f}% |",
            f"| LOW | {l} | {l/total*100:.1f}% |",
            f"| UNMATCHED | {max(u, 0)} | {max(u,0)/total*100:.1f}% |",
        ]
        return "\n".join(lines)

    def generate_verification_summary(self, dataset: MergedDataset) -> str:
        """Summary of how many poles need each verification type."""
        poles = dataset.poles

        def count(attr): return sum(1 for p in poles if getattr(p, attr, False))

        lines = [
            "## Verification Requirements Summary",
            "",
            "| Requirement | Poles Affected | Action |",
            "|-------------|----------------|--------|",
            f"| Voltage verification | {count('voltage_verification_required')}/{len(poles)} "
            f"| Obtain DNO-certified voltage spec |",
            f"| Conductor verification | {count('conductor_verification_required')}/{len(poles)} "
            f"| Obtain DNO conductor spec |",
            f"| Pole class verification | {count('pole_class_verification_required')}/{len(poles)} "
            f"| Obtain DNO pole class and strength rating |",
            f"| Condition verification | {count('condition_verification_required')}/{len(poles)} "
            f"| DNO re-inspection required (severe defects) |",
            f"| Identity verification | {count('identity_verification_required')}/{len(poles)} "
            f"| Confirm pole identity with DNO |",
            f"| Equipment conflicts | {count('equipment_conflict_flag')}/{len(poles)} "
            f"| Resolve field vs baseline discrepancy |",
        ]
        return "\n".join(lines)

    def generate_pole_table(self, dataset: MergedDataset) -> str:
        """Per-pole summary table."""
        lines = [
            "## Per-Pole Summary",
            "",
            "| Support No | Confidence | Design Ready | Voltage | Conductor "
            "| Pole Class | Condition | Identity | Actions |",
            "|-----------|------------|-------------|---------|-----------|"
            "-----------|-----------|----------|---------|",
        ]

        def yn(val): return "✓" if val else "-"

        for pole in dataset.poles:
            lines.append(
                f"| {pole.support_no} "
                f"| {pole.match_confidence} "
                f"| {yn(pole.design_ready)} "
                f"| {yn(pole.voltage_verification_required)} "
                f"| {yn(pole.conductor_verification_required)} "
                f"| {yn(pole.pole_class_verification_required)} "
                f"| {yn(pole.condition_verification_required)} "
                f"| {yn(pole.identity_verification_required)} "
                f"| {len(pole.designer_actions)} |"
            )
        return "\n".join(lines)

    def generate_design_blockers(self, dataset: MergedDataset) -> str:
        """Detailed listing of blocked poles with specific actions."""
        blocked = [p for p in dataset.poles if p.design_blocked]

        lines = [
            "## Design Blockers",
            "",
            f"**{len(blocked)} poles cannot proceed to design** — "
            "DNO engineering specifications must be obtained first.",
            "",
        ]

        for pole in blocked:
            lines.append(f"### Pole {pole.support_no}")
            lines.append(f"- **Match Confidence**: {pole.match_confidence}")
            lines.append(f"- **Folder**: {pole.folder_name or 'N/A'}")
            if pole.special_flags:
                lines.append(f"- **Special Flags**: {', '.join(pole.special_flags)}")
            if pole.conflict_flags:
                lines.append(f"- **Conflicts**: {', '.join(pole.conflict_flags)}")
            lines.append("- **Actions Required**:")
            for action in pole.designer_actions:
                lines.append(f"  * {action}")
            lines.append("")

        return "\n".join(lines)

    def generate_unmatched_section(self, dataset: MergedDataset) -> str:
        """Unmatched poles section."""
        lines = [
            "## Unmatched Poles",
            "",
        ]

        if dataset.unmatched_baseline:
            lines.append(f"### Baseline Poles Not Surveyed ({len(dataset.unmatched_baseline)} poles)")
            lines.append("")
            lines.append("These poles appear in the DNO baseline but have no field evidence.")
            lines.append("A field visit is required before these can be included in design.")
            lines.append("")
            for pole in dataset.unmatched_baseline:
                sno = pole.get("support_no", "UNKNOWN")
                e = pole.get("easting", "")
                n = pole.get("northing", "")
                lines.append(f"- **{sno}** — Easting: {e}, Northing: {n}")
            lines.append("")
        else:
            lines.append("### Baseline Poles Not Surveyed: **0** ✓")
            lines.append("")

        if dataset.unmatched_field:
            lines.append(f"### Field Poles Not In Baseline ({len(dataset.unmatched_field)} poles)")
            lines.append("")
            lines.append("These poles have field evidence but are not listed in the DNO baseline.")
            lines.append("Investigate — they may be unlisted assets or evidence-folder errors.")
            lines.append("")
            for pole in dataset.unmatched_field:
                lines.append(f"- **{pole.get('folder_name', 'UNKNOWN')}** (Support No: {pole.get('support_no', '?')})")
            lines.append("")
        else:
            lines.append("### Field Poles Not In Baseline: **0** ✓")
            lines.append("")

        return "\n".join(lines)

    def generate_action_items(self, dataset: MergedDataset) -> str:
        """Prioritised action item list for the project lead/designer."""
        all_actions: set[str] = set()
        for pole in dataset.poles:
            all_actions.update(pole.designer_actions)

        lines = [
            "## Recommended Next Steps",
            "",
            "Complete these actions before design can proceed:",
            "",
        ]

        # Priority order
        priority = [
            "Obtain DNO-certified voltage specification",
            "Obtain DNO conductor specification (size, type, material)",
            "Obtain DNO pole class and strength rating",
            "Confirm pole identity with DNO (match confidence < HIGH)",
            "Obtain DNO re-inspection (severe defects observed in field)",
            "Resolve equipment conflict: field observation differs from baseline record",
        ]

        step = 1
        for action in priority:
            if action in all_actions:
                count = sum(1 for p in dataset.poles if action in p.designer_actions)
                lines.append(f"{step}. **{action}** — {count} pole(s)")
                step += 1

        if dataset.total_unmatched_baseline > 0:
            lines.append(
                f"{step}. **Schedule field revisit for {dataset.total_unmatched_baseline} "
                f"unmatched baseline pole(s)**"
            )
            step += 1

        if dataset.review_required_count > 0:
            lines.append(
                f"{step}. **Manual review required for {dataset.review_required_count} "
                f"MEDIUM/LOW confidence match(es)**"
            )

        lines.append("")
        lines.append("---")
        lines.append("*Report generated by GridFlow Stage 4C.4 Merge Engine*")

        return "\n".join(lines)

    def export_csv(self, dataset: MergedDataset, output_path: "str | Path") -> None:
        """Export per-pole summary as CSV."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "support_no",
            "match_confidence",
            "design_ready",
            "design_blocked",
            "voltage_verification",
            "conductor_verification",
            "pole_class_verification",
            "condition_verification",
            "identity_verification",
            "equipment_conflict",
            "conflict_flags",
            "special_flags",
            "actions_count",
        ]

        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for pole in dataset.poles:
                writer.writerow({
                    "support_no": pole.support_no,
                    "match_confidence": pole.match_confidence,
                    "design_ready": "yes" if pole.design_ready else "no",
                    "design_blocked": "yes" if pole.design_blocked else "no",
                    "voltage_verification": "yes" if pole.voltage_verification_required else "no",
                    "conductor_verification": "yes" if pole.conductor_verification_required else "no",
                    "pole_class_verification": "yes" if pole.pole_class_verification_required else "no",
                    "condition_verification": "yes" if pole.condition_verification_required else "no",
                    "identity_verification": "yes" if pole.identity_verification_required else "no",
                    "equipment_conflict": "yes" if pole.equipment_conflict_flag else "no",
                    "conflict_flags": "|".join(pole.conflict_flags),
                    "special_flags": "|".join(pole.special_flags),
                    "actions_count": len(pole.designer_actions),
                })

        logger.info("CSV exported to %s (%d rows)", output_path, len(dataset.poles))
