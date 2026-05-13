"""
Data models for baseline-to-field matching.

Pydantic v2 models representing match results and registers for Stage 4C.3.
"""

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class MatchResult(BaseModel):
    """Result of matching a single baseline pole to field evidence."""

    model_config = ConfigDict(use_enum_values=False)

    baseline_pole_id: str = Field(..., description="Baseline pole_id")
    baseline_support_no: str = Field(..., description="Baseline support number")
    field_folder: Optional[str] = Field(None, description="Matched field folder name")
    field_support_no: Optional[str] = Field(None, description="Matched field support number")
    match_type: str = Field(default="UNMATCHED", description="EXACT/PROXIMITY/UNMATCHED")
    match_confidence: str = Field(default="UNMATCHED", description="HIGH/MEDIUM/LOW/UNMATCHED")
    confidence_reasons: list[str] = Field(default_factory=list)
    conflict_flags: list[str] = Field(default_factory=list)
    review_required: bool = Field(default=False)
    metadata: dict[str, Any] = Field(default_factory=dict)


class MatchRegisterEntry(BaseModel):
    """Single row in the match register CSV/report."""

    model_config = ConfigDict(use_enum_values=False)

    support_no: str
    baseline_pole_id: Optional[str] = None
    field_folder: Optional[str] = None
    match_confidence: str = "UNMATCHED"
    match_type: str = "UNMATCHED"
    identity_verified: bool = False
    review_required: bool = False
    conflict_flags: list[str] = Field(default_factory=list)


class MatchRegister(BaseModel):
    """Complete baseline-to-field match register."""

    model_config = ConfigDict(use_enum_values=False)

    baseline_total: int = 0
    field_total: int = 0
    matched: int = 0
    unmatched_baseline: int = 0
    unmatched_field: int = 0
    match_rate: float = 0.0
    high_confidence: int = 0
    medium_confidence: int = 0
    low_confidence: int = 0
    entries: list[MatchRegisterEntry] = Field(default_factory=list)

    def compute_stats(self) -> None:
        """Recalculate statistics from entries."""
        self.high_confidence = sum(1 for e in self.entries if e.match_confidence == "HIGH")
        self.medium_confidence = sum(1 for e in self.entries if e.match_confidence == "MEDIUM")
        self.low_confidence = sum(1 for e in self.entries if e.match_confidence == "LOW")
        matched = sum(1 for e in self.entries if e.match_type != "UNMATCHED")
        self.matched = matched
        if self.baseline_total > 0:
            self.match_rate = (matched / self.baseline_total) * 100
