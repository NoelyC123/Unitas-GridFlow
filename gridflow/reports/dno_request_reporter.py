"""DNO data request report for Stage 5A pilot output packs."""

from datetime import datetime
from typing import List

from gridflow.merge.models import MergedPole


class DNORequestReporter:
    """Generate an actionable DNO engineering data request."""

    def generate(self, merged_poles: List[MergedPole]) -> str:
        """Return Markdown report generated only from MergedPole records."""
        poles = list(merged_poles)
        blocked = [p for p in poles if not p.design_ready]
        lines = [
            "# DNO Data Request - Job GridFlow Pipeline",
            "",
            f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Status:** {len(blocked)} poles require DNO engineering data",
            "",
            "## Summary",
            "",
            self._summary_text(poles, blocked),
            "",
        ]

        sections = [
            (
                "CRITICAL",
                "Missing Conductor Specification",
                self._by_flag(poles, "conductor_verification_required", "conductor_spec_missing"),
                [
                    "Conductor type (AAC, ACSR, AAAC, XLPE, Cu)",
                    "Conductor size and material",
                ],
                "Cannot proceed with span sag calculations, loading analysis, or clearance verification until conductor specification is obtained.",
            ),
            (
                "CRITICAL",
                "Missing Pole Class",
                self._by_flag(poles, "pole_class_verification_required", "pole_class_missing"),
                [
                    "Pole class or strength rating",
                    "Design load capacity and manufactured height where available",
                ],
                "Cannot make retention, replacement, stay, or loading decisions without pole class or strength specification.",
            ),
            (
                "HIGH",
                "Voltage Conflicts",
                self._voltage_conflict_poles(poles),
                [
                    "Correct operating voltage for each affected pole",
                    "Circuit diagram or voltage boundary confirmation where transitions exist",
                ],
                "Voltage uncertainty creates safety risk, incorrect clearance calculations, and potential statutory non-compliance.",
                "Baseline voltage differs from field-captured voltage or field voltage is uncertain.",
            ),
            (
                "HIGH",
                "Identity Confirmation Required",
                self._by_flag(
                    poles, "identity_verification_required", "identity_confirmation_required"
                ),
                [
                    "Pole identity confirmation via DNO asset register",
                    "Alternative support number formats if baseline notation differs",
                ],
                "Identity errors can lead to wrong-pole design, construction errors, asset register mismatch, and safety incidents.",
                "Match confidence is below HIGH or support number variant requires confirmation.",
            ),
            (
                "MEDIUM",
                "Equipment Conflicts",
                self._equipment_conflict_poles(poles),
                [
                    "Confirm equipment present on each affected pole",
                    "Provide current DNO equipment record if baseline is out of date",
                ],
                "Equipment discrepancies can change design assumptions, isolation planning, and site risk controls.",
                "Field evidence and baseline equipment context differ.",
            ),
            (
                "MEDIUM",
                "Condition Verification Required",
                self._by_flag(
                    poles, "condition_verification_required", "condition_verification_required"
                ),
                [
                    "Current DNO inspection outcome",
                    "Re-inspection decision or condition note for affected pole",
                ],
                "Condition concerns may affect retention, replacement, access planning, or construction safety.",
            ),
        ]

        for section in sections:
            lines.extend(self._section(*section))

        if not blocked:
            lines.extend(
                [
                    "## No DNO Request Blockers",
                    "",
                    "No poles are currently blocked by the verification flags available in the merged records.",
                    "",
                ]
            )

        lines.extend(
            [
                "## Next Steps",
                "",
                "1. Review this request with the internal project team.",
                "2. Customize for the DNO submission format.",
                "3. Submit via the established DNO data request process.",
                "4. Track the request until DNO data is received.",
                "5. Re-run GridFlow after DNO data is available to verify design-readiness improvement.",
                "",
                "This report distinguishes DNO data gaps from pipeline failure: matched poles can remain design-blocked because engineering records are missing.",
                "",
                "---",
                "*Report generated by GridFlow Stage 5A.2*",
            ]
        )
        return "\n".join(lines)

    @staticmethod
    def _summary_text(poles: list[MergedPole], blocked: list[MergedPole]) -> str:
        if not poles:
            return "No merged poles were supplied. No DNO request can be generated."
        high = sum(1 for p in poles if DNORequestReporter._evidence_quality(p) == "HIGH")
        quality_pct = high / len(poles) * 100
        return (
            f"This job requires DNO engineering specifications for {len(blocked)} "
            f"of {len(poles)} poles before design can proceed. Field and baseline "
            f"reconciliation is not the same as engineering approval; {quality_pct:.0f}% "
            "of evidence packages are HIGH quality, but missing DNO records can still block design."
        )

    @staticmethod
    def _section(priority, title, poles, required, impact, issue=None) -> list[str]:
        if not poles:
            return []
        icon = DNORequestReporter._priority_icon(priority)
        reference = DNORequestReporter._get_standard_ref(title)
        lines = [
            f"## {icon} {priority} PRIORITY - {title}",
            "",
            f"**Poles affected:** {', '.join(p.support_no for p in poles)}",
            "",
        ]
        if issue:
            lines.extend([f"**Issue:** {issue}", ""])
        lines.extend(["**Required from DNO:**"])
        lines.extend(f"- {item}" for item in required)
        lines.extend(["", f"**Design impact:** {impact}", ""])
        if reference:
            lines.extend([f"**Reference:** {reference}", ""])
        return lines

    @staticmethod
    def _priority_icon(priority: str) -> str:
        return {"CRITICAL": "⚠️", "HIGH": "❌", "MEDIUM": "ℹ️"}.get(priority, "ℹ️")

    @staticmethod
    def _get_standard_ref(section_type: str) -> str:
        refs = {
            "Missing Conductor Specification": (
                "ENA G7/4 Section 3.2 (conductor selection); BS EN 50341-1"
            ),
            "Missing Pole Class": "ENA G7/4 Section 2.3 (pole classification); ETR 132",
            "Voltage Conflicts": "ESQCR 2002 Regulation 19 (statutory clearances)",
            "Identity Confirmation Required": "ENA P28 (records and plans policy)",
            "Equipment Conflicts": "ETR 132 (overhead line design assumptions)",
            "Condition Verification Required": "ESQCR 2002 safety obligations",
        }
        return refs.get(section_type, "")

    @classmethod
    def _by_flag(cls, poles: list[MergedPole], attr: str, metadata_key: str) -> list[MergedPole]:
        return [p for p in poles if getattr(p, attr, False) or cls._metadata_flag(p, metadata_key)]

    @staticmethod
    def _voltage_conflict_poles(poles: list[MergedPole]) -> list[MergedPole]:
        return [
            p
            for p in poles
            if "VOLTAGE_CONFLICT" in p.conflict_flags
            or p.voltage_verification_required
            or DNORequestReporter._metadata_flag(p, "voltage_conflict")
        ]

    @staticmethod
    def _equipment_conflict_poles(poles: list[MergedPole]) -> list[MergedPole]:
        return [
            p
            for p in poles
            if "EQUIPMENT_CONFLICT" in p.conflict_flags
            or DNORequestReporter._metadata_flag(p, "equipment_conflict")
        ]

    @staticmethod
    def _metadata_flag(pole: MergedPole, key: str) -> bool:
        flags = pole.metadata.get("verification_flags", {})
        return bool(flags.get(key)) if isinstance(flags, dict) else False

    @staticmethod
    def _evidence_quality(pole: MergedPole) -> str:
        if pole.field_photo_count >= 3 and pole.notes_content:
            return "MEDIUM" if "NO_POLE_POPUP" in pole.special_flags else "HIGH"
        return "LOW"
