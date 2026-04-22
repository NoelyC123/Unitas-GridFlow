# Current State

## Project status

The project is in:

**Working local MVP + Phase 1 complete + Phase 2A complete + next: validation-led product improvement**

The project is NOT in:

- repo setup mode (completed)
- branding cleanup mode (completed)
- baseline tooling/test setup mode (completed)

---

## What works right now

### MVP flow (confirmed)

    upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs

---

### Core routes (working)

- `/upload` — CSV upload form
- `/api/presign` — upload handling
- `/api/import/<job_id>` — QA processing
- `/map/view/<job_id>` — Leaflet map
- `/pdf/qa/<job_id>` — PDF download
- `/jobs/` — job browser
- `/health/full` — health check

---

### System capabilities

- CSV upload and persistence
- QA processing pipeline
- Issue generation (`issues.csv`)
- Map data generation (`map_data.json`)
- PDF QA report generation
- Job storage and browsing
- Column/header normalisation for core survey fields
- Multiple regional rulepacks for 11kV validation

---

### Testing and quality

- pytest suite is active and passing
- pre-commit hooks active
- Ruff linting active
- GitHub Actions CI active (on push/PR)

---

### Environment and setup

- Local development environment working (`.venv312`)
- Python 3.13 configured
- Canonical repository established (`Unitas-GridFlow`)
- Local and GitHub repos aligned

---

## What is weak right now

### 1. Real-world validation gap (PRIMARY WEAKNESS)

- The project now has a credible working MVP, but it has not yet been tested against real survey files from real jobs.
- The central unresolved question is whether the current tool catches issues that actual users care about.
- This is now the most important project risk.

---

### 2. Rule depth is still limited

- The rule engine is now meaningfully better than placeholder level.
- However, the current rules are not yet deeply differentiated or truly DNO-grade.
- The project still needs real-world evidence to determine which rules matter most and which are noise.

---

### 3. Input handling — raw controller format now supported

- Phase 2A improved column/header normalisation for structured CSVs.
- Validation batch 2 added support for raw GNSS controller dump CSVs (Job:/Version:/Units: metadata-header format).
- Irish Grid TM65 (EPSG:29900) and ITM (EPSG:2157) detection and conversion to WGS84 is now implemented.
- Real-world survey inputs with other formats (Leica GSI, Trimble JXL, non-CSV) are still not handled.

---

### 4. Architecture contains MVP debt

- Some logic was implemented quickly during the recovery/build phase.
- The codebase is stable and acceptable for the current stage.
- Refactoring is not the current priority unless it is driven by validation findings.

---

### 5. No browser automation

- No Playwright or UI automation exists yet.
- Testing is still backend-focused.
- This remains low priority unless the tool begins to see real repeated use.

---

## Current development phase

The project has moved beyond setup and stabilisation.

It is now in:

**Working MVP + Phase 1 complete + Phase 2A complete + next: validation-led proof-of-value work**

---

## Current priority

**Validate the current tool against one or more real survey files from real jobs**

Goal:

- determine whether the current MVP provides meaningful value on real-world inputs
- identify what the tool catches that users actually care about
- identify what the tool misses, mishandles, or overflags
- use real evidence to define the next development phase

---

## Current counts

- **DNO rulepacks live:** 4 (`SPEN_11kV`, `SSEN_11kV`, `NIE_11kV`, `ENWL_11kV`)
- **QA check types:** 10
- **Tests passing:** 67

---

## What changed recently

### Phase 1 — QA rule improvements completed

- Rule engine significantly improved beyond basic placeholder validation
- Added stronger domain-oriented checks such as:
  - coordinate consistency
  - duplicate coordinate pairs
  - span distance logic
- Added 4 regional rulepacks covering:
  - SPEN
  - SSEN
  - NIE
  - ENWL
- Test coverage increased alongside rule changes

---

### Phase 2A — Input schema normalisation completed

- Column name normalisation added to `_normalize_dataframe` in `app/routes/api_intake.py`
- Headers are stripped, lowercased, and spaces replaced with underscores before alias mapping
- Alias coverage expanded for all core fields
- Added support for common real-world variations such as:
  - capitalised headers
  - spaced headers
  - abbreviated field names
  - OSGB alias names for easting/northing
- Test coverage increased from 35 to 38 passing tests

---

### Validation batch 2 — raw controller intake + completeness tightening

- Ran first real-job validation (job 28-14 513, NIE Networks, Strabane area)
- Confirmed the tool could not parse the raw GNSS controller dump format (metadata-header CSV)
- Added `is_raw_controller_dump()` and `parse_raw_controller_dump()` to `app/controller_intake.py`
- Added first-line format detection in `app/routes/api_intake.py` finalize route
- Raw parser correctly maps point numbers, grid coordinates, feature codes, HEIGHT attributes, and REMARK attributes
- GPS instrument elevation (col 3) intentionally not mapped to height — only explicit HEIGHT inline attributes map there
- Added `feature_codes_found` to `build_completeness_summary` output
- Completeness summary now correctly surfaces: record count, position status, CRS, per-field coverage, and feature codes found
- Test count increased from 38 to 66

---

### Strategic review completed

An external AI strategic review was completed on 2026-04-22.

The distilled conclusion was:

- continue the project
- keep the scope narrow
- treat the strongest near-term framing as internal tool / consultancy leverage asset
- shift the next phase toward validation-led development rather than feature-led expansion

This conclusion is captured in:

- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`

---

### Control layer remains stable

- The active control layer remains the source of truth
- Project structure and working rules remain stable
- No code regressions were introduced during documentation and strategy updates

---

## Next checkpoint trigger

Update this file when:

- real survey files have been tested through the tool
- validation findings materially change project direction
- a major weakness is resolved
- the next development phase becomes clearer from real evidence

---

## Expected next update

This file should next be updated when:

**The tool is tested on further real survey files, or when the next development phase (rules refinement, output improvements) is informed by real-file evidence.**

The first real-file validation (job 28-14 513) is now complete. The intake gap has been fixed. The next material update will come from testing on additional files or from a user reviewing the completeness output on a real job.
