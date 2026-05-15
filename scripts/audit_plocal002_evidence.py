#!/usr/bin/env python3
"""Audit and organise the P_LOCAL_002 field evidence pack.

This is a local evidence-management utility. It does not alter GridFlow
pipeline behaviour or runtime application logic.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

DEFAULT_ROOT = Path("real_pilot_data/P_LOCAL_002")
EVIDENCE_DIR = "enwl_enrichment_clean"
AUDIT_PATH = Path("route_notes/P_LOCAL_002_EVIDENCE_AUDIT.md")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".tif", ".tiff", ".webp"}


@dataclass(frozen=True)
class PoleEvidenceAudit:
    """Audit result for one pole evidence folder."""

    folder_name: str
    folder_path: Path
    pole_index: str
    support_number: str
    support_status: str
    field_photo_count: int
    enwl_screenshot_count: int
    map_screenshot_count: int
    notes_file_count: int
    notes_present: bool
    pole_notes_exists: bool
    missing_flags: tuple[str, ...]
    next_action: str


def parse_folder_name(folder_name: str) -> tuple[str, str, str]:
    """Extract pole index and support number status from a pole folder name."""
    index_match = re.match(r"^(?P<index>\d{1,3})(?:_|$)", folder_name)
    pole_index = index_match.group("index") if index_match else "UNKNOWN"

    support_match = re.search(r"(?:^|_)SUPPORT_(?P<support>[A-Za-z0-9]+)", folder_name)
    if not support_match:
        return pole_index, "UNKNOWN", "MISSING"

    support_number = support_match.group("support").upper()
    if support_number == "UNKNOWN":
        return pole_index, "UNKNOWN", "UNKNOWN"
    return pole_index, support_number, "KNOWN"


def count_image_files(path: Path) -> int:
    """Count image files directly under a directory."""
    if not path.exists() or not path.is_dir():
        return 0
    return sum(
        1
        for item in path.iterdir()
        if item.is_file()
        and not item.name.startswith(".")
        and item.suffix.lower() in IMAGE_EXTENSIONS
    )


def count_note_files(path: Path) -> int:
    """Count note files directly under a directory."""
    if not path.exists() or not path.is_dir():
        return 0
    return sum(1 for item in path.iterdir() if item.is_file() and not item.name.startswith("."))


def missing_evidence_flags(
    support_status: str,
    field_photo_count: int,
    enwl_screenshot_count: int,
    map_screenshot_count: int,
    notes_file_count: int,
) -> tuple[str, ...]:
    """Return missing evidence flags for a pole folder."""
    flags: list[str] = []
    if support_status != "KNOWN":
        flags.append("SUPPORT_NUMBER_UNKNOWN")
    if field_photo_count == 0:
        flags.append("FIELD_PHOTOS_MISSING")
    if enwl_screenshot_count == 0:
        flags.append("ENWL_SCREENSHOTS_MISSING")
    if map_screenshot_count == 0:
        flags.append("MAP_SCREENSHOTS_MISSING")
    if notes_file_count == 0:
        flags.append("NOTES_MISSING")
    return tuple(flags)


def recommended_next_action(flags: tuple[str, ...], pole_notes_exists: bool) -> str:
    """Generate a concise next action based on missing evidence."""
    if not flags and pole_notes_exists:
        return "Evidence appears complete; review notes for survey quality."
    if flags == ("NOTES_MISSING",) and not pole_notes_exists:
        return "Complete draft pole_notes.md."
    if "SUPPORT_NUMBER_UNKNOWN" in flags:
        return "Confirm support number from ENWL popup or route context; complete notes."
    if "FIELD_PHOTOS_MISSING" in flags:
        return "Add or recover field photos before pipeline validation."
    if "ENWL_SCREENSHOTS_MISSING" in flags or "MAP_SCREENSHOTS_MISSING" in flags:
        return "Add missing map/ENWL screenshots and complete notes."
    return "Resolve missing evidence flags and complete pole_notes.md."


def scan_pole_folder(folder_path: Path) -> PoleEvidenceAudit:
    """Scan one pole folder."""
    pole_index, support_number, support_status = parse_folder_name(folder_path.name)

    field_photo_count = count_image_files(folder_path / "field_photos")
    enwl_screenshot_count = count_image_files(folder_path / "enwl_screenshots")
    map_screenshot_count = count_image_files(folder_path / "map_screenshots")
    notes_file_count = count_note_files(folder_path / "notes")
    pole_notes_exists = (folder_path / "notes" / "pole_notes.md").exists()

    flags = missing_evidence_flags(
        support_status=support_status,
        field_photo_count=field_photo_count,
        enwl_screenshot_count=enwl_screenshot_count,
        map_screenshot_count=map_screenshot_count,
        notes_file_count=notes_file_count,
    )

    return PoleEvidenceAudit(
        folder_name=folder_path.name,
        folder_path=folder_path,
        pole_index=pole_index,
        support_number=support_number,
        support_status=support_status,
        field_photo_count=field_photo_count,
        enwl_screenshot_count=enwl_screenshot_count,
        map_screenshot_count=map_screenshot_count,
        notes_file_count=notes_file_count,
        notes_present=notes_file_count > 0,
        pole_notes_exists=pole_notes_exists,
        missing_flags=flags,
        next_action=recommended_next_action(flags, pole_notes_exists),
    )


def scan_evidence(root: Path) -> list[PoleEvidenceAudit]:
    """Scan all pole folders under the P_LOCAL_002 clean evidence directory."""
    evidence_root = root / EVIDENCE_DIR
    if not evidence_root.exists():
        raise FileNotFoundError(f"Evidence folder not found: {evidence_root}")

    pole_folders = sorted(
        item
        for item in evidence_root.iterdir()
        if item.is_dir() and re.match(r"^\d{1,3}_", item.name)
    )
    return [scan_pole_folder(folder) for folder in pole_folders]


def render_missing_evidence(flags: tuple[str, ...]) -> str:
    """Render missing evidence bullets for draft notes."""
    if not flags:
        return "- None identified by audit script."
    return "\n".join(f"- {flag}" for flag in flags)


def draft_notes_template(audit: PoleEvidenceAudit) -> str:
    """Create draft pole_notes.md content for one pole."""
    support = audit.support_number if audit.support_status == "KNOWN" else "UNKNOWN"
    return f"""# P_LOCAL_002 — Pole {audit.pole_index} — Support {support}

## Identity
Support number:
ENWL FID:
SPN:
Coordinates:
Field GPS:

## Access
Private/public:
Permission:
Base visible:
Top visible:
Obstruction:
Safe access:

## Field Photos
Full pole:
Top:
Base:
ID/marking:
Span previous:
Span next:
Overview:

## ENWL Evidence
Pole popup:
Conductor popup:
Sleeve/joint/termination popup:
Route context screenshot:

## Observations
Material:
Pole type:
Pole class:
Stay present:
Downlead/cable guard:
Transformer/switch/fuse/link:
Vegetation issue:
Access issue:
Condition:
Uncertainties:

## GridFlow Interpretation
Evidence status:
Confirmed / likely / uncertain

## Missing Evidence
{render_missing_evidence(audit.missing_flags)}
"""


def create_draft_notes(audit: PoleEvidenceAudit, overwrite: bool = False) -> bool:
    """Create notes/pole_notes.md if missing, or overwrite when requested."""
    notes_dir = audit.folder_path / "notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    notes_path = notes_dir / "pole_notes.md"
    if notes_path.exists() and not overwrite:
        return False
    notes_path.write_text(draft_notes_template(audit), encoding="utf-8")
    return True


def render_audit_markdown(audits: list[PoleEvidenceAudit], root: Path) -> str:
    """Render the evidence audit markdown report."""
    generated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(audits)
    known_support = sum(1 for audit in audits if audit.support_status == "KNOWN")
    notes_ready = sum(1 for audit in audits if audit.notes_present)
    missing_any = sum(1 for audit in audits if audit.missing_flags)

    lines = [
        "# P_LOCAL_002 Evidence Audit",
        "",
        f"**Generated:** {generated}",
        f"**Root:** `{root}`",
        f"**Evidence folder:** `{root / EVIDENCE_DIR}`",
        "",
        "## Summary",
        "",
        f"- **Pole folders:** {total}",
        f"- **Known support numbers:** {known_support}/{total}",
        f"- **Notes present:** {notes_ready}/{total}",
        f"- **Folders with missing evidence flags:** {missing_any}/{total}",
        "",
        "## Pole Evidence Table",
        "",
        "| Pole | Folder | Support | Support Status | Field Photos | ENWL Screenshots | Map Screenshots | Notes | Missing Flags | Recommended Next Action |",
        "|---|---|---|---|---:|---:|---:|---|---|---|",
    ]

    for audit in audits:
        flags = ", ".join(audit.missing_flags) if audit.missing_flags else "None"
        notes = "YES" if audit.notes_present else "NO"
        lines.append(
            "| "
            f"{audit.pole_index} | "
            f"`{audit.folder_name}` | "
            f"{audit.support_number} | "
            f"{audit.support_status} | "
            f"{audit.field_photo_count} | "
            f"{audit.enwl_screenshot_count} | "
            f"{audit.map_screenshot_count} | "
            f"{notes} | "
            f"{flags} | "
            f"{audit.next_action} |"
        )

    lines.extend(
        [
            "",
            "## Missing Evidence Flag Definitions",
            "",
            "- `SUPPORT_NUMBER_UNKNOWN` - folder does not currently contain a confirmed support number.",
            "- `FIELD_PHOTOS_MISSING` - no image files found under `field_photos/`.",
            "- `ENWL_SCREENSHOTS_MISSING` - no image files found under `enwl_screenshots/`.",
            "- `MAP_SCREENSHOTS_MISSING` - no image files found under `map_screenshots/`.",
            "- `NOTES_MISSING` - no note files found under `notes/`.",
            "",
            "## Recommended Workflow",
            "",
            "1. Confirm unknown support numbers from ENWL popup evidence or route context.",
            "2. Complete every `notes/pole_notes.md` draft before pipeline validation.",
            "3. Add or recover missing field photos and screenshots where available.",
            "4. Re-run this audit after evidence updates.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_audit(root: Path, audits: list[PoleEvidenceAudit]) -> Path:
    """Write the audit markdown file and return its path."""
    audit_path = root / AUDIT_PATH
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.write_text(render_audit_markdown(audits, root), encoding="utf-8")
    return audit_path


def run_audit(root: Path, overwrite_notes: bool = False, verbose: bool = False) -> Path:
    """Scan evidence, create missing draft notes, and write the audit file."""
    audits = scan_evidence(root)
    created_notes = 0

    for audit in audits:
        if create_draft_notes(audit, overwrite=overwrite_notes):
            created_notes += 1
            if verbose:
                print(f"Created notes: {audit.folder_path / 'notes' / 'pole_notes.md'}")
        elif verbose:
            print(f"Kept existing notes: {audit.folder_path / 'notes' / 'pole_notes.md'}")

    # Re-scan after draft note creation so the report reflects current notes status.
    refreshed_audits = scan_evidence(root)
    audit_path = write_audit(root, refreshed_audits)

    if verbose:
        print(f"Scanned pole folders: {len(refreshed_audits)}")
        print(f"Draft notes created/updated: {created_notes}")
        print(f"Audit written: {audit_path}")

    return audit_path


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Audit and organise P_LOCAL_002 field survey evidence."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_ROOT,
        help="P_LOCAL_002 root folder (default: real_pilot_data/P_LOCAL_002)",
    )
    parser.add_argument(
        "--overwrite-notes",
        action="store_true",
        help="Overwrite existing notes/pole_notes.md files.",
    )
    parser.add_argument("--verbose", action="store_true", help="Print scan progress.")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    audit_path = run_audit(
        root=args.root,
        overwrite_notes=args.overwrite_notes,
        verbose=args.verbose,
    )
    print(f"Evidence audit written: {audit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
