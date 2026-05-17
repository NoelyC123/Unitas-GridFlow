# Matching Engine Root Cause Analysis

**Date:** 2026-05-17
**Issue:** `run_pipeline.py` returns 0/12 matched when
`validate_phase4_matching.py` returns 12/12 on identical inputs

---

## How Matching Is Supposed to Work

`run_pipeline.py` runs four stages:

1. **Stage 1 — Baseline Ingest:** `CSVParser.parse()` reads the baseline CSV and produces
   a `BaselineDataset` where each `BaselinePole` has `pole_id`, `support_no`, coordinates, etc.

2. **Stage 2 — Field Evidence Import:** `FolderScanner.scan()` scans the field evidence
   root and produces a `FieldDataset` where each `FieldPole` has `support_no` extracted
   from the folder name.

3. **Stage 3 — Matching:** `SupportNumberMatcher.match()` builds a lookup keyed on
   normalised `fp.support_no` for each field pole, then for each baseline pole tries to
   find it by normalising `bp.support_no`.

4. **Stage 4 — Merge:** `DataMerger.merge()` combines matched pairs into `MergedPole` records.

The intended matching key is `support_no` — the physical pole identification number on the
asset register and on the field plate.

---

## What Actually Happens with P_LOCAL_002

### Stage 1 — Baseline CSV format misdetection

P_LOCAL_002 baseline CSV columns:

```
pole_id,easting,northing,voltage,asset_type,status
```

`CSVParser.detect_format()` checks for:
- ENWL: looks for `ENID` and `Support No` columns → **NOT FOUND**
- TRIMBLE: looks for `Feature Code` and `Point ID` columns → **NOT FOUND**
- Falls through to **GENERIC**

`_parse_generic()` then tries to find a support number column:

```python
support_cols = [c for c in df.columns if "support" in c.lower() or "name" in c.lower()]
support_col = next((c for c in support_cols), None)
```

No column in `P_LOCAL_002_baseline.csv` contains "support" or "name". So:

```python
support_no = None   # for every single row
```

Every `BaselinePole` is created with `support_no = None`. The `pole_id` field correctly
receives the value from the `pole_id` CSV column (e.g., `"902202"`), but this is never
used for matching.

Additionally, `_parse_generic()` skips any row where easting or northing is blank:

```python
if easting is None or northing is None:
    continue
```

Poles 903101 and 903203 (blank coordinates) are **silently dropped** — they never appear
in the baseline dataset at all.

**Stage 1 result:** 10 `BaselinePole` objects, all with `support_no = None`.

---

### Stage 2 — Field evidence scan

`FolderScanner._extract_support_no()` correctly parses the folder name:

```python
parts = folder_name.split("_")  # ['01', 'SUPPORT', '902202']
candidate = parts[2]             # '902202'
```

For folders with descriptors (`11_SUPPORT_903202_LV_TEE_OFF`):
```python
parts = ['11', 'SUPPORT', '903202', 'LV', 'TEE', 'OFF']
candidate = parts[2]  # '903202' ✅
```

Field poles correctly get `support_no = "902202"`, `"903202"`, etc.

**However**, the scanner only reads `.txt` files as notes:

```python
NOTES_EXTENSIONS = {".txt", ".TXT"}
```

P_LOCAL_002 notes files are `pole_notes.md` (`.md` extension). None are read. All poles
get `notes_present = False` and `notes_content = None`.

**Stage 2 result:** 12 `FieldPole` objects with correct `support_no` values but
`notes_present = False` for all.

---

### Stage 3 — Matching fails completely

`SupportNumberMatcher.match()` builds the field lookup:

```python
field_by_normalized: dict[str, object] = {}
for fp in field_dataset.poles:
    key = self._normalize(fp.support_no)   # "902202", "902201", ...
    field_by_normalized[key] = fp
```

Field lookup is populated correctly: `{"902202": ..., "902201": ..., ...}`.

For each baseline pole:

```python
b_key = self._normalize(bp.support_no or "")
# bp.support_no is None for every pole
# bp.support_no or "" → ""
# _normalize("") → ""
# b_key = "" for every baseline pole
```

`_try_match()` then:
1. Tries `""` in `field_by_normalized` → **not found**
2. Tries stripping suffix: `re.sub(r"[A-Z]+$", "", "")` = `""` = `b_key` → condition
   `stripped != b_key` is False → no second attempt
3. Returns `UNMATCHED` for every pole

**Stage 3 result:** 0/10 matched. 100% UNMATCHED. This is the correct
(unfortunately) outcome given that `support_no = None` for all baseline poles.

---

## Why `validate_phase4_matching.py` Gets 12/12

`validate_phase4_matching.py` uses a completely different matching approach:

```python
# Load baseline as raw dict rows
baseline_rows = load_baseline(csv_path)  # csv.DictReader — no column remapping

# For each row, use pole_id directly as the lookup key
pole_id = str(baseline_row.get("pole_id", "")).strip()  # "902202"

# Build field index: support_number → folder_path
field_index = build_field_index(field_root)
# Parses folder names: "01_SUPPORT_902202" → "902202" → Path

# Match by pole_id (which IS the support number in this CSV)
folder = field_index.get(pole_id)  # "902202" → folder ✅
```

This works because:
- It reads the CSV as raw dicts (no column remapping)
- It uses `pole_id` directly as the matching key
- In P_LOCAL_002 baseline, `pole_id` values are the support numbers (`902202`, `902201`, ...)
- The field index parses folder names the same way as `validate_phase4_matching.py`

The two scripts happen to produce the same result because `pole_id` in the P_LOCAL_002
CSV equals the support number. The full pipeline makes this assumption invisible by trying
to use `support_no` (which is never set).

---

## Root Cause Summary

Four bugs, in order of severity:

### Bug 1 — CRITICAL: GENERIC parser does not detect `pole_id` as support number

**File:** `gridflow/baseline/csv_parser.py`, `_parse_generic()`

**Problem:** When no column named "support" or "name" is found, `support_no` is set to
`None`. The P_LOCAL_002 CSV uses `pole_id` as the support number column.

**Effect:** Every baseline pole has `support_no = None`. Matching fails for 100% of poles.

---

### Bug 2 — CRITICAL: Matcher never falls back to `pole_id`

**File:** `gridflow/matching/support_number_matcher.py`, `_try_match()`

**Problem:** Only `bp.support_no` is used for matching. When `support_no` is `None`,
`b_key = ""` and no match is possible. `bp.pole_id` is never tried.

**Effect:** 0% match rate when `support_no` is None, even if `pole_id` would match.

---

### Bug 3 — MEDIUM: Blank-coordinate rows silently dropped

**File:** `gridflow/baseline/csv_parser.py`, `_parse_generic()` and `_parse_enwl()`

**Problem:** Rows where easting or northing is blank are silently skipped. This drops
903101 and 903203 entirely from the baseline dataset.

**Effect:** Even if matching were fixed, only 10/12 poles would be matchable. The two
poles without coordinates never receive `baseline_coordinate_missing` flags because they
don't exist in the dataset.

---

### Bug 4 — MEDIUM: Notes scanner misses `.md` files

**File:** `gridflow/field/folder_scanner.py`

**Problem:** `NOTES_EXTENSIONS = {".txt", ".TXT"}` — `.md` files are not included.

**Effect:** All P_LOCAL_002 poles show `notes_present = False` and `notes_content = None`,
degrading match confidence scoring and preventing note content from reaching the merged output.

---

## Recommended Fix Approach

### Fix 1 (Critical): Teach the GENERIC parser to fall back to `pole_id` as `support_no`

In `_parse_generic()`, after the support column search, if no support column is found,
check whether `pole_id` values look like support numbers (all digits or digits+letters):

```python
if not support_col:
    # Fall back: use pole_id as support_no if it looks numeric
    support_col = id_col  # use the same column as pole_id
```

### Fix 2 (Critical): Add `pole_id` fallback to the matcher

In `SupportNumberMatcher._try_match()`, add a third attempt using `baseline_pole.pole_id`
when `bp.support_no` is absent:

```python
# Attempt 3: fall back to pole_id if support_no was not set
if not bp.support_no:
    fid_key = self._normalize(baseline_pole.pole_id)
    if fid_key in field_by_normalized:
        fp = field_by_normalized[fid_key]
        return MatchResult(..., match_type="EXACT",
                           confidence_reasons=["POLE_ID_FALLBACK"])
```

### Fix 3 (Medium): Include blank-coordinate rows with a warning flag

In both `_parse_enwl()` and `_parse_generic()`, remove the `continue` for blank
coordinates. Instead, include the pole and let `verification_flag_generator.py` set
`baseline_coordinate_missing = True`.

### Fix 4 (Medium): Add `.md` to notes extensions

In `folder_scanner.py`:
```python
NOTES_EXTENSIONS = {".txt", ".TXT", ".md", ".MD"}
```
