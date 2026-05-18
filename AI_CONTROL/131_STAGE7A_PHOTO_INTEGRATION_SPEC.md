# Stage 7A — Photo Integration Specification

**Date:** 2026-05-18
**Branch:** `codex/stage7a-photo-integration` (backend) + `claude-code/stage7a-photo-spec` (spec)
**Status:** Spec only — no runtime code changed

---

## Purpose

Make field photos accessible to the workspace pole detail page and CLI tooling.
Currently the workspace shows `field_photo_count: 9` (a bare integer). Designers cannot
see the actual photos without manually navigating the local file system.

Stage 7A builds the photo-loading backend. Stage 7B adds workspace display.

---

## Current State

- Field photos exist in every pole folder under `field_photos/`
- P_LOCAL_002 has 99 photos across 12 poles (ranging from 6 to 14 per pole)
- `MergedPole.field_photo_count` is an integer count only
- `MergedPole.photo_paths` field exists in the model but is not surfaced in the workspace
- The workspace pole detail page shows only "Photos: 9" (no filenames, no images)
- The job registration step (`gridflow/registration.py`) copies only the pipeline run
  directory — field evidence folders are NOT included in `uploads/jobs/<job_id>/`

### P_LOCAL_002 Photo Inventory

| Pole | Folder | Photos |
|---|---|---|
| 01 | `01_SUPPORT_902202` | 6 |
| 02 | `02_SUPPORT_902201` | 10 |
| 03 | `03_SUPPORT_900343` | 7 |
| 04 | `04_SUPPORT_900342A` | 7 |
| 05 | `05_SUPPORT_900344` | 9 |
| 06 | `06_SUPPORT_900345` | 14 |
| 07 | `07_SUPPORT_903104` | 9 |
| 08 | `08_SUPPORT_903103` | 7 |
| 09 | `09_SUPPORT_903102` | 8 |
| 10 | `10_SUPPORT_903101` | 9 |
| 11 | `11_SUPPORT_903202_LV_TEE_OFF` | 7 |
| 12 | `12_SUPPORT_903203_LV_TERMINAL_STREET_LIGHT` | 6 |
| **Total** | | **99** |

---

## Important Constraint: Filename Patterns

All P_LOCAL_002 filenames are sequential camera numbers:
`IMG_0903.JPG`, `IMG_0904.JPG`, ..., `IMG_0946.JPG`

No descriptive text in filenames (no "top", "base", "equipment", etc.).

The photo type detection logic must handle this gracefully:
- If no pattern matches any filename, classify the **first file** in the folder as
  `full_pole` and the rest as `unknown`
- Do not force a type onto a photo that has no evidence for it
- Never fail or error on unrecognised filenames

The named-pattern detection (`*top*`, `*base*`, `*equipment*`, etc.) is forward-looking
for future jobs that use descriptive filenames. For P_LOCAL_002 it will classify all but
the first photo as `unknown`.

---

## Stage 7A Scope

### In scope

- `gridflow/photos/__init__.py` and `gridflow/photos/loader.py` — backend photo loader
- `scripts/list_pole_photos.py` — CLI photo listing per pole and across all poles
- Update `gridflow/evidence_combiner/combiner.py` to add `photo_count` and
  `photo_types_present` to the combined evidence record
- `tests/test_photo_loader.py` — tests for loader

### Out of scope — Stage 7A

- Workspace display (no template changes, no route changes)
- Photo upload, editing, or annotation
- Thumbnail generation or image processing
- EXIF/metadata extraction
- Lightbox or gallery UI components
- Any changes to `app/` routes
- Any changes to `app/templates/`

---

## Photo Type Classification

### Detection priority (applied in order)

| Priority | Type | Filename patterns |
|---|---|---|
| 1 | `pole_top` | `*top*`, `*pole_top*`, `*poletop*` (case-insensitive) |
| 2 | `pole_base` | `*base*`, `*pole_base*`, `*foundation*` |
| 3 | `equipment` | `*equipment*`, `*transformer*`, `*switch*`, `*abs*` |
| 4 | `span` | `*span*`, `*conductor*`, `*wire*` |
| 5 | `context` | `*context*`, `*overview*`, `*access*`, `*surroundings*` |
| 6 | `full_pole` | First file in folder alphabetically when no patterns match |
| 7 | `unknown` | All remaining files when no patterns match |

### Purpose per type

| Type | Purpose | Typical count |
|---|---|---|
| `full_pole` | Overall pole condition, whole structure visible | 1 |
| `pole_top` | Crossarms, insulators, conductors, top equipment | 1–2 |
| `pole_base` | Foundation, ground contact, lower pole condition | 1 |
| `equipment` | Transformer, switch, ABS, links, fuse | 1–3 |
| `span` | Overhead conductors, stays, stay anchors | 1–2 |
| `context` | Access route, surrounding land, landmarks | 1–2 |
| `unknown` | Unclassified (common with sequential filenames) | varies |

---

## Data Schemas

### `PhotoFile`

```python
@dataclass(frozen=True)
class PhotoFile:
    filename: str           # e.g. "IMG_0903.JPG"
    filepath: Path          # absolute path to file
    photo_type: str         # full_pole | pole_top | pole_base | equipment | span | context | unknown
    size_bytes: int         # file size in bytes
    exists: bool            # True if file exists at filepath
```

### `PhotoSet`

```python
@dataclass(frozen=True)
class PhotoSet:
    pole_id: str            # folder name e.g. "05_SUPPORT_900344"
    pole_folder_path: Path  # absolute path to the pole folder
    photo_files: list[PhotoFile]

    @property
    def count(self) -> int: ...
    def by_type(self, photo_type: str) -> list[PhotoFile]: ...
    def type_summary(self) -> dict[str, int]: ...  # {"full_pole": 1, "unknown": 8, ...}
```

---

## Loader API

### `load_pole_photos(pole_folder_path: Path) -> PhotoSet`

Scans `pole_folder_path/field_photos/` and returns a `PhotoSet`. Returns an empty
`PhotoSet` if the folder does not exist or contains no supported image files.

Never raises on missing folders. Logs a warning and returns empty.

### `load_survey_photos(survey_root: Path) -> dict[str, PhotoSet]`

Scans all `NN_SUPPORT_*` subfolders under `survey_root/enwl_enrichment_clean/` and
returns a dict mapping `pole_id` → `PhotoSet`.

### Supported extensions

`{".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG", ".heic", ".HEIC"}`

---

## CLI: `scripts/list_pole_photos.py`

### Single pole

```bash
python3 scripts/list_pole_photos.py \
  --survey real_pilot_data/P_LOCAL_002 \
  --pole 05_SUPPORT_900344
```

Expected output:
```
Pole: 05_SUPPORT_900344
Photos: 9
  IMG_0903.JPG  full_pole   88 KB
  IMG_0904.JPG  unknown     142 KB
  IMG_0905.JPG  unknown     156 KB
  IMG_0906.JPG  unknown     203 KB
  IMG_0907.JPG  unknown     189 KB
  IMG_0908.JPG  unknown     215 KB
  IMG_0909.JPG  unknown     178 KB
  IMG_0910.JPG  unknown     201 KB
  IMG_0911.JPG  unknown     167 KB
```

(All files appear as `unknown` / `full_pole` because sequential filenames carry no type signal.)

### All poles

```bash
python3 scripts/list_pole_photos.py \
  --survey real_pilot_data/P_LOCAL_002 \
  --all
```

Expected output (Markdown table):

```
| Pole                                   | Photos | full_pole | pole_top | pole_base | equipment | span | context | unknown |
|----------------------------------------|--------|-----------|----------|-----------|-----------|------|---------|---------|
| 01_SUPPORT_902202                      |      6 |         1 |        0 |         0 |         0 |    0 |       0 |       5 |
| 02_SUPPORT_902201                      |     10 |         1 |        0 |         0 |         0 |    0 |       0 |       9 |
...
| Total                                  |     99 |        12 |        0 |         0 |         0 |    0 |       0 |      87 |
```

---

## Evidence Combiner Update

Add to the combined evidence record in `gridflow/evidence_combiner/combiner.py`:

```json
{
  "photo_count": 9,
  "photo_types_present": ["full_pole", "unknown"],
  "photos_available": true,
  "photo_summary": {
    "full_pole": 1,
    "unknown": 8
  }
}
```

`photos_available` is `True` when `photo_count > 0`. The combiner calls
`load_pole_photos()` from `gridflow.photos.loader` to populate this.

**Design-readiness caution:** Photo evidence informs evidence quality but does not
directly affect `design_ready`. The readiness assessor already counts photos
(`photo_count >= 3` is one of its checks). The combiner addition is provenance enrichment,
not a readiness change.

---

## Tests: `tests/test_photo_loader.py`

| Test | What it verifies |
|---|---|
| `test_load_pole_photos_returns_correct_count` | P_LOCAL_002 Pole 05: returns 9 photos |
| `test_load_pole_photos_first_photo_is_full_pole` | First IMG_*.JPG in folder → `full_pole` |
| `test_load_pole_photos_remaining_are_unknown` | Remaining sequential filenames → `unknown` |
| `test_load_pole_photos_with_descriptive_filename` | `*_top_*` → `pole_top` (fixture) |
| `test_load_pole_photos_missing_folder_returns_empty` | Non-existent path → empty PhotoSet |
| `test_load_pole_photos_empty_folder_returns_empty` | Folder with no images → empty PhotoSet |
| `test_load_survey_photos_returns_all_poles` | P_LOCAL_002 → 12 PhotoSets |
| `test_load_survey_photos_total_count` | Sum across all poles = 99 |
| `test_photo_file_size_bytes_populated` | `size_bytes > 0` for real files |
| `test_photo_set_type_summary` | Summary dict has correct type counts |
| `test_combined_evidence_includes_photo_count` | Combiner output has `photo_count: 9` |
| `test_combined_evidence_photos_available_flag` | `photos_available: true` when photos exist |

---

## Architectural Note: Workspace Photo Serving (Stage 7B Blocker)

Photos are in `real_pilot_data/` (local-only, gitignored). The registered job directory
(`uploads/jobs/<job_id>/`) does not contain photos. The workspace cannot display photos
without one of the following:

**Option A — Flask photo-serving route (recommended for Stage 7B):**
Add a route `/photos/<job_id>/<pole_folder>/<filename>` that reads from the original
field evidence path, stored in the job's `02_field_dataset.json` (which records
`dataset_path`). The route would read `dataset_path` + `/field_photos/<filename>`.

**Option B — Copy photos during registration:**
Modify `gridflow/registration.py` to also copy the field evidence folder. High disk
cost (99 photos per job).

**Option C — Symlink:**
Registration creates a symlink from `uploads/jobs/<job_id>/field_evidence/` →
original evidence path. Fast but fragile on Windows.

Stage 7A (backend loader + CLI) does not need to solve this — it works directly with local
paths. Stage 7B must choose and implement one of these options before photos can appear in
the workspace.

---

## Acceptance Criteria — Stage 7A

| Criterion | Requirement |
|---|---|
| Photo loader works on P_LOCAL_002 | `load_pole_photos(pole_05_path)` returns 9 photos |
| All 12 poles detected | `load_survey_photos()` returns 12 PhotoSets |
| Photo types classified | First photo `full_pole`, rest `unknown` for sequential filenames |
| Graceful failure | Missing folder returns empty PhotoSet, no exception |
| Combined evidence updated | `photo_count`, `photo_types_present`, `photos_available` present |
| CLI works | `list_pole_photos.py --all` prints table for all 12 poles |
| Tests pass | All tests in `test_photo_loader.py` pass |
| No workspace changes | `app/templates/` and `app/routes/` unchanged |
| `pytest -q` passes | No regressions |
