from __future__ import annotations

import math

import pandas as pd

# All thresholds are PROVISIONAL — not hard engineering truth.
# They must be easy to change as real-world evidence refines them.
DEFAULT_CONFIG: dict = {
    "angle_split_threshold_deg": 30.0,  # provisional secondary signal
    "gap_split_threshold_m": 300.0,  # provisional
    "expole_match_threshold_m": 15.0,  # provisional
    "detached_gap_threshold_m": 500.0,  # provisional
    "target_section_size": 60,  # provisional heuristic for balanced splits
}

_EXPOLE_CODES: frozenset[str] = frozenset({"EXpole", "expole", "EXPOLE"})

# Angle-type records are ALWAYS section split candidates regardless of
# deviation angle magnitude. This is the primary criterion — not the 30° threshold.
_ANGLE_CODES: frozenset[str] = frozenset({"Angle", "angle", "ANGLE"})

# Columns that must be present for the sequencer to operate.
# lat/lon and height/location are optional — carried through if present.
_REQUIRED_COLUMNS: frozenset[str] = frozenset(
    {"easting", "northing", "_record_role", "structure_type", "pole_id"}
)


def _safe_val(v: object) -> object:
    """Return v, converting NaN/None to None."""
    if v is None:
        return None
    try:
        if pd.isna(v):
            return None
    except Exception:
        pass
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    return v


def _safe_num(v: object) -> float | None:
    v = _safe_val(v)
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _empty_result(cfg: dict, reason: str) -> dict:
    return {
        "status": "ok",
        "reason": reason,
        "chain": [],
        "matched_expoles": [],
        "unmatched_expoles": [],
        "context_features": [],
        "detached_records": [],
        "sections": [],
        "interleaved_view": [],
        "config_used": cfg,
        "summary": {
            "status": "ok",
            "reason": reason,
            "total_sequenced": 0,
            "total_expoles_matched": 0,
            "total_expoles_unmatched": 0,
            "total_section_breaks": 0,
            "total_detached": 0,
            "section_count": 0,
            "confidence_counts": {},
            "confidence_warning": None,
        },
    }


def _make_chain_record(row: "pd.Series", seq_pos: int, confidence: str) -> dict:
    return {
        "seq": seq_pos + 1,
        "point_id": _safe_val(row.get("pole_id")),
        "feature_code": _safe_val(row.get("structure_type")),
        "easting": _safe_num(row.get("easting")),
        "northing": _safe_num(row.get("northing")),
        "lat": _safe_num(row.get("lat")),
        "lon": _safe_num(row.get("lon")),
        "height": _safe_num(row.get("height")),
        "remark": _safe_val(row.get("location")),
        "span_to_next_m": None,
        "deviation_angle_deg": None,
        "replaces_point_id": None,
        "replaces_distance_m": None,
        "candidate_section_break": False,
        "section_split_candidate": False,
        "section_id": None,
        "section_boundary": False,
        "design_pole_number": None,
        "section_sequence_number": None,
        "sequence_confidence": confidence,
    }


def _make_expole_record(row: "pd.Series") -> dict:
    return {
        "point_id": _safe_val(row.get("pole_id")),
        "feature_code": _safe_val(row.get("structure_type")),
        "easting": _safe_num(row.get("easting")),
        "northing": _safe_num(row.get("northing")),
        "height": _safe_num(row.get("height")),
        "matched_to_proposed_id": None,
        "matched_design_pole_number": None,
        "distance_m": None,
    }


def _is_detached(
    row: "pd.Series",
    all_eastings: list[float | None],
    all_northings: list[float | None],
    threshold_m: float,
) -> tuple[bool, str]:
    """Return (is_detached, reason). A record is detached if either:
    - its REMARK (location field) contains 'not required' (case-insensitive), OR
    - it is >threshold_m from ALL other structural records.
    """
    remark = _safe_val(row.get("location")) or ""
    if "not required" in str(remark).lower():
        return True, "remark: not required"

    e = _safe_num(row.get("easting"))
    n = _safe_num(row.get("northing"))
    if e is None or n is None:
        return False, ""

    # If no other records exist to compare against, cannot be classified isolated
    valid_others = [
        (oe, on_)
        for oe, on_ in zip(all_eastings, all_northings)
        if oe is not None and on_ is not None
    ]
    if not valid_others:
        return False, ""

    for oe, on_ in valid_others:
        dist = math.sqrt((e - oe) ** 2 + (n - on_) ** 2)
        if dist <= threshold_m:
            return False, ""

    return True, "large spatial gap from main route"


def _separate_detached(proposed: "pd.DataFrame", cfg: dict) -> tuple["pd.DataFrame", list[dict]]:
    """Remove detached records from the proposed pool before chain building."""
    if proposed.empty:
        return proposed, []

    threshold = cfg["detached_gap_threshold_m"]
    all_e = [_safe_num(proposed.at[i, "easting"]) for i in proposed.index]
    all_n = [_safe_num(proposed.at[i, "northing"]) for i in proposed.index]

    keep_indices = []
    detached: list[dict] = []

    for pos, (i, row) in enumerate(proposed.iterrows()):
        # Build lists excluding current record for the neighbour check
        other_e = all_e[:pos] + all_e[pos + 1 :]
        other_n = all_n[:pos] + all_n[pos + 1 :]
        is_det, reason = _is_detached(row, other_e, other_n, threshold)
        if is_det:
            detached.append(
                {
                    "point_id": _safe_val(row.get("pole_id")),
                    "feature_code": _safe_val(row.get("structure_type")),
                    "easting": _safe_num(row.get("easting")),
                    "northing": _safe_num(row.get("northing")),
                    "remark": _safe_val(row.get("location")),
                    "detach_reason": reason,
                }
            )
        else:
            keep_indices.append(i)

    kept = proposed.loc[keep_indices].copy() if keep_indices else proposed.iloc[0:0].copy()
    return kept, detached


def _build_chain(proposed: "pd.DataFrame", cfg: dict) -> list[dict]:
    """Build ordered proposed-pole chain using greedy nearest-neighbour.

    File order is the starting point and the tiebreaker for equidistant records.
    """
    n = len(proposed)
    if n == 0:
        return []

    records = proposed.reset_index(drop=True)
    eastings = [_safe_num(records.at[i, "easting"]) for i in range(n)]
    northings = [_safe_num(records.at[i, "northing"]) for i in range(n)]

    visited = [False] * n
    chain_indices: list[int] = []
    ambiguous_positions: set[int] = set()

    # Start from first record in file order
    visited[0] = True
    chain_indices.append(0)
    current = 0

    for step in range(1, n):
        curr_e = eastings[current]
        curr_n = northings[current]

        best_dist = math.inf
        best_candidates: list[int] = []

        for j in range(n):
            if visited[j]:
                continue
            e_j = eastings[j]
            n_j = northings[j]
            if e_j is None or n_j is None or curr_e is None or curr_n is None:
                continue
            dist = math.sqrt((e_j - curr_e) ** 2 + (n_j - curr_n) ** 2)
            if dist < best_dist - 1e-6:
                best_dist = dist
                best_candidates = [j]
            elif abs(dist - best_dist) <= 1e-6:
                best_candidates.append(j)

        if not best_candidates:
            break

        if len(best_candidates) > 1:
            ambiguous_positions.add(step)

        # File order as tiebreaker: smallest original index wins
        next_idx = min(best_candidates)
        visited[next_idx] = True
        chain_indices.append(next_idx)
        current = next_idx

    # Build chain records
    chain: list[dict] = []
    for seq_pos, rec_idx in enumerate(chain_indices):
        row = records.iloc[rec_idx]
        if seq_pos in ambiguous_positions:
            confidence = "low"
        elif rec_idx == seq_pos:
            confidence = "high"
        else:
            confidence = "medium"
        chain.append(_make_chain_record(row, seq_pos, confidence))

    # Span distances between consecutive proposed poles
    for i in range(len(chain) - 1):
        e1, n1 = chain[i]["easting"], chain[i]["northing"]
        e2, n2 = chain[i + 1]["easting"], chain[i + 1]["northing"]
        if all(v is not None for v in (e1, n1, e2, n2)):
            chain[i]["span_to_next_m"] = round(math.sqrt((e2 - e1) ** 2 + (n2 - n1) ** 2), 1)

    # Deviation angles at internal poles only — first and last remain None
    for i in range(1, len(chain) - 1):
        e0, n0 = chain[i - 1]["easting"], chain[i - 1]["northing"]
        e1, n1 = chain[i]["easting"], chain[i]["northing"]
        e2, n2 = chain[i + 1]["easting"], chain[i + 1]["northing"]
        if any(v is None for v in (e0, n0, e1, n1, e2, n2)):
            continue
        vx_in, vy_in = e1 - e0, n1 - n0
        vx_out, vy_out = e2 - e1, n2 - n1
        mag_in = math.sqrt(vx_in**2 + vy_in**2)
        mag_out = math.sqrt(vx_out**2 + vy_out**2)
        if mag_in < 1e-10 or mag_out < 1e-10:
            continue
        cos_a = max(-1.0, min(1.0, (vx_in * vx_out + vy_in * vy_out) / (mag_in * mag_out)))
        chain[i]["deviation_angle_deg"] = round(math.degrees(math.acos(cos_a)), 1)

    # Section split candidates:
    # Angle-type records are ALWAYS candidates (primary criterion).
    # Large deviation angle or large gap are secondary signals.
    angle_thr = cfg["angle_split_threshold_deg"]
    gap_thr = cfg["gap_split_threshold_m"]
    for i, rec in enumerate(chain):
        is_angle_type = rec["feature_code"] in _ANGLE_CODES
        is_angle_break = (
            rec["deviation_angle_deg"] is not None and rec["deviation_angle_deg"] >= angle_thr
        )
        is_gap_break = (
            i < len(chain) - 1
            and rec["span_to_next_m"] is not None
            and rec["span_to_next_m"] >= gap_thr
        )
        rec["section_split_candidate"] = is_angle_type
        rec["candidate_section_break"] = is_angle_break or is_gap_break

    return chain


def _assign_sections(chain: list[dict], cfg: dict) -> list[dict]:
    """Assign section_id, section_boundary, design_pole_number, and
    section_sequence_number to each chain record.

    Section split candidates (Angle-type records) are chosen using a balanced
    heuristic: prefer splits that produce sections near target_section_size.

    The boundary record appears as the LAST record of Section N and the FIRST
    record of Section N+1. It is NOT duplicated in the chain list — instead
    section membership metadata covers both.

    design_pole_number: global sequential counter (1-based) across full chain,
    counting only chain records. Does NOT restart per section.

    section_sequence_number: 1-based counter within each section, restarting at
    the first non-shared record of each section.
    """
    if not chain:
        return []

    n = len(chain)
    target = cfg.get("target_section_size", 60)

    # Find all candidate split indices
    candidate_indices = [i for i, r in enumerate(chain) if r["section_split_candidate"]]

    # Choose actual split points from candidates using balanced heuristic.
    # A split at index i means: chain[i] ends Section N and starts Section N+1.
    # We pick candidates greedily: if a candidate is near the target boundary, use it.
    chosen_splits: list[int] = []
    if candidate_indices and n > target:
        last_split = 0
        for ci in candidate_indices:
            # Only consider after minimum half-target distance from last split
            if ci - last_split >= target // 2:
                chosen_splits.append(ci)
                last_split = ci

    # Build section boundary list: list of chain indices that are boundaries
    # Each boundary index is the end of one section and the start of the next.
    # chosen_splits contains internal boundary indices.
    section_boundaries: set[int] = set(chosen_splits)

    # Assign section IDs
    # Records between start (inclusive) and boundary (inclusive) belong to section N.
    # The boundary record also starts section N+1.
    current_section = 1
    section_starts: list[int] = [0]  # index where each section starts in chain

    for i, rec in enumerate(chain):
        rec["section_id"] = current_section
        if i in section_boundaries and i < n - 1:
            rec["section_boundary"] = True
            current_section += 1
            section_starts.append(i)  # boundary is also the start of next section
        else:
            rec["section_boundary"] = False

    # design_pole_number: global sequential (1-based), all chain records
    for dpn, rec in enumerate(chain, start=1):
        rec["design_pole_number"] = dpn

    # section_sequence_number: 1-based within each section, restarting after boundary
    # For boundary records: they get the last number of section N.
    # The FIRST non-boundary record of section N+1 restarts at 1.
    sec_counter: dict[int, int] = {}
    for rec in chain:
        sid = rec["section_id"]
        if sid not in sec_counter:
            sec_counter[sid] = 0
        sec_counter[sid] += 1
        rec["section_sequence_number"] = sec_counter[sid]

    # For boundary records, they belong to section N but also start section N+1.
    # The section_sequence_number already counts them correctly within section N.
    # The first record of N+1 that is NOT a boundary gets seq 1 — but the
    # boundary record itself was assigned section_id = N (not N+1). So the
    # first genuine N+1 record has a fresh counter.
    # Re-walk to fix: the boundary gets ssn from section N. The first record
    # after the boundary is section N+1 with ssn=1 — already correct.

    return chain


def _build_sections_metadata(chain: list[dict]) -> list[dict]:
    """Build per-section summary metadata from annotated chain."""
    if not chain:
        return []

    sections: dict[int, dict] = {}
    for rec in chain:
        sid = rec["section_id"]
        if sid not in sections:
            sections[sid] = {
                "section_id": sid,
                "start_seq": rec["seq"],
                "end_seq": rec["seq"],
                "pole_count": 0,
                "boundary_point_id": None,
                "overlap_with_next_section": False,
            }
        sections[sid]["end_seq"] = rec["seq"]
        sections[sid]["pole_count"] += 1
        if rec["section_boundary"]:
            sections[sid]["boundary_point_id"] = rec["point_id"]
            sections[sid]["overlap_with_next_section"] = True

    return list(sections.values())


def _match_expoles(
    expoles: "pd.DataFrame",
    chain: list[dict],
    cfg: dict,
) -> tuple[list[dict], list[dict]]:
    """Match each EXpole to the nearest proposed pole within threshold."""
    threshold = cfg["expole_match_threshold_m"]
    matched: list[dict] = []
    unmatched: list[dict] = []

    proposed_positions = [
        (rec["point_id"], rec["easting"], rec["northing"], rec.get("design_pole_number"))
        for rec in chain
        if rec["easting"] is not None and rec["northing"] is not None
    ]

    for _, row in expoles.iterrows():
        ex_e = _safe_num(row.get("easting"))
        ex_n = _safe_num(row.get("northing"))
        ex_record = _make_expole_record(row)

        if ex_e is None or ex_n is None or not proposed_positions:
            unmatched.append(ex_record)
            continue

        best_dist = math.inf
        best_prop_id = None
        best_dpn = None

        for prop_id, prop_e, prop_n, dpn in proposed_positions:
            if prop_e is None or prop_n is None:
                continue
            dist = math.sqrt((ex_e - prop_e) ** 2 + (ex_n - prop_n) ** 2)
            if dist < best_dist:
                best_dist = dist
                best_prop_id = prop_id
                best_dpn = dpn

        if best_dist <= threshold:
            dist_rounded = round(best_dist, 1)
            ex_record["matched_to_proposed_id"] = best_prop_id
            ex_record["matched_design_pole_number"] = best_dpn
            ex_record["distance_m"] = dist_rounded
            matched.append(ex_record)
            # Back-annotate the matched proposed pole in the chain
            for chain_rec in chain:
                if chain_rec["point_id"] == best_prop_id:
                    chain_rec["replaces_point_id"] = _safe_val(row.get("pole_id"))
                    chain_rec["replaces_distance_m"] = dist_rounded
                    break
        else:
            unmatched.append(ex_record)

    return matched, unmatched


def _build_context_list(context: "pd.DataFrame") -> list[dict]:
    result = []
    for _, row in context.iterrows():
        result.append(
            {
                "point_id": _safe_val(row.get("pole_id")),
                "feature_code": _safe_val(row.get("structure_type")),
                "easting": _safe_num(row.get("easting")),
                "northing": _safe_num(row.get("northing")),
                "height": _safe_num(row.get("height")),
                "remark": _safe_val(row.get("location")),
            }
        )
    return result


def _build_interleaved_view(
    df: "pd.DataFrame",
    chain: list[dict],
    matched_expoles: list[dict],
    context_features: list[dict],
    detached_records: list[dict],
) -> list[dict]:
    """Build the interleaved D2D working view.

    All records (proposed, EXpole, context) appear in ORIGINAL FILE ORDER within
    each section. Each record gets: Role, Section_ID, Design_Pole_No,
    Section_Seq_No, Matched_Proposed_ID.

    Detached records appear at the end in a dedicated "Detached" section.

    The file-order position is preserved — records are NOT rearranged to sit
    beside their matched proposed pole.
    """
    # Build lookup maps from chain and matched expoles
    chain_by_id: dict[str, dict] = {r["point_id"]: r for r in chain if r.get("point_id")}
    expole_match_by_id: dict[str, dict] = {
        r["point_id"]: r for r in matched_expoles if r.get("point_id")
    }
    detached_ids: set[str] = {r["point_id"] for r in detached_records if r.get("point_id")}

    interleaved: list[dict] = []

    for _, row in df.iterrows():
        pid = _safe_val(row.get("pole_id"))
        role = _safe_val(row.get("_record_role")) or "unknown"
        fcode = _safe_val(row.get("structure_type"))
        e = _safe_num(row.get("easting"))
        n_ = _safe_num(row.get("northing"))
        h = _safe_num(row.get("height"))
        remark = _safe_val(row.get("location"))

        rec: dict = {
            "point_id": pid,
            "feature_code": fcode,
            "easting": e,
            "northing": n_,
            "height": h,
            "remark": remark,
            "role": None,
            "section_id": None,
            "section_boundary": False,
            "design_pole_number": None,
            "section_sequence_number": None,
            "matched_proposed_id": None,
            "matched_design_pole_number": None,
        }

        if str(pid) in detached_ids:
            rec["role"] = "Detached"
        elif fcode in _EXPOLE_CODES:
            rec["role"] = "Existing"
            if str(pid) in expole_match_by_id:
                match = expole_match_by_id[str(pid)]
                rec["matched_proposed_id"] = match.get("matched_to_proposed_id")
                rec["matched_design_pole_number"] = match.get("matched_design_pole_number")
        elif role == "context":
            rec["role"] = "Context"
        elif str(pid) in chain_by_id:
            chain_rec = chain_by_id[str(pid)]
            rec["role"] = "Proposed"
            rec["section_id"] = chain_rec.get("section_id")
            rec["section_boundary"] = chain_rec.get("section_boundary", False)
            rec["design_pole_number"] = chain_rec.get("design_pole_number")
            rec["section_sequence_number"] = chain_rec.get("section_sequence_number")
        else:
            rec["role"] = role.capitalize() if role else "Unknown"

        interleaved.append(rec)

    # Add detached records at the end (they may not be in df if filtered earlier)
    # Actually detached records are filtered from proposed before chain building,
    # but they ARE still in the original df — so they'll appear inline above.
    # No extra append needed.

    return interleaved


def sequence_route(df: "pd.DataFrame", config: dict | None = None) -> dict:
    """
    Build a spatially sequenced route from a normalised, role-classified DataFrame.

    Input df must already have _record_role set by classify_record_roles() in
    app/controller_intake.py. The sequencer consumes existing classification —
    it does NOT re-parse feature codes.

    EXpole records are excluded from the main chain and matched to proposed poles
    by spatial proximity. All thresholds in DEFAULT_CONFIG are PROVISIONAL.

    Stage 2B additions:
    - Detached record separation (before chain building)
    - Angle-type section split candidates (primary criterion)
    - Section membership assignment with overlapping boundaries
    - Global design pole numbering (does not restart per section)
    - Section sequence numbering (restarts per section)
    - Interleaved D2D working view (file order preserved)
    - Confidence warning if >50% of chain records are medium/low confidence
    """
    cfg = {**DEFAULT_CONFIG, **(config or {})}

    # Validate required columns before any processing
    for col in sorted(_REQUIRED_COLUMNS):
        if col not in df.columns:
            return {
                "status": "error",
                "reason": f"missing required column: {col}",
                "chain": [],
                "matched_expoles": [],
                "unmatched_expoles": [],
                "context_features": [],
                "detached_records": [],
                "sections": [],
                "interleaved_view": [],
                "config_used": cfg,
                "summary": {},
            }

    structural = df[df["_record_role"] == "structural"].copy()
    context = df[df["_record_role"] == "context"].copy()

    if structural.empty:
        return _empty_result(cfg, "no_structural_records")

    is_expole = structural["structure_type"].isin(_EXPOLE_CODES)
    expoles = structural[is_expole].copy()
    proposed_raw = structural[~is_expole].copy()

    if proposed_raw.empty:
        return _empty_result(cfg, "no_proposed_records")

    # Stage 2B: separate detached records before chain building
    proposed, detached_records = _separate_detached(proposed_raw, cfg)

    if proposed.empty:
        return _empty_result(cfg, "no_proposed_records")

    chain = _build_chain(proposed, cfg)

    # Stage 2B: assign section membership and design numbering
    chain = _assign_sections(chain, cfg)

    # Stage 2B: EXpole matching now carries design_pole_number from chain
    matched, unmatched = _match_expoles(expoles, chain, cfg)
    context_features = _build_context_list(context)

    # Stage 2B: sections metadata
    sections = _build_sections_metadata(chain)

    # Stage 2B: interleaved view
    interleaved_view = _build_interleaved_view(
        df, chain, matched, context_features, detached_records
    )

    break_count = sum(1 for r in chain if r["candidate_section_break"])
    confidence_counts: dict[str, int] = {}
    for r in chain:
        c = r["sequence_confidence"]
        confidence_counts[c] = confidence_counts.get(c, 0) + 1

    total = len(chain)
    non_high = confidence_counts.get("medium", 0) + confidence_counts.get("low", 0)
    confidence_warning: str | None = None
    if total > 0 and non_high / total > 0.5:
        confidence_warning = (
            f"WARNING: {non_high}/{total} chain records are medium or low confidence. "
            "File order may not match survey capture order — designer review required."
        )

    summary = {
        "status": "ok",
        "reason": None,
        "total_sequenced": len(chain),
        "total_expoles_matched": len(matched),
        "total_expoles_unmatched": len(unmatched),
        "total_section_breaks": break_count,
        "total_detached": len(detached_records),
        "section_count": len(sections),
        "confidence_counts": confidence_counts,
        "confidence_warning": confidence_warning,
    }

    return {
        "status": "ok",
        "reason": None,
        "chain": chain,
        "matched_expoles": matched,
        "unmatched_expoles": unmatched,
        "context_features": context_features,
        "detached_records": detached_records,
        "sections": sections,
        "interleaved_view": interleaved_view,
        "config_used": cfg,
        "summary": summary,
    }
