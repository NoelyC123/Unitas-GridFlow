"""
Data models for baseline asset ingestion.

Defines Pydantic v2 models for representing DNO/Trimble baseline data
with validation, serialization, and type safety.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VoltageLevel(str, Enum):
    """Voltage classification for poles."""

    LV = "LV"  # Low voltage (up to 1kV)
    HV = "HV"  # High voltage (1-35kV)
    EHV = "EHV"  # Extra high voltage (35-230kV)
    UNKNOWN = "UNKNOWN"


class AssetType(str, Enum):
    """Classification of pole/tower type."""

    POLE = "POLE"
    TOWER = "TOWER"
    COLUMN = "COLUMN"
    UNKNOWN = "UNKNOWN"


class AssetStatus(str, Enum):
    """Status of baseline asset."""

    IN_SERVICE = "IN_SERVICE"
    DECOMMISSIONED = "DECOMMISSIONED"
    PLANNED = "PLANNED"
    UNKNOWN = "UNKNOWN"


class BaselinePole(BaseModel):
    """
    Represents a single pole/tower in baseline asset data.

    Attributes:
        pole_id: Unique identifier from DNO system (e.g., "16938106")
        support_no: Support number (e.g., "903203"). May be None for unknown poles.
        easting: OSGB36 easting coordinate (meters)
        northing: OSGB36 northing coordinate (meters)
        latitude: WGS84 latitude. Calculated if not provided.
        longitude: WGS84 longitude. Calculated if not provided.
        route_id: Route identifier. Inferred if missing.
        pole_sequence: Position in route. Calculated if missing.
        voltage_level: Voltage classification (LV/HV/EHV/UNKNOWN)
        asset_type: Type of structure (POLE/TOWER/COLUMN/UNKNOWN)
        feature_code: DNO feature classification code
        status: Service status (IN_SERVICE/DECOMMISSIONED/etc)
        metadata: Additional fields from source CSV
    """

    pole_id: str = Field(..., description="Unique DNO system identifier")
    support_no: Optional[str] = Field(None, description="Support number or asset code")
    easting: float = Field(..., description="OSGB36 easting (meters)")
    northing: float = Field(..., description="OSGB36 northing (meters)")
    latitude: Optional[float] = Field(None, description="WGS84 latitude")
    longitude: Optional[float] = Field(None, description="WGS84 longitude")
    route_id: Optional[str] = Field(None, description="Route identifier")
    pole_sequence: Optional[int] = Field(None, description="Position in route sequence")
    voltage_level: VoltageLevel = Field(default=VoltageLevel.UNKNOWN)
    asset_type: AssetType = Field(default=AssetType.UNKNOWN)
    feature_code: Optional[str] = Field(None, description="DNO feature classification")
    status: AssetStatus = Field(default=AssetStatus.UNKNOWN)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional fields")

    @field_validator("easting")
    def validate_easting(cls, v: float) -> float:
        """Validate easting is within UK bounds (0-700,000m)."""
        if not 0 <= v <= 700000:
            raise ValueError(f"Easting {v} outside UK bounds (0-700000)")
        return v

    @field_validator("northing")
    def validate_northing(cls, v: float) -> float:
        """Validate northing is within UK bounds (0-1,300,000m)."""
        if not 0 <= v <= 1300000:
            raise ValueError(f"Northing {v} outside UK bounds (0-1300000)")
        return v

    @field_validator("latitude")
    def validate_latitude(cls, v: Optional[float]) -> Optional[float]:
        """Validate latitude is within UK bounds (-5 to 60 degrees)."""
        if v is not None and not (-5 <= v <= 60):
            raise ValueError(f"Latitude {v} outside UK bounds (-5 to 60)")
        return v

    @field_validator("longitude")
    def validate_longitude(cls, v: Optional[float]) -> Optional[float]:
        """Validate longitude is within UK bounds (-11 to 3 degrees)."""
        if v is not None and not (-11 <= v <= 3):
            raise ValueError(f"Longitude {v} outside UK bounds (-11 to 3)")
        return v

    model_config = ConfigDict(
        use_enum_values=False,
        json_schema_extra={
            "example": {
                "pole_id": "16938106",
                "support_no": "903203",
                "easting": 354123.45,
                "northing": 456789.12,
                "latitude": 54.123456,
                "longitude": -2.987654,
                "route_id": "ROUTE_001",
                "pole_sequence": 1,
                "voltage_level": "LV",
                "asset_type": "POLE",
                "status": "IN_SERVICE",
                "metadata": {},
            }
        },
    )


class ValidationIssue(BaseModel):
    """Represents a single validation issue found during dataset validation."""

    pole_id: str = Field(..., description="Affected pole identifier")
    field: str = Field(..., description="Field name with issue")
    issue_type: str = Field(..., description="MISSING, INVALID, DUPLICATE, etc")
    message: str = Field(..., description="Human-readable error message")
    severity: str = Field(..., description="ERROR or WARNING")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pole_id": "16938106",
                "field": "support_no",
                "issue_type": "MISSING",
                "message": "Support number not provided",
                "severity": "WARNING",
            }
        },
    )


class ValidationReport(BaseModel):
    """
    Summary report of dataset validation results.

    Attributes:
        total_poles: Total poles in dataset
        valid_poles: Poles with no ERROR issues
        valid_with_warnings: Poles with only WARNING issues
        issues: List of detected issues
        warnings: Summary warnings
        errors: Summary errors
        is_valid: True if zero ERROR severity issues
    """

    total_poles: int
    valid_poles: int
    valid_with_warnings: int
    issues: List[ValidationIssue] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True if dataset has no errors (warnings OK)."""
        return all(issue.severity != "ERROR" for issue in self.issues)

    @property
    def issue_count(self) -> int:
        """Count of all issues."""
        return len(self.issues)

    @property
    def error_count(self) -> int:
        """Count of ERROR severity issues."""
        return sum(1 for issue in self.issues if issue.severity == "ERROR")

    @property
    def warning_count(self) -> int:
        """Count of WARNING severity issues."""
        return sum(1 for issue in self.issues if issue.severity == "WARNING")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_poles": 100,
                "valid_poles": 98,
                "valid_with_warnings": 2,
                "issues": [],
                "warnings": ["2 poles have missing support numbers"],
                "errors": [],
                "is_valid": True,
            }
        },
    )


class BaselineDataset(BaseModel):
    """
    Complete baseline dataset with metadata.

    Represents a parsed and validated baseline CSV export containing
    poles, metadata, and validation results.
    """

    poles: List[BaselinePole] = Field(default_factory=list, description="List of pole records")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Dataset metadata")
    validation_report: Optional[ValidationReport] = Field(None, description="Validation results")

    @property
    def pole_count(self) -> int:
        """Number of poles in dataset."""
        return len(self.poles)

    @property
    def has_coordinates(self) -> bool:
        """True if all poles have OSGB36 coordinates."""
        return all(p.easting and p.northing for p in self.poles)

    @property
    def has_wgs84(self) -> bool:
        """True if all poles have WGS84 coordinates."""
        return all(p.latitude and p.longitude for p in self.poles)

    @property
    def has_routes(self) -> bool:
        """True if all poles have route assignments."""
        return all(p.route_id for p in self.poles)

    @property
    def has_sequences(self) -> bool:
        """True if all poles have sequence numbers."""
        return all(p.pole_sequence is not None for p in self.poles)

    def get_by_pole_id(self, pole_id: str) -> Optional[BaselinePole]:
        """Retrieve pole by pole_id."""
        for pole in self.poles:
            if pole.pole_id == pole_id:
                return pole
        return None

    def get_by_support_no(self, support_no: str) -> Optional[BaselinePole]:
        """Retrieve pole by support_no."""
        for pole in self.poles:
            if pole.support_no == support_no:
                return pole
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "metadata": self.metadata,
            "poles": [pole.model_dump() for pole in self.poles],
            "validation_report": self.validation_report.model_dump()
            if self.validation_report
            else None,
        }

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metadata": {
                    "source_file": "baseline.csv",
                    "format": "ENWL",
                    "ingestion_date": "2026-05-13T14:35:00",
                    "total_poles": 10,
                },
                "poles": [],
                "validation_report": None,
            }
        },
    )
