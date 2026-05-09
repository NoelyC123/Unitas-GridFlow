# GridFlow API Reference

Practical reference for the public functions and classes most likely to
be useful when extending GridFlow. Grouped by module. Each entry lists
the signature, purpose, key inputs/outputs, and any side effects.

> ⚠ **Stage 4 schema and validators are library code only.** They are
> imported by their tests and the template generator; nothing in the
> live request path uses them yet. Where this matters, the entry is
> tagged **(not runtime-integrated)**.

---

## `app/controller_intake.py`

Trimble-aware parser plus role-classification and design-readiness
summaries.

### `parse_raw_controller_dump(path: Path | str) -> pd.DataFrame`

Parses a positional / attribute-pair Trimble controller dump (F001-class
format). Returns a DataFrame with the canonical six columns:
`pole_id`, `easting`, `northing`, `height`, `structure_type`, `location`.
GPS elevation in column 3 is intentionally discarded.

### `parse_controller_csv(df: pd.DataFrame) -> pd.DataFrame`

Parses an already-loaded controller-style DataFrame (3-column variant).
Same output schema as `parse_raw_controller_dump`.

### `is_controller_csv(df) -> bool` / `is_raw_controller_dump(first_line: str) -> bool`

Format sniffers used by the upload route to decide which parser to call.

### `detect_grid_crs(easting: float, northing: float) -> str`

Returns the most likely CRS identifier given a representative coordinate
pair: `EPSG:29902` (Irish Grid TM65), `EPSG:2157` (ITM), or
`EPSG:27700` (OSGB).

### `convert_grid_to_wgs84(df: pd.DataFrame) -> pd.DataFrame`

Adds `lat` / `lon` columns by reprojecting `easting` / `northing` per
the detected CRS. Mutates and returns the same DataFrame.

### `classify_record_roles(df: pd.DataFrame) -> pd.DataFrame`

Adds a `record_role` column: `structural`, `context`, `anchor`, etc.

### `build_completeness_summary(df) -> dict`

Returns per-field present/missing percentages. Used by the design
readiness calculations.

### `build_top_design_risks(issues_df, completeness) -> list[dict]` / `build_design_readiness(completeness) -> dict`

Higher-level summaries aggregated from QA output and completeness, used
by the briefing PDF.

---

## `app/routes/api_intake.py`

Flask blueprint that owns the upload-to-map-data pipeline.

### `process_job(job_short, ...) -> dict`

Top-level orchestrator. Reads the uploaded CSV, runs cleaning, geometry
normalisation, span generation, QA, replacement-pair sequencing, and
GeoJSON assembly. Writes `map_data.json` to the job directory and
returns a summary dict.

**Side effects:** writes files under `uploads/projects/<P>/files/<F>/`
or `uploads/jobs/<J>/`.

### `clean_numeric_field(value) -> float | None` / `clean_text_field(value) -> str | None`

Robust per-cell cleaners. Strip units, ignore `N/A`, treat blanks as
None, etc. Pure functions.

### `validate_required_fields(df) -> tuple[bool, list[str]]`

Checks every required field is present in the cleaned DataFrame.
Returns `(ok, missing_field_names)`.

### `generate_import_summary(...)` / `format_import_summary(summary) -> str`

Build the human-readable ingest summary shown after upload.

### `_build_feature_collection(...)`

Internal: assembles the per-pole and per-span GeoJSON the viewer reads.
This is where popup-bound properties land.

### `_build_replacement_links(...)` / `_build_replacement_narratives(...)`

Internal: connect EX/PR pairs and produce the design narrative strings.

### `finalize(job_short)` *(Flask route)*

Marks a job as finalised; writes status flags to `meta.json`.

---

## `app/qa_engine.py`

Confidence-aware QA over the cleaned DataFrame.

### `run_qa_checks(df, rules)`

Top-level QA entry point. `rules` is a rulepack (typically the DNO one
selected by `app/dno_rules.py`). Returns a DataFrame of issues with
severity, field, and message.

### `classify_height_confidence(record) -> dict[str, str]`

Returns `{ confidence: "high"|"medium"|"low", reason: ... }` based on
record role, structure type, and presence of an attribute pair.

### `classify_source_confidence(record) -> dict[str, object]`

Per-feature geometry / source-confidence label used by the viewer's
geometry-trust banner.

### `parse_attachments(record) -> dict[str, object]`

Extracts photo/attachment indicators from the record's REMARK or
auxiliary fields.

### `validate_coordinate_consistency(records) -> list[dict]` / `validate_span_distances(records, ...)`

Lower-level checks called inside `run_qa_checks`.

### `infer_display_network_fields(record, ...)`

Best-effort inference of a network identifier (line / circuit /
section) from the surveyor's free-text remarks.

---

## `app/geometry_pipeline.py`

Pure geometry helpers.

### `normalize_geometry_for_span_generation(records, ...) -> CleanedGeometry`

Snaps near-duplicate points, merges duplicates, removes zero-length
sequences, and recomputes span distances.

### `validate_coordinates(...) -> bool` / `calculate_distance(lat1, lon1, lat2, lon2) -> float` / `calculate_bearing(...) -> float`

Geometry primitives; metric-aware (haversine for lat/lon, euclidean for
projected coords).

### `class CleanedGeometry(NamedTuple)`

Result of `normalize_geometry_for_span_generation`. Carries the cleaned
chain plus counts of merged/removed records for the import summary.

---

## `app/field_reference.py`

Canonical field metadata catalogue.

### `get_field_definition(field_name: str) -> dict | None`

Returns the schema entry for a canonical field name. None if unknown.

### `get_display_label(field_name: str) -> str` / `get_field_unit(field_name: str) -> str | None` / `get_fields_for_group(group: str) -> list[str]`

Read-only views over the schema for popup/report rendering.

### `get_missing_wording(field_name, structure_type=None) -> str`

Returns the contextual "missing" text. **Important** — this is where
the C2E2 truthfulness rule lives: `Pol` height returns `Not measured`,
`material` returns `Not recorded in survey`, etc.

### `resolve_alias(column_name: str) -> str | None`

Maps an arbitrary CSV column header to its canonical field name (or
None).

### `get_all_aliases(field_name: str) -> list[str]`

Inverse of `resolve_alias` — every alias accepted for a given canonical
name.

---

## `app/field_validators.py`

Field-display + truthfulness helpers (consumed by the popup renderer).

### `is_measured(value) -> bool`

True if the value represents real measurement evidence (not blank, not
a sentinel "unknown" string).

### `is_missing_legitimate(field_name, structure_type, value) -> bool`

True when the missing value is *expected* for the structure type (e.g.
a `Pol` with no height).

### `validate_field_value(...) -> dict` / `validate_height_value(...) -> dict`

Per-field validation results: `{valid, severity, reason}`.

### `format_field_display(field, value, structure_type=None) -> str`

Single-string render of a field for UI/PDF.

### `get_popup_display_value(field, value, structure_type=None) -> dict`

Returns `{label, value, source_label, severity, is_measured}` — the
canonical popup-row payload.

### `classify_field_completeness(...) -> str`

Per-field completeness category (used in the design-readiness summary).

---

## `app/structured_capture_schema.py` *(not runtime-integrated)*

Stage 4 field catalogue. Pure stdlib.

### `get_stage4_field_definition(field_name: str) -> dict | None`

Resolves canonical names and aliases. Returns the full schema entry.

### `get_stage4_fields() -> list[dict]` / `get_stage4_fields_by_group(group: str) -> list[dict]`

Bulk views.

### `get_stage4_required_fields() -> list[str]`

Currently `["capture_source", "captured_by", "capture_date"]`.

### `get_stage4_template_headers() -> list[str]`

CSV header order in canonical declaration order.

### `is_stage4_field(field_name: str) -> bool`

True if the name (or any alias) matches a Stage 4 field.

### Module constants

`CURRENT_STATUS = "stage4_future_capture"`,
`SOURCE = "structured_capture"`,
`GROUPS` (id → label dict),
plus enum vocabularies `CONDITION_VALUES`, `SEVERITY_VALUES`,
`LEAN_SEVERITY_VALUES`, `VOLTAGE_VALUES`, `PRESENCE_VALUES`,
`CONFIDENCE_VALUES`.

---

## `app/structured_capture_validators.py` *(not runtime-integrated)*

Pure validation helpers. No Flask, no pandas, no I/O. Result shape:
`{valid: bool, errors: list[str], warnings: list[str], normalised: dict}`.

### `is_blank(value) -> bool`

Treats `None`, empty strings, and tokens like `n/a`, `none`, `null`,
`tbc`, `?` as blank.

### `normalise_bool(value) -> str`

Returns one of `"yes"` / `"no"` / `"unknown"`. Unrecognised input
collapses to `"unknown"`.

### `validate_allowed_value(field_name, value) -> result`

Validates a single value against the schema's `allowed_values`. Unknown
field names are themselves blocking errors.

### `validate_required_fields(row) -> result`

Checks every Stage 4 required field is present and non-blank.

### `validate_stage4_row(row) -> result` / `validate_stage4_rows(rows) -> result`

Row- and batch-level validation. Unknown columns produce a warning, not
an error.

### `classify_stage4_completeness(row) -> str`

Returns `"empty"` / `"partial"` / `"minimum"` / `"complete"`.

### `normalise_stage4_row(row) -> dict`

Returns a copy with values lowercased / stripped / canonicalised. Free
text is stripped; enums are matched case-insensitively and returned in
canonical case (e.g. `"11kv"` → `"11kV"`).

---

## `scripts/manual_review.py`

Selenium-based browser validation harness.

### `main(argv: list[str] | None = None) -> int`

CLI entry point. Boots a local Flask server (or uses `--base-url`),
drives headless Chrome, runs the baseline suite plus any
`--checklist` YAMLs, writes `validation_runs/<UTC>/...`. Exit codes:
`0` all pass, `1` any failure, `2` setup error.

### `class ManualReviewRunner`

Carries the per-run state: results list, console buffer, screenshot
directory. The interesting methods are `_baseline_checks(driver, job)`
and `_run_checklist_check(driver, job, check)`.

### `resolve_job_target(value: str) -> JobTarget`

Resolves any of: `P010/F001`, `P010` (first file), `J12345` (legacy
job), `Gordon` / `Bellsprings` (aliases), or free-text search across
`project.json` / `meta.json`.

### `load_checklist(path: Path) -> list[dict]`

Loads a YAML or JSON checklist via PyYAML, validates each item has
`id` and `type`. Used by the `--checklist` flag.

### Supported checklist types

`selector_visible`, `text_present`, `popup_text_contains`,
`click_selector`, `route_highlight_active`,
`planner_awareness_visible`.

---

## `scripts/start_task.py`

Records the start of a control-layer task.

### `main(argv: list[str] | None = None) -> int`

Reads `--task`, `--owner`, `--branch`, optional `--status` / `--summary`.
Appends to `AI_CONTROL/03_WORKER_LOG.md`, replaces the marked active-task
sections in `AI_CONTROL/00_PROJECT_BOARD.md` and
`AI_CONTROL/05_HANDOFF.md`.

### `replace_marked_section(path, start_marker, end_marker, replacement) -> None`

Helper used to overwrite the bounded board/handoff sections without
disturbing surrounding content. If the markers are missing, appends a
fresh marked section instead of corrupting the file.

---

## `scripts/log_worker_update.py`

### `main(argv: list[str] | None = None) -> int`

Appends a worker update entry to `AI_CONTROL/03_WORKER_LOG.md`. Required
flags: `--worker`, `--branch`, `--summary`. Optional: `--files`,
`--validation`, `--next-action`.

### `append_update(*, worker, branch, summary, files, validation, next_action) -> None`

Library-level entry the CLI calls; useful from other scripts that want
to emit a worker entry with a known timestamp.

---

## `scripts/log_validation_run.py`

### `main(argv: list[str] | None = None) -> int`

Appends both a `04_VALIDATION_LOG.md` entry **and** a worker-log entry
attributing it to `worker: validation`. Required: `--branch`, `--status`,
`--command`. Optional: `--commit`, `--jobs`, `--report`, `--failures`,
`--notes`.

### `append_validation(*, branch, status, command, ...) -> None`

Library-level entry.

---

## `scripts/generate_structured_capture_template.py`

### `main(argv: list[str] | None = None) -> int`

CLI for the Stage 4 CSV template. Default output:
`templates/structured_capture_template.csv`. Flags:
`--output PATH`, `--include-descriptions`, `--stdout`.

### `render_template(*, include_descriptions: bool) -> str`

Pure function that returns the rendered CSV text without writing
anything. Used by tests.

### `build_description_block() -> list[str]`

Returns the list of `#`-prefixed comment lines, one per Stage 4 field
plus group separators.

---

## Cross-References

- [FIELD_REFERENCE_GUIDE.md](FIELD_REFERENCE_GUIDE.md) — what each field means and where it comes from.
- [ARCHITECTURE.md](ARCHITECTURE.md) — pipeline diagram and module map.
- [VALIDATION_WORKFLOW.md](VALIDATION_WORKFLOW.md) — when to run which validation step.
- [README_MANUAL_REVIEW.md](../README_MANUAL_REVIEW.md) — manual review harness usage.
- [README_PROJECT_CONTROL.md](../README_PROJECT_CONTROL.md) — Project Control Center usage.
