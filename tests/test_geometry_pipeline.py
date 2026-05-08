"""Tests for geometry utility functions in geometry_pipeline."""

from __future__ import annotations

import pytest

from app.geometry_pipeline import (
    calculate_bearing,
    calculate_distance,
    validate_coordinates,
)

# Valid OSGB easting/northing pair used throughout (central England).
_E = 300_000.0
_N = 400_000.0


# ---------------------------------------------------------------------------
# validate_coordinates
# ---------------------------------------------------------------------------


class TestValidateCoordinates:
    def test_valid_pair_returns_true(self):
        ok, err = validate_coordinates(_E, _N)
        assert ok is True
        assert err is None

    def test_none_easting_invalid(self):
        ok, err = validate_coordinates(None, _N)
        assert ok is False
        assert err is not None

    def test_none_northing_invalid(self):
        ok, err = validate_coordinates(_E, None)
        assert ok is False
        assert err is not None

    def test_non_numeric_easting_invalid(self):
        ok, err = validate_coordinates("not-a-number", _N)
        assert ok is False
        assert "Non-numeric" in err

    def test_nan_easting_invalid(self):
        ok, err = validate_coordinates(float("nan"), _N)
        assert ok is False

    def test_inf_northing_invalid(self):
        ok, err = validate_coordinates(_E, float("inf"))
        assert ok is False

    def test_easting_zero_invalid(self):
        ok, err = validate_coordinates(0.0, _N)
        assert ok is False
        assert "outside OSGB" in err

    def test_easting_at_upper_bound_invalid(self):
        ok, err = validate_coordinates(700_000.0, _N)
        assert ok is False

    def test_northing_zero_invalid(self):
        ok, err = validate_coordinates(_E, 0.0)
        assert ok is False

    def test_northing_at_upper_bound_invalid(self):
        ok, err = validate_coordinates(_E, 1_300_000.0)
        assert ok is False

    def test_record_id_included_in_error(self):
        _, err = validate_coordinates(None, _N, record_id="P001")
        assert "P001" in err

    def test_string_numeric_accepted(self):
        ok, err = validate_coordinates("300000", "400000")
        assert ok is True


# ---------------------------------------------------------------------------
# calculate_distance
# ---------------------------------------------------------------------------


class TestCalculateDistance:
    def _rec(self, e, n, elev=None, pid="P"):
        r = {"easting": e, "northing": n, "point_id": pid}
        if elev is not None:
            r["elevation"] = elev
        return r

    def test_known_distance_horizontal(self):
        r1 = self._rec(_E, _N, pid="A")
        r2 = self._rec(_E + 100, _N, pid="B")
        dist, err = calculate_distance(r1, r2, include_elevation=False)
        assert err is None
        assert dist == pytest.approx(100.0, abs=0.01)

    def test_known_distance_diagonal(self):
        r1 = self._rec(_E, _N, pid="A")
        r2 = self._rec(_E + 30, _N + 40, pid="B")
        dist, err = calculate_distance(r1, r2, include_elevation=False)
        assert err is None
        assert dist == pytest.approx(50.0, abs=0.01)

    def test_elevation_included_gives_3d_distance(self):
        r1 = self._rec(_E, _N, elev=0.0, pid="A")
        r2 = self._rec(_E, _N + 40, elev=30.0, pid="B")
        dist, err = calculate_distance(r1, r2, include_elevation=True)
        assert err is None
        assert dist == pytest.approx(50.0, abs=0.01)

    def test_elevation_missing_falls_back_to_horizontal(self):
        r1 = self._rec(_E, _N, pid="A")
        r2 = self._rec(_E, _N + 100, pid="B")
        dist, err = calculate_distance(r1, r2, include_elevation=True)
        assert err is None
        assert dist == pytest.approx(100.0, abs=0.01)

    def test_invalid_coords_returns_error(self):
        r1 = self._rec(None, None, pid="X")
        r2 = self._rec(_E, _N, pid="Y")
        dist, err = calculate_distance(r1, r2)
        assert dist is None
        assert err is not None

    def test_same_point_returns_zero(self):
        r = self._rec(_E, _N, pid="A")
        dist, err = calculate_distance(r, r)
        assert err is None
        assert dist == pytest.approx(0.0, abs=0.001)


# ---------------------------------------------------------------------------
# calculate_bearing
# ---------------------------------------------------------------------------


class TestCalculateBearing:
    def _rec(self, e, n, pid="P"):
        return {"easting": e, "northing": n, "point_id": pid}

    def test_north_bearing(self):
        r1 = self._rec(_E, _N, pid="A")
        r2 = self._rec(_E, _N + 100, pid="B")
        bearing, err = calculate_bearing(r1, r2)
        assert err is None
        assert bearing == pytest.approx(0.0, abs=0.01)

    def test_east_bearing(self):
        r1 = self._rec(_E, _N, pid="A")
        r2 = self._rec(_E + 100, _N, pid="B")
        bearing, err = calculate_bearing(r1, r2)
        assert err is None
        assert bearing == pytest.approx(90.0, abs=0.01)

    def test_south_bearing(self):
        r1 = self._rec(_E, _N, pid="A")
        r2 = self._rec(_E, _N - 100, pid="B")
        bearing, err = calculate_bearing(r1, r2)
        assert err is None
        assert bearing == pytest.approx(180.0, abs=0.01)

    def test_west_bearing(self):
        r1 = self._rec(_E, _N, pid="A")
        r2 = self._rec(_E - 100, _N, pid="B")
        bearing, err = calculate_bearing(r1, r2)
        assert err is None
        assert bearing == pytest.approx(270.0, abs=0.01)

    def test_bearing_in_range_0_360(self):
        r1 = self._rec(_E, _N, pid="A")
        r2 = self._rec(_E - 50, _N - 50, pid="B")
        bearing, err = calculate_bearing(r1, r2)
        assert err is None
        assert 0.0 <= bearing < 360.0

    def test_invalid_coords_returns_error(self):
        r1 = self._rec(None, None, pid="X")
        r2 = self._rec(_E, _N, pid="Y")
        bearing, err = calculate_bearing(r1, r2)
        assert bearing is None
        assert err is not None
