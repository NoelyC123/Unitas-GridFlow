# CURSOR HANDOFF — PHASE C2/D READY

**Date:** 2026-05-01
**Status:** READY FOR CURSOR
**Priority:** HIGH (Professional survey-display quality)

---

## WHAT TO TELL CURSOR

**Copy this exact command to Cursor:**

```
Phase C2/D is approved. This completes Phase C to professional survey-display standards.

Read the full specification:
/Users/noelcollins/Unitas-GridFlow/PHASE_C2_CURSOR_TASKS.md

Start with Package C2-1: Map UX Refinement (1 week / 8-10 hours)

Tasks:
1. Reduce marker sizes 25-40% (fix visual clutter)
2. Split right panel into "Map Layers" + "Review Filters" sections
3. Better EX/PR symbols: EX = square, PR = circle (shape + color clarity)
4. Angle as overlay badge on EX/PR markers (not separate type)
5. Context records muted/hidden by default (secondary visual weight)
6. Shorten match warnings + add visual dashed lines between EX/PR pairs
7. Update map key with real symbol examples

Test on Gordon or Bellsprings after implementation.
All 300+ tests must stay green.

Report completion when done. Do NOT proceed to Package C2-2 without approval.
```

---

## WHAT CURSOR HAS

1. **Complete specification:** `PHASE_C2_CURSOR_TASKS.md` (8,600+ words)
   - Package C2-1: Map UX Refinement (detailed)
   - Package C2-2: Popup Data Model Expansion (detailed)
   - Package C2-3: Field Maps Parity (optional)
   - Code examples for all changes
   - Asset-specific popup layouts
   - Full acceptance criteria

2. **Evidence documents** (already in repo):
   - `P011_OPERATIONAL_FEEDBACK_2026-04-30.md`
   - `AI_CONTROL/28_DOMAIN_REFERENCE_SUMMARY.md`
   - `AI_CONTROL/29_PRACTITIONER_REVIEW_SUMMARY.md`
   - `CURSOR_BRIEF_PHASE_C.md` (Phase C C1-C4 reference)

3. **Updated control files:**
   - `AI_CONTROL/02_CURRENT_TASK.md` (current focus)
   - `AI_CONTROL/00_PROJECT_CANONICAL.md` (project truth)

---

## TIMELINE

**Package C2-1:** 1 week (8-10 hours Cursor work)
**Package C2-2:** 1-2 weeks (12-16 hours Cursor work)
**Package C2-3:** Optional (4-6 hours Cursor work)

**Total Phase C2/D:** 2-4 weeks / 24-32 hours

---

## AFTER PHASE C2/D COMPLETE

**Validation on real jobs:**
- P010, P011, Gordon, Bellsprings

**Then decide:**
- Stage 4 (structured capture, tablets, photos) — 6-12 months
- OR more refinement based on validation
- OR operational use + adoption focus

---

## PROJECT CONTEXT (For Reference)

**Current state:**
- Phase C C1-C4 foundation complete (Cursor already did this)
- 300 tests passing
- Popups show ~12 fields
- Map UX needs professional refinement

**Phase C2/D goal:**
- Map UX professional quality (markers, symbols, panels)
- Popups show 25-35 fields (professional survey-display)
- Asset-specific layouts (existing vs proposed vs angle vs stay vs context)
- Field Maps display parity

**This brings GridFlow to professional survey-display standards BEFORE Stage 4 structured capture.**

---

## KEY FILES CURSOR NEEDS

**Primary specification:**
- `/Users/noelcollins/Unitas-GridFlow/PHASE_C2_CURSOR_TASKS.md`

**Evidence/context:**
- `/Users/noelcollins/Unitas-GridFlow/P011_OPERATIONAL_FEEDBACK_2026-04-30.md`
- `/Users/noelcollins/Unitas-GridFlow/AI_CONTROL/28_DOMAIN_REFERENCE_SUMMARY.md`
- `/Users/noelcollins/Unitas-GridFlow/AI_CONTROL/29_PRACTITIONER_REVIEW_SUMMARY.md`

**Code locations:**
- `app/templates/map_viewer.html` (map template)
- `app/static/js/map-viewer.js` (map rendering logic)
- `app/static/css/map-viewer.css` (map styles)
- `app/routes/map_preview.py` (popup data generation)
- `app/qa_engine.py` (field extraction logic)

---

**Everything is ready. Just give Cursor the command above.** ✅
