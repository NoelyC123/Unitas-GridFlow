"""Tests for FolderScanner."""

from pathlib import Path

import pytest

from gridflow.field import FolderScanner

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def scanner():
    return FolderScanner()


class TestScanDatasets:
    def test_scan_valid_dataset(self, scanner):
        result = scanner.scan(FIXTURES / "valid_dataset")
        assert result.total_poles == 2
        assert len(result.poles) == 2

    def test_scan_edge_cases(self, scanner):
        result = scanner.scan(FIXTURES / "edge_cases")
        assert result.total_poles == 3

    def test_scan_empty_dataset(self, scanner):
        result = scanner.scan(FIXTURES / "empty_dataset")
        assert result.total_poles == 0

    def test_scan_nonexistent_raises(self, scanner):
        with pytest.raises(FileNotFoundError):
            scanner.scan("/nonexistent/path")

    def test_scan_flags_edge_cases(self, scanner):
        result = scanner.scan(FIXTURES / "edge_cases")
        folders = {p.folder_name: p for p in result.poles}

        no_popup = folders.get("08_SUPPORT_900346_HV_LINK_NO_POLE_POPUP")
        assert no_popup is not None
        assert "NO_POLE_POPUP" in no_popup.special_flags
        assert "HV_LINK" in no_popup.special_flags

        joint_user = folders.get("07_SUPPORT_903503_JOINT_USER")
        assert joint_user is not None
        assert "JOINT_USER" in joint_user.special_flags

        variant = folders.get("03_SUPPORT_903201A_LV_SECTION")
        assert variant is not None
        assert "VARIANT_SUPPORT_NO" in variant.special_flags

    def test_scan_malformed_partial_support_folder(self, scanner, tmp_path):
        """Folders that partially match NN_SUPPORT_* but lack digits are scanned as UNKNOWN."""
        pole_dir = tmp_path / "01_SUPPORT_ALPHA_LV"
        (pole_dir / "field_photos").mkdir(parents=True)
        (pole_dir / "map_screenshots").mkdir()
        (pole_dir / "notes").mkdir()
        (pole_dir / "field_photos" / "photo_001.jpeg").touch()
        (pole_dir / "field_photos" / "photo_002.jpeg").touch()
        (pole_dir / "field_photos" / "photo_003.jpeg").touch()
        (pole_dir / "map_screenshots" / "map_popup.png").touch()
        (pole_dir / "notes" / "identity_notes.txt").write_text("Support No: ALPHA")

        result = scanner.scan(tmp_path)

        assert result.total_poles == 1
        assert result.poles[0].support_no == "UNKNOWN"
        assert "UNKNOWN_SUPPORT" in result.poles[0].special_flags

    def test_scan_reads_latin1_notes_content(self, scanner, tmp_path):
        """Notes reader should fall back when a notes file is not UTF-8."""
        pole_dir = tmp_path / "01_SUPPORT_903203_LV"
        (pole_dir / "field_photos").mkdir(parents=True)
        (pole_dir / "map_screenshots").mkdir()
        (pole_dir / "notes").mkdir()
        (pole_dir / "field_photos" / "photo_001.jpeg").touch()
        (pole_dir / "field_photos" / "photo_002.jpeg").touch()
        (pole_dir / "field_photos" / "photo_003.jpeg").touch()
        (pole_dir / "map_screenshots" / "map_popup.png").touch()
        (pole_dir / "notes" / "identity_notes.txt").write_bytes(
            "Support No: 903203\nCondition: Café pole note".encode("latin-1")
        )

        result = scanner.scan(tmp_path)

        assert result.total_poles == 1
        assert "Café pole note" in result.poles[0].notes_content


class TestExtractSupportNo:
    def test_extract_pure_numeric(self, scanner):
        assert scanner._extract_support_no("01_SUPPORT_903203_LV") == "903203"

    def test_extract_variant_suffix(self, scanner):
        assert scanner._extract_support_no("03_SUPPORT_903201A_LV_SECTION") == "903201A"

    def test_extract_hv_link(self, scanner):
        assert scanner._extract_support_no("08_SUPPORT_900346_HV_LINK") == "900346"

    def test_extract_unknown(self, scanner):
        assert scanner._extract_support_no("01_SUPPORT_NODIGITS_LV") == "UNKNOWN"

    def test_extract_purely_alphabetic_support_as_unknown(self, scanner):
        assert scanner._extract_support_no("01_SUPPORT_ALPHA_LV_SECTION") == "UNKNOWN"


class TestExtractSequenceNo:
    def test_extract_sequence(self, scanner):
        assert scanner._extract_sequence_no("01_SUPPORT_903203_LV") == 1

    def test_extract_sequence_10(self, scanner):
        assert scanner._extract_sequence_no("10_SUPPORT_902206_HV") == 10


class TestExtractVoltage:
    def test_extract_lv(self, scanner):
        assert scanner._extract_voltage_category("01_SUPPORT_903203_LV_TERMINAL") == "LV"

    def test_extract_hv(self, scanner):
        assert scanner._extract_voltage_category("05_SUPPORT_902204_HV_TRANSFORMER") == "HV"

    def test_extract_unknown(self, scanner):
        assert scanner._extract_voltage_category("01_SUPPORT_903203_SECTION") == "UNKNOWN"


class TestSpecialFlags:
    def test_detect_no_popup(self, scanner):
        flags = scanner._detect_special_flags("08_SUPPORT_900346_HV_LINK_NO_POLE_POPUP")
        assert "NO_POLE_POPUP" in flags

    def test_detect_joint_user(self, scanner):
        flags = scanner._detect_special_flags("07_SUPPORT_903503_JOINT_USER")
        assert "JOINT_USER" in flags

    def test_detect_variant_support(self, scanner):
        flags = scanner._detect_special_flags("03_SUPPORT_903201A_LV_SECTION")
        assert "VARIANT_SUPPORT_NO" in flags

    def test_detect_hv_link(self, scanner):
        flags = scanner._detect_special_flags("08_SUPPORT_900346_HV_LINK")
        assert "HV_LINK" in flags

    def test_detect_transition(self, scanner):
        flags = scanner._detect_special_flags(
            "06_SUPPORT_903101_LV_OVERHEAD_UNDERGROUND_TRANSITION"
        )
        assert "OH_UG_TRANSITION" in flags


class TestFileCounters:
    def test_count_photos(self, scanner):
        folder = FIXTURES / "valid_dataset" / "01_SUPPORT_903203_LV_TERMINAL"
        assert scanner._count_photos(folder) == 3

    def test_count_screenshots(self, scanner):
        folder = FIXTURES / "valid_dataset" / "01_SUPPORT_903203_LV_TERMINAL"
        assert scanner._count_screenshots(folder) == 1

    def test_has_notes(self, scanner):
        folder = FIXTURES / "valid_dataset" / "01_SUPPORT_903203_LV_TERMINAL"
        assert scanner._has_notes(folder) is True

    def test_no_photos_missing_dir(self, scanner, tmp_path):
        empty = tmp_path / "pole"
        empty.mkdir()
        assert scanner._count_photos(empty) == 0
