"""Phase 3G — replacement pair intelligence: confidence scoring and match labels."""

from __future__ import annotations

from typing import Any

REPLACEMENT_MATCH_TYPES: dict[str, str] = {
    "direct_replacement": "EX and PR within ~0.5m — strong co-location",
    "nearby_replacement": "Offset within tolerance — likely replacement pair",
    "co_located_cluster": "Multiple structures close together — verify intent",
    "repositioned": "Noticeable offset — possible repositioned replacement",
    "unmatched_ex": "Existing pole flagged without a nearby proposed partner in data",
    "unmatched_pr": "Proposed pole without linked existing reference",
    "ambiguous_cluster": "Ambiguous proximity — manual pairing review",
}


def _height_m(props: dict[str, Any]) -> float | None:
    for key in ("measured_height_m", "proposed_height_m", "height"):
        v = props.get(key)
        if v is None or v == "":
            continue
        try:
            return float(v)
        except (TypeError, ValueError):
            continue
    return None


def calculate_replacement_confidence(
    ex_props: dict[str, Any],
    pr_props: dict[str, Any],
    offset_m: float | None,
) -> dict[str, Any]:
    """Score 0–100 heuristic for EX↔PR pairing audit (design support, not acceptance test)."""
    factors: dict[str, Any] = {}
    score = 0

    if offset_m is None:
        factors["offset_m"] = None
        score += 15
    else:
        factors["offset_m"] = offset_m
        if offset_m < 0.5:
            score += 45
            factors["offset_band"] = "co_located"
        elif offset_m < 5.0:
            score += 35
            factors["offset_band"] = "tight"
        elif offset_m < 20.0:
            score += 25
            factors["offset_band"] = "nearby"
        else:
            score += 10
            factors["offset_band"] = "wide"

    ex_h = _height_m(ex_props)
    pr_h = _height_m(pr_props)
    if ex_h is not None and pr_h is not None:
        delta = abs(ex_h - pr_h)
        factors["height_delta_m"] = round(delta, 2)
        if delta < 0.26:
            score += 20
        elif delta < 1.0:
            score += 12
        elif delta < 3.0:
            score += 6
    else:
        factors["height_delta_m"] = None

    pc_e = str(ex_props.get("pole_class") or "")
    pc_p = str(pr_props.get("pole_class") or "")
    if pc_e and pc_p and pc_e.strip().lower() == pc_p.strip().lower():
        score += 10
        factors["pole_class_match"] = True
    else:
        factors["pole_class_match"] = bool(pc_e and pc_p)

    mat_e = str(ex_props.get("material") or "").lower()
    mat_p = str(pr_props.get("material") or "").lower()
    if mat_e and mat_p:
        factors["material_compatible"] = mat_e == mat_p or mat_e in mat_p or mat_p in mat_e
        if factors["material_compatible"]:
            score += 5
    else:
        factors["material_compatible"] = None

    if offset_m is not None and offset_m < 0.5:
        match_type = "direct_replacement"
    elif offset_m is not None and offset_m < 20.0:
        match_type = "nearby_replacement"
    elif offset_m is not None:
        match_type = "repositioned"
    else:
        match_type = "nearby_replacement"

    return {
        "confidence_pct": max(0, min(100, score)),
        "match_type": match_type,
        "match_type_detail": REPLACEMENT_MATCH_TYPES.get(match_type, ""),
        "factors": factors,
        "detection_method": "automatic_proximity_match",
        "review_status": "unconfirmed",
    }


def enrich_replacement_pair_intelligence(data: dict[str, Any]) -> None:
    """Attach ``replacement_pair_audit`` blobs to paired poles when links exist."""
    feats = data.get("features") or []
    if not isinstance(feats, list):
        return

    by_id: dict[str, dict[str, Any]] = {}
    for feat in feats:
        if not isinstance(feat, dict) or feat.get("type") != "Feature":
            continue
        props = feat.get("properties")
        if not isinstance(props, dict):
            continue
        pid = str(props.get("pole_id") or props.get("point_id") or "").strip()
        if pid:
            by_id[pid] = props

    seen: set[tuple[str, str]] = set()
    audits = 0
    for feat in feats:
        if not isinstance(feat, dict):
            continue
        props = feat.get("properties")
        if not isinstance(props, dict):
            continue
        bb = props.get("being_replaced_by")
        rp = props.get("replacing")
        other_id = None
        ex_id = pr_id = None
        if bb:
            other_id = str(bb).strip()
            ex_id = str(props.get("pole_id") or props.get("point_id") or "").strip()
            pr_id = other_id
        elif rp:
            other_id = str(rp).strip()
            pr_id = str(props.get("pole_id") or props.get("point_id") or "").strip()
            ex_id = other_id
        if not other_id or not ex_id or not pr_id:
            continue
        key = tuple(sorted((ex_id, pr_id)))
        if key in seen:
            continue
        seen.add(key)
        ex_p = by_id.get(ex_id)
        pr_p = by_id.get(pr_id)
        if not ex_p or not pr_p:
            continue
        offset = props.get("match_offset_m")
        if offset is None:
            offset = ex_p.get("match_offset_m") or pr_p.get("match_offset_m")
        try:
            offset_f = float(offset) if offset is not None else None
        except (TypeError, ValueError):
            offset_f = None

        audit = calculate_replacement_confidence(ex_p, pr_p, offset_f)
        audit["ex_pole_id"] = ex_id
        audit["pr_pole_id"] = pr_id
        audit["pair_id"] = f"{ex_id}_{pr_id}"
        ex_p["replacement_pair_audit"] = audit
        pr_p["replacement_pair_audit"] = audit
        audits += 1

    meta = data.setdefault("metadata", {})
    if isinstance(meta, dict):
        meta["replacement_pair_audit_count"] = audits
