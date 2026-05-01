from __future__ import annotations

from app.asset_classifier import classify_asset_type, get_popup_type_label


def test_classify_bt_expole_remark_as_third_party_telecoms() -> None:
    result = classify_asset_type(
        {
            "pole_id": "72",
            "structure_type": "EXpole",
            "location": "bt pole",
            "material": "wood",
        }
    )

    assert result["primary_type"] == "third_party_infrastructure"
    assert result["infrastructure_owner"] == "telecoms"
    assert result["subtype"] == "BT/Openreach pole"
    assert result["is_structural_pole"] is False
    assert result["is_electric_network"] is False
    assert result["classification_confidence"] == "high"
    assert "not part of electric network" in result["warnings"][0]
    assert get_popup_type_label(result) == "Third-Party Telecoms Pole (BT/Openreach)"


def test_classify_standard_expole_remains_electric_structural() -> None:
    result = classify_asset_type(
        {
            "pole_id": "73",
            "structure_type": "EXpole",
            "location": "existing pole",
            "material": "wood",
        }
    )

    assert result["primary_type"] == "electric_network"
    assert result["infrastructure_owner"] == "DNO"
    assert result["is_structural_pole"] is True
