---
status: ACTIVE
created: 2026-05-10
branch: codex/stage4c-runtime-integration-architecture
---

# 57 — Stage 4C Runtime Boundary Rules

This document defines the **strict boundaries** for Stage 4 data access during Stage 4C (runtime intake). These rules prevent scope leakage and ensure Stage 4 data is isolated from the design output layer until Stage 4D formal approval.

---

## Core principle

**Stage 4 data is intake-layer only until Stage 4D.**

No Stage 4 field appears in:
- C2E2 popup (Review OS)
- Design Chain export
- PDF report generation
- QA output
- Any designer-facing report

Exception: After Stage 4D gate (future), Stage 4 appears in Review OS with explicit labels.

---

## File-level boundaries

### TOUCHABLE files (Stage 4C allows writes)

**`app/routes/api_intake.py`**
- Create `StructuredCaptureIntake` handler
- Parse CSV file from upload
- Call `validate_stage4_rows()` from library
- Execute merge algorithm (see 56)
- Persist `job_structured_capture` records
- Create audit logs
- Return merge result summary (JSON)

**`app/models/structured_capture_models.py`** (NEW)
- Define `JobStructuredCaptureRecord` class
- Define `MergeAuditLog` class
- Database migrations (alembic)

**`scripts/merge_safety_check.py`**
- Expand Stage 4C boundary validation
- Scan `api_intake.py` for illicit Stage 4 imports
- Verify no Stage 4 data creation outside api_intake.py

**`tests/test_stage4c_runtime_boundary.py`** (NEW)
- Verify Stage 4 records persist correctly
- Verify Trimble records unchanged after merge
- Verify no Stage 4 leak to popup fields
- Verify audit logging works

---

### FORBIDDEN files (Stage 4C must not modify)

**`app/qa_engine.py`**
- **Read-only access**: query Stage 4 records by pole_id
- **Forbidden**: create, update, or delete Stage 4 records
- **Forbidden**: surface Stage 4 fields in QA output
- **Rationale**: QA logic may change; Stage 4 must be immutable intake

**`app/routes/api_qc.py`**
- **Forbidden**: any Stage 4 field references
- **Forbidden**: return Stage 4 data to caller
- **Rationale**: QA results are distinct from intake

**`app/static/js/map-viewer.js`**
- **Forbidden**: any `stage4_` field references
- **Forbidden**: render Stage 4 data in popup
- **Rationale**: C2E2 popup is frozen until Stage 4D

**`app/dno_rules.py`**
- **Forbidden**: reference Stage 4 data for DNO rule selection
- **Rationale**: DNO rules are Trimble-based; Stage 4 is orthogonal

**`app/pdf_generator.py`**
- **Forbidden**: include Stage 4 fields in report output
- **Rationale**: PDF is Stage 1–3 evidence; Stage 4 is future

**`app/routes/api_export.py` (Design Chain export)**
- **Forbidden**: export Stage 4 records to Design Chain
- **Rationale**: Design Chain is Trimble-based; Stage 4 is advisory

---

## Data structure boundaries

### What Stage 4 records contain

`job_structured_capture` table:

```python
# ALLOWED to persist
pole_id, upload_id, merge_timestamp, merge_source, merge_ready, completeness,
conflict_with_trimble, unmatched_trimble,
condition, voltage_carried, stay_present, stay_type, lean_direction,
equipment_present, equipment_type, clearance_issues, defect_notes,
conductor_size, stay_required, lean_severity, verification_required,
confidence_level, capture_date, captured_by, capture_source
```

### What Trimble records contain (UNCHANGED)

`job_trimble_baseline` table: unchanged by Stage 4C merge.

### What C2E2 popup contains (UNCHANGED)

```javascript
// Allowed fields (from Trimble + Stage 1–3)
pole_id, type, material, class, classification, ...

// FORBIDDEN: any stage4_* or new Stage 4 field
// Exceptions: structure_type, asset_intent, material (legitimate shared names)
//   → Already in C2E2 from Trimble, no conflict
```

---

## Query boundaries

### Allowed queries (Stage 4C intake layer)

```python
# api_intake.py can query Stage 4 for:
- Does this pole_id have existing Stage 4 record? (duplicate check)
- What are all Stage 4 records for this job? (merge summary)
```

### Forbidden queries (all other layers)

**qa_engine.py**:
- ❌ Cannot query Stage 4 to influence QA severity
- ❌ Cannot include Stage 4 completeness in PASS/FAIL decision
- ❌ Cannot use Stage 4 confidence_level for alerting

**map-viewer.js**:
- ❌ Cannot fetch Stage 4 records
- ❌ Cannot display Stage 4 fields in popup

**pdf_generator.py**:
- ❌ Cannot query Stage 4 records
- ❌ Cannot include Stage 4 evidence in report

---

## Feature flag requirement

**Stage 4C data must be gated behind a feature flag.**

```python
# In config.py
FEATURE_STAGE4C_INTAKE_ENABLED = False  # Starts disabled

# In api_intake.py
@app.post('/api/intake/stage4-csv')
def upload_stage4_csv():
    if not current_app.config.get('FEATURE_STAGE4C_INTAKE_ENABLED'):
        return {'error': 'Stage 4C intake disabled'}, 403
    # ... merge logic
```

**When to enable**:
- Only after Stage 4C go/no-go gate passes (document 50)
- Only after real field pilot succeeds (document 59)
- Only after merge_safety_check.py validates boundaries
- Explicitly set by operator (not auto-enabled by deployment)

---

## Validation: leakage guard suite

Automated checks run pre-merge:

### 1. Import scanning (`scripts/merge_safety_check.py`)

```bash
# Stage 4C boundary check
# Scan files for Stage 4 imports and field references
# Report: any imports of structured_capture outside api_intake.py
# Report: any stage4_* field references in forbidden files
```

Must pass:
- No imports from `structured_capture_validators` outside `api_intake.py`
- No import of `JobStructuredCaptureRecord` outside `api_intake.py` and `structured_capture_models.py`
- No references to `stage4_` fields in `qa_engine.py`, `map_viewer.js`, `dno_rules.py`
- No references to structured_capture in `pdf_generator.py`

### 2. Test suite (`tests/test_stage4c_runtime_boundary.py`)

```python
# Test: Stage 4 records persist but don't appear in QA output
def test_stage4_intake_does_not_affect_qa():
    # Merge a Stage 4 CSV
    # Run QA
    # Assert: QA output is identical to pre-merge QA

# Test: Popup fields do not contain Stage 4 data
def test_popup_fields_have_no_stage4():
    # Fetch popup field groups from C2E2
    # Assert: no stage4_* fields, no new structured_capture fields
    # Exception: structure_type, asset_intent, material (shared names)

# Test: PDF report does not include Stage 4 fields
def test_pdf_report_excludes_stage4():
    # Generate PDF with Stage 4 records in job
    # Assert: PDF contains no Stage 4 field values

# Test: Design Chain export is unchanged
def test_design_chain_export_excludes_stage4():
    # Export to Design Chain
    # Assert: output is identical to pre-Stage 4C export
```

### 3. Manual boundary review

Before Stage 4C gate approval:
- [ ] Code review confirms no Stage 4 field references in forbidden files
- [ ] All tests in `test_stage4c_runtime_boundary.py` pass
- [ ] `merge_safety_check.py` reports no boundary violations
- [ ] Feature flag is set to False by default

---

## Job data flow (Stage 4C isolated)

```
┌─────────────────────────────────────────────┐
│ Review OS / Browser                         │
│ (C2E2 Popup, Map, QA Output)               │
│                                             │
│ Fields: Trimble baseline (unchanged)        │
│ Stage 4 data: HIDDEN                        │
└──────────────────┬──────────────────────────┘
                   │
                   │ queries (Trimble only)
                   ↓
┌──────────────────────────────────────────────┐
│ app/qa_engine.py                            │
│ (Read-only access to Stage 4 for future     │
│  QA enhancements, but NOT used in 4C)       │
└──────────────────┬──────────────────────────┘
                   │
                   │ reads Trimble
                   ↓
┌──────────────────────────────────────────────┐
│ Database                                     │
│                                              │
│ job_trimble_baseline (unchanged by 4C)      │
│ job_structured_capture (NEW — 4C only)     │
│ job_stage4_audit_log (NEW — 4C only)       │
└──────────────────┬──────────────────────────┘
                   ↑
                   │ writes (Stage 4C merge)
                   │
┌──────────────────────────────────────────────┐
│ app/routes/api_intake.py                    │
│ (Stage 4 CSV upload handler)                │
│                                              │
│ - Receive CSV upload                        │
│ - Validate (stage4_validators library)      │
│ - Merge (append-only, no overwrite)         │
│ - Log audit trail                           │
└──────────────────────────────────────────────┘
                   ↑
                   │
            ┌──────────────┐
            │ Surveyor CSV │
            └──────────────┘
```

---

## Enforcement checklist

✅ **Code review requirements**:
- [ ] No Stage 4 imports in `qa_engine.py`, `map_viewer.js`, `pdf_generator.py`
- [ ] No `stage4_` field references in designer-facing output code
- [ ] Feature flag present and defaults to False
- [ ] `api_intake.py` is sole writer to `job_structured_capture`

✅ **Test requirements**:
- [ ] `test_stage4c_runtime_boundary.py` exists and passes
- [ ] Leakage guard tests pass
- [ ] Integration test: merge doesn't affect QA output or popup

✅ **Scanning requirements**:
- [ ] `merge_safety_check.py` Stage 4C validator runs pre-merge
- [ ] No boundary violations reported
- [ ] CI block prevents merge if boundary violated

---

## Review gate

Before merging Stage 4C code to master:

1. **Code review**: verify boundary rules are hardened
2. **Test run**: all leakage guards and boundary tests pass
3. **Manual scan**: `merge_safety_check.py` reports green
4. **Feature flag check**: Stage 4C intake is disabled by default
5. **Sign-off**: Noel approves boundary enforcement

See `AI_CONTROL/50_STAGE4C_GO_NO_GO_GATE.md` for formal gate.
