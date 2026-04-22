# Changelog

All notable changes to Unitas GridFlow are recorded here, session by session.

This file is the rolling history of what shipped. Each entry is dated.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

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
- 4 DNO rulepacks live (SPEN_11kV, SSEN_11kV, NIE_11kV, ENWL_11kV).
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
- 3 DNO rulepacks live (SPEN_11kV, SSEN_11kV, NIE_11kV).
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
- 2 DNO rulepacks live (SPEN_11kV, SSEN_11kV).
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
