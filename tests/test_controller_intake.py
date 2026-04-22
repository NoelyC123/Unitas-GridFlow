from __future__ import annotations

import pandas as pd
import pytest

from app.controller_intake import (
    build_completeness_summary,
    convert_grid_to_wgs84,
    detect_grid_crs,
    is_controller_csv,
    is_raw_controller_dump,
    parse_controller_csv,
    parse_raw_controller_dump,
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


def test_build_completeness_summary_includes_feature_codes_found() -> None:
    df = pd.DataFrame(
        [
            {"pole_id": "1", "structure_type": "Angle", "easting": 242186.0, "northing": 402362.0},
            {"pole_id": "2", "structure_type": "Pol", "easting": 242200.0, "northing": 402380.0},
            {"pole_id": "3", "structure_type": "Hedge", "easting": 242250.0, "northing": 402400.0},
        ]
    )
    summary = build_completeness_summary(df)
    assert "feature_codes_found" in summary
    assert set(summary["feature_codes_found"]) == {"Angle", "Pol", "Hedge"}


# ---------------------------------------------------------------------------
# is_raw_controller_dump
# ---------------------------------------------------------------------------


def test_is_raw_controller_dump_detects_job_version_units_header() -> None:
    assert is_raw_controller_dump("Job:28-14 513,Version:24.00,Units:Metres") is True


def test_is_raw_controller_dump_returns_false_for_plain_csv_header() -> None:
    assert is_raw_controller_dump("pole_id,easting,northing,height,material") is False


def test_is_raw_controller_dump_returns_false_for_controller_column_header() -> None:
    # Structured controller export with actual column names — not a raw dump
    assert is_raw_controller_dump("Point,Code,Grid E,Grid N,Elev,Desc") is False


# ---------------------------------------------------------------------------
# parse_raw_controller_dump
# ---------------------------------------------------------------------------

_RAW_DUMP_CONTENT = """\
Job:28-14 513,Version:24.00,Units:Metres
PRS485572899536,219497.298,413575.610,118.985,
1,242186.075,402362.807,99.505,Angle,Angle:STRING,1,Angle:TAG,5,Angle:REMARK,convert to tee
2,242200.000,402380.000,100.000,Pol,Pol:STRING,2,Pol:TAG,6,Pol:HEIGHT,10.5
3,242250.000,402400.000,101.000,Hedge
4,242300.000,402420.000,101.500,EXpole,EXpole:REMARK,new term pole pos
"""


def test_parse_raw_controller_dump_extracts_correct_record_count(tmp_path) -> None:
    f = tmp_path / "dump.csv"
    f.write_text(_RAW_DUMP_CONTENT)
    df = parse_raw_controller_dump(f)
    # 4 survey points — metadata and PRS rows must be excluded
    assert len(df) == 4


def test_parse_raw_controller_dump_skips_prs_and_metadata_rows(tmp_path) -> None:
    f = tmp_path / "dump.csv"
    f.write_text(_RAW_DUMP_CONTENT)
    df = parse_raw_controller_dump(f)
    assert "PRS485572899536" not in df["pole_id"].values


def test_parse_raw_controller_dump_maps_height_from_attribute_not_gps_elevation(
    tmp_path,
) -> None:
    # Point 1 has no HEIGHT attribute (only STRING/TAG/REMARK) → height should be NaN
    # Point 2 has HEIGHT attribute = 10.5 → height should be 10.5
    # Point 3 has no attributes at all → height should be NaN
    f = tmp_path / "dump.csv"
    f.write_text(_RAW_DUMP_CONTENT)
    df = parse_raw_controller_dump(f).set_index("pole_id")

    assert pd.isna(df.loc["1", "height"])
    assert df.loc["2", "height"] == pytest.approx(10.5)
    assert pd.isna(df.loc["3", "height"])


def test_parse_raw_controller_dump_maps_remark_to_location(tmp_path) -> None:
    f = tmp_path / "dump.csv"
    f.write_text(_RAW_DUMP_CONTENT)
    df = parse_raw_controller_dump(f).set_index("pole_id")

    assert df.loc["1", "location"] == "convert to tee"
    assert df.loc["4", "location"] == "new term pole pos"
    assert pd.isna(df.loc["3", "location"])


def test_parse_raw_controller_dump_maps_feature_code_to_structure_type(tmp_path) -> None:
    f = tmp_path / "dump.csv"
    f.write_text(_RAW_DUMP_CONTENT)
    df = parse_raw_controller_dump(f).set_index("pole_id")

    assert df.loc["1", "structure_type"] == "Angle"
    assert df.loc["3", "structure_type"] == "Hedge"
    assert df.loc["4", "structure_type"] == "EXpole"


def test_parse_raw_controller_dump_easting_northing_are_numeric(tmp_path) -> None:
    f = tmp_path / "dump.csv"
    f.write_text(_RAW_DUMP_CONTENT)
    df = parse_raw_controller_dump(f)

    assert df["easting"].dtype.kind == "f"
    assert df["northing"].dtype.kind == "f"
    assert df.loc[0, "easting"] == pytest.approx(242186.075)
    assert df.loc[0, "northing"] == pytest.approx(402362.807)
