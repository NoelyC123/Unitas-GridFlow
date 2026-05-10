# 48 — Stage 4A Runtime Leakage Guard

Companion to: [46_STAGE4A_SAFETY_AUDIT.md](46_STAGE4A_SAFETY_AUDIT.md)
Snapshot: master HEAD `857861e`, date 2026-05-10.

## Purpose

This document defines the runtime surfaces that Stage 4 structured capture
must not reach before the explicitly approved Stage 4C/4D phases, and
describes the automated mechanisms that detect premature leakage.

---

## Why Leakage Is the Primary Risk

The Stage 4 schema and validators are already on master. They are correct
Python code and import without errors. The risk is not that the code is
broken — the risk is that a future branch accidentally wires Stage 4 fields
or source labels into:

- The C2E2 popup renderer (map-viewer.js)
- The Flask upload route (api_intake.py)
- The QA issue engine (qa_engine.py)
- The Trimble controller intake (controller_intake.py)
- HTML templates shown to users

If any of these surfaces gain Stage 4 references before Stage 4C/4D, then:

- Popups could show empty Stage 4 sections ("Not captured" for 20+ fields)
- QA rules could penalise a job for not having structured capture data
- The upload endpoint could silently accept malformed Stage 4 CSVs
- C2E2 popup truthfulness could regress

---

## Leakage Detection Mechanisms

### 1. Automated leakage tests (run with pytest)

`tests/test_structured_capture_leakage.py` contains 19 tests across 7 classes.
These tests must pass on every branch that touches Stage 4 code.

| Class | Surface guarded | Key assertion |
|-------|----------------|---------------|
| `TestMapViewerLeakage` | `app/static/js/map-viewer.js` | Zero Stage 4 tokens; `hasValue()` count ≥ 43 |
| `TestApiIntakeLeakage` | `app/routes/api_intake.py` | No `structured_capture` import or reference |
| `TestQAEngineLeakage` | `app/qa_engine.py` | No Stage 4 schema/source references |
| `TestControllerIntakeLeakage` | `app/controller_intake.py` | No structured capture wiring |
| `TestC2E2PopupLeakage` | `app/field_reference.py` popup groups | No Stage 4 fields in popup groups or field definitions |
| `TestFieldReferenceLeakage` | Source vocabulary | Only known live sources |
| `TestReviewOSLeakage` | `templates/**/*.html` | Zero Stage 4 tokens in HTML templates |

### 2. Merge safety check (run before merging)

`scripts/merge_safety_check.py` has four Stage 4A-specific checks that fire
when the branch name starts with `codex/stage4a`, `claude-code/stage4a`, or
`stage4a`:

| Check | Level | What it detects |
|-------|-------|----------------|
| `stage4a_runtime_boundary` | BLOCK | Branch touched forbidden runtime files |
| `stage4a_map_viewer_boundary` | BLOCK | map-viewer.js modified in a Stage 4A branch |
| `stage4a_leakage_tokens` | WARN | Stage 4 tokens appear in added lines of non-library files |
| `stage4a_popup_test_coverage` | WARN | field_reference.py changed without popup test updates |

Run before merging any Stage 4A branch:

```bash
python scripts/merge_safety_check.py codex/stage4a-library-correctness-fixes
```

### 3. Worker safety check (run before starting work)

`scripts/worker_safety_check.py` — no Stage 4A-specific checks, but the
`check_git_working_tree()` check will catch uncommitted AI_CONTROL edits and
the `check_map_viewer_untouched()` check can be invoked with
`--forbid-map-viewer` to block map-viewer changes.

---

## Stage 4 Leakage Token Reference

The following tokens trigger leakage detection if they appear in added lines of
non-library runtime files:

| Token | Why it signals leakage |
|-------|----------------------|
| `structured_capture` | Stage 4 source label / import name |
| `stage4_future_capture` | Stage 4 status constant |
| `lean_direction` | Stage 4 structural field not in any C2E2 popup |
| `lean_severity` | Stage 4 structural field not in any C2E2 popup |
| `pole_class` | Stage 4 pole spec field — distinct from C2E2 `structure_type` |
| `pole_strength` | Stage 4 pole spec field |
| `pole_material` | Stage 4 pole spec field |
| `capture_source` | Stage 4 metadata field |
| `captured_by` | Stage 4 metadata field |
| `capture_date` | Stage 4 metadata field |

**Note:** `equipment_present` and `equipment_type` are intentionally excluded
from this list because they are used in the existing C2E2 popup context.

---

## Approved Leakage Exceptions

There are no approved leakage exceptions at Stage 4A.

At Stage 4C (controlled runtime integration), the following leakage is approved:

- `app/routes/api_intake.py` may import and use Stage 4 schema/validators to
  accept a Stage 4 CSV alongside a Trimble job upload.
- A new merge service may import Stage 4 validators for `pole_id` matching.

At Stage 4D (browser surfacing), the following leakage is approved:

- `app/static/js/map-viewer.js` may reference Stage 4 source labels and field
  values only after structured values are merged and labelled.
- `app/field_reference.py::FIELD_DEFINITIONS` may be extended with Stage 4
  fields only for display purposes, with `source="structured_capture"`.

---

## Updating the Leakage Tests

If Stage 4C or 4D work legitimately requires a leakage guard to be updated:

1. The update must be on the correct Stage 4 phase branch.
2. The PR description must explicitly name the guard being updated and why.
3. The guard must be narrowed, not removed (e.g., allow `api_intake.py` to
   reference structured capture but do not remove the QA engine guard).
4. The `hasValue()` guard count baseline in `TestMapViewerLeakage` must be
   updated to the new count, not relaxed.

---

## Leakage Incident Protocol

If a Stage 4 leakage test fails unexpectedly on a non-Stage-4 branch:

1. Stop. Do not merge the branch.
2. Read the failing test to identify which surface and which token.
3. Check `git diff master` for the file mentioned in the test failure.
4. If it is an accidental addition: revert the change.
5. If it is an intentional Stage 4C/4D feature: confirm the current branch is
   the correct Stage 4 phase and update the guard per the rules above.
6. Re-run the full leakage test suite before proceeding.
