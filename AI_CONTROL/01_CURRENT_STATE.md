# Current State

## Project status

The project is in: **working local MVP + baseline/tooling/testing complete**

The project is NOT in:
- repo setup mode (done)
- branding cleanup mode (done)
- baseline tool/test establishment mode (done)

---

## What works right now

### MVP flow (confirmed)
```
upload CSV → save file → run QA → save outputs → view map → download PDF → browse jobs
```

### Routes (confirmed working)
- `/upload` — CSV upload form
- `/api/presign` — S3 signed URL
- `/api/import/<job_id>` — QA processing
- `/map/view/<job_id>` — Leaflet map
- `/pdf/qa/<job_id>` — PDF download
- `/jobs/` — job browser
- `/health/full` — health check

### Testing and CI
- 14 passing tests (pytest)
- pre-commit, Ruff active
- GitHub Actions CI active (on push/PR)

### Code quality
- Local environment working (Python 3.13, .venv312)
- Canonical repo established (Unitas-GridFlow)
- Live branding updated to Unitas GridFlow

---

## What is weak right now

### 1. QA rules are basic (PRIORITY)
- `app/dno_rules.py` contains placeholder/basic checks
- Not enough to represent genuine DNO-grade validation
- This is the biggest current weakness and the reason for Phase 1

### 2. Input handling is narrow
- One representative CSV schema is supported
- Broader real-world survey variation is not yet handled
- Phase 2 priority (after QA rules work)

### 3. Architecture still has MVP debt
- Some code paths were built quickly during recovery
- Cleanup/refactoring can wait until QA rules are stronger

### 4. No browser automation
- Playwright is not active
- Testing is backend-focused only
- Phase 3 priority (lowest urgency)

---

## Current development phase

**This project has moved past baseline/setup.**

It is now in: **working MVP ready for product-improvement phase**

The immediate priority is no longer:
- repo organisation ✓ (done)
- branding alignment ✓ (done)
- tool/test setup ✓ (done)
- baseline discipline ✓ (done)

The immediate priority is now:
- **better QA rules** (Phase 1)

---

## What changed recently

The control layer was redesigned to be lean and practical:

- Reduced from 8 overlapping files to 5 focused files
- Removed historical/reference content from daily files
- Created separate reference file for context preservation
- Established clear "read this file for X question" navigation

The project itself (app code, tests, repo) remains stable:
- MVP continues to work
- All tests continue to pass
- CI/CD continues to validate

---

## Next checkpoint trigger

Update this file when:
- A previously broken flow starts working
- The MVP state changes materially
- The current task is completed
- The next priority changes
- A new development phase begins

The next likely checkpoint will be when Phase 1 (better QA rules) is completed.
