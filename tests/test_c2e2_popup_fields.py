"""Tests for C2E2 popup field reference and validators.

Covers:
- field_reference.py: FIELD_DEFINITIONS, POPUP_FIELD_GROUPS, helpers
- field_validators.py: all 7 validator functions

Test data is grounded in real survey patterns from Gordon Pt1 and
Bellsprings files: Pol records (no height expected), EXpole records
(height expected), material always absent from Trimble format.
"""

from __future__ import annotations

from app.field_reference import (
    ALWAYS_PRESENT_FIELDS,
    DERIVED_FIELDS,
    FIELD_DEFINITIONS,
    POPUP_FIELD_GROUPS,
    POPUP_GROUP_ORDER,
    TRIMBLE_ATTRIBUTE_FIELDS,
    get_all_aliases,
    get_display_label,
    get_field_unit,
    get_fields_for_group,
    get_missing_wording,
    resolve_alias,
)
from app.field_validators import (
    classify_field_completeness,
    format_field_display,
    get_popup_display_value,
    is_measured,
    is_missing_legitimate,
    validate_field_value,
    validate_height_value,
)

# ---------------------------------------------------------------------------
# Helpers for test fixtures
# ---------------------------------------------------------------------------


def _pol_props(**overrides):
    """Minimal properties for an intermediate pole (Pol) — no height expected."""
    base = {
        "pole_id": "42",
        "structure_type": "Pol",
        "asset_intent": None,
        "record_role": "structural",
        "easting": 300000.0,
        "northing": 400000.0,
        "height": None,
        "qa_status": "PASS",
        "issue_count": 0,
        "warn_count": 0,
        "name": None,
        "material": None,
        "relationship": None,
    }
    base.update(overrides)
    return base


def _expole_props(**overrides):
    """Properties for an existing pole (EXpole) — height typically present."""
    base = {
        "pole_id": "29",
        "structure_type": "EXpole",
        "asset_intent": "Existing asset",
        "record_role": "structural",
        "easting": 365155.028,
        "northing": 643657.644,
        "height": 9.2,
        "qa_status": "PASS",
        "issue_count": 0,
        "warn_count": 0,
        "name": "ex pole",
        "material": None,
        "relationship": "replacement_pair",
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# TestFieldPresence — verifying FIELD_DEFINITIONS catalogue
# ---------------------------------------------------------------------------


class TestFieldPresence:
    def test_all_field_groups_present(self):
        for group in ("identity", "geometry", "quality", "survey_context", "relationship"):
            assert group in POPUP_FIELD_GROUPS

    def test_group_order_matches_groups(self):
        for g in POPUP_GROUP_ORDER:
            assert g in POPUP_FIELD_GROUPS

    def test_geometry_group_contains_core_fields(self):
        assert "easting" in POPUP_FIELD_GROUPS["geometry"]
        assert "northing" in POPUP_FIELD_GROUPS["geometry"]
        assert "height" in POPUP_FIELD_GROUPS["geometry"]

    def test_identity_group_contains_pole_id(self):
        assert "pole_id" in POPUP_FIELD_GROUPS["identity"]

    def test_quality_group_contains_qa_status(self):
        assert "qa_status" in POPUP_FIELD_GROUPS["quality"]

    def test_relationship_group_contains_replacement_fields(self):
        group = POPUP_FIELD_GROUPS["relationship"]
        assert "being_replaced_by" in group
        assert "replacing" in group

    def test_field_definitions_has_minimum_16_fields(self):
        assert len(FIELD_DEFINITIONS) >= 16

    def test_every_group_field_has_definition(self):
        for group_fields in POPUP_FIELD_GROUPS.values():
            for field in group_fields:
                assert field in FIELD_DEFINITIONS, f"No definition for '{field}'"

    def test_always_present_fields_defined(self):
        assert "pole_id" in ALWAYS_PRESENT_FIELDS
        assert "qa_status" in ALWAYS_PRESENT_FIELDS
        assert "easting" in ALWAYS_PRESENT_FIELDS

    def test_trimble_attribute_fields_include_height(self):
        assert "height" in TRIMBLE_ATTRIBUTE_FIELDS

    def test_trimble_attribute_fields_include_name(self):
        assert "name" in TRIMBLE_ATTRIBUTE_FIELDS

    def test_derived_fields_include_qa_status(self):
        assert "qa_status" in DERIVED_FIELDS

    def test_derived_fields_include_asset_intent(self):
        assert "asset_intent" in DERIVED_FIELDS

    def test_material_source_is_survey_not_derived(self):
        assert FIELD_DEFINITIONS["material"]["source"] == "survey"

    def test_height_has_validation_bounds(self):
        validation = FIELD_DEFINITIONS["height"]["validation"]
        assert validation is not None
        assert "min" in validation and "max" in validation

    def test_qa_status_has_allowed_values(self):
        allowed = FIELD_DEFINITIONS["qa_status"]["validation"]["allowed"]
        assert "PASS" in allowed
        assert "WARN" in allowed
        assert "FAIL" in allowed


# ---------------------------------------------------------------------------
# TestMissingValueWording — labels for absent fields
# ---------------------------------------------------------------------------


class TestMissingValueWording:
    def test_height_missing_on_pol_is_intermediate_note(self):
        wording = get_missing_wording("height", "Pol")
        assert "intermediate" in wording.lower()

    def test_height_missing_on_expole_is_check_note(self):
        wording = get_missing_wording("height", "EXpole")
        assert "check" in wording.lower()

    def test_height_missing_no_type_is_not_measured(self):
        wording = get_missing_wording("height")
        assert "not measured" in wording.lower()

    def test_material_missing_wording_says_not_recorded(self):
        wording = get_missing_wording("material")
        assert "not recorded" in wording.lower()

    def test_name_missing_wording_is_dash(self):
        wording = get_missing_wording("name")
        assert wording == "—"

    def test_relationship_missing_wording_is_dash(self):
        wording = get_missing_wording("relationship")
        assert wording == "—"

    def test_unknown_field_returns_dash(self):
        wording = get_missing_wording("completely_unknown_field")
        assert wording == "—"

    def test_easting_missing_wording_says_not_recorded(self):
        wording = get_missing_wording("easting")
        assert "not recorded" in wording.lower()

    def test_qa_status_missing_wording_says_not_assessed(self):
        wording = get_missing_wording("qa_status")
        assert "not assessed" in wording.lower()

    def test_conditional_missing_height_on_angle(self):
        wording = get_missing_wording("height", "Angle")
        assert "check" in wording.lower()

    def test_conditional_missing_height_on_prpole(self):
        wording = get_missing_wording("height", "PRpole")
        assert "not measured" in wording.lower()


# ---------------------------------------------------------------------------
# TestFieldValueValidation — validate_field_value and validate_height_value
# ---------------------------------------------------------------------------


class TestFieldValueValidation:
    def test_valid_height_passes(self):
        ok, err = validate_field_value(9.5, "height")
        assert ok is True
        assert err is None

    def test_height_below_minimum_fails(self):
        ok, err = validate_field_value(0.1, "height")
        assert ok is False
        assert "below minimum" in err

    def test_height_above_maximum_fails(self):
        ok, err = validate_field_value(35.0, "height")
        assert ok is False
        assert "exceeds maximum" in err

    def test_none_height_is_not_an_error(self):
        ok, err = validate_field_value(None, "height")
        assert ok is True

    def test_valid_qa_status_passes(self):
        for status in ("PASS", "WARN", "FAIL"):
            ok, err = validate_field_value(status, "qa_status")
            assert ok is True, f"Expected PASS for status={status!r}"

    def test_invalid_qa_status_fails(self):
        ok, err = validate_field_value("UNKNOWN", "qa_status")
        assert ok is False

    def test_negative_issue_count_fails(self):
        ok, err = validate_field_value(-1, "issue_count")
        assert ok is False

    def test_zero_issue_count_passes(self):
        ok, err = validate_field_value(0, "issue_count")
        assert ok is True

    def test_unknown_field_always_passes(self):
        ok, err = validate_field_value("anything", "completely_unknown_field")
        assert ok is True

    def test_string_numeric_height_coerced_and_validated(self):
        ok, err = validate_field_value("9.5", "height")
        assert ok is True

    def test_non_numeric_height_string_fails(self):
        ok, err = validate_field_value("very tall", "height")
        assert ok is False
        assert "numeric" in err

    def test_validate_height_value_plausible(self):
        ok, advisory = validate_height_value(9.2, "EXpole")
        assert ok is True
        assert advisory is None

    def test_validate_height_value_absent_on_pol_ok(self):
        ok, advisory = validate_height_value(None, "Pol")
        assert ok is True
        assert advisory is None

    def test_validate_height_value_absent_on_expole_advisory(self):
        ok, advisory = validate_height_value(None, "EXpole")
        assert ok is True
        assert advisory is not None
        assert "check" in advisory.lower()

    def test_validate_height_value_implausibly_low(self):
        ok, advisory = validate_height_value(0.1, "EXpole")
        assert ok is False

    def test_validate_height_value_implausibly_high(self):
        ok, advisory = validate_height_value(40.0, "EXpole")
        assert ok is False

    def test_validate_height_non_numeric(self):
        ok, advisory = validate_height_value("not a number", "EXpole")
        assert ok is False


# ---------------------------------------------------------------------------
# TestAliasMapping — resolve_alias and get_all_aliases
# ---------------------------------------------------------------------------


class TestAliasMapping:
    def test_canonical_name_resolves_to_itself(self):
        assert resolve_alias("height") == "height"
        assert resolve_alias("pole_id") == "pole_id"

    def test_ht_resolves_to_height(self):
        assert resolve_alias("ht") == "height"
        assert resolve_alias("Ht") == "height"
        assert resolve_alias("HT") == "height"

    def test_remark_resolves_to_name(self):
        assert resolve_alias("remark") == "name"
        assert resolve_alias("remarks") == "name"
        assert resolve_alias("location") == "name"

    def test_e_resolves_to_easting(self):
        assert resolve_alias("e") == "easting"
        assert resolve_alias("E") == "easting"

    def test_n_resolves_to_northing(self):
        assert resolve_alias("n") == "northing"

    def test_osgb_e_resolves_to_easting(self):
        assert resolve_alias("osgb_e") == "easting"

    def test_elev_resolves_to_height(self):
        assert resolve_alias("elev") == "height"

    def test_unknown_alias_returns_none(self):
        assert resolve_alias("definitely_not_a_field") is None

    def test_get_all_aliases_includes_canonical(self):
        aliases = get_all_aliases("height")
        assert "height" in aliases

    def test_get_all_aliases_includes_ht(self):
        aliases = get_all_aliases("height")
        assert "ht" in aliases

    def test_get_all_aliases_unknown_field_returns_field_name(self):
        aliases = get_all_aliases("unknown_field")
        assert aliases == ["unknown_field"]

    def test_get_display_label_known_field(self):
        assert get_display_label("height") == "Measured Height"
        assert get_display_label("pole_id") == "Point ID"

    def test_get_display_label_unknown_field_capitalises(self):
        label = get_display_label("some_unknown_field")
        assert isinstance(label, str)
        assert len(label) > 0

    def test_get_field_unit_height_is_metres(self):
        assert get_field_unit("height") == "m"

    def test_get_field_unit_easting_is_metres(self):
        assert get_field_unit("easting") == "m"

    def test_get_field_unit_qa_status_is_none(self):
        assert get_field_unit("qa_status") is None

    def test_get_fields_for_group_identity(self):
        fields = get_fields_for_group("identity")
        assert "pole_id" in fields
        assert "structure_type" in fields

    def test_get_fields_for_group_unknown_returns_empty(self):
        assert get_fields_for_group("nonexistent_group") == []


# ---------------------------------------------------------------------------
# TestConditionalFields — structure_type-aware behaviour
# ---------------------------------------------------------------------------


class TestConditionalFields:
    def test_height_missing_legitimate_for_pol(self):
        assert is_missing_legitimate("height", "Pol") is True

    def test_height_missing_not_legitimate_for_expole(self):
        assert is_missing_legitimate("height", "EXpole") is False

    def test_height_missing_not_legitimate_for_angle(self):
        assert is_missing_legitimate("height", "Angle") is False

    def test_height_missing_legitimate_for_hedge(self):
        assert is_missing_legitimate("height", "Hedge") is True

    def test_height_missing_legitimate_for_fence(self):
        assert is_missing_legitimate("height", "Fence") is True

    def test_height_missing_legitimate_for_crossing(self):
        assert is_missing_legitimate("height", "LVxing") is True

    def test_height_missing_legitimate_no_type(self):
        assert is_missing_legitimate("height", None) is True

    def test_material_always_legitimate_missing(self):
        for st in ("Pol", "EXpole", "Angle", None):
            assert is_missing_legitimate("material", st) is True

    def test_land_use_always_legitimate_missing(self):
        assert is_missing_legitimate("land_use") is True

    def test_pole_id_never_legitimate_missing(self):
        assert is_missing_legitimate("pole_id") is False

    def test_qa_status_never_legitimate_missing(self):
        assert is_missing_legitimate("qa_status") is False

    def test_relationship_always_legitimate_missing(self):
        assert is_missing_legitimate("relationship") is True

    def test_format_height_with_unit(self):
        assert format_field_display(9.5, "height", "EXpole") == "9.5m"

    def test_format_height_integer_no_trailing_zero(self):
        # 10.0 should format as "10m" not "10.0m"
        assert format_field_display(10.0, "height", "EXpole") == "10m"

    def test_format_missing_height_on_pol(self):
        result = format_field_display(None, "height", "Pol")
        assert "intermediate" in result.lower()

    def test_format_missing_height_on_expole(self):
        result = format_field_display(None, "height", "EXpole")
        assert "check" in result.lower()

    def test_format_missing_material(self):
        result = format_field_display(None, "material")
        assert "not recorded" in result.lower()


# ---------------------------------------------------------------------------
# TestIntegration — full pipeline on realistic feature properties
# ---------------------------------------------------------------------------


class TestIntegration:
    def test_pol_properties_completeness_height_is_absent_ok(self):
        props = _pol_props()
        result = classify_field_completeness(props, ["pole_id", "height", "qa_status", "material"])
        assert result["pole_id"] == "present"
        assert result["height"] == "absent_ok"
        assert result["qa_status"] == "present"
        assert result["material"] == "absent_ok"

    def test_expole_missing_height_is_absent_warn(self):
        props = _expole_props(height=None)
        result = classify_field_completeness(props, ["height"])
        assert result["height"] == "absent_warn"

    def test_expole_with_height_is_present(self):
        props = _expole_props(height=9.2)
        result = classify_field_completeness(props, ["height"])
        assert result["height"] == "present"

    def test_relationship_absent_is_ok_for_plain_pol(self):
        props = _pol_props()
        result = classify_field_completeness(props, ["relationship"])
        assert result["relationship"] == "absent_ok"

    def test_get_popup_display_value_height_on_expole(self):
        props = _expole_props()
        val = get_popup_display_value("height", props)
        assert val == "9.2m"

    def test_get_popup_display_value_missing_height_on_pol(self):
        props = _pol_props()
        val = get_popup_display_value("height", props)
        assert "intermediate" in val.lower()

    def test_get_popup_display_value_material_always_not_recorded(self):
        props = _expole_props()
        val = get_popup_display_value("material", props)
        assert "not recorded" in val.lower()

    def test_get_popup_display_value_with_alias_ht(self):
        # Property stored under alias 'ht' should still resolve
        props = {"ht": 7.5, "structure_type": "Angle"}
        val = get_popup_display_value("height", props)
        assert val == "7.5m"

    def test_get_popup_display_value_with_alias_location_for_name(self):
        props = {"location": "pole 1", "structure_type": "Angle"}
        val = get_popup_display_value("name", props)
        assert val == "pole 1"

    def test_validate_field_value_on_full_expole_properties(self):
        props = _expole_props()
        for field in ("height", "qa_status", "issue_count"):
            ok, err = validate_field_value(props.get(field), field)
            assert ok, f"Expected valid for {field}: err={err}"

    def test_classify_full_pol_record(self):
        props = _pol_props()
        fields = [
            "pole_id",
            "structure_type",
            "asset_intent",
            "record_role",
            "easting",
            "northing",
            "height",
            "qa_status",
            "issue_count",
            "warn_count",
            "name",
            "material",
            "relationship",
        ]
        result = classify_field_completeness(props, fields)
        assert result["pole_id"] == "present"
        assert result["easting"] == "present"
        assert result["qa_status"] == "present"
        assert result["height"] == "absent_ok"  # Pol — no height expected
        assert result["material"] == "absent_ok"  # Trimble format gap
        assert result["name"] == "absent_ok"  # optional
        assert result["relationship"] == "absent_ok"  # no pairing

    def test_classify_full_expole_record_with_height(self):
        props = _expole_props()
        result = classify_field_completeness(props, ["height", "material", "name"])
        assert result["height"] == "present"
        assert result["material"] == "absent_ok"
        assert result["name"] == "present"

    def test_is_measured_on_list_values(self):
        # Lists (like warn_texts) are truthy when non-empty
        assert is_measured([]) is True  # empty list is not None/nan/empty-string
        assert is_measured(["warn"]) is True

    def test_is_measured_on_zero_is_true(self):
        # Zero is a valid measured value (0 issues)
        assert is_measured(0) is True

    def test_classify_records_with_zero_issue_count(self):
        props = _pol_props(issue_count=0)
        result = classify_field_completeness(props, ["issue_count"])
        assert result["issue_count"] == "present"
