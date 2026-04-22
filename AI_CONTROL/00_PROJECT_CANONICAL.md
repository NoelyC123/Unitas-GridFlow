# Project Canonical

## What this project is

**Unitas GridFlow** is a narrow pre-CAD QA and compliance tool for UK electricity network survey-to-design handoffs.

**Identity:** A DNO survey compliance gatekeeper.

---

## Why this project exists

This project comes from repeated real-world friction in the handoff between field survey and office design for UK electricity network work.

The idea did not begin software-first. It came from direct exposure to:

- how survey data is captured in the field
- how it is transferred to office teams
- how it is interpreted and converted into design and CAD outputs

The key insight:

**The biggest inefficiency sits in the survey-to-design handoff, not in the engineering design itself.**

Unitas GridFlow exists to act as a structured gate between survey and design by:

- validating incoming survey data
- checking for missing or inconsistent information
- applying practical workflow and DNO-style rules
- flagging issues early
- producing cleaner, design-ready outputs before office time is wasted

---

## Core function

The system:

- ingests survey CSV data
- normalises it into a working schema
- applies DNO-specific QA validation
- generates structured issues
- visualises outputs on a Leaflet map
- produces PDF QA reports

---

## Canonical locations

### GitHub
- Repo: `https://github.com/NoelyC123/Unitas-GridFlow`
- Branch: `master`

### Local
- Folder: `/Users/noelcollins/Unitas-GridFlow`
- Environment: `.venv312`

**Rule:** This is the only active repository. Older SpanCore / EW Design Tool repos are archived.

---

## Project structure (authoritative)

The repository is intentionally split into three layers:

### 1. ACTIVE PROJECT (used for development)
- `AI_CONTROL/`
- `app/`
- `tests/`
- `sample_data/`
- `README.md`
- `CHANGELOG.md`
- `CLAUDE.md`
- root config/runtime files

This is the only surface used for development.

---

### 2. ARCHIVE / REFERENCE (do not use for development)
- `_archive/`

Contains:
- old control layers
- project synthesis
- AI bundles
- quarantine code
- legacy documentation

These are **historical only**.

---

### 3. LOCAL / TOOL FILES (not project truth)
- `.env`
- `.vscode/`
- `.claude/`
- `.venv312/`
- caches / coverage

These are environment-specific and not part of the shared system.

---

## Current MVP status

### Working flow

```
upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs
```

### Working routes

- `/upload`
- `/api/presign`
- `/api/import/<job_id>`
- `/map/view/<job_id>`
- `/pdf/qa/<job_id>`
- `/jobs/`
- `/health/full`

### Job outputs

- `uploads/jobs/<job_id>/meta.json`
- `uploads/jobs/<job_id>/<uploaded_csv>.csv`
- `uploads/jobs/<job_id>/issues.csv`
- `uploads/jobs/<job_id>/map_data.json`

---

## Tech stack

### Runtime
- Python 3.13
- Flask
- pandas, geopandas, shapely, pyproj
- ReportLab
- Leaflet, Bootstrap 5

### Quality
- pytest (test suite active)
- Ruff
- pre-commit
- GitHub Actions CI

---

## Current phase

**Working MVP complete → now improving product quality**

Current focus:
- improve QA rule quality in `app/dno_rules.py`

---

## Main current weakness

The system currently has:

**Basic / placeholder QA rules**

This limits real-world usefulness.

---

## Key source files

### QA logic (priority)
- `app/dno_rules.py`
- `app/qa_engine.py`

### Pipeline
- `app/routes/api_intake.py`
- `app/routes/api_upload.py`
- `app/routes/map_preview.py`
- `app/routes/pdf_reports.py`

### Tests
- `tests/`

---

## Development principles

- Keep scope narrow (pre-CAD QA only)
- Focus on real-world usefulness
- Prioritise QA rules as first-class logic
- Avoid turning this into a general platform

---

## Useful commands

```bash
source .venv312/bin/activate
python run.py
pytest -v
pre-commit run --all-files
git add . && git commit -m "..." && git push origin master
```

---

## Navigation

- What should I work on? → `02_CURRENT_TASK.md`
- What works right now? → `01_CURRENT_STATE.md`
- How do I work? → `03_WORKING_RULES.md`
- What changed last session? → `04_SESSION_HANDOFF.md`
