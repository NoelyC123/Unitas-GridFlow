"""
Validation for field evidence datasets.

Checks for evidence completeness, naming compliance,
and duplicate detection.
"""

import logging

from gridflow.baseline.models import ValidationIssue, ValidationReport
from gridflow.field.models import FieldDataset

logger = logging.getLogger(__name__)


class FieldDatasetValidator:
    """Validate field evidence dataset quality."""

    def validate(self, dataset: FieldDataset) -> ValidationReport:
        """
        Validate dataset and return ValidationReport.

        Args:
            dataset: FieldDataset to validate

        Returns:
            ValidationReport with all detected issues
        """
        issues = []
        warnings = []
        errors = []

        if not dataset.poles:
            warnings.append("Dataset is empty — no poles found")
            return ValidationReport(
                total_poles=0,
                valid_poles=0,
                valid_with_warnings=0,
                warnings=warnings,
                errors=errors,
            )

        issues.extend(self._check_minimum_evidence(dataset))
        issues.extend(self._check_folder_naming(dataset))
        dup_issues, dup_warnings = self._check_duplicate_support_numbers(dataset)
        issues.extend(dup_issues)
        warnings.extend(dup_warnings)
        notes_issues, notes_warnings = self._check_notes_completeness(dataset)
        issues.extend(notes_issues)
        warnings.extend(notes_warnings)

        error_poles = {i.pole_id for i in issues if i.severity == "ERROR"}
        warning_poles = {i.pole_id for i in issues if i.severity == "WARNING"}
        valid_poles = dataset.total_poles - len(error_poles)
        valid_with_warnings = len(warning_poles - error_poles)

        if error_poles:
            errors.append(f"{len(error_poles)} poles have ERROR severity issues")
        if warning_poles:
            warnings.append(f"{len(warning_poles)} poles have WARNING severity issues")

        return ValidationReport(
            total_poles=dataset.total_poles,
            valid_poles=valid_poles,
            valid_with_warnings=valid_with_warnings,
            issues=issues,
            warnings=warnings,
            errors=errors,
        )

    @staticmethod
    def _check_minimum_evidence(dataset: FieldDataset) -> list[ValidationIssue]:
        """Flag poles with insufficient evidence."""
        issues = []

        for pole in dataset.poles:
            if pole.field_photo_count < 3:
                issues.append(
                    ValidationIssue(
                        pole_id=pole.support_no,
                        field="field_photo_count",
                        issue_type="INSUFFICIENT",
                        message=f"Only {pole.field_photo_count} photos (need ≥3)",
                        severity="WARNING",
                    )
                )

            if pole.map_screenshot_count == 0:
                issues.append(
                    ValidationIssue(
                        pole_id=pole.support_no,
                        field="map_screenshot_count",
                        issue_type="MISSING",
                        message="No map screenshots found",
                        severity="WARNING",
                    )
                )

            if not pole.notes_present:
                issues.append(
                    ValidationIssue(
                        pole_id=pole.support_no,
                        field="notes_present",
                        issue_type="MISSING",
                        message="No notes file found",
                        severity="WARNING",
                    )
                )

        return issues

    @staticmethod
    def _check_folder_naming(dataset: FieldDataset) -> list[ValidationIssue]:
        """Validate NN_SUPPORT_* folder naming pattern."""
        issues = []

        for pole in dataset.poles:
            parts = pole.folder_name.split("_")
            valid = (
                len(parts) >= 3
                and parts[0].isdigit()
                and len(parts[0]) == 2
                and parts[1].upper() == "SUPPORT"
            )
            if not valid:
                issues.append(
                    ValidationIssue(
                        pole_id=pole.support_no,
                        field="folder_name",
                        issue_type="INVALID",
                        message=f"Folder does not match NN_SUPPORT_* pattern: {pole.folder_name}",
                        severity="ERROR",
                    )
                )

        return issues

    @staticmethod
    def _check_duplicate_support_numbers(
        dataset: FieldDataset,
    ) -> tuple[list[ValidationIssue], list[str]]:
        """Detect duplicate support numbers."""
        issues = []
        warnings = []

        seen: dict[str, list[str]] = {}
        for pole in dataset.poles:
            if pole.support_no not in seen:
                seen[pole.support_no] = []
            seen[pole.support_no].append(pole.folder_name)

        duplicates = {sno: folders for sno, folders in seen.items() if len(folders) > 1}
        for support_no, folders in duplicates.items():
            issues.append(
                ValidationIssue(
                    pole_id=support_no,
                    field="support_no",
                    issue_type="DUPLICATE",
                    message=f"support_no '{support_no}' found in {len(folders)} folders",
                    severity="WARNING",
                )
            )
            warnings.append(f"Duplicate support_no: {support_no} in {folders}")

        return issues, warnings

    @staticmethod
    def _check_notes_completeness(
        dataset: FieldDataset,
    ) -> tuple[list[ValidationIssue], list[str]]:
        """Warn if notes exist but support_no not found in parsed content."""
        issues = []
        warnings = []

        for pole in dataset.poles:
            if pole.notes_present and pole.parsed_notes:
                notes_support = pole.parsed_notes.get("support_no")
                if not notes_support:
                    issues.append(
                        ValidationIssue(
                            pole_id=pole.support_no,
                            field="parsed_notes.support_no",
                            issue_type="MISSING",
                            message="Notes present but support_no not found in parsed content",
                            severity="WARNING",
                        )
                    )
                    warnings.append(f"No support_no in notes for {pole.folder_name}")

        return issues, warnings
