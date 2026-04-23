# Unitas GridFlow

**Pre-CAD QA, validation, and workflow support for UK electricity network survey-to-design handoffs.**

---

## Overview

Unitas GridFlow is a narrow workflow tool for validating survey inputs before CAD/design handoff.

Its role is to:

- ingest survey CSV data
- normalise input into a consistent internal schema
- apply rule-based QA validation
- generate structured issues
- render mapped outputs
- produce a PDF QA report
- retain job outputs locally for review

Short version:

**A narrow pre-CAD QA gatekeeper for survey-to-design workflows**

---

## Why this project exists

Unitas GridFlow exists because repeated real-world friction was observed in the handoff between field survey and office design.

The main problem is not usually the engineering calculation itself.

The main problem is often that incoming survey information is:

- inconsistent
- incomplete
- awkward to interpret
- mixed in quality
- discovered to be defective too late in the process

The project is intended to act as a structured gate between survey and design by:

- validating incoming data early
- catching missing or inconsistent information
- applying practical workflow / DNO-style checks
- surfacing issues before office time is wasted downstream

---

## Current MVP Status

The project currently has a working local MVP.

### Working flow

    upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs

### Confirmed working components

- upload page
- upload / presign flow
- CSV save to job folder
- intake / finalise route
- QA processing
- `issues.csv` generation
- `map_data.json` generation
- PDF QA report route
- jobs listing page
- representative input schema with header normalisation
- pytest coverage
- GitHub Actions CI (`pre-commit` + `pytest`)

---

## Current status

The project has moved beyond setup and baseline scaffolding.

### Completed so far

- working local MVP
- 4 live regional rulepacks
- 10 QA check types
- Phase 1 complete: QA rule improvements
- Phase 2A complete: input/header normalisation improvements
- Validation batch 2 complete: raw GNSS controller dump intake + completeness reporting
- Validation batch 3 complete: coord_consistency fix for non-OSGB grids + QA noise suppression for controller files
- Validation batch 4 complete: NIE_11kV rulepack auto-detection from Irish Grid CRS + completeness surfacing in map view and PDF
- Validation batch 5 complete: design readiness verdict + survey coverage categories + enhanced map popups
- Validation batch 6 complete: issue-text popup explanation + interactive pass/fail filter + Records label + design-readiness wording + overlap detection
- Validation batch 7 complete: feature-aware QA (Hedge skipped in span checks) + record inspection panel + "not captured" height in popups
- 86 passing tests
- active control layer for project truth and direction

### Current main unresolved issue

The biggest remaining uncertainty is now:

**real-world validation**

The project still needs proof that the current tool provides meaningful value on real survey files for real users.

---

## Current development focus

Primary priority:

**Validation-led next phase**

This means the next important step is to:

- test the current tool against one or more real survey files from real jobs
- identify what works
- identify what breaks
- identify what real users actually care about
- refine the next development phase from that evidence

This is now more important than abstract feature expansion.

---

## Current limitations

- real-world validation still missing
- rules are meaningful for an MVP but not yet deeply differentiated or truly DNO-grade
- issue modelling is still lightweight
- browser E2E coverage not yet implemented
- output model is still MVP-level, not production-grade

---

## Best current framing

At this stage, the strongest realistic framing is:

- internal workflow tool
- consultancy leverage asset
- narrow productivity / QA layer

Less realistic framing right now:

- broad SaaS platform
- major standalone utility software business
- fully mature DNO compliance product

---

## Project structure

The repository is intentionally split into three layers:

### 1. ACTIVE PROJECT (used for development)

- `AI_CONTROL/` → control layer (project truth + direction)
- `app/` → Flask application
- `tests/` → pytest suite
- `sample_data/` → example inputs
- `README.md`
- `CHANGELOG.md`
- `CLAUDE.md`
- `WORKFLOW_SYSTEM.md` → how the project operates across all tools
- `PROJECT_DEEP_CONTEXT.md`
- root config files

### 2. ARCHIVE (reference only — do not use for development)

- `_archive/`

Contains:

- old control layers
- AI synthesis outputs
- legacy documentation
- quarantined code
- upload bundles

These are historical only.

### 3. LOCAL / TOOL FILES (not project truth)

- `.env`
- `.vscode/`
- `.claude/`
- `.venv312/`
- caches / coverage

---

## Control layer (important)

Project direction is controlled by:

- `AI_CONTROL/00_PROJECT_CANONICAL.md`
- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/03_WORKING_RULES.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`
- `AI_CONTROL/05_PROJECT_REFERENCE.md`
- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md`

These define:

- what the project is
- current state
- current task
- development rules
- session continuity
- strategic conclusions

---

## Quick start

### Create and activate environment

    python3.13 -m venv .venv312
    source .venv312/bin/activate
    python -m pip install --upgrade pip setuptools wheel
    python -m pip install -r requirements.txt
    python -m pip install pre-commit ruff pytest

### Run the app

    python run.py

### Run tests

    pytest -v

### Run linting

    pre-commit run --all-files

---

## Tech stack

- Python 3.13
- Flask
- pandas / geopandas
- shapely / pyproj
- reportlab
- Leaflet
- Bootstrap 5
- pytest
- Ruff
- pre-commit
- GitHub Actions CI

---

## Development principles

- Stay strictly narrow in scope
- Work one task at a time
- Prefer small, targeted changes
- Avoid unnecessary rewrites
- Do not introduce features outside current scope
- Do not assume more features are the right next step without validation evidence

---

## Key files

- `app/dno_rules.py` — QA rulepacks
- `app/qa_engine.py` — QA engine
- `app/routes/api_intake.py` — CSV intake and normalisation
- `app/routes/api_upload.py` — upload handling
- `app/routes/map_preview.py` — map logic
- `app/routes/pdf_reports.py` — PDF generation
- `tests/` — must remain green

---

## After any code change

Always run:

    pytest -v
    pre-commit run --all-files

Then:

    git add .
    git commit -m "clear message"
    git push

---

## Final note

This project is intentionally narrow.

It is not a general platform.

It is a specialist pre-CAD QA layer for survey-to-design workflows, and the next meaningful step is proving that it provides real-world value on real survey files.
