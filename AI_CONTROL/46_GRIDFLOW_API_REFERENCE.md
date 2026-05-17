# GridFlow API Reference

**Version:** Post-commit 8afeee0 (4 critical bugs fixed)
**Date:** 2026-05-17
**Validation:** P_LOCAL_002 — 12/12 parsed, 12/12 matched, 12/12 notes, 1464 tests passing

All signatures and field names in this document are taken directly from the production code.

---

## `gridflow.baseline.csv_parser.CSVParser`

### Purpose

Parse baseline CSV files from DNO systems into `BaselineDataset` objects. Handles ENWL,
Trimble, and Generic formats with automatic detection.

### `detect_format(csv_path: Path) -> str`

Detect CSV format from column headers.

**Returns:** `"ENWL"` | `"TRIMBLE"` | `"GENERIC"`

- ENWL detected by: `ENID` + `Support No` columns
- TRIMBLE detected by: `Feature Code` + `Point ID` columns
- Generic: fallback for all other column layouts (including P_LOCAL_002)

---

### `parse(csv_path: Path, format_hint: Optional[str] = None) -> BaselineDataset`

Parse a baseline CSV file.

**Parameters:**
- `csv_path` — `Path` to baseline CSV
- `format_hint` — `"ENWL"` | `"TRIMBLE"` | `"GENERIC"` | `None` (auto-detect)

**Returns:** `BaselineDataset`

**Raises:**
- `FileNotFoundError` — CSV not found
- `ValueError` — CSV is empty or missing required columns

**Key behaviour (post-8afeee0):**
- All three parser paths (`_parse_enwl`, `_parse_trimble`, `_parse_generic`) now fall back
  to `pole_id` when no explicit support number column is found:
  `support_no = str(row.get("Support No", "")).strip() or pole_id`
- Rows with blank easting/northing are **included** (not dropped) with
  `metadata["coordinate_status"] = "MISSING"`

**Example:**

```python
from pathlib import Path
from gridflow.baseline.csv_parser import CSVParser

parser = CSVParser()
dataset = parser.parse(Path("P_LOCAL_002_baseline.csv"))

print(f"Poles parsed: {dataset.pole_count}")
for pole in dataset.poles:
    print(f"  {pole.support_no}: {pole.metadata.get('coordinate_status')}")
```

---

## `gridflow.baseline.models.BaselinePole`

Pydantic model for a single parsed baseline pole.

**Key fields:**

```python
pole_id: str                    # Primary identifier from CSV (e.g. "902202")
support_no: Optional[str]       # Support number; falls back to pole_id after fix
easting: Optional[float]        # OSGB36 easting (None when coordinate_status=MISSING)
northing: Optional[float]       # OSGB36 northing (None when coordinate_status=MISSING)
latitude: Optional[float]       # WGS84 latitude (populated after transformation)
longitude: Optional[float]      # WGS84 longitude
voltage_level: VoltageLevel     # LV / HV / EHV / UNKNOWN enum
asset_type: AssetType           # POLE / TOWER / COLUMN / UNKNOWN enum
status: AssetStatus             # IN_SERVICE / DECOMMISSIONED / PLANNED / UNKNOWN enum
metadata: dict                  # {"coordinate_status": "COMPLETE" | "MISSING", ...}
```

**Note:** `coordinate_status` is stored in `metadata`, not as a top-level field.

---

## `gridflow.baseline.models.BaselineDataset`

Container for all parsed baseline poles.

**Key fields:**

```python
poles: list[BaselinePole]
metadata: dict                  # {"format": ..., "total_rows": ..., "parsed_poles": ...}
```

**Key methods:**

```python
dataset.pole_count              # property: len(poles)
dataset.get_by_pole_id(id)      # → Optional[BaselinePole]
dataset.get_by_support_no(no)   # → Optional[BaselinePole]
dataset.has_coordinates()       # → bool: True if all poles have OSGB36 coords
```

---

## `gridflow.field.folder_scanner.FolderScanner`

### Purpose

Scan a field evidence directory tree and produce a `FieldDataset`.

### Configuration constants

```python
NOTES_EXTENSIONS = {".txt", ".TXT", ".md", ".MD"}   # Bug 4 fix: .md added
PHOTO_EXTENSIONS = {".jpeg", ".jpg", ".heic", ".JPEG", ".JPG", ".HEIC"}
SCREENSHOT_EXTENSIONS = {".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"}
```

### Expected directory structure

```
enwl_enrichment_clean/
  01_SUPPORT_902202/
    field_photos/         → counted as field photos
    enwl_screenshots/     → counted as screenshots (stored in screenshot_paths)
    map_screenshots/      → counted as map screenshots
    notes/
      pole_notes.md       → detected (post-fix) + read as notes_content
  02_SUPPORT_902201/
    ...
  11_SUPPORT_903202_LV_TEE_OFF/
    ...
```

Folder pattern: `NN_SUPPORT_{support_no}[_DESCRIPTOR...]`

### `scan(dataset_path: str | Path) -> FieldDataset`

**Parameters:**
- `dataset_path` — root folder containing `NN_SUPPORT_*` subdirectories

**Returns:** `FieldDataset`

**Raises:**
- `FileNotFoundError` — directory not found

**Support number extraction:**
```
"01_SUPPORT_902202"              → support_no = "902202"
"11_SUPPORT_903202_LV_TEE_OFF"   → support_no = "903202"  (parts[2] of "_" split)
"12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT" → support_no = "903203"
```

**Example:**

```python
from gridflow.field.folder_scanner import FolderScanner

scanner = FolderScanner()
dataset = scanner.scan("real_pilot_data/P_LOCAL_002/enwl_enrichment_clean")

print(f"Poles scanned: {dataset.total_poles}")
for pole in dataset.poles:
    print(f"  {pole.support_no}: {pole.field_photo_count} photos, notes={pole.notes_present}")
```

---

## `gridflow.field.models.FieldPole`

Pydantic model for one scanned field evidence folder.

**Key fields:**

```python
folder_name: str                # Full folder name e.g. "01_SUPPORT_902202"
support_no: str                 # Extracted from parts[2] of folder name
sequence_no: Optional[int]      # Leading NN from folder name
voltage_category: str           # "LV" | "HV" | "EHV" | "UNKNOWN"
pole_descriptor: Optional[str]  # Descriptor after voltage e.g. "TEE_OFF"
field_photo_count: int          # Files in field_photos/
map_screenshot_count: int       # Files in map_screenshots/
notes_present: bool             # True if any NOTES_EXTENSIONS file found in notes/
notes_content: Optional[str]    # Raw text of first notes file (None if absent)
parsed_notes: dict              # Output of NotesParser.parse(notes_content)
evidence_quality: str           # "HIGH" | "MEDIUM" | "LOW" (set by scorer)
special_flags: list[str]        # "NO_POLE_POPUP", "VARIANT_SUPPORT_NO", etc.
photo_paths: list[str]          # Relative paths to field photos
screenshot_paths: list[str]     # Relative paths to map screenshots
notes_path: Optional[str]       # Relative path to notes file
```

---

## `gridflow.matching.support_number_matcher.SupportNumberMatcher`

### Purpose

Match `BaselinePole` records to `FieldPole` records by support number.

### `match(baseline_dataset: BaselineDataset, field_dataset: FieldDataset) -> list[MatchResult]`

**Parameters:**
- `baseline_dataset` — output of `CSVParser.parse()`
- `field_dataset` — output of `FolderScanner.scan()`

**Returns:** `list[MatchResult]` — one entry per baseline pole

**Algorithm (post-8afeee0):**

```python
# Field lookup: normalized support_no → FieldPole
field_by_normalized = {_normalize(fp.support_no): fp for fp in field_dataset.poles}

for bp in baseline_dataset.poles:
    # Bug 2 fix: use pole_id when support_no absent
    support_no = bp.support_no or bp.pole_id
    b_key = _normalize(support_no)

    # Attempt 1: exact normalized match
    # Attempt 2: strip trailing letter suffix (900342A → 900342)
    # Otherwise: UNMATCHED
```

**Normalisation (`_normalize`):**
- Strip whitespace, uppercase
- Strip DNO prefixes (`SP`, `EN`, `WP`, `NO`, `YK`) when followed by digits

**Example:**

```python
from gridflow.matching.support_number_matcher import SupportNumberMatcher

matcher = SupportNumberMatcher()
results = matcher.match(baseline_dataset, field_dataset)

matched = sum(1 for r in results if r.match_type != "UNMATCHED")
print(f"Matched: {matched}/{len(results)}")
```

---

## `gridflow.matching.models.MatchResult`

```python
baseline_pole_id: str
baseline_support_no: str
field_folder: Optional[str]     # None when UNMATCHED
field_support_no: Optional[str]
match_type: str                 # "EXACT" | "UNMATCHED"
match_confidence: str           # "HIGH" | "MEDIUM" | "LOW" | "UNMATCHED"
confidence_reasons: list[str]   # e.g. ["VARIANT_SUFFIX_STRIPPED"]
```

---

## `gridflow.readiness.assessor.ReadinessAssessor`

### Purpose

Assess design-readiness from combined evidence (Stage 6A–6E stack). Requires ENWL trace
GeoJSON. Part of the Stage 6 pipeline — not called directly by `run_pipeline.py`.

### Status levels

| Status | Meaning | `design_ready` |
|---|---|---|
| `"ready"` | Identity linked, no critical conflicts, conductor span-confirmed | `True` |
| `"review_required"` | Identity linked, conductor route-level only | `False` |
| `"not_ready"` | Missing photos, pole class, or no conductor evidence | `False` |
| `"insufficient_evidence"` | Identity incomplete or linking confidence NONE/LOW | `False` |

### `assess_pole(survey_root, pole_folder_name, trace_path) -> ReadinessResult`

**Parameters:**
- `survey_root` — e.g., `"real_pilot_data/P_LOCAL_002"`
- `pole_folder_name` — e.g., `"05_SUPPORT_900344"`
- `trace_path` — ENWL trace GeoJSON path

**Returns:** `ReadinessResult`

### `assess_from_records(combined, linking, conflicts) -> ReadinessResult`

Lower-level method taking pre-computed inputs from Stage 6B combiner, 6C linker,
and 6D conflict detector.

### `ReadinessResult` fields

```python
pole_id: str
support_no: Optional[str]
design_ready: bool
readiness_status: str               # "ready" | "review_required" | "not_ready" | "insufficient_evidence"
readiness_confidence: str           # "high" | "medium" | "low" | "none"
readiness_reason: str               # Human-readable explanation
readiness_blockers: list[str]       # Specific actionable blockers
readiness_warnings: list[str]       # Non-blocking warnings
linking_confidence: str             # From Stage 6C linker
conflict_count: int
critical_conflicts: int
```

---

## `scripts/run_pipeline.py`

### Usage

```bash
python scripts/run_pipeline.py \
  --baseline <path/to/baseline.csv> \
  --field    <path/to/evidence_folder/> \
  --output   <output_directory/> \
  [--baseline-format AUTO|ENWL|TRIMBLE|GENERIC] \
  [--log-level DEBUG|INFO|WARNING|ERROR] \
  [--job-id <name>] \
  [--register] \
  [--overwrite-registration] \
  [--no-coord-transform] \
  [--no-route-reconstruct] \
  [--strict]
```

### Output files

All files are written to `<output>/pipeline_run_<YYYY-MM-DD_HHMMSS>/`:

```
pipeline_run_*/
  pipeline_summary.json        ← run metadata, match_rate, overall_status
  01_baseline_dataset.json
  02_field_dataset.json
  03_match_register.json
  03_match_register.csv
  04_merged_dataset.json
  04_merged_dataset.csv
  05_qa_report.md
  00_pilot_output_pack_index.md
  06_dno_data_request.md
  07_design_readiness_summary.md
  08_match_confidence_analysis.md
  09_verification_flags_breakdown.md
  10_evidence_provenance_log.md
```

### Status logic (post-fix)

`overall_status = "PARTIAL"` when any of:
- Baseline validation errors > 0
- Parsed pole count < source CSV row count
- Notes present == 0 with field poles present
- Matched count == 0 with both sides populated
- Merged total == 0 after matching succeeded

Otherwise `"PASS"`.

### P_LOCAL_002 example

```bash
python scripts/run_pipeline.py \
  --baseline real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv \
  --field    real_pilot_data/P_LOCAL_002/enwl_enrichment_clean \
  --output   validation_runs/plocal002 \
  --job-id   P_LOCAL_002 \
  --register
```

**Expected output:**
```
Stage 1/4 — Baseline Ingest...
  Format detected: GENERIC
  Poles loaded: 12
  ✓ Complete

Stage 2/4 — Field Evidence Import...
  Poles scanned: 12
  Notes parsed: 12/12
  Evidence quality: 12 HIGH / 0 MEDIUM / 0 LOW
  ✓ Complete

Stage 3/4 — Baseline-to-Field Matching...
  Matched: 12/12 poles
  Match rate: 100.0%
  Confidence: 12 HIGH / 0 MEDIUM / 0 LOW
  ✓ Complete

Stage 4/4 — Merge + QA Analysis...
  Merged poles: 12
  Design ready: 0 poles
  Design blocked: 12 poles (DNO data required)
  ✓ Complete

Overall status:  PARTIAL
Match rate:      100.0%
Design ready:    0/12 poles
Design blocked:  12/12 poles (DNO data required)
```

---

## `gridflow.merge.models.MergedPole`

Flat Pydantic model combining baseline + field + matching evidence per pole.

**Identity fields:**
```python
support_no: str
pole_id: Optional[str]
folder_name: Optional[str]
match_confidence: str           # "HIGH" | "MEDIUM" | "LOW" | "UNMATCHED"
match_type: str
```

**Coordinates:**
```python
easting: Optional[float]
northing: Optional[float]
latitude: Optional[float]
longitude: Optional[float]
route_id: Optional[str]
pole_sequence: Optional[int]
```

**Field evidence:**
```python
condition_overall: Optional[str]
defects: list[str]
equipment_observed: list[str]
field_photo_count: int
notes_content: Optional[str]
parsed_notes: dict
special_flags: list[str]
```

**Verification flags:**
```python
voltage_verification_required: bool = True
conductor_verification_required: bool = True
pole_class_verification_required: bool = True
condition_verification_required: bool = False
identity_verification_required: bool = False
equipment_conflict_flag: bool = False
```

**Design status:**
```python
design_blocked: bool = True
design_ready: bool = False
designer_actions: list[str]     # Specific actionable items
```
