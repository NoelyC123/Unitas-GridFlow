# Session Handoff

## Session summary

This session completed two major phases of work:

### Phase 1 — Full project setup
- Created Unitas-GridFlow Claude Project with Instructions + 8 knowledge files
- Fixed stale SpanCore paths in all 36 job meta files
- Created `CLAUDE.md` for Claude Code bootstrapping
- Created `.cursorrules` for Cursor Pro bootstrapping
- Fixed stale `.zshrc` proj alias
- Confirmed 20 passing tests at start of session

### Phase 2 — First QA-rule improvement
- Upgraded `dno_rules.py` from flat list to rulepack architecture
- Extended `qa_engine.py` with regex, paired_required, dependent_allowed_values
- Wired rulepack selection into `api_intake.py`
- Corrected SPEN 11kV height range to real ENA values (7m-20m)
- Added SPEN network area coordinate bounds (lat 54.5-60.9, lon -6.5 to -0.7)
- Reached 23 passing tests

---

## What is now materially true

- rulepack architecture exists and works
- SPEN_11kV rulepack is live with real-world values
- QA engine supports 6 check types: unique, required, range, allowed_values, regex,
  paired_required, dependent_allowed_values
- api_intake.py selects rules by DNO with proper fallback chain
- all development tools bootstrapped with project context
- 23 tests passing, CI active

---

## What the next session should do

1. Add coordinate consistency cross-check (lat/lon vs easting/northing)
2. Add SSEN_11kV rulepack
3. Run pytest -v to confirm still green after each change
4. Commit and push after each confirmed passing state

---

## What the next session should NOT do

- return to setup work
- broaden scope
- add features unrelated to QA rule quality
- skip pytest before committing

---

## Current weakness summary

1. No coordinate consistency check yet
2. Only one DNO rulepack (SPEN_11kV)
3. Input schema still narrow (one representative schema)
4. No browser E2E tests yet
5. Some MVP debt in route/code paths

---

## Short version

### What is complete
- full tool setup and bootstrapping
- rulepack architecture
- SPEN_11kV with real values
- 23 passing tests

### What is next
- coordinate consistency check
- SSEN_11kV rulepack
