"""Asset classification for electric-network vs third-party infrastructure."""

from __future__ import annotations

from typing import Any

TELECOMS_FEATURE_CODES = {
    "BT",
    "bt",
    "BTPole",
    "btpole",
    "BTpole",
    "Openreach",
    "openreach",
    "Telecom",
    "telecom",
    "Telecoms",
    "telecoms",
}

TELECOMS_MATERIALS = {
    "BT_pole",
    "bt_pole",
    "telecoms_pole",
    "telecom pole",
}

TELECOMS_KEYWORDS = {
    "bt pole",
    "openreach pole",
    "telecom pole",
    "telecoms pole",
    "fibre pole",
    "telephone pole",
    "virgin media",
    "copper line",
}

STREETLIGHT_FEATURE_CODES = {"SL", "streetlight", "street_light", "lamp"}
STREETLIGHT_KEYWORDS = {"streetlight", "street light", "lamp post", "lighting column"}

CUSTOMER_SERVICE_FEATURE_CODES = {"CS", "customer_service", "service_pole"}
CUSTOMER_SERVICE_KEYWORDS = {"customer pole", "service pole", "private pole"}

ELECTRIC_STRUCTURAL_CODES = {
    "EXpole",
    "expole",
    "EXPOLE",
    "PRpole",
    "prpole",
    "PRPOLE",
    "Pol",
    "pol",
    "POL",
    "Angle",
    "angle",
    "ANGLE",
    "Terminal",
    "terminal",
    "TERMINAL",
    "Stay",
    "stay",
    "Anchor",
    "anchor",
    "Pole",
    "pole",
    "POLE",
    "Wood Pole",
    "Steel Pole",
    "Concrete Pole",
    "Composite Pole",
}

ELECTRIC_EQUIPMENT_CODES = {
    "Transformer",
    "Switch",
    "Fuse",
    "Recloser",
    "RMU",
    "LV_board",
}

CONTEXT_CODES = {
    "Road",
    "road",
    "Track",
    "track",
    "Gate",
    "gate",
    "Fence",
    "fence",
    "Hedge",
    "hedge",
    "Tree",
    "tree",
    "Stream",
    "stream",
    "Wall",
    "wall",
    "Pline",
    "pline",
    "11xing",
    "33xing",
    "110xing",
    "BTxing",
    "btxing",
    "HVxing",
    "LVxing",
    "Ignore",
    "ignore",
}


def _text(record: Any, *fields: str) -> str:
    parts: list[str] = []
    for field in fields:
        value = record.get(field) if hasattr(record, "get") else None
        if value is not None:
            parts.append(str(value))
    return " ".join(parts).strip().lower()


def _contains_any(text: str, keywords: set[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def classify_asset_type(record: Any) -> dict[str, Any]:
    """Classify a survey record into electric, third-party, context, or unknown."""

    feature_code = str(
        record.get("structure_type") or record.get("feature_code") or ""
        if hasattr(record, "get")
        else ""
    ).strip()
    material = str(record.get("material") or "" if hasattr(record, "get") else "").strip()
    remarks = _text(record, "remarks", "location", "name", "description", "comment")

    if (
        feature_code in TELECOMS_FEATURE_CODES
        or material in TELECOMS_MATERIALS
        or _contains_any(remarks, TELECOMS_KEYWORDS)
    ):
        return {
            "primary_type": "third_party_infrastructure",
            "infrastructure_owner": "telecoms",
            "subtype": "BT/Openreach pole",
            "is_structural_pole": False,
            "is_electric_network": False,
            "classification_confidence": "high",
            "warnings": [
                "Third-party telecoms infrastructure - not part of electric network design"
            ],
            "classification_basis": "feature code / remarks / material analysis",
        }

    if feature_code in STREETLIGHT_FEATURE_CODES or _contains_any(remarks, STREETLIGHT_KEYWORDS):
        return {
            "primary_type": "third_party_infrastructure",
            "infrastructure_owner": "local_authority",
            "subtype": "streetlight",
            "is_structural_pole": False,
            "is_electric_network": False,
            "classification_confidence": "high",
            "warnings": ["Local authority streetlight - not part of electric network"],
            "classification_basis": "feature code / remarks analysis",
        }

    if feature_code in CUSTOMER_SERVICE_FEATURE_CODES or _contains_any(
        remarks, CUSTOMER_SERVICE_KEYWORDS
    ):
        return {
            "primary_type": "third_party_infrastructure",
            "infrastructure_owner": "customer",
            "subtype": "customer service pole",
            "is_structural_pole": False,
            "is_electric_network": False,
            "classification_confidence": "medium",
            "warnings": ["Customer-owned service pole - not DNO responsibility"],
            "classification_basis": "feature code / remarks analysis",
        }

    if feature_code in ELECTRIC_STRUCTURAL_CODES:
        return {
            "primary_type": "electric_network",
            "infrastructure_owner": "DNO",
            "subtype": "structural_support",
            "is_structural_pole": True,
            "is_electric_network": True,
            "classification_confidence": "high",
            "warnings": [],
            "classification_basis": "DNO feature code",
        }

    if feature_code in ELECTRIC_EQUIPMENT_CODES:
        return {
            "primary_type": "electric_network",
            "infrastructure_owner": "DNO",
            "subtype": "electrical_equipment",
            "is_structural_pole": False,
            "is_electric_network": True,
            "classification_confidence": "high",
            "warnings": [],
            "classification_basis": "DNO feature code",
        }

    if feature_code in CONTEXT_CODES:
        return {
            "primary_type": "context",
            "infrastructure_owner": "various",
            "subtype": "environmental_context",
            "is_structural_pole": False,
            "is_electric_network": False,
            "classification_confidence": "high",
            "warnings": [],
            "classification_basis": "context feature code",
        }

    return {
        "primary_type": "unclassified",
        "infrastructure_owner": "unknown",
        "subtype": "unknown",
        "is_structural_pole": False,
        "is_electric_network": False,
        "classification_confidence": "low",
        "warnings": ["Asset type could not be confidently classified - manual review required"],
        "classification_basis": "insufficient data",
    }


def get_popup_type_label(classification: dict[str, Any]) -> str:
    """Return a concise type label for map popups."""

    primary_type = classification.get("primary_type")
    owner = classification.get("infrastructure_owner")
    subtype = classification.get("subtype")

    if primary_type == "third_party_infrastructure":
        if owner == "telecoms":
            return "Third-Party Telecoms Pole (BT/Openreach)"
        if owner == "local_authority":
            return "Local Authority Streetlight"
        if owner == "customer":
            return "Customer Service Pole"
        return "Third-Party Infrastructure"

    if primary_type == "electric_network":
        if subtype == "structural_support":
            return "Electric Network Structural Pole"
        if subtype == "electrical_equipment":
            return "Electric Network Equipment"
        return "Electric Network Asset"

    if primary_type == "context":
        return "Environmental/Context Feature"

    return "Unclassified Asset (Review Required)"
