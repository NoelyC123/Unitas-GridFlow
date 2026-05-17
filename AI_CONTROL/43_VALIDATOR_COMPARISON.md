# Validator Comparison: Working vs Broken

**Date:** 2026-05-17
**Working:** `scripts/validate_phase4_matching.py` — 12/12 match
**Broken:** `scripts/run_pipeline.py` — 0/10 match
**Input:** Same P_LOCAL_002 baseline CSV and evidence folders

---

## How `validate_phase4_matching.py` Achieves 12/12

### Baseline loading

```python
def load_baseline(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    return rows
```

Reads the CSV as raw dicts. No column remapping. No format detection. The `pole_id`
column value (`"902202"`, `"902201"`, etc.) is preserved as-is.

### Field index

```python
def build_field_index(field_root: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for child in sorted(field_root.iterdir()):
        if not child.is_dir():
            continue
        parts = child.name.split("SUPPORT_", 1)
        if len(parts) != 2:
            continue
        support_suffix = parts[1]
        pole_id = support_suffix.split("_", 1)[0].strip()
        if pole_id:
            index[pole_id] = child
    return index
```

Splits on `"SUPPORT_"` and takes the first token of the remainder:
- `"01_SUPPORT_902202"` → suffix `"902202"` → key `"902202"` ✅
- `"11_SUPPORT_903202_LV_TEE_OFF"` → suffix `"903202_LV_TEE_OFF"` → key `"903202"` ✅
- `"12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT"` → suffix `"903203_LV..."` → key `"903203"` ✅

### Matching

```python
def validate_pole(baseline_row, field_index):
    pole_id = str(baseline_row.get("pole_id", "")).strip()
    folder = field_index.get(pole_id)
```

Uses `pole_id` from the CSV row directly as the lookup key. In P_LOCAL_002 baseline, the
`pole_id` column values ARE the support numbers. The lookup succeeds because `"902202"` →
folder is exactly what `field_index` contains.

**Why it works:** Both sides use the raw support number string without going through a
model layer that might lose the value.

---

## How `run_pipeline.py` Achieves 0/10

### Stage 1 — Baseline ingest loses the support number

`CSVParser.detect_format()` reads column headers. P_LOCAL_002 CSV has:
`pole_id, easting, northing, voltage, asset_type, status`

Neither `ENID`+`Support No` (ENWL) nor `Feature Code`+`Point ID` (TRIMBLE) is found.
Format detected: **GENERIC**.

`_parse_generic()` searches for the support number column:
```python
support_cols = [c for c in df.columns if "support" in c.lower() or "name" in c.lower()]
support_col = next((c for c in support_cols), None)  # → None
```

No match. `support_no = None` for every baseline pole created.

The `pole_id` column is read correctly into `BaselinePole.pole_id`, but this field is
**never used for matching**.

### Stage 2 — Field scan works correctly

`FolderScanner._extract_support_no()` correctly extracts support numbers from folder names.
The `FieldPole.support_no` values are correct: `"902202"`, `"903202"`, etc.

### Stage 3 — Matching fails

`SupportNumberMatcher` builds the field lookup keyed on `fp.support_no` (correct values).
For each baseline pole it computes:

```python
b_key = self._normalize(bp.support_no or "")
# bp.support_no = None → bp.support_no or "" = "" → _normalize("") = ""
```

`b_key = ""` for every baseline pole. The lookup finds nothing. Every pole returns
`UNMATCHED`.

---

## Key Algorithmic Differences

| Aspect | `validate_phase4_matching.py` | `run_pipeline.py` |
|---|---|---|
| Baseline reading | `csv.DictReader` — raw row dicts | `CSVParser` — format detection + model mapping |
| Support number source | `baseline_row["pole_id"]` directly | `bp.support_no` from model |
| Format detection | None — reads all columns as-is | Detects ENWL / TRIMBLE / GENERIC |
| Generic column mapping | N/A | Looks for "support" or "name" column |
| Field index key | `folder_name.split("SUPPORT_", 1)[1].split("_", 1)[0]` | `_normalize(fp.support_no)` |
| Matching key | `pole_id` from CSV row | `bp.support_no` from model |
| Notes reading | N/A | Only `.txt` files (misses `.md`) |
| Coordinate gaps | Allowed (no skip) | Rows skipped if easting/northing blank |

---

## Why One Works and the Other Doesn't

The working validator (`validate_phase4_matching.py`) is purpose-built for the P_LOCAL_002
baseline format. It makes no assumptions about column naming — it just reads `pole_id`
directly. The field index parsing is also direct: split on `"SUPPORT_"`, take the first token.

The broken pipeline (`run_pipeline.py`) is built for generality across multiple DNO formats.
That generality introduces a format-detection layer that fails to recognise the P_LOCAL_002
baseline format (which has column name `pole_id`, not `ENID` or `Support No`). When format
detection fails to GENERIC, the support number column cannot be identified, so every baseline
pole gets `support_no = None`. The matcher only uses `support_no`, so 100% of poles go
unmatched.

The two scripts coincidentally produce different results because `pole_id` in the P_LOCAL_002
CSV happens to equal the support number. The full pipeline does not exploit this coincidence;
it only matches on `support_no`.

---

## Can `run_pipeline.py` Use `validate_phase4_matching.py` Logic?

**Partially — but not by wholesale replacement.**

`validate_phase4_matching.py` is a structural gate only. It confirms:
- Does a folder exist for each baseline pole?
- How many photos, screenshots, notes are present?
- Was evidence complete or incomplete?

It does not:
- Parse notes content
- Score evidence quality
- Produce merged records
- Generate QA reports
- Detect verification flags
- Create the 10 standard report files

The full pipeline must continue to use the `gridflow/` module stack. The fix is to repair
the two specific bugs in the pipeline:

1. Make `CSVParser` GENERIC format recognise `pole_id` as a support number column when
   no "support" or "name" column exists.
2. Add a `pole_id` fallback in `SupportNumberMatcher._try_match()` when `support_no`
   is absent.

These are surgical, low-risk changes that bring the full pipeline into alignment with
what `validate_phase4_matching.py` already does correctly.
