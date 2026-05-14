"""Pilot output pack index report for Stage 5A."""

from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, List

from gridflow.merge.models import MergedPole


class PilotIndexReporter:
    """Generate an executive index and navigation report for pilot reviewers."""

    def __init__(
        self,
        baseline_source: str = "",
        field_source: str = "",
        output_dir: str | Path = "",
        job_name: str = "GridFlow Pipeline",
    ):
        self.baseline_source = str(baseline_source or "See pipeline_summary.json")
        self.field_source = str(field_source or "See pipeline_summary.json")
        self.output_dir = str(output_dir or "See pipeline_summary.json")
        self.job_name = job_name

    def generate(
        self, merged_poles: List[MergedPole], job_context: dict[str, Any] | None = None
    ) -> str:
        """Return Markdown report generated only from merged pole records."""
        ctx = job_context or {}
        job_id = ctx.get("job_id", self.job_name)
        baseline = ctx.get("baseline_file", self.baseline_source)
        field_source = ctx.get("field_folder", self.field_source)
        output_dir = ctx.get("output_dir", self.output_dir)
        timestamp = ctx.get("run_timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        poles = list(merged_poles)
        total = len(poles)
        ready = sum(1 for p in poles if p.design_ready)
        blocked = total - ready
        matched = sum(1 for p in poles if p.match_confidence != "UNMATCHED")
        field = sum(1 for p in poles if p.field_photo_count or p.notes_content or p.folder_name)
        flags = self._flag_counts(poles)
        top_name, top_count = self._top_blocker(flags)
        evidence = Counter(self._evidence_quality(p) for p in poles)
        confidence = Counter(p.match_confidence for p in poles)

        lines = [
            f"# GridFlow Pilot Output Pack - {job_id}",
            "",
            f"**Generated:** {timestamp}",
            "**Pipeline Status:** ✅ COMPLETE (all 4 stages succeeded)",
            f"**Design Status:** {self._design_headline(ready, blocked, total)}",
            "",
            "---",
            "",
            "## Quick Actions",
            "",
            f"- 🗺️ Map View: `/map/view/{job_id}` - Visualise poles on interactive map",
            f"- 📊 Review Workspace: `/workspace/view/{job_id}` - Browse and filter poles",
            "- 📄 Full QA Report: `05_qa_report.md` - Detailed QA findings",
            "- 📥 DNO Request: `06_dno_data_request.md` - Action missing data",
            "",
            "## Quick Stats",
            "",
            "| Metric | Value |",
            "| --- | --- |",
            f"| Baseline poles | {total} |",
            f"| Field evidence captured | {field} ({self._pct(field, total)}) |",
            f"| Poles matched | {matched} ({self._pct(matched, total)}) |",
            f"| Design-ready poles | {ready} ({self._pct(ready, total)}) |",
            f"| Design-blocked poles | {blocked} ({self._pct(blocked, total)}) |",
            f"| Top blocker | {top_name} ({top_count} poles) |",
            "",
            "## Input Sources",
            "",
            "| Field | Value |",
            "| --- | --- |",
            f"| Baseline | {baseline} |",
            f"| Field Evidence | {field_source} |",
            f"| Output Directory | {output_dir} |",
            f"| Run ID | {job_id} |",
            "",
            "## Design Readiness Headline",
            "",
            self._headline_text(ready, blocked, total),
            "",
            "## Critical Findings",
            "",
            "**Top Design Blockers:**",
        ]
        for idx, (label, count) in enumerate(flags.most_common(3), start=1):
            lines.append(f"{idx}. {label} - {count} poles")
        if not flags:
            lines.append("No design blockers raised from the merged records.")
        lines.extend(
            [
                "",
                "**Evidence Quality:**",
                f"- ✅ HIGH: {evidence['HIGH']} poles ({self._pct(evidence['HIGH'], total)})",
                f"- ⚠️ MEDIUM: {evidence['MEDIUM']} poles ({self._pct(evidence['MEDIUM'], total)})",
                f"- ❌ LOW: {evidence['LOW']} poles ({self._pct(evidence['LOW'], total)})",
                "",
                "**Match Confidence:**",
                f"- ✅ HIGH: {confidence['HIGH']} matches ({self._pct(confidence['HIGH'], total)})",
                f"- ⚠️ MEDIUM: {confidence['MEDIUM']} matches ({self._pct(confidence['MEDIUM'], total)})",
                f"- ❌ LOW: {confidence['LOW']} matches ({self._pct(confidence['LOW'], total)}) ⚠️ Requires review",
                "",
                self._output_files(total, matched),
                "",
                self._reviewer_workflow(confidence["LOW"]),
                "",
                self._decision_section(poles, ready, blocked, flags),
                "",
                "---",
                "*Report generated by GridFlow Stage 5A.2*",
            ]
        )
        return "\n".join(lines)

    def _output_files(self, total: int, matched: int) -> str:
        rate = self._pct(matched, total)
        return "\n".join(
            [
                "## Output Files",
                "",
                "**Core Pipeline Outputs:**",
                f"- `01_baseline_dataset.json` - {total} poles from baseline input",
                f"- `02_field_dataset.json` - Field evidence for {total} poles",
                f"- `03_match_register.csv` - Baseline-to-field matching ({rate} match rate)",
                f"- `04_merged_dataset.csv` - Design intelligence for {total} poles",
                "- `05_qa_report.md` - QA findings and verification requirements",
                "",
                "**Pilot Reports:**",
                f"- `06_dno_data_request.md` - DNO data requirements ({total} poles)",
                "- `07_design_readiness_summary.md` - Overall job status",
                "- `08_match_confidence_analysis.md` - Match quality analysis",
                "- `09_verification_flags_breakdown.md` - Detailed blocker analysis",
                "- `10_evidence_provenance_log.md` - Data source audit trail",
                "",
                "**Pipeline Metadata:**",
                "- `pipeline_summary.json` - Machine-readable status",
            ]
        )

    @staticmethod
    def _reviewer_workflow(low_count: int) -> str:
        return "\n".join(
            [
                "## ℹ️ Recommended Workflow",
                "",
                "**Step 1: Orientation (you are here)**",
                "Read this index to understand job status and outputs.",
                "",
                "**Step 2: Design Readiness Assessment**",
                "Open `07_design_readiness_summary.md` for ready vs blocked counts.",
                "",
                "**Step 3: Match Quality Review**",
                f"Open `08_match_confidence_analysis.md` and focus on LOW confidence matches ({low_count} poles).",
                "",
                "**Step 4: DNO Data Requirements**",
                "Open `06_dno_data_request.md` to review missing DNO engineering data.",
                "",
                "**Step 5: Detailed Verification Analysis**",
                "Open `09_verification_flags_breakdown.md` for blocker explanations and references.",
                "",
                "**Step 6: Evidence Audit (if needed)**",
                "Open `10_evidence_provenance_log.md` to trace data sources for each pole.",
            ]
        )

    def _decision_section(
        self, poles: list[MergedPole], ready: int, blocked: int, flags: Counter
    ) -> str:
        total = len(poles)
        if total == 0:
            return "## Pilot Decision\n\n**Status:** ℹ️ NO DATA\n\nNo merged poles were supplied."
        if ready == 0:
            return "\n".join(
                [
                    "## Pilot Decision",
                    "",
                    "**Status:** ⚠️ NOT READY FOR DESIGN",
                    "",
                    f"**Reason:** Missing DNO engineering specifications for {blocked} poles",
                    "",
                    "**Critical gaps:**",
                    f"- Conductor type and size: {flags['Missing conductor specification']} poles",
                    f"- Pole class/strength rating: {flags['Missing pole class']} poles",
                    f"- Voltage confirmation: {flags['Voltage conflicts or missing voltage']} poles",
                    "",
                    "**Next actions:**",
                    "1. ✅ Submit DNO data request (use Report 06)",
                    "2. ⚠️ Manually review LOW confidence matches if any are present",
                    "3. ⏳ Wait for DNO response through the established process",
                    "4. 🔄 Re-run GridFlow pipeline with DNO data",
                    "5. ✅ Verify design-ready count increases after records are supplied",
                    "6. ➡️ Then proceed to design workspace",
                    "",
                    "**Important:** This is NOT a pipeline failure. The pipeline completed successfully. Design is blocked due to missing DNO asset records, which is the expected workflow gap between field survey and engineering design.",
                ]
            )
        ready_poles = ", ".join(p.support_no for p in poles if p.design_ready) or "None"
        top, _count = self._top_blocker(flags)
        return "\n".join(
            [
                "## Pilot Decision",
                "",
                f"**Status:** ✅ READY FOR DESIGN ({ready} poles)",
                "",
                f"**Design-ready poles:** {ready_poles}",
                "",
                f"**Blocked poles:** {blocked} poles",
                f"- Reason: {top}",
                "- Action: submit DNO data request for blocked poles before final design reliance",
            ]
        )

    @staticmethod
    def _flag_counts(poles: list[MergedPole]) -> Counter:
        flags = Counter()
        for p in poles:
            if p.conductor_verification_required:
                flags["Missing conductor specification"] += 1
            if p.pole_class_verification_required:
                flags["Missing pole class"] += 1
            if p.voltage_verification_required or "VOLTAGE_CONFLICT" in p.conflict_flags:
                flags["Voltage conflicts or missing voltage"] += 1
            if p.identity_verification_required:
                flags["Identity confirmation required"] += 1
            if "EQUIPMENT_CONFLICT" in p.conflict_flags:
                flags["Equipment conflicts"] += 1
            if p.condition_verification_required:
                flags["Condition verification required"] += 1
        return flags

    @staticmethod
    def _top_blocker(flags: Counter) -> tuple[str, int]:
        return flags.most_common(1)[0] if flags else ("None", 0)

    @staticmethod
    def _design_headline(ready: int, blocked: int, total: int) -> str:
        if total == 0:
            return "ℹ️ NO DATA"
        if ready == 0:
            return "⚠️ DESIGN-BLOCKED (DNO data required)"
        if blocked == 0:
            return "✅ DESIGN-READY (all poles)"
        return f"ℹ️ PARTIAL READINESS ({ready} ready, {blocked} blocked)"

    @staticmethod
    def _headline_text(ready: int, blocked: int, total: int) -> str:
        if total == 0:
            return "ℹ️ No merged poles were supplied."
        if ready == 0:
            return "⚠️ Design blocked pending DNO engineering data."
        if blocked == 0:
            return "✅ All poles design-ready based on current verification flags."
        return f"ℹ️ Partial readiness: {ready} poles ready, {blocked} blocked."

    @staticmethod
    def _evidence_quality(pole: MergedPole) -> str:
        if pole.field_photo_count >= 3 and pole.notes_content:
            return "MEDIUM" if "NO_POLE_POPUP" in pole.special_flags else "HIGH"
        return "LOW"

    @staticmethod
    def _pct(count: int, total: int) -> str:
        return "0%" if total == 0 else f"{count / total * 100:.0f}%"
