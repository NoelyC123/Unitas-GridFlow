"""
Folder scanner for field evidence datasets.

Scans a root directory for pole evidence folders following
the NN_SUPPORT_* naming convention.
"""

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from gridflow.field.models import FieldDataset, FieldPole
from gridflow.field.notes_parser import NotesParser

logger = logging.getLogger(__name__)

# Folder name pattern: NN_SUPPORT_XXXXXX_*
FOLDER_PATTERN = re.compile(r"^(\d{2})_SUPPORT_([^_]+(?:_[A-Za-z])?(?=_|$)[^_]*)(?:_(.+))?$")

PHOTO_EXTENSIONS = {".jpeg", ".jpg", ".heic", ".JPEG", ".JPG", ".HEIC"}
SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"}
NOTES_EXTENSIONS = {".txt", ".TXT", ".md", ".MD"}


class FolderScanner:
    """Scan field evidence root folder and extract FieldDataset."""

    def __init__(self):
        self._notes_parser = NotesParser()

    def scan(self, dataset_path: "str | Path") -> FieldDataset:
        """
        Scan dataset root folder and return FieldDataset.

        Args:
            dataset_path: Path to root folder containing pole subdirectories

        Returns:
            FieldDataset with all detected poles
        """
        dataset_path = Path(dataset_path)
        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset path not found: {dataset_path}")

        logger.info("Scanning field dataset: %s", dataset_path)

        poles = []
        subdirs = sorted([d for d in dataset_path.iterdir() if d.is_dir()])

        for pole_folder in subdirs:
            folder_name = pole_folder.name

            # Skip hidden folders and duplicates
            if folder_name.startswith(".") or folder_name.startswith("_DUPLICATE_"):
                logger.debug("Skipping folder: %s", folder_name)
                continue

            # Skip if not matching expected pattern
            if not self._is_pole_folder(folder_name):
                logger.warning("Skipping non-matching folder: %s", folder_name)
                continue

            pole = self._scan_pole_folder(pole_folder)
            poles.append(pole)
            logger.debug("Scanned pole: %s → %s", folder_name, pole.support_no)

        dataset = FieldDataset(
            dataset_path=str(dataset_path),
            scan_date=datetime.now().isoformat(),
            total_poles=len(poles),
            poles=poles,
            evidence_summary=self._build_summary(poles),
        )

        logger.info("Scan complete: %d poles found", len(poles))
        return dataset

    def _scan_pole_folder(self, pole_folder: Path) -> FieldPole:
        """Extract all metadata from a single pole folder."""
        folder_name = pole_folder.name

        support_no = self._extract_support_no(folder_name)
        sequence_no = self._extract_sequence_no(folder_name)
        voltage_category = self._extract_voltage_category(folder_name)
        pole_descriptor = self._extract_pole_descriptor(folder_name)
        special_flags = self._detect_special_flags(folder_name)

        photo_count = self._count_photos(pole_folder)
        screenshot_count = self._count_screenshots(pole_folder)
        has_notes = self._has_notes(pole_folder)
        photo_paths = self._get_photo_paths(pole_folder)
        screenshot_paths = self._get_screenshot_paths(pole_folder)
        notes_path = self._get_notes_path(pole_folder)
        notes_content = self._read_notes_content(pole_folder)
        map_popup = self._determine_map_popup_present(folder_name, screenshot_count)

        parsed_notes: dict = {}
        if notes_content:
            try:
                parsed_notes = self._notes_parser.parse(notes_content)
            except Exception as e:
                logger.warning("Notes parse error for %s: %s", folder_name, e)

        return FieldPole(
            folder_name=folder_name,
            support_no=support_no,
            sequence_no=sequence_no,
            voltage_category=voltage_category,
            pole_descriptor=pole_descriptor,
            field_photo_count=photo_count,
            map_screenshot_count=screenshot_count,
            notes_present=has_notes,
            notes_content=notes_content,
            parsed_notes=parsed_notes,
            map_popup_present=map_popup,
            special_flags=special_flags,
            photo_paths=photo_paths,
            screenshot_paths=screenshot_paths,
            notes_path=notes_path,
        )

    @staticmethod
    def _is_pole_folder(folder_name: str) -> bool:
        """Return True if folder name starts with NN_SUPPORT_*."""
        parts = folder_name.split("_")
        return (
            len(parts) >= 3
            and parts[0].isdigit()
            and len(parts[0]) == 2
            and parts[1].upper() == "SUPPORT"
        )

    @staticmethod
    def _extract_support_no(folder_name: str) -> str:
        """
        Extract support number from folder name.

        Pattern: NN_SUPPORT_{support_no}_*
        Handles: 903203, 903201A, 900346 etc.
        """
        parts = folder_name.split("_")
        if len(parts) < 3:
            return "UNKNOWN"

        # parts[2] is the support number, possibly with letter suffix
        candidate = parts[2]

        # Validate: must contain digits
        if not any(c.isdigit() for c in candidate):
            return "UNKNOWN"

        return candidate.upper()

    @staticmethod
    def _extract_sequence_no(folder_name: str) -> Optional[int]:
        """Extract leading NN sequence number."""
        parts = folder_name.split("_")
        if parts and parts[0].isdigit():
            try:
                return int(parts[0])
            except ValueError:
                pass
        return None

    @staticmethod
    def _extract_voltage_category(folder_name: str) -> str:
        """Detect LV/HV/EHV from folder name."""
        name_upper = folder_name.upper()
        parts = name_upper.split("_")

        # Look for exact voltage tokens in the parts
        for part in parts:
            if part == "EHV":
                return "EHV"
            if part == "HV":
                return "HV"
            if part == "LV":
                return "LV"

        return "UNKNOWN"

    @staticmethod
    def _extract_pole_descriptor(folder_name: str) -> Optional[str]:
        """
        Extract descriptor portion after voltage indicator.

        e.g. 01_SUPPORT_903203_LV_TERMINAL_STREETLIGHT → TERMINAL_STREETLIGHT
        """
        parts = folder_name.split("_")
        if len(parts) < 4:
            return None

        # Find the voltage indicator position
        for i, part in enumerate(parts):
            if part.upper() in ("LV", "HV", "EHV"):
                remaining = parts[i + 1 :]
                if remaining:
                    return "_".join(remaining)
                return None

        # No voltage found — return everything after support_no
        if len(parts) > 3:
            return "_".join(parts[3:])
        return None

    @staticmethod
    def _detect_special_flags(folder_name: str) -> list[str]:
        """Detect special pole flags from folder name."""
        flags = []
        upper = folder_name.upper()

        if "NO_POLE_POPUP" in upper:
            flags.append("NO_POLE_POPUP")

        if "JOINT_USER" in upper:
            flags.append("JOINT_USER")

        if "TRANSITION" in upper:
            flags.append("OH_UG_TRANSITION")

        if "HV_LINK" in upper:
            flags.append("HV_LINK")

        # Detect variant support number (e.g. 903201A)
        parts = folder_name.split("_")
        if len(parts) >= 3:
            support_candidate = parts[2]
            if (
                support_candidate
                and any(c.isdigit() for c in support_candidate)
                and any(c.isalpha() for c in support_candidate)
            ):
                flags.append("VARIANT_SUPPORT_NO")

            # Detect if support_no could not be extracted at all
            if not any(c.isdigit() for c in support_candidate):
                flags.append("UNKNOWN_SUPPORT")

        return flags

    @staticmethod
    def _count_photos(pole_folder: Path) -> int:
        """Count files in field_photos/ subdirectory."""
        photos_dir = pole_folder / "field_photos"
        if not photos_dir.exists():
            return 0
        return sum(1 for f in photos_dir.iterdir() if f.is_file() and f.suffix in PHOTO_EXTENSIONS)

    @staticmethod
    def _count_screenshots(pole_folder: Path) -> int:
        """Count files in map_screenshots/ subdirectory."""
        screenshots_dir = pole_folder / "map_screenshots"
        if not screenshots_dir.exists():
            return 0
        return sum(
            1
            for f in screenshots_dir.iterdir()
            if f.is_file() and f.suffix in SCREENSHOT_EXTENSIONS
        )

    @staticmethod
    def _has_notes(pole_folder: Path) -> bool:
        """Check if any .txt file exists in notes/ subdirectory."""
        notes_dir = pole_folder / "notes"
        if not notes_dir.exists():
            return False
        return any(f.is_file() and f.suffix in NOTES_EXTENSIONS for f in notes_dir.iterdir())

    @staticmethod
    def _get_photo_paths(pole_folder: Path) -> list[str]:
        """Return relative paths to all field photos."""
        photos_dir = pole_folder / "field_photos"
        if not photos_dir.exists():
            return []
        return sorted(
            [
                str(f.relative_to(pole_folder.parent))
                for f in photos_dir.iterdir()
                if f.is_file() and f.suffix in PHOTO_EXTENSIONS
            ]
        )

    @staticmethod
    def _get_screenshot_paths(pole_folder: Path) -> list[str]:
        """Return relative paths to all map screenshots."""
        screenshots_dir = pole_folder / "map_screenshots"
        if not screenshots_dir.exists():
            return []
        return sorted(
            [
                str(f.relative_to(pole_folder.parent))
                for f in screenshots_dir.iterdir()
                if f.is_file() and f.suffix in SCREENSHOT_EXTENSIONS
            ]
        )

    @staticmethod
    def _get_notes_path(pole_folder: Path) -> Optional[str]:
        """Return relative path to first .txt file in notes/, or None."""
        notes_dir = pole_folder / "notes"
        if not notes_dir.exists():
            return None
        for f in sorted(notes_dir.iterdir()):
            if f.is_file() and f.suffix in NOTES_EXTENSIONS:
                return str(f.relative_to(pole_folder.parent))
        return None

    @staticmethod
    def _read_notes_content(pole_folder: Path) -> Optional[str]:
        """Read and return notes file content with encoding fallback."""
        notes_dir = pole_folder / "notes"
        if not notes_dir.exists():
            return None

        for f in sorted(notes_dir.iterdir()):
            if f.is_file() and f.suffix in NOTES_EXTENSIONS:
                for encoding in ("utf-8", "latin-1"):
                    try:
                        return f.read_text(encoding=encoding)
                    except (UnicodeDecodeError, OSError):
                        continue
        return None

    @staticmethod
    def _determine_map_popup_present(folder_name: str, screenshot_count: int) -> str:
        """Determine map popup availability."""
        if "NO_POLE_POPUP" in folder_name.upper():
            return "uncertain"
        if screenshot_count >= 1:
            return "yes"
        return "uncertain"

    @staticmethod
    def _build_summary(poles: list[FieldPole]) -> dict:
        """Build evidence summary statistics."""
        if not poles:
            return {"total": 0, "high": 0, "medium": 0, "low": 0}

        high = sum(1 for p in poles if p.evidence_quality == "HIGH")
        medium = sum(1 for p in poles if p.evidence_quality == "MEDIUM")
        low = sum(1 for p in poles if p.evidence_quality == "LOW")

        return {
            "total": len(poles),
            "high": high,
            "medium": medium,
            "low": low,
            "notes_present": sum(1 for p in poles if p.notes_present),
            "with_screenshots": sum(1 for p in poles if p.map_screenshot_count > 0),
        }
