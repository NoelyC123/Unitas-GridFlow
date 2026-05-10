# 46 — Stage 4A Safety Audit

Snapshot: master HEAD `857861e`, audit date 2026-05-10.
Branch: `claude-code/stage4a-safety-harness-audit`

## Purpose

This document is the formal safety boundary audit for Stage 4A library
correctness work. It defines:

- What Stage 4A may touch (safe scope)
- What Stage 4A must not touch (forbidden scope)
- The current blocker state with audit evidence
- What Codex must prove before Stage 4A can merge
- What remains blocked after Stage 4A merges

This document supersedes any informal scope notes in earlier drafts.

---

## Current Stage 4 Isolation State (Audited)

As of master HEAD `857861e`, Stage 4 structured capture is fully isolated
from the runtime application.

### Evidence of isolation

| Surface | Audit finding |
|---------|--------------|
| `app/static/js/map-viewer.js` | Zero references to `structured_capture`, `stage4_future_capture`, or any Stage 4 field name |
| `app/routes/api_intake.py` | Zero references to structured capture schema or validators |
| `app/qa_engine.py` | Zero references to structured capture |
| `app/controller_intake.py` | Zero references to structured capture |
| `app/field_reference.py` | Sources are `survey`, `derived`, `trimble_attr` only. No `structured_capture` source |
| C2E2 popup groups | No Stage 4 schema fields in `POPUP_FIELD_GROUPS` |
| HTML templates | Zero Stage 4 references in any template |

This clean state is the audit baseline. The runtime leakage tests in
`tests/test_structured_capture_leakage.py` lock this baseline and must
continue to pass after Stage 4A.

---

## Known Blockers (Pre-Stage-4A State)

Three blockers were identified in `AI_CONTROL/43_STAGE4_READINESS_SPECIFICATION.md`
and documented in `AI_CONTROL/44_STAGE4_BLOCKER_FIX_PLAN.md`.

### VLD-1: `"none"` Blank-Token Bug

**Severity:** High
**File:** `app/structured_capture_validators.py`
**Audit finding:** `"none"` is present in `_BLANK_TOKENS` (line ~27).

```python
_BLANK_TOKENS: frozenset[str] = frozenset({"", "n/a", "na", "none", "null", "tbc", "?"})
```

**Effect today:** `is_blank("none")` returns `True`. When a surveyor records
`stay_type = "none"` (no stay fitted), the validator normalises it to `None`
(unspecified). The explicit negative evidence is silently erased.

**Fields affected:** `stay_type`, `equipment_type`, `lean_direction`,
`lean_severity` — all declare `"none"` as a valid enum member meaning
"explicitly absent/none".

**Fields NOT affected by VLD-1 fix:** `condition` does not include `"none"` in
its allowed values; it must continue to reject `"none"` after the fix.

**Harness tests:** `test_stage4a_safety_boundary.py::test_vld1_*`
All VLD-1 tests are `xfail(strict=True)` and will become passing once Codex
removes `"none"` from `_BLANK_TOKENS`.

---

### VLD-2: Missing Row Identity (`pole_id`)

**Severity:** Medium
**Files:** `app/structured_capture_schema.py`, `templates/structured_capture_template.csv`
**Audit finding:** `get_stage4_template_headers()` does not include `pole_id`.
`get_stage4_field_definition("pole_id")` returns `None`.

**Effect today:** Structured capture rows cannot be keyed to Trimble/map records.
When Stage 4C runtime integration starts, merge logic has no stable identity key.
Coordinate/proximity auto-matching would be tempting but unsafe.

**Required fix scope:**
- Add `pole_id` to `_FIELD_DEFINITIONS` in `structured_capture_schema.py`
- Make it required for evidence-bearing rows
- Update `templates/structured_capture_template.csv` headers
- Update `scripts/generate_structured_capture_template.py` if needed

**Harness tests:** `test_stage4a_safety_boundary.py::test_vld2_*`
All VLD-2 tests are `xfail(strict=True)`.

---

### VLD-3: Unregistered `structured_capture` Source

**Severity:** Low (no runtime impact today, blocks Stage 4D popup surfacing)
**File:** `app/field_reference.py`
**Audit finding:** `field_reference.py` defines only `survey`, `derived`, and
`trimble_attr` as source labels. `structured_capture` is not registered.

**Effect today:** None — Stage 4 is not wired into any popup/API/report path.
**Effect at Stage 4D:** If source registration is missing, popup trust labels
cannot distinguish Trimble measured values from structured supplementary capture.
C2E2 truthfulness could regress by implying Stage 4 values have survey authority.

**Required fix scope:**
- Add `structured_capture` to the recognised source vocabulary in `field_reference.py`
- Do NOT add Stage 4 fields to `POPUP_FIELD_GROUPS` or `FIELD_DEFINITIONS`
- Do NOT change the `source` value on any existing C2E2 field

**Harness tests:** `test_stage4a_safety_boundary.py::test_vld3_*`
VLD-3 xfail test will pass once the source label is registered.
The leakage test `TestFieldReferenceLeakage::test_structured_capture_not_in_live_source_labels`
must be updated after VLD-3 is legitimately fixed.

---

## Stage 4A Allowed Scope

Stage 4A may only touch:

| File/area | Allowed change |
|-----------|----------------|
| `app/structured_capture_schema.py` | Remove `"none"` from `_BLANK_TOKENS`; add `pole_id` field definition |
| `app/structured_capture_validators.py` | Fix `is_blank()` to exclude `"none"`; update required fields for `pole_id` |
| `scripts/generate_structured_capture_template.py` | Add `pole_id` to template header generation |
| `templates/structured_capture_template.csv` | Add `pole_id` column |
| `app/field_reference.py` | Register `structured_capture` source label only — no field additions |
| `tests/test_structured_capture_schema.py` | Add pole_id assertions |
| `tests/test_structured_capture_validators.py` | Add none-enum and pole_id assertions |
| `tests/test_generate_structured_capture_template.py` | Add pole_id header assertion |
| `tests/test_c2e2_popup_fields.py` | Add source-registration guard if needed |
| Stage 4 docs in AI_CONTROL/ | Update Stage 4A acceptance state if needed |
| `AI_CONTROL/03_WORKER_LOG.md` | Worker log entry |
| `AI_CONTROL/04_VALIDATION_LOG.md` | Validation evidence |
| `AI_CONTROL/05_HANDOFF.md` | Handoff update |
| `CHANGELOG.md` | Changelog entry |

---

## Stage 4A Forbidden Scope

Stage 4A must NOT touch:

| File/area | Why forbidden |
|-----------|--------------|
| `app/static/js/map-viewer.js` | Stage 4D only; popup surfacing not allowed yet |
| `app/routes/api_intake.py` | Stage 4C only; upload route not allowed yet |
| `app/controller_intake.py` | Stage 4C only; Trimble intake pipeline unchanged |
| `app/qa_engine.py` | Stage 4C only; QA rules cannot consume Stage 4 values yet |
| `app/geometry_pipeline.py` | Stage 4C only; geometry pipeline unchanged |
| `app/span_generator.py` | Stage 4C only; span generation unchanged |
| `app/field_validators.py` | C2E2 validators must not change |
| C2E2 popup field scope | Popup rows and groups must not change |
| `app/field_reference.py::POPUP_FIELD_GROUPS` | Stage 4 fields must not appear in popup groups |
| `app/field_reference.py::FIELD_DEFINITIONS` | Existing C2E2 field definitions must not change |
| Review OS behaviour | Review workspace must be untouched |
| `_archive/` | Archive must not be touched |

---

## Merge Gate for Stage 4A

Before merging `codex/stage4a-library-correctness-fixes` → master:

1. All `xfail` tests in `test_stage4a_safety_boundary.py` must now PASS
   (i.e., the `xfail` markers are satisfied — the code was fixed).
2. All leakage tests in `test_structured_capture_leakage.py` must PASS.
3. `pytest -v` must pass (full suite, 920+ tests, no regressions).
4. `pre-commit run --all-files` must pass.
5. No forbidden runtime files in the diff.
6. `python scripts/merge_safety_check.py codex/stage4a-library-correctness-fixes` must not BLOCK.
7. Completion report names VLD-1, VLD-2, VLD-3 as resolved with test evidence.

---

## What Remains Blocked After Stage 4A

| Area | Blocked until |
|------|--------------|
| Accepting Stage 4 CSV uploads | Stage 4C |
| Merging structured rows with Trimble records | Stage 4C |
| Coordinate/proximity matching | Not approved at any stage |
| Showing Stage 4 fields in popups | Stage 4D |
| Review workspace surfacing of Stage 4 | Stage 4D |
| C2E2 popup field scope changes | Only after Stage 4D approval |

---

## Go / No-Go Statement

**Go:** Stage 4A library correctness work on `codex/stage4a-library-correctness-fixes`.
**No-go:** Any work that would touch the forbidden scope above.
**No-go:** Combining Stage 4A fixes with upload route, popup, or review workspace changes.
