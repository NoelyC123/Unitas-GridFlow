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
        # Should skip rows with missing coordinates
        assert dataset.pole_count == 0
