# GridFlow Development Roadmap — Next 10 Tasks

**Created:** 2026-05-02
**Current status:** 495 tests passing, commit `1326fc6`
**Next immediate task:** TASK_00_MAP_FINAL_CLEANUP.md (1-2 days)

---

## IMMEDIATE ACTION REQUIRED

**Task 0** is documented in: `TASK_00_MAP_FINAL_CLEANUP.md`

**After Task 0 complete, proceed with Tasks 1-10 below.**

---

## TASK 1: STAGE 4 POLISH — PRODUCTION-READY FIELD CAPTURE

**Timeline:** 2-3 weeks
**Target tests:** 510+
**Dependencies:** Task 0 complete

**What to build:**
1. Form UX refinement (validation messages, auto-save, field hints)
2. Photo handling (preview, compression, crop/rotate, count indicators)
3. Progress indicators (session timer, records counter, import progress)
4. Mobile browser testing (iOS Safari, Android Chrome, responsive layouts)
5. Real surveyor validation (1-2 field testers, feedback iteration)
6. Offline reliability (retry logic, partial sync, connection recovery)

**Key files:**
- `app/templates/field_capture_form.html`
- `app/static/js/field_capture.js`
- `app/field_capture.py`

**Tests:** Add ~15 tests for form validation, photo handling, mobile compatibility

---

## TASK 2: DESIGNER DASHBOARD

**Timeline:** 1-2 weeks
**Target tests:** 520+
**Dependencies:** Task 1 complete

**What to build:**
- Project list view (name, file count, status, last updated)
- Pending items summary (reviews not started, design decisions needed, missing evidence)
- Project cards with quick actions (Open map, Review, Export)
- Quick access (recent, starred, in-progress)

**Route:** `/designer/dashboard`

**Tests:** Add ~10 tests for project list, pending items, quick actions

---

## TASK 3: DESIGN TOOLBOX

**Timeline:** 2-3 weeks
**Target tests:** 535+
**Dependencies:** Task 2 complete

**What to build:**
1. **Span calculator** — sag, tension, clearance margin (catenary equation)
2. **Clearance checker** — measured vs required, PASS/WARN/FAIL (UK DNO tables)
3. **Material database** — timber/concrete/steel specs, cost estimates
4. **Loading calculator** — conductor weight + ice + wind
5. **Cost estimator** — material + installation per pole

**Key files:**
- `app/design_tools.py` (new)
- `app/templates/design_toolbox.html` (new)

**Tests:** Add ~15 tests validating all 5 calculations against DNO standards

---

## TASK 4: DESIGN NOTES & DECISION TRACKING

**Timeline:** 1-2 weeks
**Target tests:** 545+
**Dependencies:** Task 3 complete

**What to build:**
- Per-pole design notes (sticky notes on map or list)
- Note categories (clarification, material choice, pairing decision)
- Decision audit trail (who, when, what decided, why)
- Blocking notes (must resolve before export)

**Database:** Add `design_notes` table with audit trail

**Tests:** Add ~10 tests for note CRUD, audit trail, blocking logic

---

## TASK 5: INTEGRATED DESIGN BRIEF PDF

**Timeline:** 1 week
**Target tests:** 550+
**Dependencies:** Task 4 complete

**What to build:**

PDF with 6 sections:
1. Executive summary (project details, structure counts, readiness status)
2. Field capture summary (poles/spans captured, evidence gaps)
3. Designer decisions (pairings, materials, design notes)
4. Clearance calculations (all crossings with pass/warn/fail)
5. Design toolbox outputs (sag, loading, costs)
6. Export readiness checklist (reviews complete, blockers resolved)

**Key files:**
- `app/pdf_design_brief.py` (new)

**Tests:** Add ~5 tests for PDF generation, section completeness

---

## TASK 6: DNO COMPLIANCE CHECKLIST

**Timeline:** 1-2 weeks
**Target tests:** 560+
**Dependencies:** Task 5 complete

**What to build:**

Per-DNO compliance rulesets:
- **SPEN:** Asset ID format, required fields, format codes, submission template
- **SSEN:** Asset ID format, required fields (+ earthing), format codes
- **NIE:** Asset ID format, Irish Grid coordinates, NIE codes
- **ENWL:** Asset ID format, 11kV requirements, ENWL codes

**Compliance checker:**
- 🟢 Compliant (all required fields present, codes valid)
- 🟡 Warnings (recommended fields missing)
- 🔴 Blockers (required fields missing)

**Key files:**
- `app/dno_compliance.py` (new)

**Tests:** Add ~10 tests for each DNO ruleset (40 total)

---

## TASK 7: DNO EXPORT FORMATS

**Timeline:** 2 weeks
**Target tests:** 575+
**Dependencies:** Task 6 complete

**What to build:**

DNO-specific CSV exports:
- **SPEN CSV:** SPEN column names, asset codes, compliance flags, OSGB36 coords
- **SSEN CSV:** SSEN format
- **NIE CSV:** NIE format, Irish Grid coords (TM65/ITM)
- **ENWL CSV:** ENWL format

**Validation:** Only export if compliance passes (or warn if blockers)

**Key files:**
- `app/dno_exports.py` (new)

**Tests:** Add ~15 tests validating export formats match DNO templates exactly

---

## TASK 8: AUDIT TRAIL & SIGN-OFF

**Timeline:** 1 week
**Target tests:** 580+
**Dependencies:** Task 7 complete

**What to build:**

**Audit trail:**
- Track all changes (capture, review, approval events)
- SQLite table: `audit_log` (project_id, event_type, user, timestamp, description, before_value, after_value)
- Audit log page (chronological, filterable by type/user/date)
- Export audit log to CSV

**Three-stage sign-off:**
1. **Surveyor sign-off:** "I captured this data accurately"
2. **Designer sign-off:** "I reviewed this data and made design decisions"
3. **Project manager sign-off:** "This is ready for DNO submission"

**Sign-off page:** Shows all three, locks submission until complete

**Key files:**
- `app/audit_trail.py` (new)
- `app/templates/sign_off.html` (new)

**Tests:** Add ~5 tests for audit trail, sign-off workflow

---

## TASK 9: SUBMISSION PACKAGE GENERATION

**Timeline:** 1 week
**Target tests:** 585+
**Dependencies:** Task 8 complete

**What to build:**

Generate DNO-ready .zip package with 7 components:
1. DNO-format CSV (SPEN/SSEN/NIE/ENWL)
2. Audit trail CSV (complete change log)
3. Sign-off page PDF (all three sign-offs)
4. Map snapshot PNG (overview with legend, 300dpi)
5. Field photos (optional, organized by structure ID)
6. Design notes PDF
7. README.txt (what's in package, how to use)

**Package structure:**
```
J12946_DNO_Submission_2026-05-02.zip
├── README.txt
├── SPEN_Export_J12946.csv
├── Audit_Trail_J12946.csv
├── Sign_Off_Page.pdf
├── Map_Overview.png
├── Design_Notes.pdf
└── Photos/
    ├── pole_47_full.jpg
    └── ...
```

**Key files:**
- `app/submission_package.py` (new)

**Tests:** Add ~5 tests for package generation, structure validation

---

## TASK 10: POLECAD INTEGRATION PREP

**Timeline:** 2-3 weeks
**Target tests:** 600+
**Dependencies:** Task 9 complete

**What to build:**

**PoleCAD CSV format:**
- Columns: pole_number, easting, northing, height_m, material, pole_class, voltage_kv, conductor_type, conductor_size, phase_count, stay_type, equipment_type, clearance_flags, design_notes
- Pole numbers consecutive (no gaps)
- Material code mapping (GridFlow → PoleCAD codes)
- Clearance flags for unmeasured crossings
- Design notes export

**Validation before export:**
- ✅ All pole numbers consecutive
- ✅ No missing heights
- ✅ All material codes valid
- ✅ Clearance flags for unmeasured crossings
- ⚠️ Warn if design notes missing for proposed poles

**Key files:**
- `app/polecad_export.py` (new)

**Tests:** Add ~15 tests for format validation, pole numbering, material mapping

---

## TOTAL TIMELINE ESTIMATE

**Tasks 0-10:** 15-20 weeks (~4-5 months)

**Milestones:**
- End of Month 1: Task 0-1 complete (map cleanup + field capture polish)
- End of Month 2: Tasks 2-3 complete (dashboard + toolbox)
- End of Month 3: Tasks 4-5 complete (notes + PDF)
- End of Month 4: Tasks 6-7 complete (DNO compliance + exports)
- End of Month 5: Tasks 8-10 complete (audit + submission + PoleCAD)

---

## HOW TO USE THIS ROADMAP

**For each task:**
1. Read the task description above
2. Create detailed spec if needed (or work from this summary)
3. Tell Cursor: "Implement Task N from GRIDFLOW_ROADMAP.md"
4. Cursor reads this file and implements
5. Run tests, commit, push
6. Move to next task

**For Task 0 (immediate):**
- Read: `TASK_00_MAP_FINAL_CLEANUP.md`
- Tell Cursor: "Implement Task 0 from TASK_00_MAP_FINAL_CLEANUP.md"

---

**ROADMAP STATUS: READY FOR EXECUTION**

All 10 tasks are validated, scoped, and ready for sequential implementation.

Start with Task 0, then proceed 1→2→3→4→5→6→7→8→9→10.
