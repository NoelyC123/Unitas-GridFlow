#!/usr/bin/env python3
"""List photo inventory for one pole or an entire survey."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gridflow.photos import load_pole_photos, load_survey_photos  # noqa: E402


def _format_kb(size_bytes: int) -> str:
    return f"{round(size_bytes / 1024)} KB"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="List field photos for one pole or a whole survey."
    )
    parser.add_argument(
        "--survey", required=True, help="Survey root, e.g. real_pilot_data/P_LOCAL_002"
    )
    parser.add_argument("--pole", help="Pole folder name, e.g. 05_SUPPORT_900344")
    parser.add_argument(
        "--all", action="store_true", help="List all pole photo counts in table form"
    )
    args = parser.parse_args(argv)

    if bool(args.pole) == bool(args.all):
        parser.error("Specify exactly one of --pole or --all.")

    if args.pole:
        photo_set = load_pole_photos(_resolve_pole_dir(Path(args.survey), args.pole))
        print(f"Pole: {photo_set.pole_id}")
        print(f"Photos: {photo_set.photo_count}")
        for photo in photo_set.photo_files:
            print(f"- {photo.filename} ({photo.photo_type}, {_format_kb(photo.size_bytes)})")
        return 0

    survey = load_survey_photos(args.survey)
    print("| Pole | Photos | Full | Top | Base | Equipment | Span | Context |")
    print("|------|--------|------|-----|------|-----------|------|---------|")
    for pole_id, photo_set in survey.items():
        counts = photo_set.count_by_type()
        print(
            f"| {pole_id} | {photo_set.photo_count} | {counts['full_pole']} | "
            f"{counts['pole_top']} | {counts['pole_base']} | {counts['equipment']} | "
            f"{counts['span']} | {counts['context']} |"
        )
    return 0


def _resolve_pole_dir(survey_root: Path, pole_folder_name: str) -> Path:
    direct = survey_root / pole_folder_name
    if direct.exists():
        return direct
    clean = survey_root / "enwl_enrichment_clean" / pole_folder_name
    if clean.exists():
        return clean
    raise FileNotFoundError(f"Pole folder {pole_folder_name!r} not found under {survey_root}")


if __name__ == "__main__":
    raise SystemExit(main())
