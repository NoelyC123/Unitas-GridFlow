#!/usr/bin/env python3
# ruff: noqa: E402
"""Inspect ENWL trace GeoJSON evidence with conservative relationship labels.

This script is intentionally conservative. It displays ENWL trace evidence as
provenance and relationship context only. It does not infer design readiness,
does not clear conductor_spec_missing, and does not assign conductor records to
specific poles/spans.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from gridflow.enwl_trace import (
    DIRECT_EQUIPMENT_LINKED_TO_POLE,
    DIRECT_POLE_IDENTITY,
    NEARBY_CONTEXT_ONLY,
    ROUTE_SPAN_EVIDENCE,
    UNCERTAIN,
    ENWLEvidenceFeature,
    parse_geojson_file,
)

ROUTE_SPAN_CAUTION = "ROUTE/SPAN EVIDENCE ONLY — not per-pole design-ready proof"

RELATIONSHIP_ORDER = (
    DIRECT_POLE_IDENTITY,
    DIRECT_EQUIPMENT_LINKED_TO_POLE,
    ROUTE_SPAN_EVIDENCE,
    NEARBY_CONTEXT_ONLY,
    UNCERTAIN,
)


def main(argv: list[str] | None = None) -> int:
    """Run the ENWL trace inspector CLI."""
    parser = argparse.ArgumentParser(
        description=(
            "Inspect ENWL trace GeoJSON evidence and print conservative "
            "provenance relationship summaries."
        )
    )
    parser.add_argument(
        "geojson_paths",
        nargs="+",
        help="One or more ENWL trace GeoJSON FeatureCollection files.",
    )
    args = parser.parse_args(argv)

    exit_code = 0
    for raw_path in args.geojson_paths:
        try:
            inspect_path(Path(raw_path))
        except Exception as exc:  # pragma: no cover - exact exception varies by input
            exit_code = 1
            print(f"ERROR inspecting {raw_path}: {exc}", file=sys.stderr)

    return exit_code


def inspect_path(path: Path) -> None:
    """Parse and print a conservative evidence summary for one GeoJSON file."""
    dataset = parse_geojson_file(path)
    relationship_counts = Counter(feature.relationship for feature in dataset.features)

    print("=" * 80)
    print("ENWL Trace Evidence Summary")
    print("=" * 80)
    print(f"Source path: {dataset.source_path or path}")
    print(f"Feature count: {dataset.feature_count}")
    print()
    print("Relationship category counts:")

    for relationship in RELATIONSHIP_ORDER:
        print(f"- {relationship}: {relationship_counts.get(relationship, 0)}")

    print_conductor_summary(dataset.by_relationship(ROUTE_SPAN_EVIDENCE))
    print_direct_equipment_summary(dataset.by_relationship(DIRECT_EQUIPMENT_LINKED_TO_POLE))
    print_nearby_context_summary(dataset.by_relationship(NEARBY_CONTEXT_ONLY))
    print()


def print_conductor_summary(features: Iterable[ENWLEvidenceFeature]) -> None:
    """Print route/span evidence fields without implying per-pole proof."""
    route_features = list(features)

    print()
    print("Conductor / Route Evidence Summary")
    print(ROUTE_SPAN_CAUTION)

    if not route_features:
        print("- No route/span evidence records found.")
        return

    for feature in route_features:
        print(
            "- "
            f"FID={value_or_dash(feature.feature_id)} | "
            f"type={value_or_dash(feature.feature_type)} | "
            f"voltage={value_or_dash(feature.voltage or feature.nominal_voltage)} | "
            f"material={value_or_dash(feature.material)} | "
            f"cable_size={value_or_dash(feature.cable_size)} | "
            f"text_map={value_or_dash(feature.text_map)} | "
            f"rated_current={value_or_dash(feature.rated_current)}"
        )


def print_direct_equipment_summary(features: Iterable[ENWLEvidenceFeature]) -> None:
    """Print equipment records explicitly linked by fid_polestructure."""
    direct_features = list(features)

    print()
    print("Direct Equipment Link Summary")

    if not direct_features:
        print("- No equipment records with fid_polestructure found.")
        return

    for feature in direct_features:
        print(
            "- "
            f"FID={value_or_dash(feature.feature_id)} | "
            f"type={value_or_dash(feature.feature_type)} | "
            f"spn={value_or_dash(feature.spn)} | "
            f"fid_polestructure={value_or_dash(feature.fid_polestructure)}"
        )


def print_nearby_context_summary(features: Iterable[ENWLEvidenceFeature]) -> None:
    """Print nearby context counts by ENWL feature type."""
    counts = Counter(feature.feature_type or "unknown" for feature in features)

    print()
    print("Nearby Context Summary by feature_type")

    if not counts:
        print("- No nearby context records found.")
        return

    for feature_type, count in sorted(counts.items()):
        print(f"- {feature_type}: {count}")


def value_or_dash(value: object) -> str:
    """Return a printable field value."""
    if value is None:
        return "-"

    text = str(value).strip()
    return text if text else "-"


if __name__ == "__main__":
    raise SystemExit(main())
