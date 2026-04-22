# Changelog

All notable changes to Unitas GridFlow are recorded here, session by session.

This file is the rolling history of what shipped. Each entry is dated.

Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

---

## 2026-04-22 (validation batch 2 — raw controller intake + completeness tightening)

### Added

- `is_raw_controller_dump(first_line)` in `app/controller_intake.py`. Detects GNSS
  controller metadata-header format (`Job:X,Version:Y,Units:Z`) by inspecting the
  first line before `pd.read_csv` is called. This format cannot be detected from
  column names after a normal `read_csv` because the metadata row becomes the header.

- `parse_raw_controller_dump(path)` in `app/controller_intake.py`. Parses raw GNSS
  controller dump files using Python's `csv` module (chosen over `pd.read_csv` because
  raw dumps have variable column counts per row that the pandas C parser cannot handle).
  Maps: col 0 → pole_id, col 1 → easting, col 2 → northing, col 4 → structure_type.
  Extracts inline `FeatureCode:HEIGHT` attribute → height and `FeatureCode:REMARK`
  → location. GPS instrument elevation (col 3) is intentionally NOT mapped to height
  since it records terrain elevation, not declared pole height — ensuring the
  completeness summary correctly reports partial height coverage.

- First-line format detection in `app/routes/api_intake.py`. The finalize route now
  peeks at the first line of the uploaded file and routes to `parse_raw_controller_dump`
  before falling through to the existing `pd.read_csv` + `is_controller_csv` path.

- `feature_codes_found` field in `build_completeness_summary` output. Surfaces the
  sorted list of unique structure/feature codes present in the parsed data. For
  controller dumps these are the surveyor-assigned feature codes (Angle, Pol, Hedge,
  EXpole) — the one piece of structural context digitally available. Only included
  when at least one non-null code is present.

- 8 new tests in `tests/test_controller_intake.py` covering: `is_raw_controller_dump`
  detection, `parse_raw_controller_dump` record count, PRS/metadata row exclusion,
  HEIGHT attribute vs GPS elevation mapping, REMARK → location mapping, feature code
  → structure_type mapping, numeric column coercion, and `feature_codes_found` in
  completeness summary.

### Validated

- Real-file output simulated via representative test fixture matching job 28-14 513
  format. With the raw parser in place, `build_completeness_summary` would produce:
  total_records=11, height coverage=2/11 (18.2%), location/remarks=2/11 (18.2%),
  material=0/11 (0%), structure_type=11/11 (100%), grid_crs_detected=EPSG:29900,
  feature_codes_found=[Angle, EXpole, Hedge, Pol]. This matches the VALIDATION_ANALYSIS
  intent exactly.

### State at end of session

- 66 tests passing (up from 38).
- Raw GNSS controller dump format now parseable end-to-end.
- Completeness summary surfaces record count, position status, CRS, per-field coverage,
  and feature codes found.
- No changes to QA rules, map output, or PDF generation.

---

## 2026-04-22 (strategic review)

### Added

- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md` — distilled strategic conclusions from the external AI review process.

### Changed

- `AI_CONTROL/00_PROJECT_CANONICAL.md` updated to reflect the current phase more accurately and incorporate the new validation-led direction.

- `AI_CONTROL/01_CURRENT_STATE.md` updated to reflect the main unresolved risk: lack of real-world validation.

- `AI_CONTROL/02_CURRENT_TASK.md` rewritten so the next phase is validation-led rather than feature-led.

- `AI_CONTROL/03_WORKING_RULES.md` updated to formally prioritise validation evidence over abstract feature expansion.

- `AI_CONTROL/04_SESSION_HANDOFF.md` updated to record the outcome of the external AI review process.

- `AI_CONTROL/05_PROJECT_REFERENCE.md` updated to document how the external AI review work relates to the live repo without becoming a second truth system.

### State after review

- Project remains active and worth continuing.

- Best current framing remains internal tool / consultancy leverage asset.

- Main next step is testing the current tool on real survey files from real jobs.

- Main unresolved question is now whether the current tool provides meaningful value on real survey files for real users.

---

## 2026-04-22 (Phase 2A)

### Added

- Column name normalisation in `app/routes/api_intake.py`. Headers are now stripped,

  lowercased, and have spaces replaced with underscores before alias mapping runs.

  This handles capitalised exports (`Latitude`, `Structure Type`, `Asset ID`, etc.)

  automatically without any manual reformatting.

- Extended alias lists in `_normalize_dataframe`:
  - `pole_id`: adds `id`, `pole_ref`, `asset_ref`

  - `height`: adds `ht_m`

  - `structure_type`: new — covers `pole_type`, `type`

  - `material`: adds `mat`

  - `location`: adds `site`, `site_name`, `description`

  - `lon`: adds `long`

  - `easting`: new — covers `os_easting`, `grid_easting`, `grid_e`

  - `northing`: new — covers `os_northing`, `grid_northing`, `grid_n`

- Three new tests in `tests/test_api_intake.py`: capitalised headers, common

  abbreviations, OSGB aliases.

### State at end of session

- 38 tests passing.

- Column normalisation handles the most common real-world survey CSV variants.

- No changes to QA engine or rulepacks (Phase 1 closed).

---

## 2026-04-22 (Phase 1 closed)

### Changed

- `AI_CONTROL/02_CURRENT_TASK.md` rewritten: Phase 1 formally closed, Phase 2

  (input schema breadth) defined as the current task.

- `AI_CONTROL/04_SESSION_HANDOFF.md` updated to reflect Phase 1 closure and Phase 2

  entry point.

### State

- Phase 1 complete: 10 QA check types, 4 DNO rulepacks, 35 tests passing.

- Phase 2 next: normalise incoming CSV column names in `app/routes/api_intake.py`.

---

## 2026-04-22 (continued)

### Added

- `ENWL_11KV_RULES` rulepack in `app/dno_rules.py`. Covers Electricity North West

  licence area (Lancashire, Cumbria, Cheshire, Greater Manchester): lat 53.3–55.0,

  lon -3.5 to -1.8. Uses same ENA TS 43-8 height range (7–20m), pole ID regex,

  paired-coord checks, material/structure-type consistency, and coord_consistency

  (100m) as existing rulepacks.

- `ENWL_11kV` entry in `RULEPACKS` dict.

- `unique_pair` check type in `app/qa_engine.py`. Flags rows where two or more poles

  share the same composite field values (applied as lat/lon pair in all DNO rulepacks).

  Skips rows with missing values. Added to all 4 DNO rulepacks.

- `span_distance` check type in `app/qa_engine.py`. Converts consecutive pole lat/lon

  to OSGB27700 and measures distance between adjacent rows. Flags spans below 10m

  (likely duplicate entry) or above 500m (likely GPS error or missing pole). Added to

  all 4 DNO rulepacks.

- Four new tests in `tests/test_qa_engine.py` covering unique_pair and span_distance.

### Fixed

- `test_import_finalize_returns_success_for_valid_job` hardcoded issue count updated

  9→11 to reflect the two additional issues correctly raised by the new rules on the

  existing integration test fixture.

### State at end of session

- 35 tests passing.

- 10 QA check types.

- 4 DNO rulepacks live (`SPEN_11kV`, `SSEN_11kV`, `NIE_11kV`, `ENWL_11kV`).

- Control layer in sync with code.

- CI green.

---

## 2026-04-22

### Added

- Formal `_archive/` structure introduced to separate active project from historical material.

- New `AI_CONTROL/05_PROJECT_REFERENCE.md` created to preserve historical context without bloating operational files.

- Clear three-layer model defined:
  - Active project surface

  - Archive/reference surface

  - Local/tool-specific surface

### Changed

- Repository reorganised to reflect clean separation between:
  - active code and control files

  - historical synthesis and archive material

- `CLAUDE.md` rewritten to align with cleaned control layer and new repo structure.

- `.cursorrules` rewritten to match Claude bootstrap and enforce correct working model.

- `README.md` rewritten to:
  - reflect current MVP state

  - define project structure

  - document active vs archive separation

  - clarify development priorities

### Moved

- `PROJECT_SYNTHESIS/` → `_archive/docs/PROJECT_SYNTHESIS/`

- `RUNBOOK.md` → `_archive/docs/`

- `PROJECT_OPERATING_MODEL.md` → `_archive/docs/`

- `MANIFEST.md` → `_archive/docs/`

- `FRONTEND_FINAL_IMPLEMENTATION.md` → `_archive/docs/`

- AI bundle folders:
  - `CHATGPT_UPLOAD_BUNDLES/`

  - `CLAUDE_APP_UPLOAD_BUNDLES/`

  - `CLAUDE_REVIEW_BUNDLES/`

  → `_archive/ai_bundles/`

### Removed

- Legacy control-layer entry points from active usage:
  - `MASTER_PROJECT_READ_FIRST.md`

  - `AI_CONTROL/00_READ_THIS_FIRST.md`

  - `AI_CONTROL/01_PROJECT_TRUTH.md`

### Fixed

- Eliminated ambiguity between:
  - active instructions

  - historical synthesis

  - archived code

- Prevented future AI/tool drift by enforcing single authoritative control layer.

### State at end of session

- Clean repository structure established.

- Control layer fully aligned with project direction.

- Archive separated and safe from accidental use.

- Claude + Cursor environments aligned with new structure.

- Project ready for focused Phase 1 work (QA rule improvements).

---

## 2026-04-21

### Added

- `NIE_11KV_RULES` rulepack in `app/dno_rules.py`. Uses ENA TS 43-8 height range (7–20m), pole ID regex, paired-coord checks, material/structure-type consistency, and `coord_consistency` (100m). Network bounds: Northern Ireland lat 54.0–55.3, lon -8.2 to -5.4 — single contiguous licence area, no disjoint-zone caveat.

- `NIE_11kV` entry in `RULEPACKS` dict.

- Two new tests in `tests/test_qa_engine.py`: registration check + valid NIE pole (realistic Belfast coords) passes.

- `PROJECT_OPERATING_MODEL.md` — plain-English guide to how the project is organised, who does what, and how sessions run.

### Changed

- `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md`: §4 updated to reflect NIE live and 29 tests; §5 priority list updated; §6 Claude app role clarified as "primary implementation tool and control-layer custodian"; §7 hard rule 9 added (never close a session without updating handoff + changelog); §9 file map updated to include `PROJECT_OPERATING_MODEL.md`.

- `AI_CONTROL/03_CURRENT_TASK.md`: Rewritten — next task is `ENWL_11kV`.

- `AI_CONTROL/04_SESSION_HANDOFF.md`: Rewritten to record this session.

### State at end of session

- 29 tests passing.

- 8 QA check types.

- 3 DNO rulepacks live (`SPEN_11kV`, `SSEN_11kV`, `NIE_11kV`).

- Control layer in sync with code.

- CI green.

---

## 2026-04-20 (continued)

### Added

- `SSEN_11KV_RULES` rulepack in `app/dno_rules.py`. Uses same ENA TS 43-8 height range (7–20m), pole ID regex, paired-coord checks, material/structure-type consistency, and `coord_consistency` (100m) as SPEN. Network bounds cover combined SEPD (southern England) + SHEPD (northern Scotland) licence areas: lat 50.0–60.9, lon -7.5 to +1.8. Documented `TODO` to tighten with polygon check — current bounds pass coordinates in non-SSEN areas between the two zones but still catch grossly wrong coordinates.

- `SSEN_11kV` entry in `RULEPACKS` dict.

- Two new tests in `tests/test_qa_engine.py`: registration check + valid SSEN pole (realistic Inverness coords) passes.

### Triaged

- Dismissed 9 Dependabot alerts (1 high geopandas, 6 moderate Werkzeug, 2 low Flask) as "vulnerable code not actually used". Tool runs locally on macOS with no PostGIS connection, no caching proxy, and no Werkzeug file-serving path — none of the CVE prerequisites apply.

### State at end of session

- 27 tests passing.

- 2 DNO rulepacks live (`SPEN_11kV`, `SSEN_11kV`).

- CI green.

- 0 open Dependabot alerts.

---

## 2026-04-20

### Added

- `coord_consistency` QA check type in `app/qa_engine.py`. Converts lat/lon to OSGB27700 via pyproj and measures distance against declared easting/northing. Configurable tolerance (default 100m). Rows with any missing coordinate values are skipped.

- `coord_consistency` rule in `SPEN_11KV_RULES` with 100m tolerance.

- Two new tests in `tests/test_qa_engine.py` covering the new check (matching and mismatched coordinate cases).

- `.github/dependabot.yml` — weekly Dependabot updates for pip + github-actions.

- `CHANGELOG.md` — this file.

- `pytest-cov` added to dev dependencies for coverage reporting (`pytest --cov=app`).

### Changed

- `app/qa_engine.py` refactored into a clean single if/elif chain. Checks that operate on multiple fields are now grouped separately from checks that operate on a single `field` key.

- Control layer consolidated:
  - `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md` rewritten as the single primary authority. Absorbed tool roles and hard rules from the deleted `05_AI_ROLE_RULES.md`. Added §10 "how to update this file" checklist.

  - `AI_CONTROL/02_CURRENT_STATE.md` aggressively slimmed — duplicated counts and priorities removed; only technical detail retained.

  - `AI_CONTROL/03_CURRENT_TASK.md` rewritten for post-coord_consistency state; next task is `SSEN_11kV` rulepack.

  - `AI_CONTROL/04_SESSION_HANDOFF.md` rewritten to record this session's work.

  - `AI_CONTROL/06_DEVELOPMENT_PROCESS.md` slimmed — dropped sections that duplicated master truth; kept genuinely process-only content.

  - `CLAUDE.md` and `.cursorrules` slimmed — removed hard-coded counts that drift. Now reference master truth for changing facts.

### Removed

- `MASTER_PROJECT_READ_FIRST.md` (root). Redundant pointer.

- `AI_CONTROL/00_READ_THIS_FIRST.md`. Legacy pointer superseded by master truth.

- `AI_CONTROL/01_PROJECT_TRUTH.md`. Still used old "SpanCore" identity; content absorbed into master truth §1.

- `AI_CONTROL/05_AI_ROLE_RULES.md`. Content absorbed into master truth §6.

### State at end of session

- 25 tests passing.

- 8 QA check types.

- SPEN_11kV is the only live rulepack.

- Control layer reduced from 9 files to 5 active + 2 tool bootstraps + this changelog.

- CI green.

---

## Earlier history

Earlier sessions are summarised in `AI_CONTROL/04_SESSION_HANDOFF.md` and

`_archive/docs/PROJECT_SYNTHESIS/`.

This file starts at 2026-04-20.
