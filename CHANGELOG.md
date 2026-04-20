# Changelog

All notable changes to Unitas GridFlow are recorded here, session by session.

This file is the rolling history of what shipped. Each entry is dated.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

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
`PROJECT_SYNTHESIS/`. This file starts at 2026-04-20.
