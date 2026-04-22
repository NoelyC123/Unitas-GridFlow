# Current Task

## Status: Priority decision required before any new code

**Do not make any code changes until this priority decision is confirmed.**

A review of real Electricity Worx survey files (21 April 2026) revealed that the current intake
normalisation layer does not match the real Trimble CSV format. This changes the priority picture.

---

## The decision required

Two paths are available. You must confirm which comes first.

---

### Path A — Real Trimble CSV intake/normalisation (recommended)

**What this means:**
Redesign the intake normalisation layer in `app/routes/api_intake.py` (and supporting code) to
correctly parse real Trimble CSV exports, including:

- Skip the job header row (`Job:...,Version:...,Units:...`)
- Skip the PRS/base station row
- Parse variable-width feature-coded point records
- Map Trimble feature codes (`Angle`, `EXpole`, `LVxing`, `BTxing`, etc.) to internal schema
- Filter out `Ignore`-tagged rows (TAG field = `I`)
- Preserve REMARK text for each point
- Handle the HEIGHT sub-field where present (crossings, trees, hedges)
- Produce a normalised DataFrame compatible with the existing QA engine

**Why this may be higher priority:**
- Without this, the tool cannot be run on any real survey data.
- Any user validation attempt will require loading a real file first.
- All further rulepack work is being tested against synthetic sample data, not reality.
- Demonstrating the tool on a real job (e.g. 4-474 or 474c) requires this to work first.

**Also needed alongside this (smaller fixes):**
- Fix `coord_consistency` to use the correct CRS for NI data (ITM/TM65 rather than OSGB27700).
- Add Ignore-row filtering before QA processing.

---

### Path B — Continue remaining DNO rulepacks first (ENWL, NGED, UKPN)

**What this means:**
Continue the rulepack expansion pattern established by SPEN, SSEN, NIE:
- Add ENWL_11kV (Electricity North West — NW England)
- Add NGED_11kV (National Grid Electricity Distribution — Midlands, SW, S Wales)
- Add UKPN_11kV (UK Power Networks — London, SE, East Anglia)

**When this makes sense:**
- If completing UK DNO coverage is the highest near-term business priority.
- If user validation conversations are planned against GB DNO workflows rather than NI.
- If the intake rewrite is being deferred to a separate focused piece of work.

**Risk of this path:**
- All three rulepacks will be tested against the synthetic sample schema, not real Trimble data.
- The coord_consistency bug for NI remains unaddressed.
- UK rulepack rules are valid, but their testing remains synthetic.

---

## What is NOT acceptable as a next step

Making code changes before this priority decision is confirmed and recorded here.

---

## After the priority decision is confirmed, likely sequence

### If Path A (intake first):

1. Design the Trimble CSV parser — document the field mapping before writing code.
2. Implement the parser/normaliser in `app/routes/api_intake.py` or a new module.
3. Fix `coord_consistency` CRS for NI (configurable per rulepack or auto-detect).
4. Add Ignore-row filtering.
5. Update/add tests covering real Trimble format inputs.
6. Run `pytest -v` — all tests must pass.
7. Test with a real file (4-474.csv or 474c.csv) end-to-end.
8. Commit, push, update control layer.
9. Then resume rulepack expansion (ENWL, NGED, UKPN).

### If Path B (rulepacks first):

1. Add ENWL_11kV rulepack — see previous task file for work sequence.
2. Add NGED_11kV.
3. Add UKPN_11kV.
4. Then tackle real Trimble intake/normalisation as the next major phase.
5. Fix coord_consistency CRS for NI at that point.

---

## Context

Real survey files reviewed: `PROJECT_SYNTHESIS/05_SUPPORT_NOTES/REAL_SURVEY_INPUT_ANALYSIS.md`
Project rationale: `PROJECT_SYNTHESIS/00_PROJECT_RATIONALE.md`
