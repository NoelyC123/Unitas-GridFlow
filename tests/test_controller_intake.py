from __future__ import annotations

import pandas as pd
import pytest

from app.controller_intake import (
    build_completeness_summary,
    convert_grid_to_wgs84,
    detect_grid_crs,
    is_controller_csv,
    parse_controller_csv,
)

# ---------------------------------------------------------------------------
# detect_grid_crs
# ---------------------------------------------------------------------------


def test_detect_grid_crs_identifies_itm() -> None:
    # Dublin area in ITM (EPSG:2157)
    assert detect_grid_crs(715_000.0, 735_000.0) == "EPSG:2157"


def test_detect_grid_crs_identifies_tm65() -> None:
    # Dublin area in old Irish National Grid TM65 (EPSG:29900)
    assert detect_grid_crs(315_000.0, 234_000.0) == "EPSG:29900"


def test_detect_grid_crs_identifies_osgb36() -> None:
    # Lake District (England) in OSGB36 (EPSG:27700)
    assert detect_grid_crs(352_841.0, 503_122.0) == "EPSG:27700"


# ---------------------------------------------------------------------------
# convert_grid_to_wgs84
# ---------------------------------------------------------------------------


def test_convert_grid_to_wgs84_itm_produces_valid_latlon() -> None:
    # Belfast area in ITM: approximately 54.6°N, 5.9°W
    df = pd.DataFrame([{"easting": 734_000.0, "northing": 874_000.0}])
    result = convert_grid_to_wgs84(df)

    assert "lat" in result.columns
    assert "lon" in result.columns
    assert result.loc[0, "lat"] == pytest.approx(54.6, abs=0.5)
    assert result.loc[0, "lon"] == pytest.approx(-5.9, abs=0.5)
    assert result.loc[0, "_grid_crs"] == "EPSG:2157"


def test_convert_grid_to_wgs84_osgb36_produces_valid_latlon() -> None:
    # OSGB36 coordinates in Cumbria — actual pyproj output is ~54.52°N, ~2.73°W
    # (mock_survey.csv lat/lon were hand-crafted and do not match exactly)
    df = pd.DataFrame([{"easting": 352_841.0, "northing": 503_122.0}])
    result = convert_grid_to_wgs84(df)

    assert result.loc[0, "lat"] == pytest.approx(54.52, abs=0.2)
    assert result.loc[0, "lon"] == pytest.approx(-2.73, abs=0.2)
    assert result.loc[0, "_grid_crs"] == "EPSG:27700"


def test_convert_grid_to_wgs84_skips_if_latlon_already_present() -> None:
    df = pd.DataFrame([{"easting": 352_841.0, "northing": 503_122.0, "lat": 54.5, "lon": -3.0}])
    result = convert_grid_to_wgs84(df)

    # Original lat/lon should be unchanged
    assert result.loc[0, "lat"] == 54.5
    assert "_grid_crs" not in result.columns


def test_convert_grid_to_wgs84_skips_if_no_grid_columns() -> None:
    df = pd.DataFrame([{"pole_id": "P-001", "height": 11.0}])
    result = convert_grid_to_wgs84(df)
    assert "lat" not in result.columns


# ---------------------------------------------------------------------------
# is_controller_csv
# ---------------------------------------------------------------------------


def test_is_controller_csv_detects_point_and_code_columns() -> None:
    df = pd.DataFrame(columns=["Point", "Code", "Grid E", "Grid N", "Height", "Desc"])
    assert is_controller_csv(df) is True


def test_is_controller_csv_detects_elev_column() -> None:
    df = pd.DataFrame(columns=["ID", "Elev", "E", "N"])
    assert is_controller_csv(df) is True


def test_is_controller_csv_returns_false_for_structured_csv() -> None:
    df = pd.DataFrame(
        columns=["asset_id", "structure_type", "height_m", "material", "latitude", "longitude"]
    )
    assert is_controller_csv(df) is False


# ---------------------------------------------------------------------------
# parse_controller_csv
# ---------------------------------------------------------------------------


def test_parse_controller_csv_maps_controller_columns_to_schema() -> None:
    df = pd.DataFrame(
        [
            {
                "Point": "1",
                "Code": "POLE",
                "Grid E": 734_000.0,
                "Grid N": 874_000.0,
                "Elev": 45.3,
                "Desc": "Wood Pole 11m",
            }
        ]
    )
    result = parse_controller_csv(df)

    assert result.loc[0, "pole_id"] == "1"
    assert result.loc[0, "structure_type"] == "POLE"
    assert result.loc[0, "easting"] == pytest.approx(734_000.0)
    assert result.loc[0, "northing"] == pytest.approx(874_000.0)
    assert result.loc[0, "height"] == pytest.approx(45.3)
    assert result.loc[0, "location"] == "Wood Pole 11m"
    # ITM grid should be converted to lat/lon
    assert "lat" in result.columns
    assert result.loc[0, "lat"] == pytest.approx(54.6, abs=0.5)


def test_parse_controller_csv_generates_pole_id_when_no_id_column() -> None:
    df = pd.DataFrame(
        [
            {"Code": "POLE", "Grid E": 352_841.0, "Grid N": 503_122.0},
            {"Code": "POLE", "Grid E": 352_910.0, "Grid N": 503_088.0},
        ]
    )
    result = parse_controller_csv(df)

    assert result.loc[0, "pole_id"] == "P-0001"
    assert result.loc[1, "pole_id"] == "P-0002"


def test_parse_controller_csv_coerces_numeric_grid_columns() -> None:
    df = pd.DataFrame([{"point": "1", "e": "352841", "n": "503122", "h": "11.5"}])
    result = parse_controller_csv(df)

    assert result.loc[0, "easting"] == pytest.approx(352_841.0)
    assert result.loc[0, "northing"] == pytest.approx(503_122.0)
    assert result.loc[0, "height"] == pytest.approx(11.5)


# ---------------------------------------------------------------------------
# build_completeness_summary
# ---------------------------------------------------------------------------


def test_build_completeness_summary_reports_per_field_coverage() -> None:
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-001",
                "easting": 734_000.0,
                "northing": 874_000.0,
                "lat": 54.6,
                "lon": -5.9,
                "height": 11.0,
                "structure_type": "POLE",
                "material": None,
                "location": "Test Site",
            },
            {
                "pole_id": "P-002",
                "easting": 734_100.0,
                "northing": 874_100.0,
                "lat": 54.61,
                "lon": -5.91,
                "height": None,
                "structure_type": "POLE",
                "material": None,
                "location": None,
            },
        ]
    )
    summary = build_completeness_summary(df)

    assert summary["total_records"] == 2
    assert summary["fields"]["material"]["present"] == 0
    assert summary["fields"]["material"]["coverage_pct"] == 0.0
    assert summary["fields"]["height"]["present"] == 1
    assert summary["fields"]["height"]["coverage_pct"] == 50.0
    assert summary["fields"]["pole_id"]["coverage_pct"] == 100.0


def test_build_completeness_summary_position_status_latlon_and_grid() -> None:
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-001",
                "easting": 352_841.0,
                "northing": 503_122.0,
                "lat": 54.52,
                "lon": -3.01,
            }
        ]
    )
    summary = build_completeness_summary(df)
    assert summary["position_status"] == "latlon_and_grid"


def test_build_completeness_summary_position_status_grid_only() -> None:
    df = pd.DataFrame([{"pole_id": "P-001", "easting": 352_841.0, "northing": 503_122.0}])
    summary = build_completeness_summary(df)
    assert summary["position_status"] == "grid_only"


def test_build_completeness_summary_reports_grid_crs_detected() -> None:
    df = pd.DataFrame(
        [
            {
                "pole_id": "P-001",
                "easting": 734_000.0,
                "northing": 874_000.0,
                "_grid_crs": "EPSG:2157",
            }
        ]
    )
    summary = build_completeness_summary(df)
    assert summary["grid_crs_detected"] == "EPSG:2157"


def test_build_completeness_summary_empty_df_returns_no_data() -> None:
    summary = build_completeness_summary(pd.DataFrame())
    assert summary["total_records"] == 0
    assert summary["position_status"] == "no_data"
