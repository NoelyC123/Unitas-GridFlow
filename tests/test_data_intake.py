"""Tests for CSV parsing robustness utilities in api_intake."""

from __future__ import annotations

import pandas as pd

from app.routes.api_intake import (
    _normalize_dataframe,
    _remove_empty_rows,
    clean_numeric_field,
    clean_text_field,
    format_import_summary,
    generate_import_summary,
    validate_required_fields,
)

# ---------------------------------------------------------------------------
# clean_numeric_field
# ---------------------------------------------------------------------------


class TestCleanNumericField:
    def test_plain_float_passthrough(self):
        assert clean_numeric_field(9.5) == 9.5

    def test_plain_int_passthrough(self):
        assert clean_numeric_field(10) == 10.0

    def test_whitespace_stripping(self):
        assert clean_numeric_field("  123.45  ") == 123.45

    def test_metre_suffix_removed(self):
        assert clean_numeric_field("9.5m") == 9.5

    def test_km_suffix_converts_to_metres(self):
        assert clean_numeric_field("1.5km") == 1500.0

    def test_na_returns_none(self):
        assert clean_numeric_field("N/A") is None
        assert clean_numeric_field("n/a") is None

    def test_not_measured_returns_none(self):
        assert clean_numeric_field("not measured") is None

    def test_unknown_returns_none(self):
        assert clean_numeric_field("unknown") is None

    def test_empty_string_returns_none(self):
        assert clean_numeric_field("") is None
        assert clean_numeric_field("   ") is None

    def test_none_returns_none(self):
        assert clean_numeric_field(None) is None

    def test_nan_returns_none(self):

        assert clean_numeric_field(float("nan")) is None

    def test_non_numeric_string_returns_none(self):
        assert clean_numeric_field("not-a-number") is None

    def test_dash_returns_none(self):
        assert clean_numeric_field("-") is None


# ---------------------------------------------------------------------------
# clean_text_field
# ---------------------------------------------------------------------------


class TestCleanTextField:
    def test_leading_trailing_whitespace_stripped(self):
        assert clean_text_field("  EXpole  ") == "EXpole"

    def test_internal_spaces_collapsed(self):
        assert clean_text_field("EX   pole") == "EX pole"

    def test_empty_string_returns_none(self):
        assert clean_text_field("") is None
        assert clean_text_field("   ") is None

    def test_none_returns_none(self):
        assert clean_text_field(None) is None

    def test_normal_value_preserved(self):
        assert clean_text_field("Pol") == "Pol"

    def test_mixed_case_preserved(self):
        assert clean_text_field("EXpole") == "EXpole"


# ---------------------------------------------------------------------------
# _remove_empty_rows
# ---------------------------------------------------------------------------


class TestRemoveEmptyRows:
    def test_all_nan_row_removed(self):
        df = pd.DataFrame(
            {
                "easting": [100.0, None, 200.0],
                "northing": [300.0, None, 400.0],
                "height": [9.5, None, 12.0],
            }
        )
        result = _remove_empty_rows(df)
        assert len(result) == 2

    def test_row_with_no_coordinates_removed(self):
        # height is present but both coord columns are None → remove
        df = pd.DataFrame(
            {
                "easting": [100.0, None, 200.0],
                "northing": [300.0, None, 400.0],
                "height": [9.5, 10.0, 12.0],
            }
        )
        result = _remove_empty_rows(df)
        assert len(result) == 2

    def test_row_with_partial_coords_kept(self):
        # Only one coord column null — kept (other column may fill in)
        df = pd.DataFrame(
            {
                "easting": [100.0, None],
                "northing": [300.0, 400.0],
            }
        )
        result = _remove_empty_rows(df)
        assert len(result) == 2

    def test_valid_rows_unchanged(self):
        df = pd.DataFrame({"easting": [100.0, 200.0], "northing": [300.0, 400.0]})
        result = _remove_empty_rows(df)
        assert len(result) == 2

    def test_no_coord_columns_only_drops_all_nan(self):
        df = pd.DataFrame({"height": [9.5, None], "material": ["Wood", None]})
        result = _remove_empty_rows(df)
        # Row 1 has height=9.5 so not all-NaN; row 2 is all-NaN → removed
        assert len(result) == 1


# ---------------------------------------------------------------------------
# validate_required_fields
# ---------------------------------------------------------------------------


class TestValidateRequiredFields:
    def test_easting_northing_present_is_valid(self):
        df = pd.DataFrame({"easting": [100.0], "northing": [300.0]})
        is_valid, messages = validate_required_fields(df)
        assert is_valid is True

    def test_lat_lon_present_is_valid(self):
        df = pd.DataFrame({"lat": [54.5], "lon": [-3.0]})
        is_valid, messages = validate_required_fields(df)
        assert is_valid is True

    def test_no_coord_columns_is_invalid(self):
        df = pd.DataFrame({"height": [9.5], "material": ["Wood"]})
        is_valid, messages = validate_required_fields(df)
        assert is_valid is False
        assert any("coordinate" in m.lower() for m in messages)

    def test_error_message_lists_available_columns(self):
        df = pd.DataFrame({"height": [9.5]})
        _, messages = validate_required_fields(df)
        assert any("height" in m for m in messages)

    def test_missing_pole_id_produces_advisory(self):
        df = pd.DataFrame({"easting": [100.0], "northing": [300.0]})
        is_valid, messages = validate_required_fields(df)
        assert is_valid is True
        assert any("pole_id" in m or "point_id" in m for m in messages)


# ---------------------------------------------------------------------------
# Header normalization (via _normalize_dataframe)
# ---------------------------------------------------------------------------


class TestHeaderNormalization:
    def _norm(self, df: pd.DataFrame) -> pd.DataFrame:
        result, _ = _normalize_dataframe(df)
        return result

    def test_mixed_case_headers_normalised(self):
        df = pd.DataFrame({"Easting": [100], "Northing": [300]})
        result = self._norm(df)
        assert "easting" in result.columns
        assert "northing" in result.columns

    def test_whitespace_in_headers_stripped(self):
        df = pd.DataFrame({"  Easting  ": [100], " Northing ": [300]})
        result = self._norm(df)
        assert "easting" in result.columns
        assert "northing" in result.columns

    def test_e_n_single_letter_aliases(self):
        df = pd.DataFrame({"E": [100], "N": [300]})
        result = self._norm(df)
        assert "easting" in result.columns
        assert "northing" in result.columns

    def test_ht_alias_maps_to_height(self):
        df = pd.DataFrame({"easting": [100], "northing": [300], "Ht": [9.5]})
        result = self._norm(df)
        assert "height" in result.columns

    def test_osgb_style_headers(self):
        df = pd.DataFrame({"osgb_e": [100], "osgb_n": [300]})
        result = self._norm(df)
        assert "easting" in result.columns
        assert "northing" in result.columns


# ---------------------------------------------------------------------------
# generate_import_summary / format_import_summary
# ---------------------------------------------------------------------------


class TestImportSummary:
    def _make_summary(self, rows_orig=5, rows_proc=4, warnings=None):
        df_orig = pd.DataFrame({"easting": range(rows_orig), "northing": range(rows_orig)})
        df_proc = pd.DataFrame({"easting": range(rows_proc), "northing": range(rows_proc)})
        return generate_import_summary(df_orig, df_proc, warnings or [])

    def test_row_counts_correct(self):
        s = self._make_summary(rows_orig=10, rows_proc=8)
        assert s["total_rows_in_csv"] == 10
        assert s["rows_imported"] == 8
        assert s["rows_skipped"] == 2

    def test_field_coverage_computed(self):
        s = self._make_summary(rows_proc=4)
        assert "easting" in s["field_coverage"]
        assert s["field_coverage"]["easting"]["percentage"] == 100.0

    def test_warnings_included(self):
        s = self._make_summary(warnings=["Missing pole_id"])
        assert "Missing pole_id" in s["warnings"]

    def test_format_returns_string(self):
        s = self._make_summary()
        text = format_import_summary(s)
        assert isinstance(text, str)
        assert "IMPORT SUMMARY" in text
        assert "Imported successfully" in text

    def test_format_shows_skipped_when_nonzero(self):
        s = self._make_summary(rows_orig=10, rows_proc=8)
        text = format_import_summary(s)
        assert "Skipped" in text

    def test_format_hides_skipped_when_zero(self):
        s = self._make_summary(rows_orig=5, rows_proc=5)
        text = format_import_summary(s)
        assert "Skipped" not in text
