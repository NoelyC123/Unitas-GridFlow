---
status: ACTIVE
created: 2026-05-10
branch: codex/stage4b-4c-safety-pilot-harness
---

# 49 — Stage 4B Acceptance Gate

This document defines the conditions that MUST be true before any Stage 4B
branch is merged to master.

Stage 4B is the **schema/validation validation-preview layer** — importing a
Stage 4 CSV, validating it against the schema, and returning a structured
preview result (rows accepted / rejected / warnings). No runtime upload route,
no popup changes, no QA engine changes.

---

## Phase definition

| Phase | Scope | Blocked until |
|---|---|---|
| Stage 4A | Library correctness (VLD-1, VLD-2, VLD-3) | ✅ Merged `bf9bc2d` |
| Stage 4B | CSV import + validation preview (no Flask) | This gate |
| Stage 4C | Controlled runtime intake (upload route) | `50_STAGE4C_GO_NO_GO_GATE.md` |
| Stage 4D | Browser popup surfacing | Separate gate (not yet written) |

---

## Acceptance criteria

All of the following must be TRUE before a Stage 4B branch merges to master.

### A — Library integrity preserved

| # | Criterion | How to verify |
|---|---|---|
| A1 | `pytest -v` passes with 0 failures | `pytest -v` |
| A2 | All Stage 4A tests still pass (VLD-1, VLD-2, VLD-3 regressions clean) | `pytest tests/test_stage4a_safety_boundary.py -v` |
| A3 | Leakage guard suite passes (Stage 4B must not leak into runtime files) | `pytest tests/test_structured_capture_leakage.py -v` |
| A4 | `pre-commit run --all-files` passes | pre-commit |

### B — Stage 4B scope boundary

| # | Criterion | How to verify |
|---|---|---|
| B1 | Stage 4B adds NO import routes, Flask routes, or upload handling | `grep -r "structured_capture" app/routes/` returns no new entries |
| B2 | Stage 4B adds NO changes to `app/qa_engine.py` | `git diff master app/qa_engine.py` is empty |
| B3 | Stage 4B adds NO changes to `app/static/js/map-viewer.js` | `git diff master app/static/js/map-viewer.js` is empty |
| B4 | Stage 4B adds NO changes to `app/field_reference.py` | `git diff master app/field_reference.py` is empty (VLD-3 is done) |
| B5 | Stage 4B adds NO changes to `app/controller_intake.py` | `git diff master app/controller_intake.py` is empty |

### C — Validation preview correctness

| # | Criterion | How to verify |
|---|---|---|
| C1 | CSV import reads a Stage 4 template CSV and returns a list of row dicts | Unit test |
| C2 | Each imported row is passed through `validate_stage4_row()` | Unit test |
| C3 | Import result carries `valid_count`, `invalid_count`, `warning_count` | Unit test |
| C4 | Import result carries per-row `merge_ready` flags | Unit test |
| C5 | Duplicate `pole_id` detection fires across rows (not just per-row) | Unit test: `validate_stage4_rows()` |
| C6 | Import rejects non-CSV input gracefully (returns error result, does not raise) | Unit test |

### D — Golden sample baseline

| # | Criterion | How to verify |
|---|---|---|
| D1 | At least one synthetic golden sample CSV exists in `tests/fixtures/stage4/` | `ls tests/fixtures/stage4/*.csv` |
| D2 | Golden sample includes: valid row, row with blank pole_id, row with invalid enum, duplicate pole_id pair | Coverage review |
| D3 | All golden sample rows produce expected validation outcomes | Parametrised test |

### E — Merge safety gate passes

| # | Criterion | How to verify |
|---|---|---|
| E1 | `python scripts/merge_safety_check.py <branch>` exits 0 | merge_safety_check |
| E2 | No BLOCK-level findings | merge_safety_check output |

---

## Stage 4B forbidden scope

The following are explicitly out of scope for Stage 4B. Adding any of these
requires a separate branch and gate:

- Upload route (`api_intake.py`) changes to accept Stage 4 CSV
- QA engine consuming Stage 4 values
- Popup renderer (`map-viewer.js`) Stage 4 fields
- Review OS template changes
- C2E2 popup field scope changes
- Geometry pipeline or span generator changes

---

## Gate verification command sequence

Run in this order before raising the merge PR:

```bash
pytest -v
pre-commit run --all-files
python scripts/repo_health.py
python scripts/merge_safety_check.py <branch-name>
```

All must exit clean.

---

## Gate owner

Noel Collins. No Stage 4B branch merges without this gate being passed.
