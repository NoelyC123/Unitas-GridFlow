"""Tests for coordinate transformer."""

import pytest

from gridflow.baseline import BaselineDataset, BaselinePole, CoordinateTransformer


@pytest.fixture
def transformer():
    """Return transformer instance."""
    try:
        return CoordinateTransformer()
    except ImportError:
        pytest.skip("pyproj not available")


class TestCoordinateValidation:
    """Test coordinate validation."""

    def test_validate_valid_osgb36(self, transformer):
        """Test validation of valid OSGB36 coordinates."""
        assert transformer.validate_osgb36(350000, 450000)

    def test_validate_invalid_osgb36_easting(self, transformer):
        """Test rejection of out-of-bounds easting."""
        assert not transformer.validate_osgb36(999999, 450000)

    def test_validate_invalid_osgb36_northing(self, transformer):
        """Test rejection of out-of-bounds northing."""
        assert not transformer.validate_osgb36(350000, 2000000)

    def test_validate_osgb36_boundary_values(self, transformer):
        """Coordinates exactly on configured UK OSGB36 bounds are accepted."""
        assert transformer.validate_osgb36(0, 0)
        assert transformer.validate_osgb36(700000, 1300000)

    def test_validate_valid_wgs84(self, transformer):
        """Test validation of valid WGS84 coordinates."""
        assert transformer.validate_wgs84(54.5, -2.5)

    def test_validate_invalid_wgs84_latitude(self, transformer):
        """Test rejection of out-of-bounds latitude."""
        assert not transformer.validate_wgs84(70.0, -2.5)

    def test_validate_invalid_wgs84_longitude(self, transformer):
        """Test rejection of out-of-bounds longitude."""
        assert not transformer.validate_wgs84(54.5, 10.0)

    def test_validate_wgs84_boundary_values(self, transformer):
        """Coordinates exactly on configured WGS84 bounds are accepted."""
        assert transformer.validate_wgs84(50.0, -8.0)
        assert transformer.validate_wgs84(60.0, 2.5)


class TestCoordinateTransformation:
    """Test coordinate transformation."""

    def test_osgb36_to_wgs84_transformation(self, transformer):
        """Test transformation from OSGB36 to WGS84."""
        # Use known UK coordinates
        lat, lon = transformer.osgb36_to_wgs84(354123.45, 456789.12)

        # Result should be valid WGS84
        assert 50 <= lat <= 60
        assert -8 <= lon <= 3

    def test_wgs84_to_osgb36_transformation(self, transformer):
        """Test transformation from WGS84 to OSGB36."""
        # Use known UK coordinates
        easting, northing = transformer.wgs84_to_osgb36(54.5, -2.5)

        # Result should be valid OSGB36
        assert 0 <= easting <= 700000
        assert 0 <= northing <= 1300000

    def test_invalid_osgb36_transformation(self, transformer):
        """Test that invalid coordinates raise error."""
        with pytest.raises(ValueError):
            transformer.osgb36_to_wgs84(999999, 450000)


class TestDatasetTransformation:
    """Test dataset-level transformations."""

    def test_transform_dataset_adds_wgs84(self, transformer):
        """Test that transformation adds WGS84 coordinates."""
        poles = [
            BaselinePole(
                pole_id="POLE_001",
                support_no="903203",
                easting=354123.45,
                northing=456789.12,
            ),
        ]
        dataset = BaselineDataset(poles=poles)

        assert not dataset.has_wgs84
        dataset = transformer.transform_dataset(dataset)
        assert dataset.has_wgs84
        assert dataset.poles[0].latitude is not None
        assert dataset.poles[0].longitude is not None

    def test_transform_dataset_empty_dataset(self, transformer):
        """Empty datasets should pass through without errors."""
        dataset = BaselineDataset(poles=[])

        transformed = transformer.transform_dataset(dataset)

        assert transformed.poles == []
        assert transformed.has_wgs84 is True
