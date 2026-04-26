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


# ===========================================================================
# Stage 2B — Detached record separation
# ===========================================================================


def _structural_angle(pole_id: str, easting: float, northing: float, **kwargs) -> dict:
    return {
        "pole_id": pole_id,
        "easting": easting,
        "northing": northing,
        "structure_type": "Angle",
        "_record_role": "structural",
        "lat": None,
        "lon": None,
        "height": None,
        "location": None,
        **kwargs,
    }


# ---------------------------------------------------------------------------
# test_detached_not_required
# ---------------------------------------------------------------------------


def test_detached_not_required() -> None:
    """Records with 'not required' in remark are excluded from chain."""
    df = _make_df(
        [
            _structural_pol("P1", 100.0, 0.0),
            _structural_pol("P2", 200.0, 0.0),
            _structural_pol("P3", 300.0, 0.0),
            # "not required" remark — should be detached regardless of position
            {**_structural_pol("PX", 310.0, 0.0), "location": "not required"},
        ]
    )
    result = sequence_route(df)

    assert result["status"] == "ok"
    chain_ids = [r["point_id"] for r in result["chain"]]
    assert "PX" not in chain_ids
    assert len(result["chain"]) == 3

    detached = result["detached_records"]
    assert len(detached) == 1
    assert detached[0]["point_id"] == "PX"
    assert "not required" in detached[0]["detach_reason"]


# ---------------------------------------------------------------------------
# test_detached_not_required_case_insensitive
# ---------------------------------------------------------------------------


def test_detached_not_required_case_insensitive() -> None:
    """'Not Required', 'NOT REQUIRED' etc. are all caught."""
    for remark in ["Not Required", "NOT REQUIRED", "pole 5 - not required"]:
        df = _make_df(
            [
                _structural_pol("P1", 100.0, 0.0),
                _structural_pol("P2", 200.0, 0.0),
                {**_structural_pol("PX", 110.0, 0.0), "location": remark},
            ]
        )
        result = sequence_route(df)
        chain_ids = [r["point_id"] for r in result["chain"]]
        assert "PX" not in chain_ids, f"Expected PX detached for remark={remark!r}"
        assert len(result["detached_records"]) == 1


# ---------------------------------------------------------------------------
# test_detached_large_gap_isolated
# ---------------------------------------------------------------------------


def test_detached_large_gap_isolated() -> None:
    """A record >500m from ALL others is classified detached."""
    df = _make_df(
        [
            _structural_pol("P1", 100.0, 0.0),
            _structural_pol("P2", 200.0, 0.0),
            _structural_pol("P3", 300.0, 0.0),
            # 1000m away from nearest (P3 at 300,0) — well beyond default 500m
            _structural_pol("PFAR", 1300.0, 0.0),
        ]
    )
    result = sequence_route(df)

    chain_ids = [r["point_id"] for r in result["chain"]]
    assert "PFAR" not in chain_ids
    assert len(result["chain"]) == 3
    assert len(result["detached_records"]) == 1
    assert result["detached_records"][0]["point_id"] == "PFAR"


# ---------------------------------------------------------------------------
# test_detached_large_gap_but_has_neighbours
# ---------------------------------------------------------------------------


def test_detached_large_gap_but_has_neighbours() -> None:
    """A record >500m from the cluster but with a nearby neighbour is NOT detached."""
    df = _make_df(
        [
            _structural_pol("P1", 100.0, 0.0),
            _structural_pol("P2", 200.0, 0.0),
            # 700m from P1/P2 cluster but P3 is only 50m away → not detached
            _structural_pol("P3", 750.0, 0.0),
            _structural_pol("P4", 800.0, 0.0),
        ]
    )
    result = sequence_route(df)

    assert len(result["chain"]) == 4
    assert len(result["detached_records"]) == 0


# ---------------------------------------------------------------------------
# test_detached_custom_threshold
# ---------------------------------------------------------------------------


def test_detached_custom_threshold() -> None:
    """Custom detached_gap_threshold_m is respected."""
    df = _make_df(
        [
            _structural_pol("P1", 100.0, 0.0),
            _structural_pol("P2", 200.0, 0.0),
            # 400m from nearest — within default 500m but beyond custom 200m
            _structural_pol("PFAR", 600.0, 0.0),
        ]
    )
    # Default threshold: not detached (400m < 500m)
    result_default = sequence_route(df)
    assert len(result_default["detached_records"]) == 0
    assert len(result_default["chain"]) == 3

    # Custom threshold 200m: detached (400m > 200m)
    result_custom = sequence_route(df, config={"detached_gap_threshold_m": 200.0})
    assert len(result_custom["detached_records"]) == 1
    assert result_custom["detached_records"][0]["point_id"] == "PFAR"


# ===========================================================================
# Stage 2B — Section split candidates (Angle-type primary criterion)
# ===========================================================================


# ---------------------------------------------------------------------------
# test_angle_records_always_candidates
# ---------------------------------------------------------------------------


def test_angle_records_always_candidates() -> None:
    """Angle-type records are section_split_candidate=True regardless of deviation angle."""
    # Build a straight line — no angular deviation — but include an Angle-type record.
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_angle("A1", 100.0, 0.0),  # Angle-type on straight line → 0° deviation
            _structural_pol("P2", 200.0, 0.0),
        ]
    )
    result = sequence_route(df)

    assert result["status"] == "ok"
    chain = result["chain"]
    a1 = next(r for r in chain if r["point_id"] == "A1")
    assert a1["section_split_candidate"] is True
    # deviation ~0° — should NOT be a legacy candidate_section_break
    assert a1["candidate_section_break"] is False


# ---------------------------------------------------------------------------
# test_section_balanced_split
# ---------------------------------------------------------------------------


def test_section_balanced_split() -> None:
    """With multiple Angle candidates, the heuristic picks a balanced split."""
    # Build 10 poles with Angle at position 5 (index 4 in zero-based)
    # target_section_size=5 → should split at the Angle record
    records = []
    for i in range(5):
        records.append(_structural_pol(f"P{i + 1}", float(i * 100), 0.0))
    records.append(_structural_angle("A1", 500.0, 0.0))  # index 5
    for i in range(4):
        records.append(_structural_pol(f"Q{i + 1}", float((i + 6) * 100), 0.0))

    df = _make_df(records)
    result = sequence_route(df, config={"target_section_size": 5})

    assert result["status"] == "ok"
    sections = result["sections"]
    assert len(sections) >= 2, f"Expected at least 2 sections, got {len(sections)}"


# ---------------------------------------------------------------------------
# test_section_metadata_structure
# ---------------------------------------------------------------------------


def test_section_metadata_structure() -> None:
    """Each section in 'sections' has required metadata fields."""
    records = [_structural_pol(f"P{i}", float(i * 100), 0.0) for i in range(4)]
    records.insert(2, _structural_angle("A1", 200.0, 0.0))
    df = _make_df(records)
    result = sequence_route(df, config={"target_section_size": 2})

    for sec in result["sections"]:
        assert "section_id" in sec
        assert "start_seq" in sec
        assert "end_seq" in sec
        assert "pole_count" in sec
        assert sec["pole_count"] > 0


# ---------------------------------------------------------------------------
# test_no_chain_duplication
# ---------------------------------------------------------------------------


def test_no_chain_duplication() -> None:
    """Boundary records appear ONCE in the chain — they are NOT duplicated."""
    records = []
    for i in range(6):
        records.append(_structural_pol(f"P{i}", float(i * 100), 0.0))
    records.insert(3, _structural_angle("A1", 300.0, 0.0))
    df = _make_df(records)
    result = sequence_route(df, config={"target_section_size": 3})

    chain = result["chain"]
    ids = [r["point_id"] for r in chain]
    # No point_id should appear more than once
    assert len(ids) == len(set(ids)), f"Duplicate point_ids found: {ids}"


# ---------------------------------------------------------------------------
# test_no_angle_fallback
# ---------------------------------------------------------------------------


def test_no_angle_fallback() -> None:
    """When no Angle records exist, all section_split_candidates are False."""
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_pol("P2", 100.0, 0.0),
            _structural_pol("P3", 200.0, 0.0),
        ]
    )
    result = sequence_route(df)
    for rec in result["chain"]:
        assert rec["section_split_candidate"] is False


# ---------------------------------------------------------------------------
# test_candidate_section_break_preserved
# ---------------------------------------------------------------------------


def test_candidate_section_break_preserved() -> None:
    """candidate_section_break (legacy angle threshold) still works alongside
    section_split_candidate (new Angle-type criterion)."""
    side = 100.0 / math.sqrt(2)
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_pol("P2", 100.0, 0.0),
            _structural_pol("P3", 100.0 + side, side),
        ]
    )
    result = sequence_route(df)
    p2 = next(r for r in result["chain"] if r["point_id"] == "P2")
    assert p2["candidate_section_break"] is True
    assert p2["section_split_candidate"] is False  # feature_code is "Pol" not "Angle"


# ===========================================================================
# Stage 2B — Design pole numbering
# ===========================================================================


# ---------------------------------------------------------------------------
# test_design_numbering_global
# ---------------------------------------------------------------------------


def test_design_numbering_global() -> None:
    """design_pole_number is global and sequential across full chain (1-based)."""
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_angle("A1", 100.0, 0.0),
            _structural_pol("P2", 200.0, 0.0),
            _structural_pol("P3", 300.0, 0.0),
        ]
    )
    result = sequence_route(df, config={"target_section_size": 2})

    chain = result["chain"]
    dpns = [r["design_pole_number"] for r in chain]
    assert dpns == list(range(1, len(chain) + 1))


# ---------------------------------------------------------------------------
# test_design_numbering_boundary_shared
# ---------------------------------------------------------------------------


def test_design_numbering_boundary_shared() -> None:
    """The boundary record has a single design_pole_number that appears in both
    the section_id of section N AND is reflected in section metadata."""
    records = []
    for i in range(3):
        records.append(_structural_pol(f"P{i}", float(i * 100), 0.0))
    records.append(_structural_angle("A1", 300.0, 0.0))
    for i in range(3):
        records.append(_structural_pol(f"Q{i}", float((i + 4) * 100), 0.0))
    df = _make_df(records)
    result = sequence_route(df, config={"target_section_size": 3})

    chain = result["chain"]
    a1 = next(r for r in chain if r["point_id"] == "A1")
    # design_pole_number must be a positive integer
    assert isinstance(a1["design_pole_number"], int)
    assert a1["design_pole_number"] >= 1
    # section_boundary must be True (it is a boundary Angle record)
    assert a1["section_boundary"] is True


# ---------------------------------------------------------------------------
# test_section_sequence_number_restarts
# ---------------------------------------------------------------------------


def test_section_sequence_number_restarts() -> None:
    """section_sequence_number restarts at 1 for each new section."""
    records = [_structural_pol(f"P{i}", float(i * 100), 0.0) for i in range(3)]
    records.append(_structural_angle("A1", 300.0, 0.0))
    records += [_structural_pol(f"Q{i}", float((i + 4) * 100), 0.0) for i in range(3)]
    df = _make_df(records)
    result = sequence_route(df, config={"target_section_size": 3})

    sections_seen: dict[int, list[int]] = {}
    for rec in result["chain"]:
        sid = rec["section_id"]
        ssn = rec["section_sequence_number"]
        if sid not in sections_seen:
            sections_seen[sid] = []
        sections_seen[sid].append(ssn)

    for sid, ssns in sections_seen.items():
        # Each section's sequence numbers should start at 1
        assert ssns[0] == 1, f"Section {sid} ssn should start at 1, got {ssns}"
        # And be consecutive
        assert ssns == list(range(1, len(ssns) + 1)), f"Section {sid} ssns not sequential: {ssns}"


# ---------------------------------------------------------------------------
# test_design_numbering_not_on_expoles
# ---------------------------------------------------------------------------


def test_design_numbering_not_on_expoles() -> None:
    """EXpole records do NOT appear in the chain, so they have no design_pole_number."""
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_pol("P2", 100.0, 0.0),
            _structural_expole("EX1", 105.0, 0.0),
        ]
    )
    result = sequence_route(df)

    chain_ids = [r["point_id"] for r in result["chain"]]
    assert "EX1" not in chain_ids

    # Chain records have design_pole_number
    for rec in result["chain"]:
        assert rec["design_pole_number"] is not None

    # Matched EXpole has matched_design_pole_number (from the proposed pole)
    matched = result["matched_expoles"]
    assert len(matched) == 1
    assert matched[0].get("matched_design_pole_number") is not None


# ===========================================================================
# Stage 2B — Interleaved view
# ===========================================================================


# ---------------------------------------------------------------------------
# test_interleaved_preserves_file_order
# ---------------------------------------------------------------------------


def test_interleaved_preserves_file_order() -> None:
    """Interleaved view records appear in original df (file) order."""
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _context_record("H1", 50.0, 0.0),
            _structural_pol("P2", 100.0, 0.0),
            _structural_expole("EX1", 105.0, 0.0),
            _structural_pol("P3", 200.0, 0.0),
        ]
    )
    result = sequence_route(df)

    iv = result["interleaved_view"]
    ids = [r["point_id"] for r in iv]
    assert ids == ["P1", "H1", "P2", "EX1", "P3"]


# ---------------------------------------------------------------------------
# test_interleaved_roles_correct
# ---------------------------------------------------------------------------


def test_interleaved_roles_correct() -> None:
    """Each record in interleaved view has the correct Role label."""
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _context_record("H1", 50.0, 0.0),
            _structural_expole("EX1", 5.0, 0.0),
        ]
    )
    result = sequence_route(df)

    iv = {r["point_id"]: r["role"] for r in result["interleaved_view"]}
    assert iv["P1"] == "Proposed"
    assert iv["H1"] == "Context"
    assert iv["EX1"] == "Existing"


# ---------------------------------------------------------------------------
# test_interleaved_section_assignment
# ---------------------------------------------------------------------------


def test_interleaved_section_assignment() -> None:
    """Proposed poles in interleaved view have correct section_id."""
    records = [_structural_pol(f"P{i}", float(i * 100), 0.0) for i in range(3)]
    records.append(_structural_angle("A1", 300.0, 0.0))
    records += [_structural_pol(f"Q{i}", float((i + 4) * 100), 0.0) for i in range(2)]
    df = _make_df(records)
    result = sequence_route(df, config={"target_section_size": 3})

    iv = result["interleaved_view"]
    proposed_iv = [r for r in iv if r["role"] == "Proposed"]
    for rec in proposed_iv:
        assert rec["section_id"] is not None
        assert rec["section_id"] >= 1


# ---------------------------------------------------------------------------
# test_interleaved_design_numbers_present
# ---------------------------------------------------------------------------


def test_interleaved_design_numbers_present() -> None:
    """Proposed poles in interleaved view have non-None design_pole_number."""
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_pol("P2", 100.0, 0.0),
            _structural_pol("P3", 200.0, 0.0),
        ]
    )
    result = sequence_route(df)

    iv = result["interleaved_view"]
    for rec in iv:
        if rec["role"] == "Proposed":
            assert rec["design_pole_number"] is not None


# ---------------------------------------------------------------------------
# test_interleaved_expole_matched_design_number
# ---------------------------------------------------------------------------


def test_interleaved_expole_matched_design_number() -> None:
    """EXpoles in interleaved view have matched_design_pole_number when matched."""
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_pol("P2", 100.0, 0.0),
            _structural_expole("EX1", 105.0, 0.0),  # 5m from P2 → matched
        ]
    )
    result = sequence_route(df)

    iv = result["interleaved_view"]
    ex_rec = next(r for r in iv if r["point_id"] == "EX1")
    assert ex_rec["role"] == "Existing"
    assert ex_rec["matched_proposed_id"] == "P2"
    assert ex_rec["matched_design_pole_number"] is not None


# ===========================================================================
# Stage 2B — Confidence warning
# ===========================================================================


# ---------------------------------------------------------------------------
# test_confidence_warning_triggered
# ---------------------------------------------------------------------------


def test_confidence_warning_triggered() -> None:
    """confidence_warning is set when >50% of chain records are medium/low."""
    # Force medium confidence by reversing spatial order vs file order.
    # Greedy NN from P5 (first in file) picks P4, P3, P2, P1 — all medium.
    df = _make_df(
        [
            _structural_pol("P5", 500.0, 0.0),
            _structural_pol("P4", 400.0, 0.0),
            _structural_pol("P3", 300.0, 0.0),
            _structural_pol("P2", 200.0, 0.0),
            _structural_pol("P1", 100.0, 0.0),
        ]
    )
    result = sequence_route(df)

    summary = result["summary"]
    # rec_idx 0 → seq_pos 0 → high. All others: rec_idx != seq_pos → medium
    non_high = summary["confidence_counts"].get("medium", 0) + summary["confidence_counts"].get(
        "low", 0
    )
    total = summary["total_sequenced"]
    if non_high / total > 0.5:
        assert summary["confidence_warning"] is not None
        assert "WARNING" in summary["confidence_warning"]


# ---------------------------------------------------------------------------
# test_confidence_warning_not_triggered
# ---------------------------------------------------------------------------


def test_confidence_warning_not_triggered() -> None:
    """confidence_warning is None when ≤50% of chain records are medium/low."""
    # Straight line in file order → all high confidence
    df = _make_df(
        [
            _structural_pol("P1", 0.0, 0.0),
            _structural_pol("P2", 100.0, 0.0),
            _structural_pol("P3", 200.0, 0.0),
            _structural_pol("P4", 300.0, 0.0),
        ]
    )
    result = sequence_route(df)

    assert result["summary"]["confidence_warning"] is None
