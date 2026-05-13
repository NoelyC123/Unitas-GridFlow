"""
Data models for field evidence.

Pydantic v2 models representing scanned field evidence, parsed notes,
and quality assessments for Stage 4C.2.
"""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class FieldPole(BaseModel):
    """Represents a single pole folder scanned from field evidence."""

    model_config = ConfigDict(use_enum_values=False)

    folder_name: str = Field(..., description="Full folder name e.g. 01_SUPPORT_903203_LV_TERMINAL")
    support_no: str = Field(..., description="Extracted support number e.g. '903203'")
    sequence_no: Optional[int] = Field(None, description="Leading sequence NN")
    voltage_category: str = Field(default="UNKNOWN", description="LV/HV/EHV/UNKNOWN")
    pole_descriptor: Optional[str] = Field(None, description="Descriptor after voltage")

    field_photo_count: int = Field(default=0, description="Number of field photos")
    map_screenshot_count: int = Field(default=0, description="Number of map screenshots")
    notes_present: bool = Field(default=False)
    notes_content: Optional[str] = Field(None, description="Raw notes text")
    parsed_notes: dict[str, Any] = Field(default_factory=dict)

    evidence_quality: str = Field(default="LOW", description="HIGH/MEDIUM/LOW")
    map_popup_present: str = Field(default="uncertain", description="yes/uncertain")
    identity_confidence: str = Field(default="LOW", description="HIGH/MEDIUM/LOW")
    special_flags: list[str] = Field(default_factory=list)

    photo_paths: list[str] = Field(default_factory=list)
    screenshot_paths: list[str] = Field(default_factory=list)
    notes_path: Optional[str] = Field(None)
    metadata: dict[str, Any] = Field(default_factory=dict)


class FieldDataset(BaseModel):
    """Complete field evidence dataset scanned from a root folder."""

    model_config = ConfigDict(use_enum_values=False)

    dataset_path: str
    scan_date: str
    total_poles: int = 0
    poles: list[FieldPole] = Field(default_factory=list)
    evidence_summary: dict[str, Any] = Field(default_factory=dict)

    def get_by_support_no(self, support_no: str) -> Optional[FieldPole]:
        """Retrieve pole by support number."""
        for pole in self.poles:
            if pole.support_no == support_no:
                return pole
        return None
