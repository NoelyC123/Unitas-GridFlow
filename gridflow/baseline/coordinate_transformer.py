"""
Coordinate transformation between OSGB36 and WGS84.

Handles conversion between UK National Grid (OSGB36) and GPS (WGS84)
coordinate systems with validation and error handling.
"""

import logging
from typing import Tuple

try:
    from pyproj import CRS, Transformer
except ImportError:
    Transformer = None
    CRS = None

from gridflow.baseline.models import BaselineDataset, BaselinePole

logger = logging.getLogger(__name__)

# UK coordinate system bounds
OSGB36_BOUNDS = {
    "min_easting": 0,
    "max_easting": 700000,
    "min_northing": 0,
    "max_northing": 1300000,
}

WGS84_BOUNDS = {
    "min_lat": 50.0,
    "max_lat": 60.0,
    "min_lon": -8.0,
    "max_lon": 2.5,
}


class CoordinateTransformer:
    """
    Transform between OSGB36 (British National Grid) and WGS84 (GPS) coordinates.

    OSGB36: UK National Grid coordinates in meters
    WGS84: GPS coordinates in decimal degrees
    """

    def __init__(self):
        """Initialize coordinate transformer with pyproj."""
        if Transformer is None or CRS is None:
            raise ImportError(
                "pyproj required for coordinate transformation. Install with: pip install pyproj"
            )

        # Define coordinate systems
        self.osgb36 = CRS.from_epsg(27700)  # OSGB 1936 / British National Grid
        self.wgs84 = CRS.from_epsg(4326)  # WGS 84

        # Create transformers
        self.osgb_to_wgs84 = Transformer.from_crs(
            self.osgb36,
            self.wgs84,
            always_xy=True,  # Return (lon, lat) instead of (lat, lon)
        )
        self.wgs84_to_osgb = Transformer.from_crs(self.wgs84, self.osgb36, always_xy=True)

        logger.info("CoordinateTransformer initialized")

    def osgb36_to_wgs84(self, easting: float, northing: float) -> Tuple[float, float]:
        """
        Convert OSGB36 (easting, northing) to WGS84 (latitude, longitude).

        Args:
            easting: OSGB36 easting in meters
            northing: OSGB36 northing in meters

        Returns:
            Tuple of (latitude, longitude) in WGS84
        """
        if not self.validate_osgb36(easting, northing):
            raise ValueError(f"Invalid OSGB36 coordinates: ({easting}, {northing})")

        # Transform returns (lon, lat), we return (lat, lon)
        lon, lat = self.osgb_to_wgs84.transform(easting, northing)
        return lat, lon

    def wgs84_to_osgb36(self, latitude: float, longitude: float) -> Tuple[float, float]:
        """
        Convert WGS84 (latitude, longitude) to OSGB36 (easting, northing).

        Args:
            latitude: WGS84 latitude in decimal degrees
            longitude: WGS84 longitude in decimal degrees

        Returns:
            Tuple of (easting, northing) in OSGB36
        """
        if not self.validate_wgs84(latitude, longitude):
            raise ValueError(f"Invalid WGS84 coordinates: ({latitude}, {longitude})")

        # Transform expects (lon, lat), returns (easting, northing)
        easting, northing = self.wgs84_to_osgb.transform(longitude, latitude)
        return easting, northing

    @staticmethod
    def validate_osgb36(easting: float, northing: float) -> bool:
        """
        Check if OSGB36 coordinates are within UK bounds.

        Returns:
            True if coordinates are valid UK grid references
        """
        return (
            OSGB36_BOUNDS["min_easting"] <= easting <= OSGB36_BOUNDS["max_easting"]
            and OSGB36_BOUNDS["min_northing"] <= northing <= OSGB36_BOUNDS["max_northing"]
        )

    @staticmethod
    def validate_wgs84(latitude: float, longitude: float) -> bool:
        """
        Check if WGS84 coordinates are within UK bounds.

        Returns:
            True if coordinates are valid UK location
        """
        return (
            WGS84_BOUNDS["min_lat"] <= latitude <= WGS84_BOUNDS["max_lat"]
            and WGS84_BOUNDS["min_lon"] <= longitude <= WGS84_BOUNDS["max_lon"]
        )

    def transform_dataset(self, dataset: BaselineDataset) -> BaselineDataset:
        """
        Add WGS84 coordinates to all poles in dataset if missing.

        Args:
            dataset: BaselineDataset with OSGB36 coordinates

        Returns:
            BaselineDataset with WGS84 coordinates added
        """
        if dataset.has_wgs84:
            logger.info("Dataset already has WGS84 coordinates")
            return dataset

        transformed_poles = []
        errors = 0

        for pole in dataset.poles:
            try:
                # Skip if already has WGS84
                if pole.latitude and pole.longitude:
                    transformed_poles.append(pole)
                    continue

                # Transform OSGB36 to WGS84
                lat, lon = self.osgb36_to_wgs84(pole.easting, pole.northing)

                # Update pole with new coordinates
                pole.latitude = lat
                pole.longitude = lon
                transformed_poles.append(pole)

            except ValueError as e:
                logger.warning(f"Could not transform {pole.pole_id}: {e}")
                errors += 1
                transformed_poles.append(pole)  # Keep original

        logger.info(
            f"Transformed {len(transformed_poles) - errors} poles to WGS84 ({errors} errors)"
        )

        dataset.poles = transformed_poles
        return dataset

    def transform_pole(self, pole: BaselinePole) -> BaselinePole:
        """
        Add WGS84 coordinates to a single pole if missing.

        Args:
            pole: BaselinePole with OSGB36 coordinates

        Returns:
            BaselinePole with WGS84 coordinates added
        """
        if pole.latitude and pole.longitude:
            return pole

        try:
            lat, lon = self.osgb36_to_wgs84(pole.easting, pole.northing)
            pole.latitude = lat
            pole.longitude = lon
            return pole
        except ValueError as e:
            logger.warning(f"Could not transform {pole.pole_id}: {e}")
            return pole
