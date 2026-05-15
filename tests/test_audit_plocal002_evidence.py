from __future__ import annotations

from pathlib import Path

from scripts.audit_plocal002_evidence import (
    draft_notes_template,
    parse_folder_name,
    run_audit,
    scan_evidence,
)


def make_pole_folder(root: Path, name: str) -> Path:
    pole = root / "enwl_enrichment_clean" / name
    for child in ("field_photos", "enwl_screenshots", "map_screenshots", "notes"):
        (pole / child).mkdir(parents=True, exist_ok=True)
    return pole


def test_parse_folder_name_detects_known_and_unknown_support():
    assert parse_folder_name("01_SUPPORT_902202") == ("01", "902202", "KNOWN")
    assert parse_folder_name("02_SUPPORT_UNKNOWN") == ("02", "UNKNOWN", "UNKNOWN")
    assert parse_folder_name("03_OTHER") == ("03", "UNKNOWN", "MISSING")


def test_scans_pole_folders_and_counts_files(tmp_path: Path):
    pole = make_pole_folder(tmp_path, "01_SUPPORT_902202")
    (pole / "field_photos" / "full.JPG").write_text("image", encoding="utf-8")
    (pole / "field_photos" / "top.png").write_text("image", encoding="utf-8")
    (pole / "field_photos" / "ignore.txt").write_text("not image", encoding="utf-8")
    (pole / "enwl_screenshots" / "popup.PNG").write_text("image", encoding="utf-8")
    (pole / "map_screenshots" / "map.jpeg").write_text("image", encoding="utf-8")
    (pole / "notes" / "identity.txt").write_text("notes", encoding="utf-8")

    audits = scan_evidence(tmp_path)

    assert len(audits) == 1
    audit = audits[0]
    assert audit.folder_name == "01_SUPPORT_902202"
    assert audit.pole_index == "01"
    assert audit.support_number == "902202"
    assert audit.support_status == "KNOWN"
    assert audit.field_photo_count == 2
    assert audit.enwl_screenshot_count == 1
    assert audit.map_screenshot_count == 1
    assert audit.notes_file_count == 1
    assert audit.notes_present is True


def test_creates_audit_markdown(tmp_path: Path):
    make_pole_folder(tmp_path, "01_SUPPORT_902202")

    audit_path = run_audit(tmp_path)
    content = audit_path.read_text(encoding="utf-8")

    assert audit_path == tmp_path / "route_notes" / "P_LOCAL_002_EVIDENCE_AUDIT.md"
    assert "# P_LOCAL_002 Evidence Audit" in content
    assert "| Pole | Folder | Support | Support Status |" in content
    assert "`01_SUPPORT_902202`" in content
    assert "FIELD_PHOTOS_MISSING" in content


def test_creates_draft_notes_when_missing(tmp_path: Path):
    pole = make_pole_folder(tmp_path, "02_SUPPORT_UNKNOWN")

    run_audit(tmp_path)

    notes_path = pole / "notes" / "pole_notes.md"
    content = notes_path.read_text(encoding="utf-8")
    assert notes_path.exists()
    assert "# P_LOCAL_002 — Pole 02 — Support UNKNOWN" in content
    assert "## Missing Evidence" in content
    assert "- SUPPORT_NUMBER_UNKNOWN" in content


def test_does_not_overwrite_existing_notes_by_default(tmp_path: Path):
    pole = make_pole_folder(tmp_path, "03_SUPPORT_UNKNOWN")
    notes_path = pole / "notes" / "pole_notes.md"
    notes_path.write_text("KEEP THIS", encoding="utf-8")

    run_audit(tmp_path)

    assert notes_path.read_text(encoding="utf-8") == "KEEP THIS"


def test_overwrites_notes_only_with_flag(tmp_path: Path):
    pole = make_pole_folder(tmp_path, "04_SUPPORT_123456")
    notes_path = pole / "notes" / "pole_notes.md"
    notes_path.write_text("OLD CONTENT", encoding="utf-8")

    run_audit(tmp_path, overwrite_notes=True)

    content = notes_path.read_text(encoding="utf-8")
    assert content != "OLD CONTENT"
    assert "# P_LOCAL_002 — Pole 04 — Support 123456" in content


def test_draft_notes_template_auto_fills_missing_evidence(tmp_path: Path):
    pole = make_pole_folder(tmp_path, "05_SUPPORT_UNKNOWN")
    audit = scan_evidence(tmp_path)[0]

    content = draft_notes_template(audit)

    assert "## Missing Evidence" in content
    assert "- SUPPORT_NUMBER_UNKNOWN" in content
    assert "- FIELD_PHOTOS_MISSING" in content
    assert "- ENWL_SCREENSHOTS_MISSING" in content
    assert "- MAP_SCREENSHOTS_MISSING" in content
    assert "05_SUPPORT_UNKNOWN" not in content
    assert pole.exists()
