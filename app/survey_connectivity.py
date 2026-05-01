"""D2-C network connectivity display and D2-D survey metadata enrichment."""

from __future__ import annotations

import re
from typing import Any, Mapping

_RE_H_ACC = re.compile(
    r"(?:horizontal|h\.?)\s*(?:accuracy|acc)?\s*[:(]?\s*([+-]?\d+(?:\.\d+)?)\s*m",
    re.I,
)
_RE_V_ACC = re.compile(
    r"(?:vertical|v\.?)\s*(?:accuracy|acc)?\s*[:(]?\s*([+-]?\d+(?:\.\d+)?)\s*m",
    re.I,
)
_RE_PM = re.compile(r"±\s*(\d+(?:\.\d+)?)\s*m", re.I)
_RE_FIX_RTK = re.compile(r"\brtk\b|\bppk\b|fixed\s*position", re.I)
_RE_FIX_FLOAT = re.compile(r"\bfloat\b|\bautonomous\b|\bdgps\b", re.I)


def _get(record: Mapping[str, Any] | Any, key: str, default: Any = None) -> Any:
    if record is None:
        return default
    if isinstance(record, Mapping):
        return record.get(key, default)
    getter = getattr(record, "get", None)
    if callable(getter):
        return getter(key, default)
    return default


def _clean_str(v: object) -> str | None:
    if v is None or v == "":
        return None
    s = str(v).strip()
    return s or None


def parse_gnss_block(record: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Derive structured GNSS fields from row + free-text ``gnss_accuracy``."""
    raw = str(_get(record, "gnss_accuracy") or "")
    h_m = _get(record, "horizontal_accuracy_m")
    v_m = _get(record, "vertical_accuracy_m")
    fix = _clean_str(_get(record, "gnss_fix_type"))

    ha: float | None = None
    va: float | None = None
    try:
        if h_m is not None and str(h_m).strip() != "":
            ha = float(h_m)
    except ValueError:
        ha = None
    try:
        if v_m is not None and str(v_m).strip() != "":
            va = float(v_m)
    except ValueError:
        va = None

    if raw:
        mh = _RE_H_ACC.search(raw)
        mv = _RE_V_ACC.search(raw)
        if ha is None and mh:
            try:
                ha = float(mh.group(1))
            except ValueError:
                pass
        if va is None and mv:
            try:
                va = float(mv.group(1))
            except ValueError:
                pass
        if ha is None and va is None:
            mpm = _RE_PM.findall(raw)
            if len(mpm) >= 1 and ha is None:
                try:
                    ha = float(mpm[0])
                except ValueError:
                    pass
            if len(mpm) >= 2 and va is None:
                try:
                    va = float(mpm[1])
                except ValueError:
                    pass

    if not fix and raw:
        if _RE_FIX_RTK.search(raw):
            fix = "RTK fixed"
        elif _RE_FIX_FLOAT.search(raw):
            fix = "Float / differential"

    parts: list[str] = []
    if fix:
        parts.append(fix)
    if ha is not None:
        parts.append(f"±{ha} m horizontal")
    if va is not None:
        parts.append(f"±{va} m vertical")
    summary = "; ".join(parts) if parts else (_clean_str(raw) or None)

    return {
        "gnss_fix_type": fix,
        "horizontal_accuracy_m": ha,
        "vertical_accuracy_m": va,
        "gnss_accuracy_summary": summary,
    }


def parse_capture_method_display(record: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Human-readable capture method (field vs digitised vs inferred)."""
    cm = str(_get(record, "capture_method") or "").strip().lower()
    sc = str(_get(record, "source_confidence") or "").lower()
    if not cm and sc:
        cm = sc
    label = _get(record, "capture_method") or _get(record, "source_confidence")
    key = "unknown"
    if any(x in cm for x in ("rtk", "ppk", "gnss", "gps", "trimble")):
        key = "gnss"
        if "rtk" in cm or "ppk" in cm:
            label = label or "GNSS RTK / PPK"
        else:
            label = label or "GNSS"
    elif any(x in cm for x in ("total", "station", "ts ", "edm")):
        key = "total_station"
        label = label or "Total station"
    elif any(x in cm for x in ("digitis", "digitiz", "tracing", "pdf")):
        key = "digitised"
        label = label or "Digitised from drawing / GIS"
    elif any(x in cm for x in ("import", "dno", "gis")):
        key = "imported"
        label = label or "Imported / DNO GIS"
    elif any(x in cm for x in ("infer", "estimate")):
        key = "inferred"
        label = label or "Inferred from context"
    return {"capture_method_key": key, "capture_method_label": _clean_str(label) or "Not recorded"}


def merge_connectivity_into_props(props: dict[str, Any]) -> None:
    """Populate D2-C relationship display fields."""
    props["from_support_id"] = _clean_str(_get(props, "from_support_id"))
    props["to_support_id"] = _clean_str(_get(props, "to_support_id"))
    props["parent_support_id"] = _clean_str(_get(props, "parent_support_id"))
    props["parent_structure_id"] = _clean_str(_get(props, "parent_structure_id"))
    props["cable_from_asset_id"] = _clean_str(_get(props, "cable_from_asset_id"))
    props["cable_to_asset_id"] = _clean_str(_get(props, "cable_to_asset_id"))
    props["connectivity_parent_pole"] = _clean_str(
        _get(props, "parent_support_id") or _get(props, "linked_pole_id")
    )


def merge_survey_metadata_into_props(props: dict[str, Any]) -> None:
    """Populate D2-D survey audit fields on feature properties."""
    job_ref = _get(props, "survey_job_ref") or _get(props, "job_ref")
    props["survey_job_ref"] = _clean_str(job_ref)
    props["equipment_used"] = _clean_str(
        _get(props, "equipment_used") or _get(props, "survey_equipment")
    )
    props["survey_limitations"] = _clean_str(_get(props, "survey_limitations"))
    gnss = parse_gnss_block(props)
    for k in (
        "gnss_fix_type",
        "horizontal_accuracy_m",
        "vertical_accuracy_m",
        "gnss_accuracy_summary",
    ):
        v = gnss.get(k)
        if v is not None:
            props[k] = v
    cap = parse_capture_method_display(props)
    props["capture_method_key"] = cap.get("capture_method_key")
    props["capture_method_label"] = cap.get("capture_method_label")
