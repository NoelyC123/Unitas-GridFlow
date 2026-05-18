"""Load field photos from surveyed pole folders."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".tif", ".tiff"}
PHOTO_TYPES = (
    "full_pole",
    "pole_top",
    "pole_base",
    "equipment",
    "span",
    "context",
    "unknown",
)


@dataclass
class PhotoFile:
    filename: str
    filepath: str
    photo_type: str
    size_bytes: int
    exists: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass
class PhotoSet:
    pole_id: str
    pole_folder_path: str
    photo_files: list[PhotoFile]

    def count_by_type(self) -> dict[str, int]:
        counts = {photo_type: 0 for photo_type in PHOTO_TYPES}
        for photo in self.photo_files:
            counts[photo.photo_type] = counts.get(photo.photo_type, 0) + 1
        return counts

    @property
    def photo_count(self) -> int:
        return len(self.photo_files)

    @property
    def photo_types_present(self) -> list[str]:
        present = [photo_type for photo_type, count in self.count_by_type().items() if count > 0]
        return present

    def to_dict(self) -> dict[str, object]:
        return {
            "pole_id": self.pole_id,
            "pole_folder_path": self.pole_folder_path,
            "photo_files": [photo.to_dict() for photo in self.photo_files],
            "photo_count": self.photo_count,
            "photo_types_present": self.photo_types_present,
        }


def load_pole_photos(pole_folder_path: str | Path) -> PhotoSet:
    """Load one pole folder's `field_photos/` files."""
    pole_folder = Path(pole_folder_path)
    photos_dir = pole_folder / "field_photos"
    files: list[PhotoFile] = []

    if photos_dir.exists():
        image_paths = sorted(
            path
            for path in photos_dir.iterdir()
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        )
        unmatched_full_assigned = False
        for image_path in image_paths:
            photo_type = _detect_photo_type(image_path.name)
            if photo_type == "unknown" and not unmatched_full_assigned:
                photo_type = "full_pole"
                unmatched_full_assigned = True
            files.append(
                PhotoFile(
                    filename=image_path.name,
                    filepath=str(image_path),
                    photo_type=photo_type,
                    size_bytes=image_path.stat().st_size,
                    exists=image_path.exists(),
                )
            )

    return PhotoSet(
        pole_id=pole_folder.name,
        pole_folder_path=str(pole_folder),
        photo_files=files,
    )


def load_survey_photos(survey_root: str | Path) -> dict[str, PhotoSet]:
    """Load photo sets for all pole folders in a survey root."""
    survey_root = Path(survey_root)
    poles_root = (
        survey_root / "enwl_enrichment_clean"
        if (survey_root / "enwl_enrichment_clean").exists()
        else survey_root
    )

    results: dict[str, PhotoSet] = {}
    for pole_dir in sorted(path for path in poles_root.iterdir() if path.is_dir()):
        if not pole_dir.name[0:2].isdigit():
            continue
        results[pole_dir.name] = load_pole_photos(pole_dir)
    return results


def _detect_photo_type(filename: str) -> str:
    lower = filename.lower()
    if any(token in lower for token in ("top", "pole_top", "poletop")):
        return "pole_top"
    if any(token in lower for token in ("base", "pole_base", "foundation")):
        return "pole_base"
    if any(token in lower for token in ("equipment", "transformer", "switch")):
        return "equipment"
    if any(token in lower for token in ("span", "conductor")):
        return "span"
    if any(token in lower for token in ("context", "overview", "access")):
        return "context"
    return "unknown"
