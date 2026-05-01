"""UK distribution conductor/cable vocabulary and equipment display (D2-A, D2-B).

Reference data only — not a compliance engine. Used for map popups and light QA hints.
"""

from __future__ import annotations

import re
from typing import Any, Mapping

# Voltage classifications (display reference)
VOLTAGE_TYPES: dict[str, dict[str, str]] = {
    "LV": {
        "label": "Low Voltage",
        "range": "230V / 400V",
        "typical_use": "Customer connections, LV mains",
    },
    "6.6kV": {
        "label": "6.6kV Medium Voltage",
        "range": "6.6kV",
        "typical_use": "Industrial/wind farm distribution",
    },
    "11kV": {
        "label": "11kV High Voltage",
        "range": "11kV",
        "typical_use": "Primary distribution, most common HV",
    },
    "20kV": {
        "label": "20kV High Voltage",
        "range": "20kV",
        "typical_use": "Some DNO networks",
    },
    "33kV": {
        "label": "33kV High Voltage",
        "range": "33kV",
        "typical_use": "Subtransmission, bulk supply",
    },
    "66kV": {
        "label": "66kV Extra High Voltage",
        "range": "66kV",
        "typical_use": "Subtransmission",
    },
    "110kV": {
        "label": "110kV Extra High Voltage",
        "range": "110kV",
        "typical_use": "Transmission crossings (Scotland)",
    },
    "132kV": {
        "label": "132kV Extra High Voltage",
        "range": "132kV",
        "typical_use": "Transmission crossings",
    },
}

OVERHEAD_CONDUCTOR_TYPES: dict[str, dict[str, str]] = {
    "AAC": {
        "name": "All Aluminium Conductor",
        "material": "Aluminium",
        "typical_use": "Standard overhead distribution",
    },
    "AAAC": {
        "name": "All Aluminium Alloy Conductor",
        "material": "Aluminium alloy",
        "typical_use": "Improved strength overhead lines",
    },
    "ACSR": {
        "name": "Aluminium Conductor Steel Reinforced",
        "material": "Aluminium + steel core",
        "typical_use": "Long spans, high mechanical strength",
    },
    "Cu": {
        "name": "Copper conductor",
        "material": "Copper",
        "typical_use": "Older installations, heritage areas",
    },
    "ABC": {
        "name": "Aerial Bundled Cable",
        "material": "Insulated aluminium",
        "typical_use": "Tree-prone areas, LV distribution",
    },
    "Bare": {
        "name": "Bare conductor",
        "material": "Various",
        "typical_use": "Standard overhead lines",
    },
    "Covered": {
        "name": "Covered conductor",
        "material": "Various with insulation",
        "typical_use": "Wildlife/vegetation protection",
    },
}

UNDERGROUND_CABLE_TYPES: dict[str, dict[str, str]] = {
    "XLPE": {
        "name": "Cross-Linked Polyethylene",
        "insulation": "XLPE",
        "typical_use": "Modern HV/LV underground cables",
    },
    "PILC": {
        "name": "Paper Insulated Lead Covered",
        "insulation": "Oil-impregnated paper + lead sheath",
        "typical_use": "Legacy underground cables",
    },
    "Waveform": {
        "name": "Waveform LV cable",
        "insulation": "PVC/XLPE",
        "typical_use": "LV underground distribution",
    },
    "Concentric": {
        "name": "Concentric neutral cable",
        "insulation": "XLPE with concentric neutral",
        "typical_use": "LV/HV single-phase or 3-phase",
    },
    "Service": {
        "name": "Service cable",
        "insulation": "Various",
        "typical_use": "Customer service connections",
    },
}

CONDUCTOR_SIZES: dict[str, str] = {
    "7/2.75": "AAC 7-strand 2.75mm (25mm² approx)",
    "7/3.00": "AAC 7-strand 3.00mm (35mm² approx)",
    "7/3.75": "AAC 7-strand 3.75mm (50mm² approx)",
    "7/4.50": "AAC 7-strand 4.50mm (70mm² approx)",
    "19/3.00": "AAC 19-strand 3.00mm (100mm² approx)",
    "19/3.50": "AAC 19-strand 3.50mm (150mm² approx)",
    "16mm²": "16mm² (small service)",
    "25mm²": "25mm²",
    "35mm²": "35mm²",
    "50mm²": "50mm²",
    "95mm²": "95mm² (LV service/main)",
    "185mm²": "185mm² (HV)",
    "300mm²": "300mm² (HV)",
}

PHASE_CONFIGURATIONS: dict[str, dict[str, str | int]] = {
    "single": {
        "conductors": 2,
        "description": "Single phase (L + N)",
        "typical_use": "Customer services, streetlighting",
    },
    "2-phase": {
        "conductors": 3,
        "description": "Two phase (2L + N)",
        "typical_use": "Larger customer services",
    },
    "3-phase": {
        "conductors": 4,
        "description": "Three phase (3L + N)",
        "typical_use": "LV mains, industrial supplies",
    },
    "3-phase_no_neutral": {
        "conductors": 3,
        "description": "Three phase (3L, no N)",
        "typical_use": "HV overhead lines (11kV, 33kV)",
    },
}

HV_VOLTAGE_KEYS: frozenset[str] = frozenset(
    {"6.6kV", "11kV", "20kV", "33kV", "66kV", "110kV", "132kV"}
)


def _get(record: Mapping[str, Any] | Any, key: str, default: Any = None) -> Any:
    if record is None:
        return default
    if isinstance(record, Mapping):
        return record.get(key, default)
    getter = getattr(record, "get", None)
    if callable(getter):
        return getter(key, default)
    return default


def normalize_voltage_key(raw: object) -> str | None:
    if raw is None or raw == "":
        return None
    s = str(raw).strip().upper().replace(" ", "").replace("-", "")
    if not s:
        return None
    if s in VOLTAGE_TYPES:
        return s
    alias: dict[str, str] = {
        "LV": "LV",
        "400V": "LV",
        "230V": "LV",
        "LOWVOLTAGE": "LV",
        "LOW-VOLTAGE": "LV",
        "6.6KV": "6.6kV",
        "6KV": "6.6kV",
        "11KV": "11kV",
        "20KV": "20kV",
        "33KV": "33kV",
        "66KV": "66kV",
        "110KV": "110kV",
        "132KV": "132kV",
    }
    if s in alias:
        return alias[s]
    if "132" in s and "KV" in s:
        return "132kV"
    if "110" in s and "KV" in s:
        return "110kV"
    if "66" in s and "KV" in s:
        return "66kV"
    if "33" in s and "KV" in s:
        return "33kV"
    if "20" in s and "KV" in s:
        return "20kV"
    if "11" in s and "KV" in s:
        return "11kV"
    if "6.6" in s or ("6" in s and "KV" in s):
        return "6.6kV"
    return None


def normalize_overhead_conductor_type(raw: object) -> str | None:
    if raw is None or raw == "":
        return None
    s = str(raw).strip().upper()
    if "COPPER" in s or s == "CU":
        return "Cu"
    for token in ("ACSR", "AAAC", "AAC", "ABC"):
        if s.startswith(token) or f" {token}" in s or f"-{token}" in s:
            return token
    if "COVERED" in s:
        return "Covered"
    if "BARE" in s and "BUNDLE" not in s:
        return "Bare"
    return None


def normalize_underground_cable_type(raw: object) -> str | None:
    if raw is None or raw == "":
        return None
    s = str(raw).strip().upper()
    for token in ("XLPE", "PILC", "WAVEFORM", "CONCENTRIC", "SERVICE"):
        if token in s or s.startswith(token):
            mapping = {
                "XLPE": "XLPE",
                "PILC": "PILC",
                "WAVEFORM": "Waveform",
                "CONCENTRIC": "Concentric",
                "SERVICE": "Service",
            }
            return mapping[token]
    return None


def normalize_phase_config_key(raw: object) -> str | None:
    if raw is None or raw == "":
        return None
    s = str(raw).strip().lower().replace(" ", "_")
    if s in PHASE_CONFIGURATIONS:
        return s
    aliases = {
        "single": "single",
        "single_phase": "single",
        "1_phase": "single",
        "1-phase": "single",
        "2_phase": "2-phase",
        "2-phase": "2-phase",
        "two_phase": "2-phase",
        "3_phase": "3-phase",
        "3-phase": "3-phase",
        "three_phase": "3-phase",
        "3_phase_no_neutral": "3-phase_no_neutral",
        "3-phase_no_neutral": "3-phase_no_neutral",
        "hv_3_phase": "3-phase_no_neutral",
    }
    if s in aliases:
        return aliases[s]
    return None


def _is_row_underground(record: Mapping[str, Any] | Any) -> bool:
    cable = _get(record, "cable_type")
    if cable not in (None, ""):
        return True
    route = str(_get(record, "route_type") or "").lower()
    if "underground" in route or route in {"ug", "u/g", "buried"}:
        return True
    return False


def row_suggests_hv_overhead(record: Mapping[str, Any] | Any) -> bool:
    """True if normalized voltage is HV and route is treated as overhead."""
    if _is_row_underground(record):
        return False
    vkey = normalize_voltage_key(_get(record, "voltage") or _get(record, "line_voltage"))
    return vkey in HV_VOLTAGE_KEYS if vkey else False


def parse_conductor_data(record: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Parse conductor/cable fields into display-friendly structures."""

    voltage_raw = _get(record, "voltage") or _get(record, "line_voltage")
    vkey = normalize_voltage_key(voltage_raw)
    voltage_detail = dict(VOLTAGE_TYPES[vkey]) if vkey and vkey in VOLTAGE_TYPES else {}

    conductor_type_raw = _get(record, "conductor_type") or _get(record, "conductor")
    cable_type_raw = _get(record, "cable_type")
    conductor_size_raw = _get(record, "conductor_size") or _get(record, "cable_size")
    phase_raw = (
        _get(record, "phase_count") or _get(record, "phases") or _get(record, "cores_phases")
    )

    is_underground = _is_row_underground(record)
    phase_key = normalize_phase_config_key(phase_raw)
    phase_detail = {k: v for k, v in PHASE_CONFIGURATIONS[phase_key].items()} if phase_key else {}

    size_key = str(conductor_size_raw).strip() if conductor_size_raw not in (None, "") else None
    size_desc = CONDUCTOR_SIZES.get(size_key) if size_key else None

    result: dict[str, Any] = {
        "voltage_detail": voltage_detail,
        "is_overhead": not is_underground,
        "is_underground": is_underground,
        "conductor_detail": {},
        "conductor_type_normalized": None,
        "conductor_size": size_key,
        "conductor_size_description": size_desc,
        "phase_detail": phase_detail,
        "cable_type": None,
        "cable_detail": {},
        "cable_size": None,
        "cores_phases": None,
    }

    if not is_underground:
        result["cable_type"] = None
        result["cable_detail"] = {}
        result["cable_size"] = None
        ct_key = normalize_overhead_conductor_type(conductor_type_raw)
        result["conductor_type_normalized"] = ct_key
        result["conductor_detail"] = (
            dict(OVERHEAD_CONDUCTOR_TYPES[ct_key])
            if ct_key and ct_key in OVERHEAD_CONDUCTOR_TYPES
            else {}
        )
        result["cores_phases"] = None
    else:
        ck = normalize_underground_cable_type(cable_type_raw)
        display_cable = ck or (str(cable_type_raw).strip() if cable_type_raw else None)
        result["cable_type"] = display_cable
        result["cable_detail"] = (
            dict(UNDERGROUND_CABLE_TYPES[ck]) if ck and ck in UNDERGROUND_CABLE_TYPES else {}
        )
        result["cable_size"] = size_key
        result["cores_phases"] = str(phase_raw).strip() if phase_raw not in (None, "") else None

    return result


def merge_electrical_fields_into_props(props: dict[str, Any]) -> None:
    """Populate ``props`` with D2-A electrical display fields (mutates in place)."""
    parsed = parse_conductor_data(props)
    props["voltage_detail"] = parsed.get("voltage_detail") or {}
    props["is_overhead"] = bool(parsed.get("is_overhead", True))
    props["is_underground"] = bool(parsed.get("is_underground", False))
    props["conductor_detail"] = parsed.get("conductor_detail") or {}
    props["conductor_type_normalized"] = parsed.get("conductor_type_normalized")
    props["conductor_size"] = parsed.get("conductor_size")
    props["conductor_size_description"] = parsed.get("conductor_size_description")
    props["phase_detail"] = parsed.get("phase_detail") or {}
    props["cable_type"] = parsed.get("cable_type")
    props["cable_detail"] = parsed.get("cable_detail") or {}
    props["cable_size"] = parsed.get("cable_size")
    props["cores_phases"] = parsed.get("cores_phases")


# --- D2-B: Equipment & pole-top (taxonomy + parsing) ---

EQUIPMENT_TYPES: dict[str, dict[str, str]] = {
    "transformer": {
        "label": "Transformer",
        "typical_mount": "Pole or ground plinth",
        "design_note": "Confirm kVA and HV/LV arrangement before design",
    },
    "switch": {
        "label": "Switch / disconnector",
        "typical_mount": "Pole-top or ground",
        "design_note": "Identify open/closed state if safety critical",
    },
    "fuse": {
        "label": "Fuse / cut-out",
        "typical_mount": "Pole-top LV",
        "design_note": "LV service protection",
    },
    "recloser": {
        "label": "Auto-recloser",
        "typical_mount": "Pole or ground kiosk",
        "design_note": "Protection and sectionalising",
    },
    "rmu": {
        "label": "Ring Main Unit (RMU)",
        "typical_mount": "Ground-mounted housing",
        "design_note": "HV switching assembly — confirm cable terminations",
    },
    "lv_board": {
        "label": "LV distribution board / fuseways",
        "typical_mount": "Pole or kiosk",
        "design_note": "Customer or street lighting multicore take-off",
    },
    "surge_arrester": {
        "label": "Surge arrester / lightning protection",
        "typical_mount": "Pole-top",
        "design_note": "Insulation coordination",
    },
}

POLE_TOP_ARRANGEMENTS: dict[str, dict[str, str]] = {
    "crossarm": {
        "label": "Crossarm arrangement",
        "description": "Conventional crossarm / pin insulator layout",
    },
    "terminal": {
        "label": "Terminal arrangement",
        "description": "Line termination / jumpering point",
    },
    "tee": {
        "label": "Tee / branch",
        "description": "Branch take-off from main line",
    },
    "transformer_mount": {
        "label": "Transformer pole-top",
        "description": "MV/LV transformer mounted on structure",
    },
    "switch_mount": {
        "label": "Switching pole-top",
        "description": "Disconnect / switch assembly on pole",
    },
    "bundle": {
        "label": "ABC / covered bundle",
        "description": "Aerial bundled or covered line hardware",
    },
}

_RE_KVA = re.compile(r"(\d+(?:\.\d+)?)\s*k\s*v\s*a", re.I)
_RE_KVA_COMPACT = re.compile(r"(\d+(?:\.\d+)?)\s*kva", re.I)
_RE_VOLT_RATIO = re.compile(r"(\d+(?:\.\d+)?)\s*(?:[kK][vV])?\s*/\s*(\d+(?:\.\d+)?)\s*[kK]?[vV]?")


def _tokenize_equipment_hint(text: str) -> list[str]:
    t = text.lower()
    found: list[str] = []
    if "transformer" in t or " tx" in t or re.search(r"\btf\b", t) or _RE_KVA.search(text):
        found.append("transformer")
    if "rmu" in t:
        found.append("rmu")
    if "recloser" in t:
        found.append("recloser")
    if "arrester" in t or ("lightning" in t and "strike" not in t):
        found.append("surge_arrester")
    if "fuse" in t or "cut-out" in t or "cutout" in t:
        found.append("fuse")
    if "switch" in t and "recloser" not in t:
        found.append("switch")
    if "lv board" in t or "lvboard" in t or "fuseway" in t:
        found.append("lv_board")
    return list(dict.fromkeys(found))


def normalize_pole_top_key(raw: object) -> str | None:
    if raw is None or raw == "":
        return None
    s = str(raw).strip().lower().replace(" ", "_").replace("-", "_")
    aliases = {
        "cross_arm": "crossarm",
        "crossarm": "crossarm",
        "terminal": "terminal",
        "term": "terminal",
        "tee": "tee",
        "t_off": "tee",
        "transformer": "transformer_mount",
        "transformer_mount": "transformer_mount",
        "tx_mount": "transformer_mount",
        "switch": "switch_mount",
        "switch_mount": "switch_mount",
        "abc": "bundle",
        "bundled": "bundle",
    }
    if s in POLE_TOP_ARRANGEMENTS:
        return s
    return aliases.get(s)


def infer_pole_top_from_structure(structure_type: object, location: object) -> str | None:
    st = str(structure_type or "").lower()
    loc = str(location or "").lower()
    if "terminal" in st:
        return "terminal"
    if "transformer" in st or "transformer" in loc or " kva" in loc:
        return "transformer_mount"
    return None


def parse_equipment_ratings(text: object) -> dict[str, Any]:
    out: dict[str, Any] = {"kva": None, "voltage_ratio": None, "secondary_v": None}
    if text is None or text == "":
        return out
    s = str(text)
    m = _RE_KVA.search(s) or _RE_KVA_COMPACT.search(s)
    if m:
        try:
            out["kva"] = float(m.group(1))
        except ValueError:
            out["kva"] = None
    vr = _RE_VOLT_RATIO.search(s)
    if vr:
        out["voltage_ratio"] = f"{vr.group(1)}kV / {vr.group(2)}kV"
    return out


def classify_equipment_mounting(raw: object) -> str | None:
    if raw is None or raw == "":
        return None
    s = str(raw).strip().lower()
    if "ground" in s or "gound" in s or "plinth" in s or "kiosk" in s:
        return "ground"
    if "pole" in s or "oh" in s or "overhead" in s:
        return "pole"
    return None


def parse_equipment_context(record: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Derive equipment categories and display fields from free-text + structured columns."""

    equip_raw = _get(record, "equipment") or _get(record, "mounted_equipment")
    rating_raw = _get(record, "equipment_rating") or _get(record, "rating")
    st = str(_get(record, "structure_type") or "")
    loc = str(_get(record, "location") or "")
    blob = f"{equip_raw or ''} {rating_raw or ''} {st} {loc}"

    categories = _tokenize_equipment_hint(blob)
    primary = categories[0] if categories else None
    detail = {k: dict(v) for k, v in EQUIPMENT_TYPES.items() if k in categories}
    ratings = parse_equipment_ratings(rating_raw or equip_raw or "")

    ptk = normalize_pole_top_key(_get(record, "pole_top_arrangement"))
    if not ptk:
        ptk = infer_pole_top_from_structure(st, loc)
    pole_top_detail: dict[str, str] = {}
    if ptk and ptk in POLE_TOP_ARRANGEMENTS:
        pole_top_detail = dict(POLE_TOP_ARRANGEMENTS[ptk])

    mounting = classify_equipment_mounting(_get(record, "equipment_mounting"))

    return {
        "equipment_categories": categories,
        "equipment_primary_category": primary,
        "equipment_type_detail": detail,
        "equipment_kva": ratings.get("kva"),
        "equipment_voltage_ratio": ratings.get("voltage_ratio"),
        "pole_top_arrangement": ptk,
        "pole_top_detail": pole_top_detail,
        "insulator_type": _clean_str(_get(record, "insulator_type")),
        "crossarm_configuration": _clean_str(_get(record, "crossarm_configuration")),
        "earthing_status": _clean_str(_get(record, "earthing_status")),
        "asset_plate_id": _clean_str(_get(record, "asset_plate_id")),
        "equipment_mounting": mounting,
    }


def _clean_str(v: object) -> str | None:
    if v is None or v == "":
        return None
    s = str(v).strip()
    return s or None


def row_suggests_transformer_equipment(record: Mapping[str, Any] | Any) -> bool:
    """True when remarks/structure imply a transformer site needing equipment capture."""
    ctx = parse_equipment_context(record)
    if ctx.get("equipment_primary_category") == "transformer":
        return True
    st = str(_get(record, "structure_type") or "").lower()
    loc = str(_get(record, "location") or "").lower()
    if "transformer" in st or "transformer" in loc:
        return True
    if _RE_KVA.search(str(_get(record, "equipment_rating") or "")):
        return True
    if _RE_KVA.search(str(_get(record, "location") or "")):
        return True
    return False


def merge_equipment_fields_into_props(props: dict[str, Any]) -> None:
    """Populate D2-B equipment / pole-top display keys (mutates ``props``)."""
    parsed = parse_equipment_context(props)
    props["equipment_categories"] = parsed.get("equipment_categories") or []
    props["equipment_primary_category"] = parsed.get("equipment_primary_category")
    props["equipment_type_detail"] = parsed.get("equipment_type_detail") or {}
    kva = parsed.get("equipment_kva")
    props["equipment_kva"] = kva
    props["equipment_voltage_ratio"] = parsed.get("equipment_voltage_ratio")
    if kva is not None:
        props["equipment_kva_label"] = f"{gfmt(kva)} kVA"
    else:
        props["equipment_kva_label"] = None
    props["pole_top_arrangement"] = parsed.get("pole_top_arrangement")
    props["pole_top_detail"] = parsed.get("pole_top_detail") or {}
    props["insulator_type"] = parsed.get("insulator_type")
    props["crossarm_configuration"] = parsed.get("crossarm_configuration")
    props["earthing_status"] = parsed.get("earthing_status")
    props["asset_plate_id"] = parsed.get("asset_plate_id")
    props["equipment_mounting"] = parsed.get("equipment_mounting")


def gfmt(x: float) -> str:
    """Format kVA without trailing .0 when whole."""
    if float(x).is_integer():
        return str(int(x))
    return str(x)
