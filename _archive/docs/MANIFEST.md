# Unitas GridFlow — Project Manifest

**Complete inventory of every file and directory in the canonical project.**

Last updated: 20 April 2026
Canonical folder: `/Users/noelcollins/Unitas-GridFlow`
Canonical repo: `https://github.com/NoelyC123/Unitas-GridFlow`

---

## Root-Level Files

### Configuration

- `**pyproject.toml`** — Poetry project config, Python 3.13, project name: unitas-gridflow
- `**requirements.txt**` — Pip requirements (Flask, geopandas, shapely, pyproj, reportlab, etc.)
- `**poetry.lock**` — Locked dependency versions
- `**.env**` — Development environment variables (not committed)
- `**.env.example**` — Template for .env
- `**.gitignore**` — Git ignore rules
- `**.pre-commit-config.yaml**` — Pre-commit hooks (trailing whitespace, Ruff, etc.)
- `**.cursorrules**` — Cursor Pro project context
- `**CLAUDE.md**` — Claude Code project context

### Application

- `**run.py**` — WSGI entry point, calls `create_app()`, runs on port 5001
- `**start.sh**` — Dev server launcher script

### Infrastructure & Deployment

- `**docker-compose.yml**` — Docker services: Flask app, MinIO, Postgres 15, optional Nginx
- `**Makefile**` — Build targets: docker-up, docker-down, gen-pass, smoke

### Documentation

- `**README.md**` — Project overview and quick start
- `**RUNBOOK.md**` — Operations quick reference
- `**MANIFEST.md**` — This file
- `**MASTER_PROJECT_READ_FIRST.md**` — Top-level orientation for all AIs

### AI Control Layer

- `**AI_CONTROL/**` — All AI session control files (read these first every session)

---

## `app/` Directory — Core Application

### Core Logic Files

- `**__init__.py**` — Flask app factory, blueprint registration
- `**qa_engine.py**` — QA validation engine (supports unique, required, range, allowed_values, regex, paired_required, dependent_allowed_values)
- `**dno_rules.py**` — DNO rulepack definitions (BASE_RULES, SPEN_11kV, RULEPACKS dict)

### Routes (Blueprints) in `app/routes/`

- `**api_intake.py**` — `POST /api/import/<job_short>` — CSV processing, QA, outputs
- `**api_jobs.py**` — `GET /api/jobs/` and `GET /api/jobs/<id>/status`
- `**api_rulepacks.py**` — `GET /api/rulepacks/<id>`
- `**api_upload.py**` — `POST /api/presign` and `PUT /api/upload/<job_id>/<filename>`
- `**jobs_page.py**` — `GET /jobs/`
- `**map_preview.py**` — `GET /map/view/<job_id>` and `GET /map/data/<job_id>`
- `**pdf_reports.py**` — `GET /pdf/qa/<job_id>`

### Templates in `app/templates/`

- `**index.html**` — Home page (Unitas GridFlow branding)
- `**upload.html**` — Upload form with DNO selector
- `**map_viewer.html**` — Leaflet map viewer
- `**jobs.html**` — Jobs listing page

### Static Assets in `app/static/`

- `**js/upload-manager.js**` — Upload workflow
- `**js/map-viewer.js**` — Map renderer with QA status colours
- `**js/rulepack-selector.js**` — DNO dropdown
- `**js/toast.js**` — Toast notifications
- `**style.css**` — Base styles

---

## Testing

### `tests/`

- `**conftest.py**` — pytest configuration
- `**test_qa_engine.py**` — QA engine unit tests
- `**test_api_intake.py**` — API intake route tests
- `**test_app_routes.py**` — App route integration tests

**Current test count: 23 passing**

---

## Deployment & Infrastructure

### `deploy/`

- `**nginx.conf`** — Reverse proxy config (optional)

### `docker/`

- `**frontend/generate-htpasswd.sh**` — Password generator

---

## Data & Samples

### `sample_data/`

- `**mock_survey.csv**` — Representative 5-row test CSV with realistic schema
- `**mock_shapefile.zip**` — Test shapefile

### Runtime (Git-ignored)

- `**uploads/**` — Upload and job output storage
- `**temp_gis/**` — Temp GIS files

---

## Archive & Reference

### `_quarantine/`

- Legacy/reference-only code snapshots. Do not restore blindly.

---

## Current Status


| Component          | Status                      |
| ------------------ | --------------------------- |
| App factory        | ✅ Working                   |
| QA engine          | ✅ Working — 7 check types   |
| All routes         | ✅ Working                   |
| Frontend           | ✅ Working                   |
| SPEN_11kV rulepack | ✅ Live with real ENA values |
| Tests              | ✅ 23 passing                |
| CI                 | ✅ GitHub Actions active     |
| Tool bootstrapping | ✅ CLAUDE.md + .cursorrules  |
