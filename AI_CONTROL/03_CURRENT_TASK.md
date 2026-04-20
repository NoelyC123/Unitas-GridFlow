# Current Task

## Immediate task

The first QA-rule improvement step is now complete.

The project has:
- upgraded `dno_rules.py` to a rulepack architecture
- extended `qa_engine.py` with regex, paired_required, and dependent_allowed_values checks
- wired rulepack selection into `api_intake.py`
- corrected SPEN 11kV height ranges to real ENA values (7m-20m)
- added SPEN network area coordinate bounds
- reached 23 passing tests

The immediate next task is:

1. Add coordinate consistency cross-check (lat/lon vs easting/northing)
2. Add a second DNO rulepack (SSEN_11kV is the logical next choice)

---

## Why these are the next tasks

### Coordinate consistency check
Currently lat/lon and easting/northing are validated in isolation.
A common real-world survey error is mismatched coordinates —
where lat/lon points to one location and easting/northing to another.
This check would catch that. It is high signal and narrow in scope.

### Second DNO rulepack
SPEN_11kV is now solid. The next most natural extension is SSEN_11kV
(Scottish and Southern Electricity Networks), which covers a similar
geographic area with similar but distinct standards.
Adding a second rulepack proves the architecture works for multiple DNOs.

---

## What is not the current task

- broad new feature expansion
- browser E2E testing (Playwright)
- deployment / hosting
- UI redesign
- database integration
- any work not tied directly to QA rule quality

---

## Current development checkpoint

**working MVP + rulepack architecture + SPEN_11kV live + 23 tests passing**

The project has moved meaningfully from placeholder QA toward
genuinely useful DNO-grade validation. The next step continues that
same direction without broadening scope.

---

## Short version

Next two tasks in order:
1. coordinate consistency check
2. SSEN_11kV rulepack
