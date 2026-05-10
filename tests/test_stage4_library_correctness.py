"""Stage 4A library correctness and non-integration guards."""

from __future__ import annotations

from pathlib import Path

from app.field_reference import (
    FIELD_SOURCE_STRUCTURED_CAPTURE,
    POPUP_FIELD_GROUPS,
    STRUCTURED_CAPTURE_FIELDS,
    VALID_FIELD_SOURCES,
    get_field_source_label,
    is_valid_field_source,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_structured_capture_source_registered_for_library_provenance() -> None:
    assert FIELD_SOURCE_STRUCTURED_CAPTURE == "structured_capture"
    assert "structured_capture" in VALID_FIELD_SOURCES
    assert is_valid_field_source("structured_capture")
    assert get_field_source_label("structured_capture") == "Stage 4 structured capture"


def test_structured_capture_source_not_added_to_live_popup_catalogue() -> None:
    assert STRUCTURED_CAPTURE_FIELDS == frozenset()
    popup_fields = {field for fields in POPUP_FIELD_GROUPS.values() for field in fields}
    assert "pole_class" not in popup_fields
    assert "equipment_type" not in popup_fields
    assert "voltage_carried" not in popup_fields
    assert "condition" not in popup_fields


def test_stage4_not_live_integrated_into_map_viewer_or_review_os() -> None:
    map_viewer_source = (REPO_ROOT / "app/static/js/map-viewer.js").read_text(encoding="utf-8")
    assert "structured_capture" not in map_viewer_source
    assert "stage4" not in map_viewer_source.lower()
