from __future__ import annotations

import math

import pandas as pd
import pytest

from app.route_sequencer import sequence_route

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_df(records: list[dict]) -> pd.DataFrame:
    """Build a DataFrame with _record_role already set — simulating the output
    of classify_record_roles() so the sequencer receives the expected input."""
    return pd.DataFrame(records)


def _structural_pol(pole_id: str, easting: float, northing: float, **kwargs) -> dict:
    return {
        "pole_id": pole_id,
        "easting": easting,
        "northing": northing,
        "structure_type": "Pol",
        "_record_role": "structural",
        "lat": None,
        "lon": None,
        "height": None,
        "location": None,
        **kwargs,
    }


def _structural_expole(pole_id: str, easting: float, northing: float, **kwargs) -> dict:
    return {
        "pole_id": pole_id,
        "easting": easting,
        "northing": northing,
        "structure_type": "EXpole",
        "_record_role": "structural",
        "lat": None,
        "lon": None,
        "height": None,
        "location": None,
        **kwargs,
    }


def _context_record(pole_id: str, easting: float, northing: float, code: str = "Hedge") -> dict:
    return {
        "pole_id": pole_id,
        "easting": easting,
        "northing": northing,
        "structure_type": code,
        "_record_role": "context",
        "lat": None,
        "lon": None,
        "height": None,
        "location": None,
    }


# ---------------------------------------------------------------------------
# test_straight_line_sequence
# ---------------------------------------------------------------------------


def test_straight_line_sequence() -> None:
    """5 Pol records on a straight E-W line — verify order, spans, and angles."""
    df = _make_df(
        [
            _structural_pol("P1", 100.0, 0.0),
            _structural_pol("P2", 200.0, 0.0),
            _structural_pol("P3", 300.0, 0.0),
            _structural_pol("P4", 400.0, 0.0),
            _structural_pol("P5", 500.0, 0.0),
        ]
    )
    result = sequence_route(df)

    assert result["status"] == "ok"
    chain = result["chain"]
    assert len(chain) == 5

    # Sequence must be in spatial order (which equals file order here)
    assert [r["point_id"] for r in chain] == ["P1", "P2", "P3", "P4", "P5"]

    # All spans = 100m
    for i in range(4):
        assert chain[i]["span_to_next_m"] == pytest.approx(100.0, abs=0.1)
    assert chain[4]["span_to_next_m"] is None

    # First and last poles have no deviation angle
    assert chain[0]["deviation_angle_deg"] is None
    assert chain[4]["deviation_angle_deg"] is None

    # Internal poles on straight line: deviation ≈ 0
    for i in range(1, 4):
        assert chain[i]["deviation_angle_deg"] == pytest.approx(0.0, abs=0.5)


# ---------------------------------------------------------------------------
# test_expole_matching
# ---------------------------------------------------------------------------


def test_expole_matching() -> None:
    """EXpole within threshold is excluded from chain and appears in matched_expoles."""
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_pol("P2", 100.0, 0.0),
            _structural_pol("P3", 200.0, 0.0),
            # EXpole 5m from P2
            _structural_expole("EX1", 105.0, 0.0),
        ]
    )
    result = sequence_route(df)

    assert result["status"] == "ok"
    chain = result["chain"]

    # EXpole must not appear in the chain
    chain_ids = [r["point_id"] for r in chain]
    assert "EX1" not in chain_ids
    assert len(chain) == 3

    # EXpole appears in matched_expoles
    assert len(result["matched_expoles"]) == 1
    assert len(result["unmatched_expoles"]) == 0

    matched = result["matched_expoles"][0]
    assert matched["point_id"] == "EX1"
    assert matched["matched_to_proposed_id"] == "P2"
    assert matched["distance_m"] == pytest.approx(5.0, abs=0.1)


# ---------------------------------------------------------------------------
# test_expole_beyond_threshold
# ---------------------------------------------------------------------------


def test_expole_beyond_threshold() -> None:
    """EXpole beyond default 15m threshold appears in unmatched_expoles."""
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_pol("P2", 100.0, 0.0),
            _structural_pol("P3", 200.0, 0.0),
            # EXpole 20m from nearest Pol (P2 at 100,0)
            _structural_expole("EX1", 120.0, 0.0),
        ]
    )
    result = sequence_route(df)

    assert result["status"] == "ok"
    assert len(result["matched_expoles"]) == 0
    assert len(result["unmatched_expoles"]) == 1
    assert result["unmatched_expoles"][0]["point_id"] == "EX1"


# ---------------------------------------------------------------------------
# test_out_of_sequence_expole (Gordon pattern)
# ---------------------------------------------------------------------------


def test_out_of_sequence_expole() -> None:
    """EXpoles captured at end of file (rows 5-7) are matched by spatial position.

    This replicates the Gordon survey pattern where EXpole records appear after
    all Pol records in file order but are spatially interleaved along the route.
    """
    df = _make_df(
        [
            # Pol records first (file rows 0-4)
            _structural_pol("P1", 100.0, 0.0),
            _structural_pol("P2", 200.0, 0.0),
            _structural_pol("P3", 300.0, 0.0),
            _structural_pol("P4", 400.0, 0.0),
            _structural_pol("P5", 500.0, 0.0),
            # EXpoles at end of file (rows 5-7) but spatially near P2, P3, P4
            _structural_expole("EX1", 205.0, 0.0),  # 5m from P2
            _structural_expole("EX2", 308.0, 0.0),  # 8m from P3
            _structural_expole("EX3", 412.0, 0.0),  # 12m from P4
        ]
    )
    result = sequence_route(df)

    assert result["status"] == "ok"

    # All 5 Pol records in chain, all 3 EXpoles matched
    assert len(result["chain"]) == 5
    assert len(result["matched_expoles"]) == 3
    assert len(result["unmatched_expoles"]) == 0

    matched_pairs = {m["point_id"]: m["matched_to_proposed_id"] for m in result["matched_expoles"]}
    assert matched_pairs["EX1"] == "P2"
    assert matched_pairs["EX2"] == "P3"
    assert matched_pairs["EX3"] == "P4"


# ---------------------------------------------------------------------------
# test_angle_deviation
# ---------------------------------------------------------------------------


def test_angle_deviation() -> None:
    """3 poles forming a ~45-degree bend — middle pole flagged as section break."""
    # P1→P2: 100m east. P2→P3: 45° NE (both components equal).
    side = 100.0 / math.sqrt(2)  # ≈ 70.71m each axis
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_pol("P2", 100.0, 0.0),
            _structural_pol("P3", 100.0 + side, side),
        ]
    )
    result = sequence_route(df)

    assert result["status"] == "ok"
    chain = result["chain"]
    assert len(chain) == 3

    # First and last poles: no deviation angle
    assert chain[0]["deviation_angle_deg"] is None
    assert chain[2]["deviation_angle_deg"] is None

    # Middle pole: ~45° deviation, above 30° threshold → section break
    assert chain[1]["deviation_angle_deg"] == pytest.approx(45.0, abs=1.0)
    assert chain[1]["candidate_section_break"] is True

    # First and last poles must not be section breaks due to angle (no angle computed)
    assert chain[0]["candidate_section_break"] is False
    assert chain[2]["candidate_section_break"] is False


# ---------------------------------------------------------------------------
# test_context_excluded
# ---------------------------------------------------------------------------


def test_context_excluded() -> None:
    """Context records must not enter the chain — they appear in context_features."""
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _context_record("H1", 50.0, 0.0, code="Hedge"),
            _structural_pol("P2", 100.0, 0.0),
            _context_record("R1", 150.0, 0.0, code="Road"),
        ]
    )
    result = sequence_route(df)

    assert result["status"] == "ok"

    chain_ids = [r["point_id"] for r in result["chain"]]
    assert "H1" not in chain_ids
    assert "R1" not in chain_ids
    assert len(result["chain"]) == 2

    context_ids = [r["point_id"] for r in result["context_features"]]
    assert "H1" in context_ids
    assert "R1" in context_ids


# ---------------------------------------------------------------------------
# test_no_structural_records
# ---------------------------------------------------------------------------


def test_no_structural_records() -> None:
    """File with only context records — valid outcome, not an error."""
    df = _make_df(
        [
            _context_record("H1", 0.0, 0.0),
            _context_record("H2", 100.0, 0.0),
        ]
    )
    result = sequence_route(df)

    assert result["status"] == "ok", f"Expected ok, got error: {result.get('reason')}"
    assert result["chain"] == []
    assert result["summary"]["reason"] == "no_structural_records"


# ---------------------------------------------------------------------------
# test_no_proposed_records
# ---------------------------------------------------------------------------


def test_no_proposed_records() -> None:
    """File with only EXpole structural records — valid outcome, not an error."""
    df = _make_df(
        [
            _structural_expole("EX1", 0.0, 0.0),
            _structural_expole("EX2", 100.0, 0.0),
        ]
    )
    result = sequence_route(df)

    assert result["status"] == "ok", f"Expected ok, got error: {result.get('reason')}"
    assert result["chain"] == []
    assert result["summary"]["reason"] == "no_proposed_records"


# ---------------------------------------------------------------------------
# test_confidence_simple
# ---------------------------------------------------------------------------


def test_confidence_simple() -> None:
    """When file order matches spatial nearest-neighbour order, confidence is 'high'."""
    # Straight line — greedy NN picks them in file order
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_pol("P2", 100.0, 0.0),
            _structural_pol("P3", 200.0, 0.0),
        ]
    )
    result = sequence_route(df)

    assert result["status"] == "ok"
    for rec in result["chain"]:
        assert rec["sequence_confidence"] == "high", (
            f"Expected 'high' for {rec['point_id']}, got {rec['sequence_confidence']}"
        )


# ---------------------------------------------------------------------------
# test_custom_config
# ---------------------------------------------------------------------------


def test_custom_config() -> None:
    """EXpole at 10m is matched with default threshold (15m) but unmatched with 5m."""
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_pol("P2", 100.0, 0.0),
            # EXpole 10m from P2
            _structural_expole("EX1", 110.0, 0.0),
        ]
    )

    # With default config (threshold=15m): EX1 matched
    result_default = sequence_route(df)
    assert len(result_default["matched_expoles"]) == 1

    # With custom config (threshold=5m): EX1 unmatched
    result_custom = sequence_route(df, config={"expole_match_threshold_m": 5.0})
    assert len(result_custom["matched_expoles"]) == 0
    assert len(result_custom["unmatched_expoles"]) == 1


# ---------------------------------------------------------------------------
# test_missing_required_columns
# ---------------------------------------------------------------------------


def test_missing_required_columns() -> None:
    """Missing 'easting' column returns status 'error' — does NOT raise an exception."""
    df = _make_df(
        [
            {
                "pole_id": "P1",
                "northing": 402000.0,
                "structure_type": "Pol",
                "_record_role": "structural",
                # easting is intentionally absent
            }
        ]
    )
    result = sequence_route(df)

    assert result["status"] == "error", f"Expected error status, got: {result}"
    assert "easting" in result["reason"], f"Expected 'easting' in reason, got: {result['reason']}"
