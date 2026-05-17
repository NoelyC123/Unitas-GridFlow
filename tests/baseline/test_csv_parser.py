"""
Tests for CSV parser module.
"""

from pathlib import Path

import pytest

from gridflow.baseline import BaselineDataset, CSVParser


@pytest.fixture
def fixtures_dir():
    """Return path to test fixtures."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def parser():
    """Return CSV parser instance."""
    return CSVParser()


class TestCSVParserDetection:
    """Test format detection."""

    def test_detect_enwl_format(self, parser, fixtures_dir):
        """Test ENWL format detection."""
        csv_path = fixtures_dir / "enwl_sample.csv"
        assert csv_path.exists()
        fmt = parser.detect_format(csv_path)
        assert fmt == "ENWL"

    def test_detect_trimble_format(self, parser, fixtures_dir):
        """Test Trimble format detection."""
        csv_path = fixtures_dir / "trimble_sample.csv"
        assert csv_path.exists()
        fmt = parser.detect_format(csv_path)
        assert fmt == "TRIMBLE"


class TestCSVParserENWL:
    """Test ENWL format parsing."""

    def test_parse_enwl_format(self, parser, fixtures_dir):
        """Test parsing valid ENWL CSV."""
        csv_path = fixtures_dir / "enwl_sample.csv"
        dataset = parser.parse(csv_path, format_hint="ENWL")

        assert isinstance(dataset, BaselineDataset)
        assert dataset.pole_count == 10
        assert dataset.metadata["format"] == "ENWL"

    def test_enwl_pole_fields(self, parser, fixtures_dir):
        """Test that ENWL parser extracts all fields."""
        csv_path = fixtures_dir / "enwl_sample.csv"
        dataset = parser.parse(csv_path, format_hint="ENWL")
        pole = dataset.poles[0]

        assert pole.pole_id == "16938106"
        assert pole.support_no == "903203"
        assert pole.easting == 354123.45
        assert pole.northing == 456789.12
        assert pole.latitude == 54.123456
        assert pole.longitude == -2.987654


class TestCSVParserTrimble:
    """Test Trimble format parsing."""

    def test_parse_trimble_format(self, parser, fixtures_dir):
        """Test parsing valid Trimble CSV."""
        csv_path = fixtures_dir / "trimble_sample.csv"
        dataset = parser.parse(csv_path, format_hint="TRIMBLE")

        assert isinstance(dataset, BaselineDataset)
        assert dataset.pole_count == 10
        assert dataset.metadata["format"] == "TRIMBLE"

    def test_trimble_pole_fields(self, parser, fixtures_dir):
        """Test that Trimble parser extracts all fields."""
        csv_path = fixtures_dir / "trimble_sample.csv"
        dataset = parser.parse(csv_path, format_hint="TRIMBLE")
        pole = dataset.poles[0]

        assert pole.pole_id == "T001"
        assert pole.easting == 354123.45
        assert pole.northing == 456789.12


class TestCSVParserEdgeCases:
    """Test edge cases and error handling."""

    def test_parse_nonexistent_file(self, parser):
        """Test parsing nonexistent file."""
        with pytest.raises(FileNotFoundError):
            parser.parse(Path("/nonexistent/file.csv"))

    def test_parse_empty_csv(self, parser, tmp_path):
        """Test parsing empty CSV."""
        csv_path = tmp_path / "empty.csv"
        csv_path.write_text("")

        dataset = parser.parse(csv_path)
        assert dataset.pole_count == 0

    def test_parse_missing_coords(self, parser, tmp_path):
        """Test parsing CSV with missing coordinates."""
        csv_path = tmp_path / "no_coords.csv"
        csv_path.write_text("ENID,Support No\n16938106,903203\n")

        dataset = parser.parse(csv_path)
        assert dataset.pole_count == 1
        assert dataset.poles[0].pole_id == "16938106"
        assert dataset.poles[0].support_no == "903203"
        assert dataset.poles[0].easting is None
        assert dataset.poles[0].northing is None
        assert dataset.poles[0].metadata["coordinate_status"] == "MISSING"

    def test_parse_generic_uses_pole_id_as_support_fallback(self, parser, tmp_path):
        """Generic CSVs without support/name columns should use pole_id as support_no."""
        csv_path = tmp_path / "generic.csv"
        csv_path.write_text("pole_id,easting,northing,voltage\n903101,352000.0,478000.0,LV\n")

        dataset = parser.parse(csv_path, format_hint="GENERIC")

        assert dataset.pole_count == 1
        assert dataset.poles[0].pole_id == "903101"
        assert dataset.poles[0].support_no == "903101"

    def test_parse_csv_with_no_required_columns_returns_empty_dataset(self, parser, tmp_path):
        """A baseline CSV with no coordinate columns should still preserve identity rows."""
        csv_path = tmp_path / "missing_required_columns.csv"
        csv_path.write_text("Name,Description\nAlpha,No coordinate fields\n")

        dataset = parser.parse(csv_path)

        assert dataset.pole_count == 1
        assert dataset.metadata["total_rows"] == 1
        assert dataset.metadata["parsed_poles"] == 1
        assert dataset.poles[0].support_no == "Alpha"
        assert dataset.poles[0].easting is None
        assert dataset.poles[0].northing is None

    def test_parse_latin1_encoded_csv(self, parser, tmp_path):
        """CSV parser should fall back to non-UTF encodings when needed."""
        csv_path = tmp_path / "latin1.csv"
        csv_path.write_bytes(
            "ENID,Support No,Easting,Northing,Feature\n"
            "P1,903203,354123.45,456789.12,Pol\xe9\n".encode("latin-1")
        )

        dataset = parser.parse(csv_path, format_hint="ENWL")

        assert dataset.pole_count == 1
        assert dataset.poles[0].feature_code == "Polé"
