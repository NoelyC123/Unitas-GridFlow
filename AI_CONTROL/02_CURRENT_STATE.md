# Current State

## Project status

The project is now beyond the earlier recovery-and-foundation phase.

It now has:

- a working local MVP
- a canonical repo and naming structure
- a functioning quality/test stack
- active CI
- cleaned current-facing branding
- a stable baseline for real product improvement work

The project is now in:

**working local MVP + baseline/tooling/testing complete + next product-improvement phase**

---

## Canonical active project identity

### Active project name
**Unitas GridFlow**

### Canonical active repo
`NoelyC123/Unitas-GridFlow`

### Canonical active local folder
`/Users/noelcollins/Unitas-GridFlow`

### Repo rule
This is the **only active canonical repo** for the project.

Older EW / SpanCore / design-tool repos are archived and are not active development repos.

---

## Current live areas

### Core live app
- `app/`
- `run.py`
- `requirements.txt`
- `pyproject.toml`
- `README.md`
- `RUNBOOK.md`
- `sample_data/`
- `uploads/`
- `temp_gis/`

### Control / coordination layer
- `MASTER_PROJECT_READ_FIRST.md`
- `AI_CONTROL/`

### Strategic / reasoning layer
- `PROJECT_SYNTHESIS/`

### GitHub / admin layer
- `GITHUB_ADMIN/`

### Legacy / reference areas
- `_archive/`
- `_quarantine/`
- `_reference/` (if present in older contexts; not part of live app work)

---

## Current MVP status

The narrow MVP is working locally.

### Confirmed working flow
**upload CSV -> save file -> run QA -> save outputs -> view map -> download PDF -> browse jobs**

### Confirmed working parts
- `/upload` page works
- `/api/presign` works
- CSV upload/save works
- `/api/import/<job_id>` works
- QA processing runs
- `issues.csv` is written
- `map_data.json` is written
- `/map/view/<job_id>` works
- `/pdf/qa/<job_id>` works
- `/jobs/` works
- `/health/full` works

### Confirmed current-facing branding state
The live/current-facing app branding has been updated to:

**Unitas GridFlow**

This includes:
- README
- upload page
- map viewer
- jobs page
- PDF report branding
- runtime health/service naming

---

## Current testing / quality status

The baseline quality stack is now active and working.

### Confirmed active tooling
- `pre-commit`
- Ruff
- pytest
- GitHub Actions CI

### Current automated test state
There are currently **14 passing tests**.

Test coverage now includes:
- schema normalization
- issue post-processing
- CSV payload sanitization
- feature collection generation
- JSON-safe output
- health endpoint
- jobs API
- job status endpoint
- PDF endpoint
- import/finalize success path
- import/finalize error paths

### Current CI state
GitHub Actions runs on push/pull request to `master` and currently executes:
- `pre-commit run --all-files`
- `pytest -q`

This baseline/tooling/testing phase is now materially complete.

---

## Current sample/input realism status

The earlier input realism step has already been completed to an MVP-appropriate level.

### Current representative sample schema
The current sample CSV uses a more realistic schema including:
- `asset_id`
- `structure_type`
- `height_m`
- `material`
- `location_name`
- `easting`
- `northing`
- `latitude`
- `longitude`

### Current normalization behaviour
`api_intake.py` now maps that schema into the internal working fields used by the MVP QA engine.

This is no longer the earlier demo-fallback-only state.

---

## Current output structure

Successful jobs currently create outputs under:

- `uploads/jobs/<job_id>/meta.json`
- `uploads/jobs/<job_id>/<uploaded_csv>.csv`
- `uploads/jobs/<job_id>/issues.csv`
- `uploads/jobs/<job_id>/map_data.json`

This remains the practical output contract of the current MVP.

---

## What is now true that was not true before

The following material shifts have now happened:

- the repo identity is now locked to **Unitas GridFlow**
- old design-tool repos are archived
- current-facing app branding is no longer in mixed SpanCore/EW state
- quality tooling is installed and active
- automated backend tests exist and pass
- CI exists and passes
- the baseline/professionalisation phase has been completed

So the project is no longer primarily in recovery, repo setup, or baseline discipline mode.

---

## Current remaining weaknesses

The project is stronger, but still clearly MVP-stage.

### 1. QA logic remains basic
This is now the biggest current weakness.

- `app/dno_rules.py` is still placeholder/basic
- `app/qa_engine.py` still reflects MVP-level logic
- current QA checks are useful as a scaffold, but not yet strong enough to represent a truly valuable DNO-grade product

### 2. Input handling is still narrow
Although the current representative schema step is done, input handling is still limited.

- one representative schema is supported
- broader real-world input variation is not yet handled
- field mapping is still deliberately constrained

### 3. Architecture still has MVP debt
- some route/code paths were built quickly during recovery and stabilisation
- contracts are still lightweight
- there is still room for cleanup/refactor/hardening later

### 4. Browser test coverage does not yet exist
- Playwright is not yet set up
- current automated testing is backend-focused

### 5. Historical/control docs still contain legacy naming
Some non-live files still refer to SpanCore / EW Design Tool in historical or synthesis contexts.

This is not a blocker for current product work.

---

## Current best description of the product

The strongest current product identity remains:

**a narrow pre-CAD QA / compliance / submission-readiness tool for electricity survey-to-design handoffs**

Short version:

**a DNO survey compliance gatekeeper**

What has changed is that the project now has a more professional baseline and test discipline than before.

---

## Current phase of the project

The project is no longer in:

- broken-scaffold diagnosis
- missing-route recovery
- repo canonicalisation
- toolchain setup
- branding cleanup
- baseline testing establishment

It is now in:

**working MVP + baseline complete + next product-improvement phase**

---

## Current next-priority decision

The most important current product weakness is now the QA logic itself.

So the next active phase should be:

**better QA rules**

This is now a more valuable next step than:
- additional setup work
- more branding cleanup
- more baseline process work
- broad new feature expansion

---

## Current control-layer implication

Because the project has moved out of the baseline/tooling/testing phase, the control layer must now reflect that:

- `AI_CONTROL/02_CURRENT_STATE.md`
- `AI_CONTROL/03_CURRENT_TASK.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`

This file is the first of those updates.
