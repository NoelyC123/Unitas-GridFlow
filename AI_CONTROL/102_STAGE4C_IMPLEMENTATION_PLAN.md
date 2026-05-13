# Stage 4C Implementation Plan: Baseline-Field Integration Engine

## Executive Summary

- **Phase**: Stage 4C — Runtime baseline-field integration
- **Prerequisite**: Stage 4B validation (100% match rate achieved)
- **Duration**: 10-14 weeks
- **Scope**: Survey-to-design workflow automation (NOT final engineering design)
- **Limitation**: DNO engineering data still required for design authorization

## Stage 4C Objectives

### What Stage 4C DOES:

- ✅ Ingest baseline CSV (Trimble/DNO format)
- ✅ Import field evidence (photo + notes structure)
- ✅ Correlate baseline ↔ field via support numbers
- ✅ Score match confidence (HIGH/MEDIUM/LOW)
- ✅ Merge baseline + field into unified view
- ✅ Generate verification flags (`voltage_verification_required`, etc.)
- ✅ Produce designer review workspace
- ✅ Generate QA reports highlighting design blockers

### What Stage 4C DOES NOT DO:

- ❌ Final engineering design (needs DNO specs)
- ❌ Load calculations (needs conductor data)
- ❌ Compliance verification (needs DNO inspection history)
- ❌ Voltage determination (field observation is not authoritative)
- ❌ Pole class specification (not field-observable)
- ❌ Automated design authorization (designer review required)

## Implementation Phases

### Phase 4C.1 — Baseline Ingestion Engine (Weeks 1-3)

**Objective**: Parse and validate DNO/Trimble baseline CSV exports

**Components**:

1. CSV format detection (ENWL/NGED/SPEN/SSEN/UKPN/NPG)
2. Schema validation
3. Coordinate normalization (OSGB36 ↔ WGS84)
4. Support number extraction and normalization
5. Route sequence reconstruction
6. Voltage level parsing (where available)
7. Asset type classification

**Deliverables**:

- `gridflow/baseline/csv_parser.py`
- `gridflow/baseline/schema_validator.py`
- `gridflow/baseline/coordinate_transformer.py`
- `gridflow/baseline/support_number_normalizer.py`
- Pytest suite (≥80% coverage)

**Success Criteria**:

- Parse 100+ pole baseline from real ENWL CSV
- Handle malformed rows gracefully
- Validate support number uniqueness
- Generate baseline import report

**Edge Cases to Handle**:

- Missing support numbers (assign `UNKNOWN_NNN`)
- Duplicate support numbers (flag for resolution)
- Invalid coordinates (flag for review)
- Unknown voltage levels (mark as `REQUIRES_VERIFICATION`)
- Multi-circuit poles (preserve all circuits)

---

### Phase 4C.2 — Field Evidence Importer (Weeks 4-6)

**Objective**: Scan and inventory field evidence folders

**Components**:

1. Folder structure scanner (matches `AI_CONTROL/97` standard)
2. Photo inventory and metadata extraction
3. Notes parsing (`identity_notes.txt` structure)
4. Evidence quality scoring
5. Missing evidence detection
6. Duplicate detection

**Deliverables**:

- `gridflow/field/folder_scanner.py`
- `gridflow/field/photo_inventory.py`
- `gridflow/field/notes_parser.py`
- `gridflow/field/evidence_quality_scorer.py`
- Pytest suite (≥80% coverage)

**Success Criteria**:

- Scan 100+ pole field evidence folders
- Extract support numbers from folder names
- Count photos/screenshots/notes per pole
- Score evidence quality (HIGH/MEDIUM/LOW per `AI_CONTROL/96`)
- Generate field evidence inventory report

**Edge Cases to Handle**:

- Malformed folder names (flag for manual review)
- Missing subdirectories (flag as incomplete)
- Zero photos (mark as `INSUFFICIENT_EVIDENCE`)
- Non-standard notes formats (attempt parsing, flag uncertainties)
- Conflicting support numbers (flag for resolution)

---

### Phase 4C.3 — Matching Engine (Weeks 7-10)

**Objective**: Correlate baseline assets ↔ field evidence

**Components**:

1. Support number exact match
2. Coordinate proximity matching (±50m fallback)
3. Route context validation
4. Confidence scoring (per `AI_CONTROL/96` model)
5. Edge case handler (`NO_POLE_POPUP`, variant support numbers)
6. Conflict detector (baseline ≠ field)

**Deliverables**:

- `gridflow/matching/support_number_matcher.py`
- `gridflow/matching/coordinate_proximity_matcher.py`
- `gridflow/matching/confidence_scorer.py`
- `gridflow/matching/edge_case_handler.py`
- Pytest suite (≥80% coverage)

**Success Criteria**:

- Achieve ≥80% automated match rate on test datasets
- Handle P_LOCAL_001 edge cases (`NO_POLE_POPUP`, `903201A`)
- Generate match register (per `baseline_field_match_register.csv` format)
- Flag unmatched baseline poles
- Flag unmatched field evidence

**Matching Logic**:

1. Exact support number match → HIGH confidence (if evidence quality sufficient)
2. Support number match + coordinate proximity → HIGH confidence
3. Coordinate proximity only (±20m) → MEDIUM confidence
4. Coordinate proximity (±50m) + route context → MEDIUM confidence
5. No match found → Flag for manual review
6. Conflicting evidence → Flag for resolution

**Edge Cases to Handle**:

- Multiple baseline poles with same support number (flag)
- Multiple field folders claiming same support number (flag)
- Support number mismatch with coordinate match (flag for review)
- Baseline pole with no field evidence (mark as `UNVISITED`)
- Field evidence with no baseline match (mark as `EXTRA_POLE` or `ERROR`)

---

### Phase 4C.4 — Merge Engine & QA (Weeks 11-14)

**Objective**: Combine baseline + field into unified dataset with verification flags

**Components**:

1. Data merge logic (per `AI_CONTROL/98` authority hierarchy)
2. Verification flag generator
3. Conflict detector and reporter
4. QA validation report generator
5. Designer review workspace generator

**Deliverables**:

- `gridflow/merge/data_merger.py`
- `gridflow/merge/verification_flag_generator.py`
- `gridflow/merge/conflict_detector.py`
- `gridflow/merge/qa_report_generator.py`
- Pytest suite (≥80% coverage)

**Success Criteria**:

- Generate merged dataset with baseline + field + flags
- Produce QA report showing:
  - Match rate
  - Unmatched poles
  - Verification requirements
  - Design blockers
- Identify design-ready poles vs review-required poles
- Export merged dataset (CSV + JSON formats)

**Merge Logic** (per `AI_CONTROL/98`):

For each matched pole:

IDENTITY:

- `support_no`: baseline (authoritative)
- `coordinates`: baseline (survey-grade where source provides that quality)
- `pole_sequence`: baseline

CONDITION:

- `condition_observed`: field (current state)
- `defects_observed`: field (current state)
- `photo_evidence`: field

EQUIPMENT:

- `equipment_observed`: field (what is visible)
- `equipment_baseline`: baseline (if available)
- `equipment_conflict_flag`: if baseline ≠ field

ENGINEERING SPECS (REQUIRES DNO):

- `voltage_carried`: baseline IF available, else `REQUIRES_VERIFICATION`
- `conductor_size`: baseline IF available, else `REQUIRES_VERIFICATION`
- `pole_class`: baseline IF available, else `REQUIRES_VERIFICATION`

VERIFICATION FLAGS:

- `voltage_verification_required`: yes IF baseline voltage missing
- `conductor_verification_required`: yes IF baseline conductor missing
- `pole_class_verification_required`: yes IF baseline pole class missing
- `condition_verification_required`: yes IF severe defects observed
- `identity_verification_required`: yes IF match confidence = MEDIUM/LOW
- `equipment_conflict_flag`: yes IF baseline equipment ≠ field observation

**QA Report Structure**:

- Total poles in baseline: X
- Total poles with field evidence: X
- Match rate: XX%
- HIGH confidence matches: X
- MEDIUM confidence matches: X (require review)
- LOW confidence matches: X (require review)
- Unmatched baseline poles: X (not surveyed)
- Unmatched field poles: X (not in baseline)
- Poles requiring voltage verification: X
- Poles requiring conductor verification: X
- Poles requiring pole class verification: X
- Poles with severe defects: X (DNO re-inspection needed)
- Design blockers: X poles cannot proceed without DNO data

---

## Stage 4C Architecture

### Technology Stack

- **Language**: Python 3.12+
- **Framework**: Core library (no web framework initially)
- **Testing**: Pytest (≥80% coverage required)
- **Data**: Pandas for CSV, pathlib for filesystem
- **Validation**: Pydantic for schema validation
- **Coordinates**: pyproj for coordinate transformation

### Module Structure

```text
gridflow/
├── baseline/
│   ├── csv_parser.py
│   ├── schema_validator.py
│   ├── coordinate_transformer.py
│   └── support_number_normalizer.py
├── field/
│   ├── folder_scanner.py
│   ├── photo_inventory.py
│   ├── notes_parser.py
│   └── evidence_quality_scorer.py
├── matching/
│   ├── support_number_matcher.py
│   ├── coordinate_proximity_matcher.py
│   ├── confidence_scorer.py
│   └── edge_case_handler.py
├── merge/
│   ├── data_merger.py
│   ├── verification_flag_generator.py
│   ├── conflict_detector.py
│   └── qa_report_generator.py
└── validation/
    ├── dataset_validator.py
    └── qa_validator.py
```

### Testing Strategy

- Unit tests for each module (≥80% coverage)
- Integration tests for full pipeline
- Edge case tests (P_LOCAL_001 scenarios)
- Malformed data tests
- Performance tests (1000+ poles)

---

## Stage 4C Success Criteria

### Technical Success

- ✅ Ingests real DNO baseline (100+ poles)
- ✅ Imports field evidence (P_LOCAL_001 structure)
- ✅ Achieves ≥80% automated match rate
- ✅ Generates merged dataset with verification flags
- ✅ Produces QA reports identifying design blockers
- ✅ Pytest coverage ≥80%

### Operational Success

- ✅ Designer can review matched poles
- ✅ Designer can identify verification requirements
- ✅ Designer can export design-ready subset
- ✅ Designer understands what requires DNO confirmation
- ✅ QA reports are actionable

### Governance Success

- ✅ Stage 4C does NOT overclaim capabilities
- ✅ Documentation clearly states DNO data requirements
- ✅ Verification flags are comprehensive
- ✅ Uncertainty is explicitly documented
- ✅ Trust hierarchy is maintained

---

## Stage 4C Limitations (Critical)

### What Stage 4C CANNOT Replace

1. **DNO Engineering Data**
   - Voltage specifications
   - Conductor sizes and types
   - Pole strength classes
   - Load calculations
   - Asset history

2. **DNO Inspection Records**
   - Compliance verification
   - Retention categories (CNAIM)
   - Inspection outcomes
   - Scheduled replacements

3. **Design Authorization**
   - Final engineering design
   - Load calculations
   - Compliance sign-off
   - DNO approval

### Design Blockers

Poles CANNOT proceed to final design without:

- ❌ DNO-confirmed voltage specification
- ❌ DNO-confirmed conductor specification
- ❌ DNO-confirmed pole class
- ❌ DNO inspection history (if available)
- ❌ Designer review and sign-off

Stage 4C identifies these blockers but does NOT resolve them.

---

## Stage 4C Risks and Mitigations

### Risk 1: Baseline CSV Format Variability

**Risk**: DNO CSV formats vary significantly between regions

**Mitigation**: Build format detection + manual schema mapping tool

### Risk 2: Field Evidence Structure Drift

**Risk**: Future field captures may not match P_LOCAL_001 structure

**Mitigation**: Strict evidence validation (`AI_CONTROL/97` standard enforcement)

### Risk 3: Overclaiming Capabilities

**Risk**: Users assume Stage 4C produces design-ready output

**Mitigation**: Comprehensive verification flags + QA reports highlighting blockers

### Risk 4: Match Rate Below Threshold

**Risk**: Real-world datasets may not achieve 80% automated match rate

**Mitigation**: MEDIUM/LOW confidence poles flagged for manual review

### Risk 5: Edge Cases Not Covered

**Risk**: Real-world complexity exceeds P_LOCAL_001 scenarios

**Mitigation**: Edge case handler + manual review workflow

---

## Next Steps After Stage 4C

### If Stage 4C Succeeds (≥80% match rate on real dataset):

1. ✅ Stage 4C workflow demonstrated on real dataset
2. ✅ Proceed to Stage 5: Designer Review Workspace UI
3. ✅ Integrate with GridFlow web application
4. ✅ Pilot with real ICP/contractor workflow

### If Stage 4C Fails (<80% match rate):

1. ❌ Root cause analysis
2. ❌ Refine matching model
3. ❌ Consider Phase 4 same-site pilot
4. ❌ Revise evidence structure standards

---

## Sign-Off Requirements

**Stage 4C Authorization:**

- Date: [To be determined after governance audit]
- Prerequisites: Stage 4B governance audit complete
- Approved by: Project lead
- Next milestone: 4C.1 baseline ingestion complete
