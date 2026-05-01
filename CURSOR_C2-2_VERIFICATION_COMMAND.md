# CURSOR VERIFICATION COMMAND — Phase C2-2 Readiness Check

**Copy this entire command to Cursor:**

```
Before starting Phase C2-2 (Popup Data Model Expansion), perform a complete readiness verification.

VERIFICATION CHECKLIST:

1. READ AND CONFIRM - Primary Specification:
   - Read: /Users/noelcollins/Unitas-GridFlow/PHASE_C2_CURSOR_TASKS.md
   - Locate: "Package C2-2: Popup Data Model Expansion" section
   - Confirm you can see:
     * Timeline: 1-2 weeks / 12-16 hours
     * Goal: Expand popups from 12 → 25-35 fields
     * 15-20 priority fields to add (Physical, Electrical, Mechanical, Evidence)
     * Asset-specific popup layouts (5 types)
     * Code examples for field extraction
     * Acceptance criteria

2. READ AND CONFIRM - Evidence Documents:
   - Read: /Users/noelcollins/Unitas-GridFlow/P011_OPERATIONAL_FEEDBACK_2026-04-30.md
   - Read: /Users/noelcollins/Unitas-GridFlow/AI_CONTROL/28_DOMAIN_REFERENCE_SUMMARY.md
   - Read: /Users/noelcollins/Unitas-GridFlow/AI_CONTROL/29_PRACTITIONER_REVIEW_SUMMARY.md
   - Confirm you understand:
     * Why popups need more fields (designer needs)
     * Evidence quality model (measured vs inferred vs missing)
     * Practitioner terminology requirements

3. READ AND CONFIRM - Current State Context:
   - Read: /Users/noelcollins/Unitas-GridFlow/AI_CONTROL/00_PROJECT_CANONICAL.md
   - Read: /Users/noelcollins/Unitas-GridFlow/AI_CONTROL/01_CURRENT_STATE.md
   - Read: /Users/noelcollins/Unitas-GridFlow/AI_CONTROL/02_CURRENT_TASK.md
   - Confirm you understand:
     * Current phase: Phase C2/D professional refinement
     * C2-1 complete, C2-2 next
     * Stage 4 deferred until C2/D validates
     * This is NOT new scope, completing Phase C to professional standards

4. VERIFY - File Access:
   - List files you'll need to modify for C2-2:
     * app/routes/map_preview.py (popup data generation)
     * app/qa_engine.py (field extraction logic)
     * app/static/js/map-viewer.js (popup rendering)
     * app/static/css/map-viewer.css (popup styling)
   - Confirm you can access all 4 files

5. VERIFY - Understanding of C2-2 Scope:
   Answer these questions in your response:
   - Q1: How many fields should existing pole popups show after C2-2? (Answer: 25-35)
   - Q2: How many asset-specific layouts are required? (Answer: 5 - existing/proposed/angle/stay/context)
   - Q3: What are the 4 field categories being added? (Answer: Physical, Electrical, Mechanical, Evidence)
   - Q4: Should you build photo upload functionality? (Answer: NO - just photo indicators/links)
   - Q5: Should you start Stage 4 structured capture? (Answer: NO - deferred)
   - Q6: What test count must be maintained? (Answer: 300+)

6. VERIFY - What NOT to Build:
   Confirm you will NOT implement:
   - Photo upload/storage (Stage 4)
   - Tablet capture forms (Stage 4)
   - PoleCAD export (future)
   - New QA rules (not in scope)
   - Control layer updates (Noel handles)

7. CONFIRM - Development Stages Roadmap:
   List the complete development stages you're aware of:
   - Stage 1: Post-survey QA gate (COMPLETE)
   - Stage 2: Design-ready handoff (COMPLETE)
   - Stage 3: Live intake platform (COMPLETE)
   - Phase B: UI polish (COMPLETE)
   - Phase C C1-C4: Map intelligence foundation (COMPLETE)
   - Phase C2-1: Map UX refinement (COMPLETE)
   - Phase C2-2: Popup data model (NEXT - what you're verifying for)
   - Phase C2-3: Field Maps parity (OPTIONAL - after C2-2)
   - Stage 4: Structured capture (FUTURE - deferred)
   - Stage 5: Designer workspace (FUTURE)
   - Stage 6: DNO submission layer (FUTURE)

8. REPORT - Readiness Status:
   After completing steps 1-7, report:
   - ✅ or ❌ for each verification step
   - Any files you CANNOT access
   - Any specifications that are UNCLEAR
   - Any questions before starting C2-2
   - Estimated timeline for C2-2 (should be 1-2 weeks / 12-16 hours)

ONLY after completing this verification should you proceed to C2-2 implementation.

If ANY verification step fails, STOP and report what's missing.

If ALL verification steps pass, report: "C2-2 readiness verification complete. Ready to begin implementation."
```

---

**END OF VERIFICATION COMMAND**
