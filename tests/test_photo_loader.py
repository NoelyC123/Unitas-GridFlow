from __future__ import annotations

from pathlib import Path

from gridflow.evidence_combiner import combine_pole_evidence
from gridflow.photos import load_pole_photos, load_survey_photos


def test_load_pole_photos_real_folder():
    pole_dir = Path("real_pilot_data/P_LOCAL_002/enwl_enrichment_clean/05_SUPPORT_900344")
    if not pole_dir.exists():
        return

    photo_set = load_pole_photos(pole_dir)
    assert photo_set.pole_id == "05_SUPPORT_900344"
    assert photo_set.photo_count == 9
    assert photo_set.photo_files[0].photo_type == "full_pole"
    assert "full_pole" in photo_set.photo_types_present


def test_detect_photo_types_from_filename_patterns(tmp_path):
    pole_dir = tmp_path / "01_SUPPORT_123456"
    photos_dir = pole_dir / "field_photos"
    photos_dir.mkdir(parents=True)
    for name in (
        "pole_top_view.jpg",
        "pole_base_view.jpg",
        "transformer_detail.jpg",
        "span_east.jpg",
        "overview_access.jpg",
        "IMG_0001.jpg",
    ):
        (photos_dir / name).write_bytes(b"img")

    photo_set = load_pole_photos(pole_dir)
    counts = photo_set.count_by_type()
    assert counts["pole_top"] == 1
    assert counts["pole_base"] == 1
    assert counts["equipment"] == 1
    assert counts["span"] == 1
    assert counts["context"] == 1
    assert counts["full_pole"] == 1


def test_missing_folder_graceful(tmp_path):
    pole_dir = tmp_path / "02_SUPPORT_654321"
    pole_dir.mkdir()

    photo_set = load_pole_photos(pole_dir)
    assert photo_set.photo_count == 0
    assert photo_set.photo_files == []


def test_count_photos_by_type(tmp_path):
    pole_dir = tmp_path / "03_SUPPORT_777777"
    photos_dir = pole_dir / "field_photos"
    photos_dir.mkdir(parents=True)
    (photos_dir / "IMG_0001.jpg").write_bytes(b"a")
    (photos_dir / "switch_closeup.jpg").write_bytes(b"b")
    (photos_dir / "conductor_span.jpg").write_bytes(b"c")

    counts = load_pole_photos(pole_dir).count_by_type()
    assert counts["full_pole"] == 1
    assert counts["equipment"] == 1
    assert counts["span"] == 1


def test_all_poles_summary():
    survey_root = Path("real_pilot_data/P_LOCAL_002")
    if not survey_root.exists():
        return

    photo_sets = load_survey_photos(survey_root)
    assert len(photo_sets) >= 10
    assert "05_SUPPORT_900344" in photo_sets
    assert photo_sets["05_SUPPORT_900344"].photo_count == 9


def test_photos_added_to_combined_evidence():
    survey_root = Path("real_pilot_data/P_LOCAL_002")
    trace_path = survey_root / "enwl_trace" / "enwl_trace_10924865_with_ratings.geojson"
    if not survey_root.exists() or not trace_path.exists():
        return

    record = combine_pole_evidence(
        survey_root=survey_root,
        pole_folder_name="05_SUPPORT_900344",
        trace_path=trace_path,
    )
    assert record["photo_count"] == 9
    assert record["photos_available"] is True
    assert "full_pole" in record["photo_types_present"]
