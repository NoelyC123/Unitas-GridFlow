# Current Task

## Immediate task

The immediate task is:

**Approve Phase C implementation path and brief Cursor for execution.**

---

## Why this is the current task

**Evidence gathering is complete.**

You've provided 4 comprehensive technical specifications:
1. Live operational feedback (6 critical map issues)
2. Engineering analysis #1 (15 pages, 17 sources, ESQCR/PLS-CADD/NIE schema)
3. Field Maps + NIE validation (production evidence)
4. Final consolidated specification (8,604 words, definitive blueprint)

**All 4 sources independently validate Phase C C1-C4.**

Phase B (UI polish) is complete and shipped (298 tests passing).

The next uncertainty is NOT whether Phase C is correct.

The next uncertainty is: **Which implementation path?**

---

## What this task means

This task means:

**Choose one of three Phase C paths:**

### Path 1: Safe (6-8 weeks)
- C1-C2 first (feature filtering + lifecycle visualization)
- Validate on real jobs
- Then C3-C4 (stay evidence + span anomalies)
- **Pro:** Lower risk, validate in steps
- **Con:** Slower delivery

### Path 2: Fast (4-5 weeks) ⭐ **RECOMMENDED**
- All C1-C4 together
- Test after each package
- **Pro:** Fixes all 6 operational issues immediately
- **Con:** Slightly higher risk (but all 4 packages validated)

### Path 3: Conservative (6-7 weeks)
- Minimal warnings first
- Collect more evidence
- Then full C1-C4
- **Pro:** Most cautious
- **Con:** Delays solving known blockers

---

## Why Path 2 (Fast) is recommended

**Your evidence proves it:**

| Your Operational Issue | Engineering Spec | Field Maps Evidence | Final Spec | Phase C Fix |
|-----------------------|------------------|---------------------|------------|-------------|
| Context invisible (BLOCKER) | Secondary visual weight | Diamond symbols | Context/access records | C1 ✅ |
| Height misleading (BLOCKER) | Measured vs. Specification | Existing/Proposed distinction | Blank field framework | C1 ✅ |
| Symbols unclear | Shape ≠ Color paradigm | Feature type decoupled | Visual hierarchy | C1+C2 ✅ |
| Stay missing (BLOCKER) | Angle poles without stays | Mechanical support | Stay evidence | C3 ✅ |
| Span unclear | Anomaly detection | Route confidence | Span detection | C4 ✅ |
| Data insufficient | Curated popups | Design-critical first | Popup organization | C1 ✅ |

**All 6 are design blockers** backed by:
- Your live operational feedback
- Engineering analysis (17 sources)
- Field Maps production evidence
- 8,604-word consolidated spec

**Total work:** ~24 hours (Cursor)

**Interdependencies:** None (packages are independent)

---

## What success looks like

This task is successful when:

1. **You approve a Phase C path** (Path 1/2/3)
2. **I create CURSOR_BRIEF_PHASE_C.md** (extracted from your 8,604-word spec)
3. **You send Cursor the command** (copy/paste from brief)
4. **Cursor implements C1-C4** (~24 hours work)
5. **Tests stay green** (298 → should stay 298+)
6. **Validate on real jobs** (P011, P010, etc.)

---

## What NOT to do

Do NOT:

- Start Phase C without approval (wait for decision)
- Skip creating the Cursor brief (need full spec extraction)
- Assume Path 2 without confirming (you decide)
- Add features outside C1-C4 scope
- Work on Stage 4 yet (Phase C first)

---

## After Phase C approval

**When you approve (e.g., "Path 2"):**

1. **I create:** `CURSOR_BRIEF_PHASE_C.md`
   - Extract C1-C4 specs from your 8,604-word document
   - Add code patterns and examples
   - Provide file-by-file change lists
   - Include testing requirements
   - Add acceptance criteria

2. **I give you:** Cursor command (copy/paste ready)
   ```
   Phase C is approved. Read CURSOR_BRIEF_PHASE_C.md and implement
   packages C1-C4. Start with C1 (Feature-type filtering).

   Test after each package. All 298 tests must stay green.

   Report completion when all 4 packages are done.
   ```

3. **You send:** Command to Cursor

4. **Cursor implements:** C1 → C2 → C3 → C4

5. **Validate:** Test on real jobs (P010, P011, Gordon, Bellsprings)

---

## Phase C packages (ready)

### C1: Feature-Type Filtering + Blank Field Framework (3-4 hours)
**Fixes:** Context invisible, Height misleading, Symbols unclear, Data insufficient

**Your exact spec (from 8,604-word document):**
- Feature-type filters: existing/proposed/angle/stays/context/missing heights/missing specs/remarks
- Blank field framework: existing = measured height missing (BLOCKER); proposed = specification missing (REVIEW); context = hide height
- Visual symbols: Shape = asset type (EX/PR/A/ST/CTX), Color = QA status (grey/blue/red/orange)
- Popup organization: Identity → Physical → Electrical → Mechanical → Context → QA

### C2: Asset Lifecycle Visualization (4-5 hours)
**Fixes:** Symbols unclear (lifecycle states)

**Your exact spec:**
- 11 lifecycle states: existing/proposed/retained/recovered/replacement/repositioned/unmatched/suggested/confirmed
- Existing↔Proposed match visualization: dashed provisional lines
- Toggle layer on/off
- Popup lifecycle section

### C3: Stay Evidence at Angle Poles (4-5 hours)
**Fixes:** Stay missing (BLOCKER)

**Your exact spec:**
- Detect angle poles: >10° deviation OR function = "Angle"
- Scan for stay records within 20m
- Flag if missing: "⚠️ Angle pole — stay evidence not captured. Check field notes, photos or plan evidence."
- Show stay types where captured (Terminal/Angle/Tee-off/Tandem)
- Add filter: "Show angle poles missing stay evidence"

### C4: Span Anomaly Detection + Crossing Context (3-4 hours)
**Fixes:** Span unclear

**Your exact spec:**
- Calculate 3D span distance between consecutive poles
- Flag <10m: "Probable duplicate pole or GPS error"
- Flag >500m for 11kV/33kV: "Probable missing intermediate pole"
- Better crossing labels: "Road Crossing — Critical clearance check required" / "Wall/Fence — Access constraint"
- Add filters: "Show span anomalies" / "Show crossings requiring clearance"

---

## Evidence Base for Phase C (MUST USE)

All Phase C development MUST reference these 4 comprehensive specifications:

1. **Live operational feedback** (P011_OPERATIONAL_FEEDBACK_2026-04-30.md)
   - 6 critical map issues from real designer use
   - All issues map to Phase C C1-C4

2. **Engineering analysis** (GridFlow_Electrical_Survey_Review.docx)
   - 15 pages, 17 cited sources
   - ESQCR, PLS-CADD, NIE schema
   - Height vs. Specification problem
   - Shape ≠ Color paradigm

3. **Field Maps + NIE validation** (NIE_Fibrus_enhanced_Review_for_GridFlow_.docx)
   - Production Field Maps benchmarks
   - NIE 19-field MV_Poles schema
   - 15 review focus filters
   - Popup layout requirements

4. **Final consolidated specification** (Pro_GridFlow_Electrical_Survey_Review_Final_Detailed_.docx)
   - 8,604 words, 19 sections + 2 appendices
   - Complete technical blueprint
   - THIS IS THE DEFINITIVE SPEC FOR PHASE C

**Before implementing ANY Phase C package:**
- Read the relevant section from the 8,604-word spec
- Cross-reference with engineering analysis
- Verify against Field Maps evidence
- Use exact wording from specifications

**Do NOT:**
- Implement Phase C from memory
- Guess at requirements
- Skip reading the evidence
- Invent features outside C1-C4 scope

---

## Current approved focus

**Files likely involved (from your spec):**
- `app/templates/map_viewer.html`
- `app/static/js/map-viewer.js`
- `app/routes/map_preview.py`
- `app/qa_engine.py` (for C3/C4 logic)
- Tests as needed

**No other files should be touched** (Phase C scope only).

---

## Strategic note

Your 8,604-word consolidated specification says:

> "The most meaningful next improvement after current UI polish is to strengthen the map information model and popup behaviour."

**This is Phase C C1-C4 exactly.**

Your final recommendation:

> "GridFlow becomes genuinely valuable when it answers the design handoff questions more clearly than Field Maps: what was captured, what was not captured, what is existing, what is proposed, what is being replaced, what is only context, what evidence is missing, what remains provisional, and what needs human review before CAD/design."

**This is what Phase C delivers.**

---

## Domain validation questions (from your spec)

Your consolidated spec identified **15 questions requiring real surveyor/designer input**.

These should guide Phase C refinements where applicable:
1. How is proposed pole spec normally recorded?
2. What fields mandatory for existing poles?
3. What pole condition detail expected?
4. How are angle/terminal/intermediate structures identified?
5. When is a stay required?
6. How is stay bearing/direction measured?
7. What stay anchor info expected?
8. How are existing/proposed relationships captured?
9. Which line/conductor fields expected?
10. Which clearance/crossing records mandatory?
11. Which context features affect design readiness?
12. How are photos/remarks used by designers?
13. What's minimum evidence before CAD begins?
14. What's blocker vs warning vs observation?
15. How should GridFlow show evidence outside digital file?

**Phase C C1-C4 addresses questions 1-5, 8, 10, 13-14.**

---

## When to update this file

Update when:

- Phase C approval decision made
- Phase C implementation begins
- Phase C implementation completes
- Material change to immediate priorities

---

## Expected next update

This file should next be updated when:

**Phase C approval is given and CURSOR_BRIEF_PHASE_C.md is created**
