# Project Canonical

## What this project is

**Unitas GridFlow** is a narrow pre-CAD QA and compliance tool for UK electricity network survey-to-design handoffs.

**Identity:** a DNO survey compliance gatekeeper.

**Core function:** takes survey CSV data, runs DNO-specific QA checks, displays results on a map, generates PDF reports.

---

## Canonical locations

### GitHub
- **Repo:** `NoelyC123/Unitas-GridFlow`
- **Branch:** `master`

### Local
- **Folder:** `/Users/noelcollins/Unitas-GridFlow`
- **Environment:** `source .venv312/bin/activate`

**Rule:** This is the only active repo. Older EW / SpanCore repos are archived.

---

## Current MVP status

### Working flow
```
upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs
```

### Working routes
- `/upload` — CSV upload
- `/api/presign` — signed URL for upload
- `/api/import/<job_id>` — QA processing
- `/map/view/<job_id>` — Leaflet map viewer
- `/pdf/qa/<job_id>` — PDF report download
- `/jobs/` — job browser
- `/health/full` — health check

### Job outputs
- `uploads/jobs/<job_id>/meta.json`
- `uploads/jobs/<job_id>/<uploaded_csv>.csv`
- `uploads/jobs/<job_id>/issues.csv`
- `uploads/jobs/<job_id>/map_data.json`

---

## Current tech stack

### Runtime
- Python 3.13, Flask
- pandas, geopandas, shapely, pyproj
- ReportLab, Leaflet, Bootstrap 5

### Quality
- pre-commit, Ruff, pytest (14 passing tests)
- GitHub Actions CI (on push/PR to master)

---

## Current phase

**working MVP + baseline tooling complete + next: improve QA rules**

---

## Main current weakness

`app/dno_rules.py` contains placeholder/basic QA rules. This is the biggest constraint on product value.

---

## Key source files

### QA logic (priority)
- `app/dno_rules.py` — rule definitions
- `app/qa_engine.py` — QA execution

### Pipeline
- `app/routes/api_intake.py` — schema normalization
- `app/routes/api_upload.py` — upload handling
- `app/routes/map_preview.py` — map data
- `app/routes/pdf_reports.py` — PDF generation

### Tests
- `tests/` — pytest suite

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

## Quick navigation

- **What should I work on?** → `02_CURRENT_TASK.md`
- **What works right now?** → `01_CURRENT_STATE.md`
- **How do I work here?** → `03_WORKING_RULES.md`
- **What happened last session?** → `04_SESSION_HANDOFF.md`
