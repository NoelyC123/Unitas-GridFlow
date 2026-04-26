from __future__ import annotations

import math

import pandas as pd

# All thresholds are PROVISIONAL — not hard engineering truth.
# They must be easy to change as real-world evidence refines them.
DEFAULT_CONFIG: dict = {
    "angle_split_threshold_deg": 30.0,  # provisional
    "gap_split_threshold_m": 300.0,  # provisional
    "expole_match_threshold_m": 15.0,  # provisional
}

_EXPOLE_CODES: frozenset[str] = frozenset({"EXpole", "expole", "EXPOLE"})

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
        "config_used": cfg,
        "summary": {
            "status": "ok",
            "reason": reason,
            "total_sequenced": 0,
            "total_expoles_matched": 0,
            "total_expoles_unmatched": 0,
            "total_section_breaks": 0,
            "confidence_counts": {},
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
        "distance_m": None,
    }


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

    # Section break candidates — angle and gap thresholds applied separately
    angle_thr = cfg["angle_split_threshold_deg"]
    gap_thr = cfg["gap_split_threshold_m"]
    for i, rec in enumerate(chain):
        is_angle_break = (
            rec["deviation_angle_deg"] is not None and rec["deviation_angle_deg"] >= angle_thr
        )
        is_gap_break = (
            i < len(chain) - 1
            and rec["span_to_next_m"] is not None
            and rec["span_to_next_m"] >= gap_thr
        )
        rec["candidate_section_break"] = is_angle_break or is_gap_break

    return chain


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
        (rec["point_id"], rec["easting"], rec["northing"])
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

        for prop_id, prop_e, prop_n in proposed_positions:
            if prop_e is None or prop_n is None:
                continue
            dist = math.sqrt((ex_e - prop_e) ** 2 + (ex_n - prop_n) ** 2)
            if dist < best_dist:
                best_dist = dist
                best_prop_id = prop_id

        if best_dist <= threshold:
            dist_rounded = round(best_dist, 1)
            ex_record["matched_to_proposed_id"] = best_prop_id
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


def sequence_route(df: "pd.DataFrame", config: dict | None = None) -> dict:
    """
    Build a spatially sequenced route from a normalised, role-classified DataFrame.

    Input df must already have _record_role set by classify_record_roles() in
    app/controller_intake.py. The sequencer consumes existing classification —
    it does NOT re-parse feature codes.

    EXpole records are excluded from the main chain and matched to proposed poles
    by spatial proximity. All thresholds in DEFAULT_CONFIG are PROVISIONAL.
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
                "config_used": cfg,
                "summary": {},
            }

    structural = df[df["_record_role"] == "structural"].copy()
    context = df[df["_record_role"] == "context"].copy()

    if structural.empty:
        return _empty_result(cfg, "no_structural_records")

    is_expole = structural["structure_type"].isin(_EXPOLE_CODES)
    expoles = structural[is_expole].copy()
    proposed = structural[~is_expole].copy()

    if proposed.empty:
        return _empty_result(cfg, "no_proposed_records")

    chain = _build_chain(proposed, cfg)
    matched, unmatched = _match_expoles(expoles, chain, cfg)
    context_features = _build_context_list(context)

    break_count = sum(1 for r in chain if r["candidate_section_break"])
    confidence_counts: dict[str, int] = {}
    for r in chain:
        c = r["sequence_confidence"]
        confidence_counts[c] = confidence_counts.get(c, 0) + 1

    summary = {
        "status": "ok",
        "reason": None,
        "total_sequenced": len(chain),
        "total_expoles_matched": len(matched),
        "total_expoles_unmatched": len(unmatched),
        "total_section_breaks": break_count,
        "confidence_counts": confidence_counts,
    }

    return {
        "status": "ok",
        "reason": None,
        "chain": chain,
        "matched_expoles": matched,
        "unmatched_expoles": unmatched,
        "context_features": context_features,
        "config_used": cfg,
        "summary": summary,
    }
