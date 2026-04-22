# Current Task

## Phase 1 — COMPLETE

**QA rule improvements** are done.

### What was delivered
- 10 QA check types in `app/qa_engine.py`
- 4 DNO rulepacks in `app/dno_rules.py` (SPEN_11kV, SSEN_11kV, NIE_11kV, ENWL_11kV)
- 35 tests passing
- Rules catch real survey problems: missing fields, out-of-range values, coordinate
  inconsistencies, duplicate entries, impossible span lengths, material/type mismatches

### Success condition met
The tool now flags issues a surveyor or CAD engineer would recognise as real problems.

---

## Current task — Phase 2: Input schema breadth

**Make the tool accept real-world survey CSV data**

Primary file:
- `app/routes/api_intake.py`

---

## Why this is the current task

Phase 1 produced a capable QA engine — but it only works on one specific CSV column
schema. Real survey exports from different instruments and teams arrive with different
column names, capitalisations, and layouts.

Until this is solved, the tool cannot be used on actual survey data without manual
preprocessing. That is the main blocker to real-world usefulness.

---

## What Phase 2 means

This task IS:

- Normalising incoming column names to the internal schema
  (e.g. `Latitude` → `lat`, `Height (m)` → `height`, `Asset ID` → `pole_id`)
- Handling missing optional columns gracefully
- Supporting a wider range of real survey export formats
- Keeping the QA engine untouched — it receives normalised data, nothing changes there

This task is NOT:

- Redesigning the QA engine
- Adding new QA rules (Phase 1 is closed)
- Building a general ETL pipeline
- Supporting every possible format — focus on common real-world patterns

---

## Expected outcome

After Phase 2:

A user should be able to upload a survey CSV from a common field instrument or
spreadsheet export and get meaningful QA results without reformatting the file first.

---

## Execution approach

1. Collect 2–3 realistic column name variants for each core field
2. Add a normalisation mapping in `app/routes/api_intake.py`
3. Test with sample CSVs that use non-standard column names
4. Run `pytest -v` — existing tests must stay green
5. Commit, push

---

## Constraints

Do NOT:
- modify `app/qa_engine.py` (Phase 1 is closed)
- modify `app/dno_rules.py` (Phase 1 is closed)
- attempt to support every possible schema variant
- introduce new dependencies unless essential

---

## What comes next (do not start yet)

### Phase 3
Browser automation testing (Playwright) — full upload → QA → map → PDF flow.

### Later
- NGED and UKPN rulepacks
- Issue severity levels (critical / warning / info)
- Output quality improvements (PDF, map, issues.csv)

---

## When to update this file

Update when:
- Phase 2 is complete
- a blocker changes the plan
- priority shifts

Otherwise leave unchanged.
