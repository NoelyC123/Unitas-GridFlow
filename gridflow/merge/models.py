"""
Data models for merge engine output.

Pydantic v2 models for MergedPole and MergedDataset (Stage 4C.4).
"""

from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field


class MergedPole(BaseModel):
    """Unified pole record combining baseline, field, and matching evidence."""

    model_config = ConfigDict(use_enum_values=False)

    # --- Identity (from baseline, authoritative) ---
    support_no: str
    pole_id: Optional[str] = None
    folder_name: Optional[str] = None
    match_confidence: str = "UNMATCHED"
    match_type: str = "UNMATCHED"

    # --- Coordinates (from baseline) ---
    easting: Optional[float] = None
    northing: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    route_id: Optional[str] = None
    pole_sequence: Optional[int] = None

    # --- Baseline engineering specs ---
    baseline_voltage: Optional[str] = None
    baseline_asset_type: Optional[str] = None
    baseline_status: Optional[str] = None

    # --- Field condition (from notes) ---
    condition_overall: Optional[str] = None
    condition_base: Optional[str] = None
    condition_top: Optional[str] = None
    defects: list[str] = Field(default_factory=list)
    access_constraints: Optional[str] = None
    equipment_observed: list[str] = Field(default_factory=list)
    warning_signs_present: Optional[bool] = None
    stay_present: Optional[bool] = None

    # --- Field evidence ---
    field_photo_count: int = 0
    photo_paths: list[str] = Field(default_factory=list)
    notes_content: Optional[str] = None
    parsed_notes: dict[str, Any] = Field(default_factory=dict)

    # --- Flags ---
    special_flags: list[str] = Field(default_factory=list)
    conflict_flags: list[str] = Field(default_factory=list)

    # --- Verification requirements ---
    voltage_verification_required: bool = True
    conductor_verification_required: bool = True
    pole_class_verification_required: bool = True
    condition_verification_required: bool = False
    identity_verification_required: bool = False
    equipment_conflict_flag: bool = False

    # --- Design status ---
    design_blocked: bool = True
    design_ready: bool = False
    review_required: bool = False
    designer_actions: list[str] = Field(default_factory=list)

    metadata: dict[str, Any] = Field(default_factory=dict)


class MergedDataset(BaseModel):
    """Complete merged dataset combining baseline, field, and matching evidence."""

    model_config = ConfigDict(use_enum_values=False)

    baseline_source: str = ""
    field_source: str = ""
    merge_date: str = ""

    total_poles_baseline: int = 0
    total_poles_field: int = 0
    total_matched: int = 0
    total_unmatched_baseline: int = 0
    total_unmatched_field: int = 0

    design_ready_count: int = 0
    design_blocked_count: int = 0
    review_required_count: int = 0

    high_confidence_count: int = 0
    medium_confidence_count: int = 0
    low_confidence_count: int = 0

    poles: list[MergedPole] = Field(default_factory=list)
    unmatched_baseline: list[dict[str, Any]] = Field(default_factory=list)
    unmatched_field: list[dict[str, Any]] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
