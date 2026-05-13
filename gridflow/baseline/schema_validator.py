"""
Schema validation for baseline datasets.

Validates data quality, detects issues, and generates comprehensive validation reports.
"""

import logging

from gridflow.baseline.coordinate_transformer import CoordinateTransformer
from gridflow.baseline.models import (
    BaselineDataset,
    ValidationIssue,
    ValidationReport,
)

logger = logging.getLogger(__name__)


class SchemaValidator:
    """
    Validate baseline datasets for data quality and completeness.

    Checks for:
    - Required fields
    - Valid coordinates
    - Duplicate support numbers
    - Data type correctness
    - Missing values
    """

    def validate_dataset(self, dataset: BaselineDataset) -> ValidationReport:
        """
        Validate entire dataset.

        Args:
            dataset: BaselineDataset to validate

        Returns:
            ValidationReport with all issues found
        """
        logger.info(f"Validating dataset with {dataset.pole_count} poles")

        issues = []
        warnings = []
        errors = []

        if dataset.pole_count == 0:
            warnings.append("Dataset is empty")
            return ValidationReport(
                total_poles=0,
                valid_poles=0,
                valid_with_warnings=0,
                issues=[],
                warnings=warnings,
                errors=errors,
            )

        # Check required fields
        issues.extend(self._check_required_fields(dataset))

        # Check coordinates
        issues.extend(self._check_coordinate_validity(dataset))

        # Check for duplicates
        dup_issues, dup_warnings = self._check_duplicates(dataset)
        issues.extend(dup_issues)
        warnings.extend(dup_warnings)

        # Check data types
        issues.extend(self._check_data_types(dataset))

        # Calculate summary
        error_poles = {issue.pole_id for issue in issues if issue.severity == "ERROR"}
        warning_poles = {issue.pole_id for issue in issues if issue.severity == "WARNING"}
        valid_poles = dataset.pole_count - len(error_poles)
        valid_with_warnings = len(warning_poles - error_poles)

        if error_poles:
            errors.append(f"{len(error_poles)} poles have ERROR severity issues")
        if warning_poles:
            warnings.append(f"{len(warning_poles)} poles have WARNING severity issues")

        report = ValidationReport(
            total_poles=dataset.pole_count,
            valid_poles=valid_poles,
            valid_with_warnings=valid_with_warnings,
            issues=issues,
            warnings=warnings,
            errors=errors,
        )

        logger.info(
            f"Validation complete: {valid_poles} valid, {len(error_poles)} with errors, {len(warning_poles)} with warnings"
        )
        return report

    def _check_required_fields(self, dataset: BaselineDataset) -> list[ValidationIssue]:
        """Check that all poles have required fields."""
        issues = []

        for pole in dataset.poles:
            # pole_id is always required
            if not pole.pole_id:
                issues.append(
                    ValidationIssue(
                        pole_id="UNKNOWN",
                        field="pole_id",
                        issue_type="MISSING",
                        message="pole_id is required",
                        severity="ERROR",
                    )
                )

            # easting/northing are required
            if pole.easting is None:
                issues.append(
                    ValidationIssue(
                        pole_id=pole.pole_id,
                        field="easting",
                        issue_type="MISSING",
                        message="easting coordinate is required",
                        severity="ERROR",
                    )
                )

            if pole.northing is None:
                issues.append(
                    ValidationIssue(
                        pole_id=pole.pole_id,
                        field="northing",
                        issue_type="MISSING",
                        message="northing coordinate is required",
                        severity="ERROR",
                    )
                )

            # support_no is recommended but not required
            if not pole.support_no:
                issues.append(
                    ValidationIssue(
                        pole_id=pole.pole_id,
                        field="support_no",
                        issue_type="MISSING",
                        message="support_no not provided",
                        severity="WARNING",
                    )
                )

        return issues

    def _check_coordinate_validity(self, dataset: BaselineDataset) -> list[ValidationIssue]:
        """Check that coordinates are valid and within UK bounds."""
        issues = []
        transformer = CoordinateTransformer()

        for pole in dataset.poles:
            # Check OSGB36 bounds
            if pole.easting is not None and pole.northing is not None:
                if not transformer.validate_osgb36(pole.easting, pole.northing):
                    issues.append(
                        ValidationIssue(
                            pole_id=pole.pole_id,
                            field="easting/northing",
                            issue_type="INVALID",
                            message=f"Coordinates outside UK bounds: ({pole.easting}, {pole.northing})",
                            severity="ERROR",
                        )
                    )

            # Check WGS84 bounds if present
            if pole.latitude is not None and pole.longitude is not None:
                if not transformer.validate_wgs84(pole.latitude, pole.longitude):
                    issues.append(
                        ValidationIssue(
                            pole_id=pole.pole_id,
                            field="latitude/longitude",
                            issue_type="INVALID",
                            message=f"WGS84 coordinates outside UK bounds: ({pole.latitude}, {pole.longitude})",
                            severity="WARNING",
                        )
                    )

        return issues

    def _check_duplicates(
        self, dataset: BaselineDataset
    ) -> tuple[list[ValidationIssue], list[str]]:
        """Check for duplicate support numbers and pole IDs."""
        issues = []
        warnings = []

        # Check for duplicate pole_ids
        pole_ids = {}
        for pole in dataset.poles:
            if pole.pole_id in pole_ids:
                pole_ids[pole.pole_id] += 1
            else:
                pole_ids[pole.pole_id] = 1

        duplicate_ids = {pid: count for pid, count in pole_ids.items() if count > 1}
        if duplicate_ids:
            for pole_id, count in duplicate_ids.items():
                issues.append(
                    ValidationIssue(
                        pole_id=pole_id,
                        field="pole_id",
                        issue_type="DUPLICATE",
                        message=f"pole_id appears {count} times",
                        severity="ERROR",
                    )
                )
            warnings.append(f"{len(duplicate_ids)} duplicate pole_id(s) found")

        # Check for duplicate support_nos
        support_nos = {}
        for pole in dataset.poles:
            if pole.support_no:
                if pole.support_no in support_nos:
                    support_nos[pole.support_no] += 1
                else:
                    support_nos[pole.support_no] = 1

        duplicate_support = {sno: count for sno, count in support_nos.items() if count > 1}
        if duplicate_support:
            for support_no, count in duplicate_support.items():
                # Find all poles with this support_no
                for pole in dataset.poles:
                    if pole.support_no == support_no:
                        issues.append(
                            ValidationIssue(
                                pole_id=pole.pole_id,
                                field="support_no",
                                issue_type="DUPLICATE",
                                message=f"support_no '{support_no}' appears {count} times",
                                severity="WARNING",
                            )
                        )
                        break  # Only add once per support_no
            warnings.append(f"{len(duplicate_support)} duplicate support_no(s) found")

        return issues, warnings

    def _check_data_types(self, dataset: BaselineDataset) -> list[ValidationIssue]:
        """Check that data types are correct."""
        issues = []

        for pole in dataset.poles:
            # Check numeric coordinates
            if pole.easting is not None and not isinstance(pole.easting, (int, float)):
                issues.append(
                    ValidationIssue(
                        pole_id=pole.pole_id,
                        field="easting",
                        issue_type="INVALID",
                        message=f"easting must be numeric, got {type(pole.easting).__name__}",
                        severity="ERROR",
                    )
                )

            if pole.northing is not None and not isinstance(pole.northing, (int, float)):
                issues.append(
                    ValidationIssue(
                        pole_id=pole.pole_id,
                        field="northing",
                        issue_type="INVALID",
                        message=f"northing must be numeric, got {type(pole.northing).__name__}",
                        severity="ERROR",
                    )
                )

            # Check sequence is integer
            if pole.pole_sequence is not None and not isinstance(pole.pole_sequence, int):
                issues.append(
                    ValidationIssue(
                        pole_id=pole.pole_id,
                        field="pole_sequence",
                        issue_type="INVALID",
                        message=f"pole_sequence must be integer, got {type(pole.pole_sequence).__name__}",
                        severity="WARNING",
                    )
                )

        return issues
