"""
CSV parser for baseline data.

Handles parsing of different DNO and Trimble CSV formats with automatic
format detection, encoding handling, and data normalization.
"""

import logging
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from gridflow.baseline.models import (
    AssetStatus,
    AssetType,
    BaselineDataset,
    BaselinePole,
    VoltageLevel,
)

logger = logging.getLogger(__name__)


class CSVParser:
    """
    Parse baseline CSV exports from various DNO and survey systems.

    Supports:
    - ENWL Network Asset Viewer format
    - Trimble survey exports
    - Generic/unknown formats with column mapping
    """

    # Known column name mappings for different DNO formats
    ENWL_COLUMN_MAP = {
        "ENID": "pole_id",
        "Support No": "support_no",
        "Easting": "easting",
        "Northing": "northing",
        "Latitude": "latitude",
        "Longitude": "longitude",
        "Feature": "feature_code",
        "Voltage": "voltage_level",
        "Structure Type": "asset_type",
        "Status": "status",
    }

    TRIMBLE_COLUMN_MAP = {
        "Feature Code": "feature_code",
        "Point Name": "support_no",
        "Point ID": "pole_id",
        "Easting": "easting",
        "Northing": "northing",
        "Northing": "northing",
    }

    # Common encoding attempts in order
    ENCODINGS = ["utf-8", "latin-1", "cp1252", "iso-8859-1"]

    def detect_format(self, csv_path: Path) -> str:
        """
        Detect the format of a CSV file.

        Returns one of: ENWL, TRIMBLE, GENERIC
        """
        try:
            df = self._read_csv_safe(csv_path, nrows=5)
            if df is None or df.empty:
                logger.warning(f"Could not read {csv_path} for format detection")
                return "GENERIC"

            columns = set(df.columns)

            # Check for ENWL indicators
            if "ENID" in columns and "Support No" in columns:
                logger.info("Detected ENWL format")
                return "ENWL"

            # Check for Trimble indicators
            if "Feature Code" in columns and "Point ID" in columns:
                logger.info("Detected Trimble format")
                return "TRIMBLE"

            logger.info("Using generic format parser")
            return "GENERIC"

        except Exception as e:
            logger.warning(f"Format detection failed: {e}. Using GENERIC.")
            return "GENERIC"

    def parse(
        self,
        csv_path: Path,
        format_hint: Optional[str] = None,
    ) -> BaselineDataset:
        """
        Parse a baseline CSV file.

        Args:
            csv_path: Path to CSV file
            format_hint: Optional format hint (ENWL/TRIMBLE/GENERIC)

        Returns:
            BaselineDataset containing parsed poles
        """
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        logger.info(f"Parsing baseline CSV: {csv_path}")

        # Detect format if not provided
        detected_format = format_hint or self.detect_format(csv_path)

        # Read CSV
        df = self._read_csv_safe(csv_path)
        if df is None or df.empty:
            logger.warning(f"CSV is empty or unreadable: {csv_path}")
            return BaselineDataset(
                poles=[],
                metadata={"source_file": str(csv_path), "format": detected_format},
            )

        # Remove completely empty rows
        df = df.dropna(how="all")
        logger.info(f"Loaded {len(df)} rows from CSV")

        # Parse based on format
        if detected_format == "ENWL":
            return self._parse_enwl(df, csv_path)
        elif detected_format == "TRIMBLE":
            return self._parse_trimble(df, csv_path)
        else:
            return self._parse_generic(df, csv_path, detected_format)

    def _parse_enwl(self, df: pd.DataFrame, csv_path: Path) -> BaselineDataset:
        """Parse ENWL Network Asset Viewer format."""
        logger.info("Parsing ENWL format")
        poles = []
        errors = []

        for idx, row in df.iterrows():
            try:
                # Extract required fields
                pole_id = str(row.get("ENID", "")).strip()
                easting = self._parse_float(row.get("Easting"))
                northing = self._parse_float(row.get("Northing"))

                if not pole_id or easting is None or northing is None:
                    continue  # Skip incomplete rows

                # Extract optional fields
                support_no = str(row.get("Support No", "")).strip() or None
                latitude = self._parse_float(row.get("Latitude"))
                longitude = self._parse_float(row.get("Longitude"))
                feature_code = str(row.get("Feature", "")).strip() or None
                voltage_str = str(row.get("Voltage", "")).strip().upper()
                asset_type_str = str(row.get("Structure Type", "")).strip().upper()
                status_str = str(row.get("Status", "")).strip().upper()

                # Map voltage level
                voltage_level = self._map_voltage(voltage_str)
                asset_type = self._map_asset_type(asset_type_str)
                status = self._map_status(status_str)

                # Collect metadata
                metadata = {k: v for k, v in row.to_dict().items() if k not in self.ENWL_COLUMN_MAP}

                pole = BaselinePole(
                    pole_id=pole_id,
                    support_no=support_no,
                    easting=easting,
                    northing=northing,
                    latitude=latitude,
                    longitude=longitude,
                    feature_code=feature_code,
                    voltage_level=voltage_level,
                    asset_type=asset_type,
                    status=status,
                    metadata=metadata,
                )
                poles.append(pole)

            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)

        logger.info(f"Parsed {len(poles)} poles from ENWL format ({len(errors)} errors)")

        return BaselineDataset(
            poles=poles,
            metadata={
                "source_file": str(csv_path),
                "format": "ENWL",
                "total_rows": len(df),
                "parsed_poles": len(poles),
                "parse_errors": len(errors),
            },
        )

    def _parse_trimble(self, df: pd.DataFrame, csv_path: Path) -> BaselineDataset:
        """Parse Trimble survey export format."""
        logger.info("Parsing Trimble format")
        poles = []
        errors = []

        for idx, row in df.iterrows():
            try:
                # Extract required fields
                pole_id = str(row.get("Point ID", f"TRIMBLE_{idx}")).strip()
                easting = self._parse_float(row.get("Easting"))
                northing = self._parse_float(row.get("Northing"))

                if easting is None or northing is None:
                    continue

                # Extract optional fields
                support_no = str(row.get("Point Name", "")).strip() or None
                feature_code = str(row.get("Feature Code", "")).strip() or None

                metadata = {
                    k: v for k, v in row.to_dict().items() if k not in self.TRIMBLE_COLUMN_MAP
                }

                pole = BaselinePole(
                    pole_id=pole_id,
                    support_no=support_no,
                    easting=easting,
                    northing=northing,
                    feature_code=feature_code,
                    metadata=metadata,
                )
                poles.append(pole)

            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)

        logger.info(f"Parsed {len(poles)} poles from Trimble format ({len(errors)} errors)")

        return BaselineDataset(
            poles=poles,
            metadata={
                "source_file": str(csv_path),
                "format": "TRIMBLE",
                "total_rows": len(df),
                "parsed_poles": len(poles),
                "parse_errors": len(errors),
            },
        )

    def _parse_generic(
        self,
        df: pd.DataFrame,
        csv_path: Path,
        format_name: str,
    ) -> BaselineDataset:
        """Parse generic/unknown CSV format with best-effort mapping."""
        logger.info(f"Parsing generic format: {format_name}")
        poles = []
        errors = []

        # Find coordinate columns
        coord_cols = [c for c in df.columns if "east" in c.lower() or "north" in c.lower()]
        support_cols = [c for c in df.columns if "support" in c.lower() or "name" in c.lower()]
        id_cols = [c for c in df.columns if "id" in c.lower() or "enid" in c.lower()]

        easting_col = next((c for c in coord_cols if "east" in c.lower()), None)
        northing_col = next((c for c in coord_cols if "north" in c.lower()), None)
        support_col = next((c for c in support_cols), None)
        id_col = next((c for c in id_cols), None) or df.columns[0]

        logger.info(
            f"Generic format mapping: id={id_col}, easting={easting_col}, northing={northing_col}, support={support_col}"
        )

        for idx, row in df.iterrows():
            try:
                pole_id = str(row.get(id_col, f"UNKNOWN_{idx}")).strip()
                easting = self._parse_float(row.get(easting_col)) if easting_col else None
                northing = self._parse_float(row.get(northing_col)) if northing_col else None

                if easting is None or northing is None:
                    continue

                support_no = str(row.get(support_col, "")).strip() or None if support_col else None

                metadata = {k: v for k, v in row.to_dict().items()}

                pole = BaselinePole(
                    pole_id=pole_id,
                    support_no=support_no,
                    easting=easting,
                    northing=northing,
                    metadata=metadata,
                )
                poles.append(pole)

            except Exception as e:
                error_msg = f"Row {idx}: {str(e)}"
                logger.warning(error_msg)
                errors.append(error_msg)

        logger.info(f"Parsed {len(poles)} poles from generic format ({len(errors)} errors)")

        return BaselineDataset(
            poles=poles,
            metadata={
                "source_file": str(csv_path),
                "format": format_name,
                "total_rows": len(df),
                "parsed_poles": len(poles),
                "parse_errors": len(errors),
            },
        )

    def _read_csv_safe(
        self,
        csv_path: Path,
        nrows: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        """
        Read CSV with encoding fallback.

        Tries multiple encodings to handle various file formats.
        """
        for encoding in self.ENCODINGS:
            try:
                df = pd.read_csv(
                    csv_path,
                    encoding=encoding,
                    nrows=nrows,
                    on_bad_lines="skip",
                )
                logger.debug(f"Successfully read CSV with {encoding} encoding")
                return df
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
            except Exception as e:
                logger.error(f"Unexpected error reading CSV: {e}")
                return None

        logger.error(f"Could not read CSV with any encoding: {csv_path}")
        return None

    @staticmethod
    def _parse_float(value: Any) -> Optional[float]:
        """Parse a value as float, returning None if invalid."""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _map_voltage(voltage_str: str) -> VoltageLevel:
        """Map voltage string to VoltageLevel enum."""
        if not voltage_str:
            return VoltageLevel.UNKNOWN
        voltage_str = voltage_str.upper()
        if "LV" in voltage_str or voltage_str == "400":
            return VoltageLevel.LV
        if "HV" in voltage_str or voltage_str in ["11", "33"]:
            return VoltageLevel.HV
        if "EHV" in voltage_str or voltage_str in ["110", "275", "400"]:
            return VoltageLevel.EHV
        return VoltageLevel.UNKNOWN

    @staticmethod
    def _map_asset_type(asset_str: str) -> AssetType:
        """Map asset type string to AssetType enum."""
        if not asset_str:
            return AssetType.UNKNOWN
        asset_str = asset_str.upper()
        if "POLE" in asset_str:
            return AssetType.POLE
        if "TOWER" in asset_str:
            return AssetType.TOWER
        if "COLUMN" in asset_str:
            return AssetType.COLUMN
        return AssetType.UNKNOWN

    @staticmethod
    def _map_status(status_str: str) -> AssetStatus:
        """Map status string to AssetStatus enum."""
        if not status_str:
            return AssetStatus.UNKNOWN
        status_str = status_str.upper()
        if "IN_SERVICE" in status_str or status_str == "ACTIVE":
            return AssetStatus.IN_SERVICE
        if "DECOMMISS" in status_str or status_str == "RETIRED":
            return AssetStatus.DECOMMISSIONED
        if "PLANNED" in status_str:
            return AssetStatus.PLANNED
        return AssetStatus.UNKNOWN
