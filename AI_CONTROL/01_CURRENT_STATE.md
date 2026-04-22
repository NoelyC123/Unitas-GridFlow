# Current State

## Project status

The project is in:

**Working local MVP + baseline tooling complete + entering product-improvement phase**

The project is NOT in:
- repo setup mode (completed)
- branding cleanup mode (completed)
- baseline tooling/test setup mode (completed)

---

## What works right now

### MVP flow (confirmed)

```
upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs
```

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

### 1. QA rules are basic (PRIMARY WEAKNESS)

- `app/dno_rules.py` contains placeholder-level checks
- Not sufficient for real DNO-grade validation
- Limits real-world usefulness of the tool

This is the **current highest priority**.

---

### 2. Input handling is narrow

- One representative CSV schema supported
- Does not yet reflect real-world survey variability
- Will become relevant after QA rules improve

---

### 3. Architecture contains MVP debt

- Some logic implemented quickly during recovery/build phase
- Not yet optimised or refactored
- Acceptable for current stage

---

### 4. No browser automation

- No Playwright or UI automation
- Testing is backend-only
- Low priority at current stage

---

## Current development phase

The project has moved beyond setup and stabilisation.

It is now in:

**Working MVP → Product improvement phase**

---

## Current priority

**Improve QA rule quality in `app/dno_rules.py`**

Goal:
- make validation meaningful
- reflect real-world survey issues
- enforce DNO-style logic
- produce genuinely useful outputs

---

## Current counts

- **DNO rulepacks live:** 4 (SPEN_11kV, SSEN_11kV, NIE_11kV, ENWL_11kV)
- **QA check types:** 10
- **Tests passing:** 35

---

## What changed recently

### Phase 1 progress — QA rule improvements

- `ENWL_11kV` rulepack added to `app/dno_rules.py`
- `unique_pair` check added to `app/qa_engine.py` and all 4 DNO rulepacks — flags two poles sharing the same lat/lon
- `span_distance` check added to `app/qa_engine.py` and all 4 DNO rulepacks — flags spans < 10m (likely duplicate) or > 500m (likely GPS error)
- 4 new tests added; 35 total passing

---

### Control layer redesign (previous session)

- Reduced from multiple overlapping files → 6 clearly defined files
- Separated operational control from historical/reference content
- Established clear navigation ("which file answers which question")
- Removed legacy/duplicated control files

---

### Repository structure clarified

The project now follows a strict three-layer model:

1. **Active project**
   - `AI_CONTROL/`
   - `app/`
   - `tests/`
   - `sample_data/`
   - root files

2. **Archive**
   - `_archive/` (historical only)

3. **Local/tool files**
   - environment and editor-specific files

---

### System stability

- MVP functionality remains unchanged and working
- Tests continue to pass
- CI continues to validate
- No regressions introduced during restructuring

---

## Next checkpoint trigger

Update this file when:

- MVP behaviour changes
- QA rules significantly improve
- a new phase begins
- a major weakness is resolved
- project direction shifts

---

## Expected next update

This file should next be updated when:

**Phase 1 (QA rule improvements) produces meaningful validation capability**

That marks a real increase in product value.
