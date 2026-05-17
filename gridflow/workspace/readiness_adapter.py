"""Stage 6E workspace adapter for design-readiness display.

Maps from Stage 6E readiness assessment results (when available) or
from existing MergedPole verification flags (as fallback) to the four
workspace display states defined in 129_STAGE6E_READINESS_LOGIC_SPEC.md.

Never modifies design_ready or any verification flag.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from gridflow.merge.models import MergedPole

READINESS_FILE = "06_readiness_assessment.json"

DISPLAY_READY = "ready"
DISPLAY_REVIEW = "review_required"
DISPLAY_NOT_READY = "not_ready"
DISPLAY_INSUFFICIENT = "insufficient_evidence"

CONDUCTOR_CAUTION = "Conductor evidence is route-level provenance only — not per-span confirmed"


@dataclass
class PoleReadinessDisplay:
    """Readiness display state for one pole in the workspace."""

    available: bool
    display_level: str
    blockers: list[str] = field(default_factory=list)
    cautions: list[str] = field(default_factory=list)
    readiness_level: str | None = None
    source: str = "merge_pipeline"


@dataclass
class JobReadinessSummary:
    """Job-level readiness counts for the workspace header."""

    available: bool
    ready_count: int = 0
    review_count: int = 0
    not_ready_count: int = 0
    insufficient_count: int = 0
    total_poles: int = 0
    source: str = "merge_pipeline"


def load_job_readiness_summary(
    job_dir: Path,
    poles: list[MergedPole],
) -> JobReadinessSummary:
    """Return readiness counts for the job header.

    Loads Stage 6E assessment from {job_dir}/06_readiness_assessment.json
    when present. Falls back to deriving counts from MergedPole flags.
    """
    assessment = _load_assessment(job_dir)
    if assessment is not None:
        return _summary_from_assessment(assessment, len(poles))
    return _summary_from_poles(poles)


def load_pole_readiness(job_dir: Path, pole: MergedPole) -> PoleReadinessDisplay:
    """Return readiness display state for one pole.

    Loads Stage 6E assessment when present; falls back to MergedPole flags.
    Returns PoleReadinessDisplay(available=False) only when the job dir itself
    is absent — the fallback is always attempted.
    """
    assessment = _load_assessment(job_dir)
    if assessment is not None:
        record = assessment.get(pole.support_no)
        if record:
            return _display_from_record(record)

    return _display_from_pole(pole)


def _load_assessment(job_dir: Path) -> dict[str, Any] | None:
    path = Path(job_dir) / READINESS_FILE
    if not path.exists():
        return None
    try:
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data, dict):
            return data
        if isinstance(data, list):
            return {
                item["support_no"]: item
                for item in data
                if isinstance(item, dict) and "support_no" in item
            }
    except Exception:
        pass
    return None


def _display_from_record(record: dict[str, Any]) -> PoleReadinessDisplay:
    level = (record.get("readiness_level") or "").strip()
    blockers = list(record.get("readiness_blockers") or [])
    cautions = list(record.get("readiness_cautions") or [])

    if level == "DESIGN_READY":
        display = DISPLAY_READY
    elif level == "DESIGN_READY_WITH_CAUTIONS":
        display = DISPLAY_REVIEW
    elif level == "DESIGN_BLOCKED":
        display = DISPLAY_NOT_READY
    else:
        display = DISPLAY_INSUFFICIENT

    return PoleReadinessDisplay(
        available=True,
        display_level=display,
        blockers=blockers,
        cautions=cautions,
        readiness_level=level or None,
        source="stage_6e",
    )


def _display_from_pole(pole: MergedPole) -> PoleReadinessDisplay:
    """Derive display state from MergedPole verification flags."""
    blockers: list[str] = []

    if pole.voltage_verification_required:
        blockers.append("Voltage not confirmed — DNO engineering records required")
    if pole.conductor_verification_required:
        blockers.append(
            "Conductor specification not confirmed at span level — route-level evidence only"
        )
    if pole.pole_class_verification_required:
        blockers.append("Pole class / strength rating not confirmed from DNO engineering records")
    if pole.condition_verification_required:
        blockers.append("Pole condition review required")
    if pole.identity_verification_required:
        blockers.append("Pole identity confirmation required")
    if pole.equipment_conflict_flag:
        blockers.append("Equipment conflict detected")

    for action in pole.designer_actions or []:
        if action not in blockers:
            blockers.append(action)

    if pole.design_ready:
        return PoleReadinessDisplay(
            available=True,
            display_level=DISPLAY_READY,
            source="merge_pipeline",
        )

    if blockers:
        return PoleReadinessDisplay(
            available=True,
            display_level=DISPLAY_NOT_READY,
            blockers=blockers,
            cautions=[CONDUCTOR_CAUTION],
            source="merge_pipeline",
        )

    if pole.design_blocked:
        return PoleReadinessDisplay(
            available=True,
            display_level=DISPLAY_NOT_READY,
            blockers=["Design blocked — review verification flags"],
            cautions=[CONDUCTOR_CAUTION],
            source="merge_pipeline",
        )

    return PoleReadinessDisplay(
        available=True,
        display_level=DISPLAY_INSUFFICIENT,
        source="merge_pipeline",
    )


def _summary_from_assessment(
    assessment: dict[str, Any],
    total: int,
) -> JobReadinessSummary:
    ready = review = blocked = insufficient = 0
    for record in assessment.values():
        level = (record.get("readiness_level") or "").strip()
        if level == "DESIGN_READY":
            ready += 1
        elif level == "DESIGN_READY_WITH_CAUTIONS":
            review += 1
        elif level == "DESIGN_BLOCKED":
            blocked += 1
        else:
            insufficient += 1
    return JobReadinessSummary(
        available=True,
        ready_count=ready,
        review_count=review,
        not_ready_count=blocked,
        insufficient_count=insufficient,
        total_poles=total,
        source="stage_6e",
    )


def _summary_from_poles(poles: list[MergedPole]) -> JobReadinessSummary:
    ready = review = blocked = insufficient = 0
    for pole in poles:
        lvl = _display_from_pole(pole).display_level
        if lvl == DISPLAY_READY:
            ready += 1
        elif lvl == DISPLAY_REVIEW:
            review += 1
        elif lvl == DISPLAY_NOT_READY:
            blocked += 1
        else:
            insufficient += 1
    return JobReadinessSummary(
        available=True,
        ready_count=ready,
        review_count=review,
        not_ready_count=blocked,
        insufficient_count=insufficient,
        total_poles=len(poles),
        source="merge_pipeline",
    )
