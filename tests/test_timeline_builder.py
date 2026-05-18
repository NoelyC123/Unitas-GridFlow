from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from gridflow.timeline import EvidenceTimelineBuilder


def _write_file(path: Path, content: str, when: datetime) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    ts = when.timestamp()
    path.touch()
    path.chmod(0o644)
    import os

    os.utime(path, (ts, ts))


def _combined_fixture(
    tmp_path: Path, *, with_photos: bool = True, with_conflicts: bool = True
) -> dict:
    pole_dir = tmp_path / "survey" / "enwl_enrichment_clean" / "05_SUPPORT_900344"
    notes_path = pole_dir / "notes" / "pole_notes.md"
    field_photos = pole_dir / "field_photos"
    survey_dt = datetime(2026, 5, 16, 9, 0, tzinfo=UTC)
    photo_dt = datetime(2026, 5, 16, 14, 30, tzinfo=UTC)

    _write_file(notes_path, "# Notes\nSupport number: 900344\n", survey_dt)
    if with_photos:
        _write_file(field_photos / "IMG_0001.JPG", "a", photo_dt)
        _write_file(field_photos / "IMG_0002.JPG", "b", photo_dt)

    return {
        "pole_id": "05_SUPPORT_900344",
        "support_no": "900344",
        "pole_fid": "16869657",
        "spn": "61090H00344",
        "photo_count": 2 if with_photos else 0,
        "direct_equipment_records": [
            {
                "fid": "73189925",
                "feature_type": "Fault Making Switch",
                "fid_polestructure": "16869657",
                "link_basis": "fid_polestructure_match",
            }
        ],
        "contributing_files": {
            "pole_folder": str(pole_dir),
            "pole_notes": str(notes_path),
            "field_photos": str(field_photos),
        },
        "linking": {
            "linking_method": "fid_polestructure",
            "confidence": "HIGH",
            "manual_confirmation_required": False,
        },
        "readiness": {
            "readiness_status": "review_required",
            "readiness_confidence": "high",
            "readiness_blockers": [],
            "readiness_warnings": ["Conductor route-level only"],
            "assessment_timestamp": "2026-05-18T10:00:00+00:00",
        },
        "conflicts": (
            [
                {
                    "description": "Field GPS and ENWL coordinates differ by more than 50m.",
                    "severity": "WARNING",
                },
                {
                    "description": "Visible field support number differs from ENWL support number.",
                    "severity": "CRITICAL",
                },
            ]
            if with_conflicts
            else []
        ),
    }


def test_timeline_built_from_complete_combined_evidence(tmp_path: Path) -> None:
    combined = _combined_fixture(tmp_path)
    timeline = EvidenceTimelineBuilder().build("05_SUPPORT_900344", combined)

    assert timeline.pole_id == "05_SUPPORT_900344"
    event_types = [event.event_type for event in timeline.events]
    assert "survey_captured" in event_types
    assert "enwl_record_found" in event_types
    assert "link_confirmed" in event_types
    assert "photo_captured" in event_types
    assert "readiness_assessed" in event_types
    assert event_types.count("conflict_detected") == 2


def test_events_sorted_known_dates_before_unknown(tmp_path: Path) -> None:
    combined = _combined_fixture(tmp_path)
    timeline = EvidenceTimelineBuilder().build("05_SUPPORT_900344", combined)

    assert [event.event_type for event in timeline.events[:3]] == [
        "survey_captured",
        "photo_captured",
        "readiness_assessed",
    ]
    assert all(event.date == "unknown" for event in timeline.events[3:])


def test_photo_event_uses_correct_count(tmp_path: Path) -> None:
    combined = _combined_fixture(tmp_path)
    timeline = EvidenceTimelineBuilder().build("05_SUPPORT_900344", combined)
    photo_event = next(event for event in timeline.events if event.event_type == "photo_captured")
    assert photo_event.description == "2 field photos captured."
    assert photo_event.confidence == "HIGH"


def test_timeline_zero_photos_handled_gracefully(tmp_path: Path) -> None:
    combined = _combined_fixture(tmp_path, with_photos=False)
    timeline = EvidenceTimelineBuilder().build("05_SUPPORT_900344", combined)
    photo_event = next(event for event in timeline.events if event.event_type == "photo_captured")
    assert photo_event.description == "No field photos detected for this pole."
    assert photo_event.confidence == "LOW"
    assert photo_event.date == "unknown"


def test_timeline_zero_conflicts_handled_gracefully(tmp_path: Path) -> None:
    combined = _combined_fixture(tmp_path, with_conflicts=False)
    timeline = EvidenceTimelineBuilder().build("05_SUPPORT_900344", combined)
    assert [event for event in timeline.events if event.event_type == "conflict_detected"] == []


def test_partial_evidence_does_not_crash(tmp_path: Path) -> None:
    pole_dir = tmp_path / "survey" / "enwl_enrichment_clean" / "01_SUPPORT_000001"
    combined = {
        "pole_id": "01_SUPPORT_000001",
        "support_no": None,
        "photo_count": 0,
        "contributing_files": {
            "pole_folder": str(pole_dir),
            "pole_notes": str(pole_dir / "notes" / "pole_notes.md"),
            "field_photos": str(pole_dir / "field_photos"),
        },
        "linking": {},
        "readiness": {},
        "conflicts": [],
    }
    timeline = EvidenceTimelineBuilder().build("01_SUPPORT_000001", combined)
    assert timeline.pole_id == "01_SUPPORT_000001"
    assert len(timeline.events) >= 2


def test_conflict_events_one_per_conflict(tmp_path: Path) -> None:
    combined = _combined_fixture(tmp_path, with_conflicts=True)
    timeline = EvidenceTimelineBuilder().build("05_SUPPORT_900344", combined)
    conflict_events = [
        event for event in timeline.events if event.event_type == "conflict_detected"
    ]
    assert len(conflict_events) == 2
    assert all(event.confidence == "LOW" for event in conflict_events)
