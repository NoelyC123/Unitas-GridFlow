# Session Handoff

## Session summary

This session began **Phase 1: QA rule improvements**.

One rulepack was added cleanly with no architecture changes.

---

## What was completed

### ENWL_11kV rulepack added
- `ENWL_11KV_RULES` added to `app/dno_rules.py` following the exact SPEN/SSEN/NIE pattern
- Covers Electricity North West: Lancashire, Cumbria, Cheshire, Greater Manchester
- Coord bounds: lat 53.3–55.0, lon -3.5 to -1.8

### unique_pair check added
- New `elif check == “unique_pair”` branch in `app/qa_engine.py`
- Flags rows where two or more poles share the same lat/lon combination
- Skips rows with missing coordinate values
- Added to all 4 DNO rulepacks

### span_distance check added
- New `elif check == “span_distance”` branch in `app/qa_engine.py`
- Converts consecutive pole lat/lon to OSGB27700, measures distance between adjacent rows
- Flags spans < 10m (likely duplicate entry) or > 500m (likely GPS error or missing pole)
- Resets state on missing coordinates rather than producing false positives
- Added to all 4 DNO rulepacks

### Tests
- 4 new tests added to `tests/test_qa_engine.py`
- Integration test fixture count corrected in `tests/test_app_routes.py` (9→11)
- 35 tests total, all passing

---

## Current project state

### Counts

- DNO rulepacks live: 4 (SPEN_11kV, SSEN_11kV, NIE_11kV, ENWL_11kV)
- QA check types: 10
- Tests passing: 35

### What works

- Full MVP flow: upload → QA → outputs → map → PDF → jobs
- All key routes operational
- Local environment stable
- CI active and green

### What is weak

1. **QA rules — Phase 1 substantially complete, minor depth remaining**
   - 10 check types, 4 DNO rulepacks
   - Could still add height/material cross-validation (`dependent_range`) if needed

2. **Input handling is narrow** — one schema, Phase 2

3. **No browser automation** — Phase 3

---

## Current phase

**Phase 2A complete: input column normalisation delivered**

Phase 2 is in progress. The input normalisation layer now handles the most common
real-world survey CSV header variants.

---

## What was done (Phase 2A)

- `_normalize_dataframe` in `app/routes/api_intake.py` updated:
  - Added column name normalisation step (strip, lowercase, spaces→underscores)
  - Extended alias lists for all 9 core fields
  - `structure_type`, `easting`, `northing` now have explicit alias coverage
- 3 new tests in `tests/test_api_intake.py` (capitalised headers, abbreviations, OSGB aliases)
- 38 tests passing

---

## Next session should

1. Read `02_CURRENT_TASK.md` to confirm Phase 2 scope and decide whether Phase 2A
   is sufficient or further input handling work is needed
2. Candidate next steps (do not start without reviewing 02_CURRENT_TASK.md):
   - Test against real survey CSV samples to find remaining gaps
   - Add NGED or UKPN rulepacks (follows established pattern)
   - Begin issue severity work

---

## What must remain true

- Scope stays narrow (pre-CAD QA only)
- Control layer remains the single source of truth
- `_archive/` is never used for active decisions
- Code and control files stay aligned
- `pytest -v` must be green after every change
