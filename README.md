# Unitas GridFlow

**Pre-CAD QA, compliance, and workflow automation for UK electricity network survey-to-design handoffs.**

---

## Overview

Unitas GridFlow is a focused workflow tool for validating survey inputs before CAD/design handoff.

Its role is to:

- ingest survey CSV data
- normalise input into a consistent internal schema
- apply DNO-specific QA validation
- generate structured issues
- render mapped outputs
- produce a PDF QA report
- retain job outputs locally for review

Short version:

**A DNO survey compliance gatekeeper**

---

## Current MVP Status

The project currently has a **working local MVP**.

### Working flow

**upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs**

### Confirmed working components

- upload page
- upload/presign flow
- CSV save to job folder
- intake/finalise route
- QA processing
- `issues.csv` generation
- `map_data.json` generation
- PDF QA report route
- jobs listing page
- representative sample input schema
- pytest coverage
- GitHub Actions CI (`pre-commit` + `pytest`)

---

## Current limitations

- QA rules are still basic / placeholder-level
- issue modelling is still lightweight
- browser E2E coverage not yet implemented
- output model is MVP-level, not production-grade
- branding transition from legacy naming still incomplete

---

## Current development focus

Primary priority:

**Improve QA rule quality in `app/dno_rules.py`**

Goals:

- make rules realistic
- align with real DNO standards
- enforce strict validation logic
- eliminate placeholder logic

---

## Project structure

The repository is intentionally split into three layers:

### 1. ACTIVE PROJECT (used for development)

- `AI_CONTROL/` → control layer (project truth + direction)
- `app/` → Flask application
- `tests/` → pytest suite
- `sample_data/` → example inputs
- root config files

---

### 2. ARCHIVE (reference only — do not use for development)

- `_archive/`

Contains:

- old control layers
- AI synthesis outputs
- legacy documentation
- quarantined code
- upload bundles

These are **historical only**.

---

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

These define:

- what the project is
- current state
- current task
- development rules
- session continuity

---

## Quick start

### Create and activate environment

```bash
python3.13 -m venv .venv312
source .venv312/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install pre-commit ruff pytest
```

### Run the app

```bash
python run.py
```

### Run tests

```bash
pytest -v
```

### Run linting

```bash
pre-commit run --all-files
```

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

- Stay strictly MVP-focused
- Work one task at a time
- Prefer small, targeted changes
- Avoid unnecessary rewrites
- Do not introduce features outside current scope

---

## Key files

- `app/dno_rules.py` — QA rulepacks (primary focus)
- `app/qa_engine.py` — QA engine
- `app/routes/api_intake.py` — CSV pipeline
- `app/routes/api_upload.py` — upload handling
- `app/routes/map_preview.py` — map logic
- `app/routes/pdf_reports.py` — PDF generation
- `tests/` — must remain green

---

## After any code change

Always run:

```bash
pytest -v
```

Then:

```bash
git add .
git commit -m "clear message"
git push
```

---

## Final note

This project is intentionally narrow.

It is not a general platform — it is a **specialist QA layer for survey-to-design workflows**.

All development should reinforce that focus.
