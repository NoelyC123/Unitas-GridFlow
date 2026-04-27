from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.review_manager import (
    apply_pairing_overrides,
    build_review,
    calc_distance,
    delete_review,
    enrich_overrides_with_distances,
    load_review,
    save_review,
)


@pytest.fixture()
def file_dir(tmp_path: Path) -> Path:
    d = tmp_path / "files" / "F001"
    d.mkdir(parents=True)
    return d


def _minimal_seq() -> dict:
    return {
        "status": "ok",
        "chain": [
            {
                "point_id": "10",
                "feature_code": "PRpole",
                "easting": 100.0,
                "northing": 200.0,
                "replaces_point_id": "20",
                "replaces_distance_m": 1.5,
                "design_pole_number": "Pol 1",
            },
            {
                "point_id": "11",
                "feature_code": "PRpole",
                "easting": 150.0,
                "northing": 200.0,
                "replaces_point_id": None,
                "replaces_distance_m": None,
                "design_pole_number": "Pol 2",
            },
        ],
        "matched_expoles": [
            {
                "point_id": "20",
                "feature_code": "EXpole",
                "easting": 101.5,
                "northing": 200.0,
                "matched_to_proposed_id": "10",
                "matched_design_pole_number": "Pol 1",
                "distance_m": 1.5,
            }
        ],
        "unmatched_expoles": [],
        "interleaved_view": [
            {
                "point_id": "20",
                "feature_code": "EXpole",
                "role": "expole",
                "matched_proposed_id": "10",
                "matched_design_pole_number": "Pol 1",
            }
        ],
    }


class TestLoadSaveDelete:
    def test_load_missing(self, file_dir):
        assert load_review(file_dir) is None

    def test_save_and_load_roundtrip(self, file_dir):
        review = build_review("F001", "reviewed", "notes", [])
        save_review(file_dir, review)
        loaded = load_review(file_dir)
        assert loaded["file_id"] == "F001"
        assert loaded["review_status"] == "reviewed"

    def test_delete_existing(self, file_dir):
        save_review(file_dir, build_review("F001", "reviewed", "", []))
        assert delete_review(file_dir) is True
        assert load_review(file_dir) is None

    def test_delete_absent(self, file_dir):
        assert delete_review(file_dir) is False


class TestBuildReview:
    def test_first_version_is_1(self):
        r = build_review("F001", "reviewed", "notes", [])
        assert r["version"] == 1

    def test_version_increments(self):
        existing = build_review("F001", "reviewed", "", [])
        r = build_review("F001", "reviewed", "", [], existing_review=existing)
        assert r["version"] == 2

    def test_reviewed_at_set_when_reviewed(self):
        r = build_review("F001", "reviewed", "", [])
        assert r["reviewed_at"] is not None

    def test_reviewed_at_none_when_not_reviewed(self):
        r = build_review("F001", "not_reviewed", "", [])
        assert r["reviewed_at"] is None

    def test_notes_stripped(self):
        r = build_review("F001", "reviewed", "  hello  ", [])
        assert r["review_notes"] == "hello"


class TestCalcDistance:
    def test_basic_distance(self):
        assert calc_distance(0, 0, 3, 4) == 5.0

    def test_none_input(self):
        assert calc_distance(None, 0, 3, 4) is None


class TestEnrichOverrides:
    def test_fills_distances(self):
        seq = _minimal_seq()
        overrides = [
            {
                "expole_point_id": "20",
                "original_matched_to": "10",
                "reviewed_matched_to": "11",
            }
        ]
        result = enrich_overrides_with_distances(overrides, seq)
        assert result[0]["original_distance_m"] == pytest.approx(1.5, abs=0.2)
        assert result[0]["reviewed_distance_m"] == pytest.approx(48.5, abs=0.2)

    def test_none_reviewed_match_sets_none_distance(self):
        seq = _minimal_seq()
        overrides = [
            {
                "expole_point_id": "20",
                "original_matched_to": "10",
                "reviewed_matched_to": None,
            }
        ]
        result = enrich_overrides_with_distances(overrides, seq)
        assert result[0]["reviewed_distance_m"] is None


class TestApplyPairingOverrides:
    def test_no_review_returns_same_object(self):
        seq = _minimal_seq()
        result = apply_pairing_overrides(seq, None)
        assert result is seq

    def test_no_overrides_returns_same_object(self):
        seq = _minimal_seq()
        review = build_review("F001", "reviewed", "", [])
        result = apply_pairing_overrides(seq, review)
        assert result is seq

    def test_original_seq_not_mutated(self):
        seq = _minimal_seq()
        original_json = json.dumps(seq)
        review = build_review(
            "F001",
            "reviewed",
            "",
            [
                {
                    "expole_point_id": "20",
                    "original_matched_to": "10",
                    "reviewed_matched_to": "11",
                    "reviewed_distance_m": 50.0,
                }
            ],
        )
        apply_pairing_overrides(seq, review)
        assert json.dumps(seq) == original_json

    def test_reassign_matched_expole(self):
        seq = _minimal_seq()
        review = build_review(
            "F001",
            "reviewed",
            "",
            [
                {
                    "expole_point_id": "20",
                    "original_matched_to": "10",
                    "reviewed_matched_to": "11",
                    "reviewed_distance_m": 50.0,
                }
            ],
        )
        result = apply_pairing_overrides(seq, review)
        expole = next(e for e in result["matched_expoles"] if str(e["point_id"]) == "20")
        assert expole["matched_to_proposed_id"] == "11"
        assert expole["distance_m"] == 50.0

    def test_reassign_updates_chain_replaces(self):
        seq = _minimal_seq()
        review = build_review(
            "F001",
            "reviewed",
            "",
            [
                {
                    "expole_point_id": "20",
                    "original_matched_to": "10",
                    "reviewed_matched_to": "11",
                    "reviewed_distance_m": 50.0,
                }
            ],
        )
        result = apply_pairing_overrides(seq, review)
        old_chain = next(r for r in result["chain"] if str(r["point_id"]) == "10")
        new_chain = next(r for r in result["chain"] if str(r["point_id"]) == "11")
        assert old_chain["replaces_point_id"] is None
        assert new_chain["replaces_point_id"] == "20"
        assert new_chain["replaces_distance_m"] == 50.0

    def test_mark_expole_unmatched(self):
        seq = _minimal_seq()
        review = build_review(
            "F001",
            "reviewed",
            "",
            [
                {
                    "expole_point_id": "20",
                    "original_matched_to": "10",
                    "reviewed_matched_to": None,
                    "reviewed_distance_m": None,
                }
            ],
        )
        result = apply_pairing_overrides(seq, review)
        matched_ids = [str(e["point_id"]) for e in result["matched_expoles"]]
        unmatched_ids = [str(e["point_id"]) for e in result["unmatched_expoles"]]
        assert "20" not in matched_ids
        assert "20" in unmatched_ids

    def test_interleaved_view_updated(self):
        seq = _minimal_seq()
        review = build_review(
            "F001",
            "reviewed",
            "",
            [
                {
                    "expole_point_id": "20",
                    "original_matched_to": "10",
                    "reviewed_matched_to": "11",
                    "reviewed_distance_m": 50.0,
                }
            ],
        )
        result = apply_pairing_overrides(seq, review)
        iv_row = next(r for r in result["interleaved_view"] if str(r["point_id"]) == "20")
        assert iv_row["matched_proposed_id"] == "11"
