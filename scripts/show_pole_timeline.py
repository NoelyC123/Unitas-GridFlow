#!/usr/bin/env python3
"""Show a per-pole evidence timeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main(argv: list[str] | None = None) -> int:
    from gridflow.conflict_detector import ConflictDetector
    from gridflow.evidence_combiner import combine_pole_evidence, link_pole
    from gridflow.readiness import ReadinessAssessor
    from gridflow.timeline import EvidenceTimelineBuilder

    parser = argparse.ArgumentParser(
        description="Show a conservative evidence timeline for one pole."
    )
    parser.add_argument(
        "--survey", required=True, help="Survey root, e.g. real_pilot_data/P_LOCAL_002"
    )
    parser.add_argument("--pole", required=True, help="Pole folder name, e.g. 05_SUPPORT_900344")
    parser.add_argument("--trace", required=True, help="ENWL trace GeoJSON path")
    args = parser.parse_args(argv)

    combined = combine_pole_evidence(args.survey, args.pole, args.trace)
    linking = link_pole(args.survey, args.pole, args.trace)
    conflicts = ConflictDetector().detect_pole(args.survey, args.pole, args.trace)
    readiness = ReadinessAssessor().assess_from_records(combined, linking, conflicts)
    enriched = {
        **combined,
        "linking": linking.to_dict(),
        "readiness": readiness.to_dict(),
        "conflicts": [conflict.to_dict() for conflict in conflicts],
    }
    timeline = EvidenceTimelineBuilder().build(args.pole, enriched)

    print(f"Evidence Timeline: {timeline.pole_id}")
    print("─────────────────────────────────────")
    for event in timeline.events:
        label = event.source.replace("_", " ").upper()
        print(f"[{event.date_display}] {label} — {event.title} ({event.confidence})")
        print(f"              {event.description}")
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
