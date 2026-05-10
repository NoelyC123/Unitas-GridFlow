---
status: ACTIVE
created: 2026-05-10
branch: codex/stage4b-4c-safety-pilot-harness
last_reviewed: 2026-05-10
---

# 55 — Stage 4 Risk Register

This register tracks known risks in the Stage 4 structured capture
implementation. Risks are rated by likelihood (L) and impact (I) on a
1–3 scale. Score = L × I.

Review and update this register at each stage gate.

---

## Active risks

### R01 — Wrong pole_id match corrupts live job data

**Category**: Data integrity
**Likelihood**: 2 / **Impact**: 3 / **Score**: 6 (HIGH)

A Stage 4 row with a pole_id that partially matches a Trimble record (e.g.
`P008-01` vs `P008-001`) merges into the wrong pole record, silently replacing
real survey values with incorrect Stage 4 data.

**Current controls**:
- `validate_stage4_row()` rejects unsafe identity tokens
- Duplicate detection in `validate_stage4_rows()`
- `merge_ready` flag only set when pole_id is clean

**Mitigation needed for Stage 4C**:
- Exact-match only (no fuzzy matching)
- Log all merge operations with before/after record snapshot
- Trimble record values are never overwritten — Stage 4 values are additive only
- Integration test: Trimble-only job produces identical output after Stage 4C

---

### R02 — Fake completeness: Stage 4 fields present but meaningless

**Category**: Data quality
**Likelihood**: 3 / **Impact**: 2 / **Score**: 6 (HIGH)

A Stage 4 row passes validation (all required fields present) but optional
fields carry placeholder values (`unknown` everywhere, confidence_level=`low`).
The job appears more complete than it is.

**Current controls**:
- `classify_stage4_completeness()` distinguishes minimum / partial / complete
- `confidence_level` field available for self-rating

**Mitigation needed**:
- QA engine should warn when all optional Stage 4 fields are `unknown`
- Completeness classification used in PDF pre-design report (Stage 4D)
- Do not conflate `minimum` completeness with `complete` in any downstream display

---

### R03 — Stage 4 leaks into map popup before Stage 4D

**Category**: Scope leakage
**Likelihood**: 2 / **Impact**: 2 / **Score**: 4 (MEDIUM)

An AI worker or code path inadvertently surfaces Stage 4 fields in the C2E2
popup or Review OS before Stage 4D is formally approved.

**Current controls**:
- `tests/test_structured_capture_leakage.py` — 15 leakage guard tests
- `tests/test_stage4a_safety_boundary.py` — AST-based import scanning
- `merge_safety_check.py` — Stage 4 boundary checks
- `hasValue()` guard count baseline (currently 41; must not decrease)

**Mitigation needed**:
- Stage 4B/4C leakage guard expansion (this branch)
- Pre-merge review requires leakage tests to pass

---

### R04 — pole_id format mismatch between Trimble and Stage 4 CSV

**Category**: Integration correctness
**Likelihood**: 3 / **Impact**: 2 / **Score**: 6 (HIGH)

Trimble exports `P008-001` but the surveyor types `P008001` or `P008 001` in
the Stage 4 CSV. The pole_id match fails silently.

**Current controls**:
- `extract_stage4_row_identity()` normalises stripped whitespace
- `_UNSAFE_IDENTITY_TOKENS` rejects clearly blank values

**Mitigation needed**:
- Strip whitespace and normalise dashes/spaces on import
- Log and report all unmatched pole_ids in Stage 4C intake
- Real pilot validates format match on known job

---

### R05 — Stage 4B validation preview diverges from Stage 4C merge behaviour

**Category**: Implementation consistency
**Likelihood**: 2 / **Impact**: 2 / **Score**: 4 (MEDIUM)

Stage 4B validates a row as `valid` and `merge_ready`, but Stage 4C fails to
merge it due to a different code path (e.g. different normalisation, different
field lookup). User sees inconsistent results.

**Current controls**:
- Stage 4B must use exactly `validate_stage4_rows()` from the shared library
- Stage 4C must use the same function, not a re-implementation

**Mitigation needed**:
- Integration test: Stage 4B preview result == Stage 4C merge-accepted rows

---

### R06 — Schema drift — Stage 4 schema changes break existing validated CSVs

**Category**: Backward compatibility
**Likelihood**: 2 / **Impact**: 2 / **Score**: 4 (MEDIUM)

A schema change (new required field, changed allowed values) silently breaks
CSVs that previously validated cleanly.

**Current controls**:
- Golden sample suite catches schema regressions
- `structured_capture_schema.py` is library-only; changes require tests

**Mitigation needed**:
- Schema version field in template header
- Schema changelog section in `AI_CONTROL/` when allowed values change

---

### R07 — AI worker extends Stage 4 scope without gate approval

**Category**: Governance
**Likelihood**: 2 / **Impact**: 3 / **Score**: 6 (HIGH)

A Codex or Claude Code worker adds Stage 4 code to `api_intake.py`,
`qa_engine.py`, or `map-viewer.js` without Stage 4C or 4D gate approval.

**Current controls**:
- `merge_safety_check.py` Stage 4A boundary checks
- Leakage guard test suite
- Explicit "Do Not Start" list in `AI_CONTROL/05_HANDOFF.md`

**Mitigation needed**:
- Expand `merge_safety_check.py` Stage 4B/4C boundary checks (this branch)
- HANDOFF and CURRENT_TASK files always list forbidden scope explicitly

---

### R08 — Duplicate pole_id accepted across separate upload sessions

**Category**: Data integrity
**Likelihood**: 2 / **Impact**: 2 / **Score**: 4 (MEDIUM)

`validate_stage4_rows()` detects duplicates within a single CSV upload, but
two separate uploads for the same job each contain the same pole_id. The second
upload overwrites Stage 4 data from the first.

**Current controls**:
- Within-upload duplicate detection is implemented

**Mitigation needed**:
- Stage 4C must check for existing Stage 4 record with same pole_id before merge
- Conflict resolution strategy: reject second upload unless explicitly marked as update

---

## Closed risks

| ID | Description | Closed date | Resolution |
|---|---|---|---|
| VLD-1 | `"none"` in `_BLANK_TOKENS` erases valid stay/lean evidence | 2026-05-10 | Removed from blank tokens; field-aware none handling added |
| VLD-2 | No `pole_id` field in Stage 4 schema — no stable merge key | 2026-05-10 | `row_identity` group with `pole_id` required field added |
| VLD-3 | `structured_capture` not registered as source in `field_reference.py` | 2026-05-10 | Source label added (library-only, not popup wired) |

---

## Review schedule

Review this register at:
- Stage 4B merge
- Stage 4C go/no-go gate
- After each real field pilot
- After any schema change
