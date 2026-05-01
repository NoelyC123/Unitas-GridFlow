"""Phase 3F — context / crossing records: type profiles, span linking, risk hints."""

from __future__ import annotations

from typing import Any

# Owner / risk tags for designer coordination (reference labels, not compliance engine).
CONTEXT_TYPES: dict[str, dict[str, str]] = {
    "bt": {"owner": "BT/Openreach", "risk": "coordination"},
    "openreach": {"owner": "BT/Openreach", "risk": "coordination"},
    "lv_line": {"owner": "Network operator", "risk": "crossing"},
    "lvline": {"owner": "Network operator", "risk": "crossing"},
    "33kv": {"owner": "Transmission / distribution", "risk": "voltage_separation"},
    "road": {"owner": "Highway authority", "risk": "clearance"},
    "track": {"owner": "Highway authority", "risk": "clearance"},
    "footway": {"owner": "Highway authority", "risk": "clearance"},
    "rail": {"owner": "Network Rail / rail operator", "risk": "clearance"},
    "water": {"owner": "Water / environmental", "risk": "foundation"},
    "hedge": {"owner": "Landowner", "risk": "access"},
    "tree": {"owner": "Landowner", "risk": "access"},
    "fence": {"owner": "Landowner", "risk": "access"},
    "wall": {"owner": "Landowner / property", "risk": "access"},
    "building": {"owner": "Property owner", "risk": "clearance"},
    "utility": {"owner": "Third-party utility", "risk": "crossing"},
    "pline": {"owner": "Pipeline operator", "risk": "crossing"},
    "xing": {"owner": "Various", "risk": "clearance"},
}

_HIGH_TIERS = frozenset({"high"})


def _structure_lower(props: dict[str, Any]) -> str:
    return str(props.get("structure_type") or "").strip().lower()


def is_crossing_context_record(props: dict[str, Any]) -> bool:
    """True when this point should receive Phase 3F crossing linkage."""
    if str(props.get("record_role") or "").strip().lower() == "context":
        return True
    st = _structure_lower(props)
    if not st:
        return False
    hints = (
        "road",
        "track",
        "xing",
        "pline",
        "btxing",
        "lvxing",
        "hvxing",
        "hedge",
        "tree",
        "fence",
        "wall",
        "gate",
        "stream",
        "rail",
        "footway",
        "building",
    )
    return any(h in st for h in hints)


def context_profile_for_structure(structure_type: str | None) -> dict[str, Any]:
    """Match ``CONTEXT_TYPES`` by substring; fallback to generic third-party profile."""
    st = (structure_type or "").lower()
    if not st:
        return {
            "context_kind": "unknown",
            "owner": "",
            "risk_category": "unknown",
            "coordination_required": False,
        }
    for token, profile in CONTEXT_TYPES.items():
        if token in st:
            risk = profile["risk"]
            return {
                "context_kind": token,
                "owner": profile["owner"],
                "risk_category": risk,
                "coordination_required": risk in ("coordination", "crossing", "clearance"),
            }
    return {
        "context_kind": "other",
        "owner": "Unknown / not classified",
        "risk_category": "context",
        "coordination_required": False,
    }


def assess_crossing_risk(
    context_props: dict[str, Any],
    span_props: dict[str, Any] | None,
) -> dict[str, Any]:
    """Summarise clearance / coordination hints for a context point + optional span."""
    measured = context_props.get("clearance_measured")
    required = context_props.get("clearance_required_m")
    span_risk = None
    if isinstance(span_props, dict):
        span_risk = str(span_props.get("crossing_risk_level") or "none").lower()
    links = context_props.get("span_crossing_links") or []
    tier_max = "none"
    for link in links:
        if not isinstance(link, dict):
            continue
        t = str(link.get("crossing_tier") or "").lower()
        if t == "high":
            tier_max = "high"
            break
        if t == "medium" and tier_max != "high":
            tier_max = "medium"
        elif t == "low" and tier_max == "none":
            tier_max = "low"

    if tier_max in _HIGH_TIERS or span_risk == "high":
        risk_level = "high"
    elif tier_max == "medium" or span_risk == "medium":
        risk_level = "medium"
    elif tier_max == "low" or span_risk == "low":
        risk_level = "low"
    else:
        risk_level = "low"

    action = None
    prof = context_profile_for_structure(context_props.get("structure_type"))
    if measured in (None, "") and risk_level in ("high", "medium"):
        action = "Measure statutory / design clearance versus survey context where required."
    elif prof["coordination_required"]:
        action = "Confirm third-party coordination if construction affects this context."

    return {
        "risk_level": risk_level,
        "clearance_measured_m": measured,
        "clearance_required_m": required,
        "span_risk_hint": span_risk,
        "crossing_hit_tier_max": tier_max,
        "designer_action": action,
    }


def enrich_context_crossing_records(data: dict[str, Any]) -> None:
    """Attach span crossing links + profiles to context survey points (mutates ``data``)."""
    feats = data.get("features") or []
    if not isinstance(feats, list):
        return

    span_features = data.get("span_features") or []
    links_by_point: dict[str, list[dict[str, Any]]] = {}
    if isinstance(span_features, list):
        for sf in span_features:
            if not isinstance(sf, dict):
                continue
            sp = sf.get("properties")
            if not isinstance(sp, dict):
                continue
            fp, tp = sp.get("from_point_id"), sp.get("to_point_id")
            risk = str(sp.get("crossing_risk_level") or "none")
            for hit in sp.get("crossing_hits_survey") or []:
                if not isinstance(hit, dict):
                    continue
                pid = str(hit.get("point_id") or "").strip()
                if not pid:
                    continue
                links_by_point.setdefault(pid, []).append(
                    {
                        "from_point_id": fp,
                        "to_point_id": tp,
                        "distance_m": hit.get("distance_m"),
                        "crossing_tier": hit.get("crossing_tier"),
                        "span_crossing_risk_level": risk,
                    }
                )

    enriched = 0
    for feat in feats:
        if not isinstance(feat, dict) or feat.get("type") != "Feature":
            continue
        props = feat.get("properties")
        if not isinstance(props, dict):
            continue
        if not is_crossing_context_record(props):
            continue
        pid = str(props.get("pole_id") or props.get("point_id") or "").strip()
        props["context_type_profile"] = context_profile_for_structure(props.get("structure_type"))
        props["span_crossing_links"] = links_by_point.get(pid, [])
        span_proxy: dict[str, Any] | None = None
        if props["span_crossing_links"]:
            first_hit = props["span_crossing_links"][0]
            lvl = first_hit.get("span_crossing_risk_level")
            span_proxy = {"crossing_risk_level": lvl}
        props["context_crossing_assessment"] = assess_crossing_risk(props, span_proxy)
        enriched += 1

    meta = data.setdefault("metadata", {})
    if isinstance(meta, dict):
        meta["context_crossing_phase3f_count"] = enriched
