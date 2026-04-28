#!/usr/bin/env python3
"""Create a shareable validation evidence pack for a GridFlow run.

The script is intentionally read-only against app outputs. It copies existing
artifacts and uses Flask's test client to render PDF/design-chain exports into the pack.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
UPLOADS_ROOT = REPO_ROOT / "uploads"
PROJECTS_ROOT = UPLOADS_ROOT / "projects"
JOBS_ROOT = UPLOADS_ROOT / "jobs"
DEFAULT_OUTPUT_ROOT = Path.home() / "Desktop"


@dataclass(frozen=True)
class RunContext:
    kind: str
    display_id: str
    source_dir: Path
    input_dir: Path
    output_routes: dict[str, str]
    project_dir: Path | None = None


def _safe_label(value: str) -> str:
    label = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return label.strip("_") or "validation"


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _copy_if_exists(src: Path, dest: Path, manifest: list[str], label: str | None = None) -> bool:
    if not src.exists():
        manifest.append(f"- missing: `{src}`")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    final_dest = dest if label is None else dest.parent / label
    shutil.copy2(src, final_dest)
    manifest.append(f"- copied: `{src}` -> `{final_dest.relative_to(dest.parents[2])}`")
    return True


def _find_input_file(source_dir: Path, meta: dict) -> Path | None:
    uploaded_path = meta.get("uploaded_path")
    if uploaded_path:
        path = Path(uploaded_path)
        if path.exists():
            return path

    filename = meta.get("filename")
    if filename:
        path = source_dir / str(filename)
        if path.exists():
            return path

    csv_files = sorted(source_dir.glob("*.csv"))
    return csv_files[0] if csv_files else None


def _context_from_args(args: argparse.Namespace) -> RunContext:
    if args.run:
        if "/" in args.run:
            project_id, file_id = args.run.split("/", 1)
            args.project_id = project_id.strip()
            args.file_id = file_id.strip()
        else:
            args.job_id = args.run.strip()

    if args.project_id or args.file_id:
        if not args.project_id or not args.file_id:
            raise SystemExit("--project-id and --file-id must be provided together")
        project_dir = PROJECTS_ROOT / args.project_id
        source_dir = project_dir / "files" / args.file_id
        if not source_dir.exists():
            raise SystemExit(f"Project file directory not found: {source_dir}")
        return RunContext(
            kind="project",
            display_id=f"{args.project_id}/{args.file_id}",
            source_dir=source_dir,
            input_dir=source_dir,
            project_dir=project_dir,
            output_routes={
                "qa_report.pdf": f"/pdf/qa/project/{args.project_id}/{args.file_id}",
                "design_chain_export.csv": (
                    f"/d2d/export/project/{args.project_id}/{args.file_id}"
                ),
                "raw_working_audit.csv": (
                    f"/d2d/interleaved/project/{args.project_id}/{args.file_id}"
                ),
            },
        )

    if args.job_id:
        source_dir = JOBS_ROOT / args.job_id
        if not source_dir.exists():
            raise SystemExit(f"Job directory not found: {source_dir}")
        return RunContext(
            kind="legacy_job",
            display_id=args.job_id,
            source_dir=source_dir,
            input_dir=source_dir,
            output_routes={
                "qa_report.pdf": f"/pdf/qa/{args.job_id}",
                "design_chain_export.csv": f"/d2d/export/{args.job_id}",
                "raw_working_audit.csv": f"/d2d/interleaved/{args.job_id}",
            },
        )

    raise SystemExit("Provide --run, --job-id, or --project-id with --file-id")


def _create_pack_root(context: RunContext, output_root: Path, label: str | None) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_label = _safe_label(label or context.display_id)
    pack_root = output_root / f"Unitas_GridFlow_Validation_Run_{timestamp}_{run_label}"
    pack_root.mkdir(parents=True, exist_ok=False)
    return pack_root


def _copy_core_outputs(context: RunContext, pack_root: Path, manifest: list[str]) -> None:
    input_dir = pack_root / "01_Input"
    outputs_dir = pack_root / "02_App_Outputs"

    meta = _load_json(context.source_dir / "meta.json")
    input_file = _find_input_file(context.input_dir, meta)
    if input_file:
        _copy_if_exists(input_file, input_dir / input_file.name, manifest)
    else:
        manifest.append("- missing: original input CSV")

    if context.project_dir:
        _copy_if_exists(
            context.project_dir / "project.json", outputs_dir / "project.json", manifest
        )

    known_outputs = [
        ("meta.json", "meta.json"),
        ("issues.csv", "issues.csv"),
        ("map_data.json", "map_data.json"),
        ("sequenced_route.json", "sequenced_route.json"),
        ("review.json", "review_decisions.json"),
    ]
    for source_name, dest_name in known_outputs:
        _copy_if_exists(context.source_dir / source_name, outputs_dir / dest_name, manifest)


def _render_route_outputs(context: RunContext, pack_root: Path, manifest: list[str]) -> None:
    sys.path.insert(0, str(REPO_ROOT))
    from app import create_app  # noqa: PLC0415

    app = create_app()
    client = app.test_client()
    outputs_dir = pack_root / "02_App_Outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    for filename, route in context.output_routes.items():
        response = client.get(route)
        dest = outputs_dir / filename
        if response.status_code == 200:
            dest.write_bytes(response.data)
            manifest.append(f"- generated: `{route}` -> `{dest.relative_to(pack_root)}`")
        else:
            manifest.append(f"- unavailable: `{route}` returned HTTP {response.status_code}")


def _copy_screenshots(args: argparse.Namespace, pack_root: Path, manifest: list[str]) -> None:
    screenshots_dir = pack_root / "03_Screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    screenshot_paths: list[Path] = []
    if args.screenshots:
        screenshot_paths.extend(Path(p).expanduser() for p in args.screenshots)
    if args.screenshots_dir:
        source_dir = Path(args.screenshots_dir).expanduser()
        if source_dir.exists():
            image_suffixes = {".png", ".jpg", ".jpeg", ".heic", ".webp"}
            screenshot_paths.extend(
                sorted(
                    path
                    for path in source_dir.iterdir()
                    if path.is_file() and path.suffix.lower() in image_suffixes
                )
            )
        else:
            manifest.append(f"- missing screenshots directory: `{source_dir}`")

    copied = 0
    for idx, src in enumerate(screenshot_paths, start=1):
        if not src.exists():
            manifest.append(f"- missing screenshot: `{src}`")
            continue
        dest = screenshots_dir / f"{idx:02d}_{_safe_label(src.stem)}{src.suffix.lower()}"
        shutil.copy2(src, dest)
        copied += 1
        manifest.append(f"- copied screenshot: `{src}` -> `{dest.relative_to(pack_root)}`")

    if copied == 0:
        (screenshots_dir / "README.md").write_text(
            "# Screenshots\n\n"
            "Add phone/desktop screenshots here before sharing the validation pack.\n",
            encoding="utf-8",
        )


def _write_notes(context: RunContext, pack_root: Path) -> None:
    notes_dir = pack_root / "04_Notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    notes_path = notes_dir / "validation_notes.md"
    notes_path.write_text(
        f"""# Validation Notes — {context.display_id}

## Run Summary

- Run type: {context.kind}
- Run ID: {context.display_id}
- Pack created: {datetime.now().isoformat(timespec="seconds")}

## Questions To Answer

1. Did the remote phone upload feel usable?
2. Did the project dashboard make sense after upload?
3. Were the EXpole pairings acceptable without changes?
4. Were the Design Chain Export and Raw Working Audit good enough to reduce manual spreadsheet work?
5. What was the biggest friction or missing piece?
6. Did anything look misleading?
7. Did any download/export fail?
8. What should be improved next?

## Notes

- What worked:
- What failed:
- What was confusing:
- What saved time:
- What still required manual design-chain preparation:
- Whether reviewed exports were useful:
- Recommended next task:
""",
        encoding="utf-8",
    )


def _write_review_prompt(context: RunContext, pack_root: Path) -> None:
    prompt_dir = pack_root / "05_AI_Prompt"
    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = prompt_dir / "review_prompt.txt"
    prompt_path.write_text(
        f"""You are reviewing a Unitas GridFlow validation evidence pack.

Run under review: {context.display_id}

Unitas GridFlow is a survey-to-design handoff tool for UK overhead-line
electricity survey files. It supports post-survey QA, provisional design-chain exports,
named projects, designer review, local daily intake, and controlled remote
access through Cloudflare Tunnel + Access.

Please inspect the included evidence:
- 01_Input/original or uploaded survey CSV
- 02_App_Outputs/meta.json
- 02_App_Outputs/issues.csv
- 02_App_Outputs/map_data.json
- 02_App_Outputs/sequenced_route.json, if present
- 02_App_Outputs/review_decisions.json, if present
- 02_App_Outputs/qa_report.pdf
- 02_App_Outputs/design_chain_export.csv
- 02_App_Outputs/raw_working_audit.csv
- 03_Screenshots/
- 04_Notes/validation_notes.md

Review questions:
1. Does the app output match the raw input evidence?
2. Is the project/dashboard state internally consistent?
3. Are the QA/design-readiness findings understandable and useful?
4. Are existing/proposed proximity QA and design-chain exports plausible enough
   to reduce manual spreadsheet work?
5. What is the strongest validation signal?
6. What is the biggest risk or friction?
7. What should the next narrow improvement be?

Do not recommend hosted deployment, app accounts, cloud storage, photo upload,
tablet capture, live Trimble sync, Stage 4, Stage 5, or Stage 6 unless the
evidence clearly justifies changing scope.
""",
        encoding="utf-8",
    )


def _write_manifest(context: RunContext, pack_root: Path, manifest: list[str]) -> None:
    manifest_path = pack_root / "00_MANIFEST.md"
    manifest_path.write_text(
        "# Validation Evidence Pack Manifest\n\n"
        f"- Run type: `{context.kind}`\n"
        f"- Run ID: `{context.display_id}`\n"
        f"- Source directory: `{context.source_dir}`\n"
        f"- Created: `{datetime.now().isoformat(timespec='seconds')}`\n\n"
        "## Actions\n\n" + "\n".join(manifest) + "\n",
        encoding="utf-8",
    )


def _zip_pack(pack_root: Path) -> Path:
    zip_path = pack_root.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(pack_root.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(pack_root.parent))
    return zip_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a Unitas GridFlow validation evidence pack."
    )
    target = parser.add_argument_group("target")
    target.add_argument("--run", help="Run identifier, e.g. P007/F001 or J16535")
    target.add_argument("--project-id", help="Project ID, e.g. P007")
    target.add_argument("--file-id", help="Project file ID, e.g. F001")
    target.add_argument("--job-id", help="Legacy job ID, e.g. J16535")

    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--label",
        help="Optional label to include in the pack folder name",
    )
    parser.add_argument(
        "--screenshots",
        nargs="*",
        help="Optional screenshot files to copy into the pack",
    )
    parser.add_argument(
        "--screenshots-dir",
        help="Optional directory of screenshots to copy into the pack",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Also create a .zip next to the pack folder",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    context = _context_from_args(args)
    output_root = args.output_root.expanduser()
    output_root.mkdir(parents=True, exist_ok=True)
    pack_root = _create_pack_root(context, output_root, args.label)

    manifest: list[str] = []
    _copy_core_outputs(context, pack_root, manifest)
    _render_route_outputs(context, pack_root, manifest)
    _copy_screenshots(args, pack_root, manifest)
    _write_notes(context, pack_root)
    _write_review_prompt(context, pack_root)
    _write_manifest(context, pack_root, manifest)

    print(f"Created validation pack: {pack_root}")
    if args.zip:
        zip_path = _zip_pack(pack_root)
        print(f"Created zip archive: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
