# Session Handoff

## Session summary

This session completed two things:

1. **Validation batch 3** — fixed coord_consistency false positives for non-OSGB
   grid-derived files and suppressed structurally meaningless QA noise for raw
   controller dump inputs.

2. **Docs alignment batch** — aligned core project documents (00_PROJECT_CANONICAL.md,
   README.md, CLAUDE.md, CHANGELOG.md) with WORKFLOW_SYSTEM.md and the current
   validation-led project position.

---

## What was completed this session

### Validation batch 3 — coord_consistency fix + QA noise suppression

- `coord_consistency` CRS guard added to `app/qa_engine.py`. When `_grid_crs` is
  set and is not `EPSG:27700`, the check is skipped. Without this, every real NIE
  job (TM65 coordinates) produced a false positive on every pole — the check was
  converting lat/lon to OSGB27700 and comparing against TM65 easting/northing values
  which are in a different coordinate space.

- `filter_rules_for_controller()` added to `app/dno_rules.py`. Removes checks that
  produce noise rather than signal for controller dump files: `required`/`allowed_values`
  for `material` (absent from format), `allowed_values` for `structure_type` (feature
  codes Angle/Pol/Hedge are valid surveyor codes, not schema values), and
  `dependent_allowed_values` (structure_type → material mapping meaningless without
  material). Span distance, unique_pair, coordinate bounds, regex, and required pole_id
  are preserved.

- Filter applied in `app/routes/api_intake.py` when `file_type == "controller"`.
  Structured CSV path unchanged.

- 3 new focused tests added. 70 total tests passing (up from 67).

### Docs alignment batch

- `WORKFLOW_SYSTEM.md` added to repo by user — defines the operating model across all
  AI tools (ChatGPT orchestrator, Claude Code builder, Claude Desktop verifier).

- `AI_CONTROL/00_PROJECT_CANONICAL.md` updated:
  - core principle statement added (trusted gate, reliability/clarity/design-readiness)
  - `WORKFLOW_SYSTEM.md` added to active project structure and navigation
  - `app/controller_intake.py` added to key source files
  - phase status updated to include validation batches 2 and 3

- `README.md` updated:
  - test count corrected (38 → 70)
  - completed steps updated to include batches 2 and 3
  - stale limitation removed ("intake centered on structured CSV only")
  - `WORKFLOW_SYSTEM.md` added to project structure

- `AI_CONTROL/04_SESSION_HANDOFF.md` (this file) rewritten to current state.

- `CLAUDE.md` updated with WORKFLOW_SYSTEM.md reference.

- `CHANGELOG.md` updated with docs alignment entry.

---

## What is now true

### Project state

- Working local MVP exists
- Phase 1 (QA rule improvements) complete
- Phase 2A (input/header normalisation) complete
- Validation batch 2 (raw controller intake + completeness) complete
- Validation batch 3 (coord_consistency fix + QA noise suppression) complete
- 70 tests passing, pre-commit clean, CI active
- Raw GNSS controller dump files can be parsed end-to-end
- NIE real jobs no longer generate false positives from coord_consistency
- Controller dump QA output contains only meaningful signal

### Strategic state

- WORKFLOW_SYSTEM.md now defines the operating model for all tools
- Core principle: trusted gate between survey and design
- Project remains validation-led, not feature-led
- Next meaningful question: is the completeness output useful to a real designer?

---

## Current phase

**Working MVP + Phase 1 complete + Phase 2A complete + Validation batches 2 and 3 complete + current: Phase 2C — validation-led proof-of-value work**

---

## Next session should

1. Read `02_CURRENT_TASK.md`
2. Obtain user feedback on whether the completeness summary output is useful
3. If more real files are available, run them through the system and record:
   - whether intake handles them correctly
   - whether completeness output is the right level of detail
   - what a designer would actually need to act on the report
4. Consider Phase 3: surfacing completeness summary in the map view UI
5. Use real evidence to define the next precise development step

---

## What should not happen next

Do NOT:

- broaden the product into a larger platform
- add more rulepacks without validation evidence
- focus on commercial packaging before proof-of-value exists
- treat more feature work as the default next step

---

## What must remain true

- Scope stays narrow (pre-CAD QA only)
- Control layer remains the single source of truth
- `_archive/` is never used for active decisions
- `pytest -v` must be green after every code change
- Real-world validation evidence takes priority over abstract expansion
- WORKFLOW_SYSTEM.md defines tool roles — Claude Code is the execution engine only
