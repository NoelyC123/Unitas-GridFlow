"""UK distribution conductor/cable vocabulary for survey display (D2-A).

Reference data only — not a compliance engine. Used for map popups and light QA hints.
"""

from __future__ import annotations

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
