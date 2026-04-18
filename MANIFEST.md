# SpanCore Project Manifest

**Complete inventory of every file and directory in the canonical project.**

Last updated: 17 April 2026  
Canonical folder: `/Users/noelcollins/SpanCore-EW-Design-Tool-LOCAL`

---

## Root-Level Files

### Configuration
- **`pyproject.toml`** — Poetry project config, Python 3.11+, 19 dependencies
- **`requirements.txt`** — Pip requirements (Flask 3.1.1, geopandas, shapely, pyproj, etc.)
- **`poetry.lock`** — Locked dependency versions
- **`.env`** — Development environment (FLASK_ENV=development, PORT=5010)
- **`.env.example`** — Template for .env (reference only, do not edit)
- **`.gitignore`** — Git ignore rules (protects .env, uploads/, temp_gis/, venv)

### Application
- **`run.py`** — WSGI entry point, calls `create_app()` from `app/__init__.py`
- **`start.sh`** — Dev server launcher script

### Infrastructure & Deployment
- **`docker-compose.yml`** — Docker services: Flask app (port 5010), MinIO, Postgres 15, optional Nginx
- **`Makefile`** — Build targets: `docker-up`, `docker-down`, `gen-pass`, `smoke`

### Documentation
- **`README.md`** — Project overview and quick start
- **`RUNBOOK.md`** — Operations quick reference
- **`MANIFEST.md`** — This file

### Code Generation
- **`generate_mock_shapefile.py`** — Creates sample shapefile for testing

---

## `app/` Directory — Core Application

### Core Logic Files
- **`__init__.py`** (53 lines) — Flask app factory, blueprint registration, inline routes
- **`qa_engine.py`** (35 lines) — QA validation engine, WORKING
- **`dno_rules.py`** (5 lines) — DNO rule definitions, PLACEHOLDER

### Routes (Blueprints) in `app/routes/`
- **`api_intake.py`** — `POST /api/import/<job_short>` — STUB
- **`api_jobs.py`** — `GET /api/jobs/` — STUB
- **`api_rulepacks.py`** — `GET /api/rulepacks/<id>` — STUB
- **`jobs_page.py`** — `GET /jobs/` — FUNCTIONAL
- **`map_preview.py`** — `GET /map/data/<job_id>` — STUB

### Templates in `app/templates/`
- **`index.html`** — Home page
- **`upload.html`** — Upload form with DNO selector
- **`map_viewer.html`** — Leaflet map viewer

### Static Assets in `app/static/`
- **`js/upload-manager.js`** — Upload workflow
- **`js/map-viewer.js`** — Map renderer
- **`js/rulepack-selector.js`** — DNO dropdown
- **`js/toast.js`** — Toast notifications
- **`style.css`** — Base styles

---

## Deployment & Infrastructure

### `deploy/`
- **`nginx.conf`** — Reverse proxy config (optional)

### `docker/`
- **`frontend/generate-htpasswd.sh`** — Password generator

---

## Data & Samples

### `sample_data/`
- **`mock_survey.csv`** — 5-row test CSV
- **`mock_shapefile.zip`** — Test shapefile

### Runtime (Git-ignored)
- **`uploads/`** — Upload storage
- **`temp_gis/`** — Temp files

---

## Archive & Reference

### `_quarantine/`
- **`20251029_163204/routes.py`** — Pre-refactor monolithic version (REFERENCE ONLY)
- **`20251029_170333/`** — Mid-refactor snapshot
- **`ARCHIVE/routes_monolithic_backup.py`** — Old code backup

---

## Status Summary

| Component | Status | Action |
|-----------|--------|--------|
| App factory | ✅ Working | Keep, do not modify |
| QA engine | ✅ Complete | Keep, do not modify |
| Routes (5) | ⚠️ Stubs | Complete in Phase 1 |
| Frontend | ✅ Complete | Keep, do not modify |
| Config | ✅ Clean | Keep as-is |
| Docker stack | ✅ Ready | Ready to use |

---

## What's Missing (Phase 1 Recovery)

- `POST /api/presign` — Upload presign endpoint (~20 lines)
- `PUT /api/upload/put/` — File receiver (~10 lines)
- `GET /api/jobs/<id>/status` — Status polling (~15 lines)
- `GET /map/view/<job_id>` — Map page route (~3 lines)
- Wire QA into finalize — Processing (~20 lines)
- Real GeoJSON in /map/data/ — Geometry output (~30 lines)
- Fix index.html — Home page (~15 lines)

---

## Safe to Modify

✅ `app/dno_rules.py` — extend with real rules  
✅ `app/routes/api_*.py` — implement missing endpoints  
✅ Templates and styles — add features  
✅ Config files — update as needed  

❌ `app/__init__.py` — Flask factory  
❌ `app/qa_engine.py` — core logic  
❌ `run.py` — WSGI entry point  
🔒 `.env` — never commit  
🔒 `uploads/`, `temp_gis/` — runtime only  
🔒 `_quarantine/` — reference only  

---

*Complete manifest. For recovery plan, see handover pack.*
