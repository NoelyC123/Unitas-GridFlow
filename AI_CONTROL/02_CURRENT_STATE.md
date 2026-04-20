# Current State

## Project status

The project has now moved beyond the earlier broken-scaffold state and into a working narrow MVP state.

The live local MVP currently supports a real end-to-end flow:

**upload CSV -> save file -> run QA -> save outputs -> view map -> download PDF -> browse jobs**

This means the immediate recovery phase for the narrow MVP has materially succeeded.

---

## Current live areas

### Core live app
- `app/`
- `run.py`
- `requirements.txt`
- `pyproject.toml`
- `README.md`
- `RUNBOOK.md`
- `docker-compose.yml`
- `sample_data/`
- `uploads/`
- `temp_gis/`

### AI / strategy / control layer
- `AI_CONTROL/`
- `PROJECT_SYNTHESIS/`

### Legacy / reference / archive areas
- `_reference/`
- `_archive/`
- `_quarantine/`

---

## Current narrow MVP status

The narrow MVP is now **working locally**.

### Confirmed working flow
- `/upload` page loads
- CSV upload works
- `/api/presign` works
- uploaded CSV is saved under `uploads/jobs/<job_id>/`
- `/api/import/<job_id>` works
- QA processing runs
- `issues.csv` is created
- `map_data.json` is created
- `meta.json` is created
- `/map/view/<job_id>` works
- `/map/data/<job_id>` works
- `/pdf/qa/<job_id>` works
- `/jobs/` works and lists previous jobs

### Current MVP user journey
1. Open upload page
2. Select CSV
3. Upload and validate
4. Auto-redirect to map page
5. Inspect markers and summary
6. Download PDF
7. Browse previous jobs from `/jobs/`

---

## Current live MVP files

### App entry / config
- `run.py`
- `requirements.txt`

### Core app
- `app/__init__.py`
- `app/qa_engine.py`
- `app/dno_rules.py`

### Live routes
- `app/routes/api_upload.py`
- `app/routes/api_intake.py`
- `app/routes/api_jobs.py`
- `app/routes/api_rulepacks.py`
- `app/routes/jobs_page.py`
- `app/routes/map_preview.py`
- `app/routes/pdf_reports.py`

### Live templates
- `app/templates/upload.html`
- `app/templates/map_viewer.html`
- `app/templates/jobs.html`
- `app/templates/index.html`

### Live frontend JS
- `app/static/js/upload-manager.js`
- `app/static/js/map-viewer.js`
- `app/static/js/rulepack-selector.js`
- `app/static/js/toast.js`

---

## Current output structure

Successful jobs now create files under:

- `uploads/jobs/<job_id>/meta.json`
- `uploads/jobs/<job_id>/mock_survey.csv` (or uploaded CSV filename)
- `uploads/jobs/<job_id>/issues.csv`
- `uploads/jobs/<job_id>/map_data.json`

This output structure is now part of the practical current truth of the local MVP.

---

## What is now true that was not true before

The following earlier blockers have been resolved:

- `app/routes/api_upload.py` now exists
- `/api/presign` now exists and works
- upload no longer fails at presign stage
- `api_intake` is wired and processing jobs
- map route works
- PDF route works
- jobs page works

So the old “missing upload route / missing presign / upload currently fails” state is obsolete.

---

## Current remaining weaknesses

Although the narrow MVP now works, it is still an early local MVP and has important limitations.

### Rules / QA realism
- `dno_rules.py` is still placeholder-level and not yet a real DNO-grade ruleset
- `qa_engine.py` is still basic
- current sample-data handling uses MVP-friendly normalization logic rather than true field-standard logic
- issue modelling is still simplistic

### Data realism
- `sample_data/mock_survey.csv` is only a demo dataset
- field mapping is still lightweight
- current normalization is pragmatic for MVP proof, not production-grade schema handling

### Product maturity
- jobs are stored locally as files, not in a proper persistent app database
- no authentication / permissions model
- no production deployment hardening
- no true multi-user workflow
- UI is now usable, but still MVP-level rather than polished production UX

### Architecture / quality
- some code was written quickly during recovery and may need cleanup/refactor
- output contracts are not yet formally defined
- error handling is improved but not production-grade

---

## Current best description of the product

The strongest current product identity remains:

**a narrow pre-CAD QA / compliance / submission-readiness tool for electricity survey-to-design handoffs**

Short version:

**a DNO survey compliance gatekeeper**

This has not changed.

What has changed is that the product now has a real local MVP flow rather than only a recovery plan.

---

## Current phase of the project

The project is no longer in:
- “missing-route recovery only”
- or “broken scaffold diagnosis only”

It is now in:

**working narrow MVP + control-layer refresh + next-priority decision phase**

That means the immediate task is no longer “make upload work at all”.

The immediate task is now:
- update the control files
- lock the new canonical current state
- decide the next best development priority

---

## Current likely next development options

Once the control layer is updated, the next development decision will likely be between:

1. **better QA rules**
2. **more realistic sample/input handling**
3. **cleanup / refactor / hardening**

Those should be evaluated from the new working-MVP baseline, not from the old broken baseline.

---

## Current control-layer implication

Because the live MVP state has changed materially, the following files must now be updated to reflect the new truth:

- `AI_CONTROL/02_CURRENT_STATE.md`
- `AI_CONTROL/03_CURRENT_TASK.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`

This file is the first of those updates.