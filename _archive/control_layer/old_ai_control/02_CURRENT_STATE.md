# Current State — Deeper Technical Reference

This file holds technical detail that doesn't belong in the master truth file.
It does NOT repeat facts that change often (test counts, check-type counts, priorities) — those
live in `00_MASTER_SOURCE_OF_TRUTH.md`.

---

## MVP flow

**upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs**

### Working parts
- `/upload` page
- `/api/presign`
- CSV upload/save to job folder
- `/api/import/<job_id>` — selects rulepack by DNO, runs QA, writes outputs
- `issues.csv` output
- `map_data.json` output
- `/map/view/<job_id>`
- `/pdf/qa/<job_id>`
- `/jobs/`
- `/health/full`

### Job output contract

Successful jobs create:
- `uploads/jobs/<job_id>/meta.json`
- `uploads/jobs/<job_id>/<uploaded_csv>.csv`
- `uploads/jobs/<job_id>/issues.csv`
- `uploads/jobs/<job_id>/map_data.json`

---

## Real survey input — confirmed state (21 April 2026)

Real survey-origin files from Electricity Worx are now confirmed and available for testing.

### What has been reviewed

- Three real Trimble CSV exports: jobs 4-474, 474c, 513 (all Northern Ireland, Strabane area)
- One Trimble binary `.job` file (474c) — proprietary format, not a practical intake target
- ArcGIS/SpatialNI design print confirming TM65 Irish Grid coordinate system
- PoleCAD-style design drawing with annotated work instructions
- Handwritten field notebook sketches (jobs 5/474 and 513)

Full analysis: `PROJECT_SYNTHESIS/05_SUPPORT_NOTES/REAL_SURVEY_INPUT_ANALYSIS.md`

### Critical finding — current intake schema does not match real data

The current sample CSV and normalisation logic assume a flat named-column schema:
```
asset_id, structure_type, height_m, material, location_name, easting, northing, latitude, longitude
```

Real Trimble CSV exports use a completely different variable-width, feature-coded format:
```
Job:28-14 4-474,Version:24.00,Units:Metres          ← job header row
PRS485572899536,219497.298,413575.610,118.985,       ← base station row
point_id, easting, northing, height, feature_code, [feature_code]:STRING, string_number,
[feature_code]:TAG, tag_value, [feature_code]:REMARK, remark_text,
[feature_code]:LAND USE, land_use[, [feature_code]:HEIGHT, feature_height]
```

Feature codes observed: `Pol`, `Angle`, `EXpole`, `Fence`, `Wall`, `Road`, `Track`, `Hedge`,
`Tree`, `LVxing`, `BTxing`, `Ignore`.

**The current intake normalisation layer cannot process real survey files without rework.**

### Critical finding — NI coordinate projection is wrong in current code

All three real CSV files use Irish Grid coordinates (TM65 / EPSG:29902 or ITM / EPSG:2157):
- Eastings: ~242,000–245,000
- Northings: ~402,000–413,000
- Confirmed by ArcGIS print: "Coordinate System: TM65 Irish Grid"

The current `coord_consistency` check converts lat/lon to OSGB27700 (EPSG:27700 — British
National Grid). **This is the wrong projection for Northern Ireland data.** The NIE_11kV
rulepack's coord_consistency rule will produce incorrect results until this is addressed.

Fix options: (a) detect NI coordinates and switch CRS automatically, or (b) make the target
CRS configurable per rulepack. This decision is pending.

### Critical finding — Ignore-tagged rows must be filtered

Trimble CSV exports include `Ignore`-tagged points (TAG field = `I`). These must be excluded
before QA processing. Point 10000 in `28-14 474c.csv` is an example.

### Finding — .job file is not the first intake target

The Trimble `.job` file is a proprietary binary format (Trimble General Survey Journal). It
requires a Trimble SDK to parse. The CSV export is the practical intake path.

### Finding — remark text carries design-critical context

Trimble REMARK fields contain free-text annotations: section identifiers, pole position flags,
structural conversion instructions, conductor notes. These must be preserved and surfaced in
outputs, not silently dropped during normalisation.

---

## QA architecture

### `app/dno_rules.py`
- `BASE_RULES` — generic UK-wide rules used as fallback.
- `DNO_RULES` — backwards-compatible alias for `BASE_RULES`.
- `SPEN_11KV_RULES`, `SSEN_11KV_RULES`, `NIE_11KV_RULES` — DNO-specific rulepacks.
- `RULEPACKS` dict — `{"DEFAULT": BASE_RULES, "SPEN_11kV": ..., "SSEN_11kV": ..., "NIE_11kV": ...}`.

### `app/qa_engine.py`
Each check returns issues as DataFrame rows with `{Issue, Row}` columns.
See master truth §4 for the current list of check types.

The engine uses a single if/elif chain. Checks fall into two groups:
- Single-field checks: `unique`, `required`, `range`, `allowed_values`, `regex`.
- Multi-field checks: `paired_required`, `dependent_allowed_values`, `coord_consistency`.

**Known limitation:** `coord_consistency` uses OSGB27700 as target CRS. Wrong for NI data.

### `app/routes/api_intake.py`
Rulepack selection chain:
`RULEPACKS[requested_dno]` → fallback to `RULEPACKS["DEFAULT"]` → fallback to `DNO_RULES`.

**Known limitation:** Input normalisation maps the current flat sample schema only. Does not
handle real Trimble CSV format.

---

## Testing

Test layout (see master truth §4 for current total):
- `tests/test_api_intake.py` — normalisation, post-processing, sanitization, feature collection.
- `tests/test_app_routes.py` — route behaviour, health, jobs API, PDF, import/finalize paths.
- `tests/test_qa_engine.py` — per-check-type behaviour.

Quality stack:
- `pre-commit` — trailing whitespace, EOF fix, YAML/JSON/large-file checks, Ruff hooks.
- `Ruff` — lint + format.
- `pytest` — backend unit and integration tests.
- `pytest-cov` — coverage reporting (`pytest --cov=app`).
- `GitHub Actions` — runs `pre-commit run --all-files` and `pytest -q` on every push/PR to `master`.
- `Dependabot` — weekly dependency updates via `.github/dependabot.yml`.

---

## Non-blocking technical debt

Known items that don't block the current priority but should be addressed when next relevant:

- Historical test jobs linger in `uploads/jobs/`.
- `issues.csv` payloads are still verbose.
- `app/routes/api_rulepacks.py` returns stub data — needs wiring to real `RULEPACKS` dict.
- `Makefile` has a stale port (5010 instead of 5001).
- GitHub Actions shows a non-blocking Node.js deprecation warning for upstream actions.
- No automated browser tests (Playwright not yet active).
- `docker-compose.yml` exists at root but isn't used by current dev flow.

---

## Known weaknesses

See master truth §4 for the canonical list. Key addition as of 21 April 2026:

- **Intake normalisation does not match real Trimble CSV format** — highest priority gap
  discovered from real survey file review.
- **coord_consistency uses wrong CRS for NI data** — needs fix before NIE_11kV rulepack
  can be trusted on real files.
- **Ignore-row filtering not yet implemented.**
