# SpanCore / EW Design Tool

**Pre-CAD QA, compliance, and workflow automation for UK electricity network survey-to-design handoffs.**

---

## Quick Start

### Install dependencies
```bash
python3.12 -m venv .venv312
source .venv312/bin/activate
pip install -r requirements.txt
```

### Run the app
```bash
source .venv312/bin/activate
python run.py
```

App runs at `http://localhost:5010`

### Run with Docker
```bash
docker-compose up
```

---

## Project Status

**Current state:** Blueprint-based Flask app, 70% scaffolded, 0% runnable end-to-end.

**Working:**
- Flask app factory (`app/__init__.py`)
- QA rule engine (`app/qa_engine.py`)
- Five API blueprint stubs
- Complete frontend (HTML/JS/CSS)
- Docker stack

**Missing:**
- Upload presign/PUT endpoints
- Status polling endpoint
- Real file persistence
- Map view renderer
- Actual QA processing in finalize endpoint
- Real DNO rulesets (4 placeholders exist)

**Next phase:** Complete Phase 0 and Phase 1 of recovery plan (see PHASE_RECOVERY.md).

---

## File Structure

See `MANIFEST.md` for complete inventory.

---

## Development

- **Entry point:** `run.py`
- **App factory:** `app/__init__.py`
- **Core logic:** `app/qa_engine.py`, `app/dno_rules.py`
- **Routes:** `app/routes/*.py` (five blueprints)
- **Frontend:** `app/templates/*.html`, `app/static/`

---

## Configuration

- `.env` — Flask config (development mode, port 5010)
- `pyproject.toml` — Poetry config
- `docker-compose.yml` — Docker services (Flask, MinIO, Postgres)
- `Makefile` — Build targets

---

## Key Directories

| Directory | Purpose |
|-----------|---------|
| `app/` | Application code |
| `app/routes/` | Flask blueprints (API endpoints) |
| `app/templates/` | HTML templates |
| `app/static/` | CSS, JS, assets |
| `deploy/` | Nginx config |
| `docker/` | Docker-specific files |
| `sample_data/` | Sample CSV and shapefile for testing |
| `uploads/` | Runtime upload storage (git-ignored) |
| `temp_gis/` | Runtime temp files (git-ignored) |
| `_quarantine/` | Archive of old/reference code |

---

## References

- `MANIFEST.md` — Complete file-by-file inventory
- `RUNBOOK.md` — Quick reference
- `_quarantine/` — Old code and snapshots (reference only)

---

*Last updated: 17 April 2026*
