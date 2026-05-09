#!/usr/bin/env python3
"""Generate the Stage 4 structured-capture CSV template.

Writes a CSV file whose header row is the canonical Stage 4 schema header
list. With ``--include-descriptions`` the file is prefixed with comment
lines (``#``-prefixed) describing each field, group, allowed values, and
unit. The default output path is ``templates/structured_capture_template.csv``
relative to the repository root.

The script depends only on the Python standard library and on
``app.structured_capture_schema``. It does not import the Flask app and
does not touch live upload state.
"""

from __future__ import annotations

import argparse
import csv
import sys
from io import StringIO
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.structured_capture_schema import (  # noqa: E402  (path tweak above)
    GROUPS,
    get_stage4_fields,
    get_stage4_template_headers,
)

DEFAULT_OUTPUT = REPO_ROOT / "templates" / "structured_capture_template.csv"


def _format_allowed(allowed: tuple[str, ...] | None) -> str:
    if not allowed:
        return "free text"
    return " | ".join(allowed)


def build_description_block() -> list[str]:
    """Return ``#``-prefixed comment lines describing every Stage 4 field."""

    lines: list[str] = [
        "# GridFlow Stage 4 structured capture template",
        "# All fields are FUTURE structured capture (current_status: stage4_future_capture).",
        "# Trimble controller exports do NOT supply these fields today.",
        "# Allowed values are case-insensitive on input.",
        "# Blank, 'unknown', and '?' are all treated as unknown.",
        "#",
    ]
    by_group: dict[str, list[dict]] = {key: [] for key in GROUPS}
    for definition in get_stage4_fields():
        by_group[definition["group"]].append(definition)

    for group_id, group_label in GROUPS.items():
        lines.append(f"# Group: {group_label}")
        for definition in by_group[group_id]:
            required = " (required)" if definition["required"] else ""
            unit = f" [{definition['unit']}]" if definition.get("unit") else ""
            lines.append(
                "#   {name}{required}{unit} — {allowed} — {desc}".format(
                    name=definition["field_name"],
                    required=required,
                    unit=unit,
                    allowed=_format_allowed(definition["allowed_values"]),
                    desc=definition["description"],
                )
            )
        lines.append("#")
    return lines


def render_template(*, include_descriptions: bool) -> str:
    """Render the template content as a single string (no file I/O)."""

    buffer = StringIO()
    if include_descriptions:
        buffer.write("\n".join(build_description_block()))
        buffer.write("\n")

    writer = csv.writer(buffer)
    writer.writerow(get_stage4_template_headers())
    return buffer.getvalue()


def write_template(output_path: Path, *, include_descriptions: bool) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        render_template(include_descriptions=include_descriptions), encoding="utf-8"
    )
    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output path for the CSV template (default: {DEFAULT_OUTPUT.relative_to(REPO_ROOT)})",
    )
    parser.add_argument(
        "--include-descriptions",
        action="store_true",
        help="Prepend # comment lines describing every field, group, and allowed values",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print the template to stdout instead of writing a file",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rendered = render_template(include_descriptions=args.include_descriptions)
    if args.stdout:
        sys.stdout.write(rendered)
        return 0
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"Wrote Stage 4 template: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
