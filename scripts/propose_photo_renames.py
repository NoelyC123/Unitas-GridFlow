#!/usr/bin/env python3
"""Produce a dry-run CSV manifest of proposed photo renames."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gridflow.photos.loader import IMAGE_EXTENSIONS  # noqa: E402

TYPE_PREFIXES = (
    "full_pole",
    "pole_top",
    "pole_base",
    "equipment",
    "span",
    "context",
)

CSV_COLUMNS = [
    "pole_folder",
    "support_no",
    "old_filename",
    "proposed_filename",
    "proposed_type",
    "confidence",
    "reason",
    "action_required",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Produce a dry-run photo rename manifest.")
    parser.add_argument(
        "--survey", required=True, help="Survey root, e.g. real_pilot_data/P_LOCAL_002"
    )
    parser.add_argument("--output", required=True, help="Output CSV manifest path")
    args = parser.parse_args(argv)

    rows = build_manifest(Path(args.survey))

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Manifest complete: {output_path}")
    print(f"Rows: {len(rows)}")
    return 0


def build_manifest(survey_root: Path) -> list[dict[str, str]]:
    poles_root = survey_root / "enwl_enrichment_clean"
    if not poles_root.exists():
        raise FileNotFoundError(f"Survey evidence folder not found: {poles_root}")

    rows: list[dict[str, str]] = []
    for pole_dir in sorted(
        [path for path in poles_root.iterdir() if path.is_dir() and "_SUPPORT_" in path.name],
        key=lambda path: _pole_sort_key(path.name),
    ):
        support_no = _support_no_from_folder(pole_dir.name)
        photos_dir = pole_dir / "field_photos"
        photo_files = (
            sorted(
                [
                    path
                    for path in photos_dir.iterdir()
                    if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
                ]
            )
            if photos_dir.exists()
            else []
        )

        has_any_descriptive = any(_contains_descriptive_keyword(path.name) for path in photo_files)

        for index, photo_path in enumerate(photo_files, start=1):
            old_filename = photo_path.name
            proposed_type, confidence, reason = _proposal_for_filename(
                old_filename,
                index=index,
                has_any_descriptive=has_any_descriptive,
            )
            proposed_filename = (
                old_filename
                if _already_prefixed(old_filename) or reason == "already_descriptive"
                else f"{proposed_type}_{old_filename}"
            )
            rows.append(
                {
                    "pole_folder": pole_dir.name,
                    "support_no": support_no,
                    "old_filename": old_filename,
                    "proposed_filename": proposed_filename,
                    "proposed_type": proposed_type,
                    "confidence": confidence,
                    "reason": reason,
                    "action_required": "YES" if confidence == "LOW" else "NO",
                }
            )
    return rows


def _proposal_for_filename(
    filename: str,
    *,
    index: int,
    has_any_descriptive: bool,
) -> tuple[str, str, str]:
    if _already_prefixed(filename):
        proposed_type = _type_from_prefix(filename) or "unknown"
        return proposed_type, "HIGH", "already_descriptive"

    descriptive_type = _type_from_keyword(filename)
    if descriptive_type:
        return descriptive_type, "HIGH", "already_descriptive"

    if not has_any_descriptive:
        return _positional_type(index), "LOW", "positional_assignment"

    return "unknown", "LOW", "positional_assignment"


def _already_prefixed(filename: str) -> bool:
    lower = filename.lower()
    return any(lower.startswith(f"{prefix}_") for prefix in TYPE_PREFIXES)


def _contains_descriptive_keyword(filename: str) -> bool:
    return _type_from_keyword(filename) is not None or _already_prefixed(filename)


def _type_from_prefix(filename: str) -> str | None:
    lower = filename.lower()
    for prefix in TYPE_PREFIXES:
        if lower.startswith(f"{prefix}_"):
            return prefix
    return None


def _type_from_keyword(filename: str) -> str | None:
    lower = filename.lower()
    if "full" in lower:
        return "full_pole"
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
    return None


def _positional_type(index: int) -> str:
    if index == 1:
        return "full_pole"
    if index == 2:
        return "pole_top"
    if index == 3:
        return "pole_base"
    if index in (4, 5):
        return "equipment"
    if index in (6, 7):
        return "span"
    return "context"


def _support_no_from_folder(folder_name: str) -> str:
    parts = folder_name.split("_")
    if "SUPPORT" in parts:
        idx = parts.index("SUPPORT")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return ""


def _pole_sort_key(pole_id: str) -> tuple[int, str]:
    prefix = pole_id.split("_", 1)[0]
    return (int(prefix) if prefix.isdigit() else 999, pole_id)


if __name__ == "__main__":
    raise SystemExit(main())
