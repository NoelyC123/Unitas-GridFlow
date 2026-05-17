# Phase 4 Lessons Learned

**Date:** 2026-05-17
**Job:** P_LOCAL_002
**Final verdict:** CONDITIONAL GO (IMPROVED) — after content fixes applied
**Reference:** `AI_CONTROL/98_PHASE_4_VERDICT.md`

---

## What Worked Well ✅

### 1. Conservative Methodology — Data Integrity Over False Completeness

**Decision:** When ENWL screenshots for Poles 10 and 12 did not show readable coordinate
values, Codex declined to fabricate values. Coordinate rows were left blank and the gap
was documented.

**Impact:** Two honest gaps documented instead of two plausible-but-wrong values in the
baseline. The coordinate completeness review (`P_LOCAL_002_COORDINATE_COMPLETENESS_REVIEW.md`)
accurately reflects reality.

**Lesson:** Conservative > complete when evidence is unclear. A blank row with a named
flag is more useful than a made-up value that passes validation silently and corrupts
downstream work.

**Apply to:** All future data extraction tasks. Blank + flagged is always preferable to
inferred + silent.

---

### 2. Structured Evidence Organisation — Folder Structure Scales

**Approach:** Uniform pole folder structure across all 12 poles:
`XX_SUPPORT_XXXXXX/field_photos/`, `enwl_screenshots/`, `map_screenshots/`, `notes/`

**Impact:** `validate_phase4_matching.py` and `audit_plocal002_evidence.py` could scan all
12 folders without any per-pole configuration. The structure is also human-readable for
review without running any code.

**Lesson:** Folder structure that mirrors the evidence hierarchy scales well and makes both
automated and human validation straightforward.

**Apply to:** Standardise this structure as the required format for all future jobs
(P_LOCAL_003, Real DNO job). The audit script already assumes it.

---

### 3. Real Conflict Detection — Visual Inspection Found a Real Mismatch

**Example:** Pole 06 (support 900345) — ENWL records `pole_class = Stub Pole`.
Field photos show an H-pole / double-pole arrangement with a 100 kVA transformer.

**Impact:** A genuine discrepancy between the DNO asset register and the field observation
was caught. This is exactly the type of conflict GridFlow should surface before design begins.

**Lesson:** Visual inspection of field photos against ENWL popup attributes finds real
conflicts that automated matching alone cannot detect. The combination is necessary.

**Apply to:** Automate structural classification conflict rules in Stage 4C (see
`gridflow/conflict_detector/detector.py`). Use Pole 06 as the anchor test case.

---

### 4. Two-Layer Validation — Structural vs Content Quality

**Tool:** `scripts/validate_phase4_matching.py` for structural pass/fail gate;
`scripts/audit_plocal002_evidence.py` for evidence completeness audit.

**Result:** Structural validation (folder exists, photos present) passed 12/12.
Content quality (notes complete, not just present) initially revealed 2 gaps.

**Lesson:** Structural validation and content quality validation serve different purposes
and should be run separately. A file that exists is not the same as a file that is complete.
The audit script checks presence; content completeness requires a second check.

**Apply to:** Add note-content validation to the audit script (check for "Support UNKNOWN"
and empty/0-byte notes as distinct failure modes, not just absence).

---

### 5. Multi-AI Orchestration — Role Separation Prevents Conflicts

**Team used:** Claude Desktop (planning and decisions) + Codex (backend execution) +
Claude Code (parallel documentation and workspace work)

**Impact:** Multiple parallel tasks completed in a single working day without file
conflicts. Each worker stayed within its defined scope.

**Lesson:** AI role separation prevents overlapping edits, speeds execution, and allows
genuinely parallel progress on independent tasks. The key is explicit scope boundaries
per worker, not general instructions.

**Apply to:** Continue the orchestrated workflow for Stage 4C. Codex handles backend
modules and tests; Claude Code handles control documents, workspace display, and review
tasks; Claude Desktop makes scope decisions.

---

## What Didn't Work / Needed Fixing ⚠️

### 1. Screenshot Coordinate Extraction — Screenshots Not Always Machine-Readable

**Issue:** The ENWL Network Asset Viewer screenshots for Poles 10 and 12 did not expose
readable coordinate text in the current evidence captures. No BNG or lat/lon value was
legible.

**Impact:** 2/12 poles left with blank baseline coordinates. Coordinate completeness
remained at 10/12 = 83% at the end of the field-evidence review.

**Lesson:** Cannot rely solely on screenshots for coordinate extraction. Screenshots are
human-readable artefacts, not structured data exports.

**Fix needed:** Direct ENWL Network Asset Viewer lookup by FID (16788439 for 903101;
16938106 for 903203) to retrieve coordinates. This is a Noel action (Task 4 in
`30_STAGE4C_IMPLEMENTATION_PLAN.md`). The FIDs are confirmed; the lookup is straightforward.

---

### 2. Initial Notes Quality — File Presence ≠ File Complete

**Issue:** Pole 11 (903202) had a 0-byte notes file. Pole 12 (903203) had a placeholder
with "Support UNKNOWN" as the heading. Both passed the audit's presence check.

**Impact:** Content quality review revealed 10/12 complete at initial Phase 4 assessment.
Both poles required additional work to produce substantive notes.

**Lesson:** The audit script checks that a notes file exists (`notes_missing` flag). It
does not check whether the notes contain meaningful content. These are different checks
requiring different rules.

**Fix needed:** Enhance `audit_plocal002_evidence.py` (or add a separate content
validator) to flag: (a) zero-byte notes files, (b) notes files containing "Support UNKNOWN"
or equivalent placeholder markers.

---

### 3. Audit Timestamp Regeneration — Run-Time Noise in Git

**Issue:** Running `audit_plocal002_evidence.py --verbose` regenerates a timestamp in
`P_LOCAL_002_EVIDENCE_AUDIT.md`. Running the script multiple times during the same review
session caused `git status` to show the audit file as modified, creating noise.

**Impact:** Required multiple `git checkout -- <file>` reverts to keep the working tree
clean before commits.

**Lesson:** Idempotent-output audit scripts are easier to work with. A timestamp that
changes on every run makes git diff noisy and requires manual cleanup.

**Fix needed (low priority):** Consider using a content-hash or last-modified-date
comparison rather than a run timestamp, so re-runs only write the file if content
has actually changed.

---

## Critical Decisions Made

### 1. Accept 10/12 Baseline Completeness and Proceed

**Decision:** Proceed with 2 coordinate gaps documented rather than block Stage 4C
until gaps are closed.

**Rationale:** The two gaps are a baseline data gap, not an evidence or identity gap.
Both poles have confirmed ENWL FID, SPN, and support number. Blocking all of Stage 4C
for a 2-row coordinate lookup is disproportionate.

**Result:** CORRECT. Stage 4C proceeds; coordinate closure is Task 4 (a Noel action)
that can be done in under an hour once ENWL NAV is open.

---

### 2. Document Pole 06 Conflict; Do Not Resolve Prematurely

**Decision:** Flag the ENWL Stub Pole vs field H-pole discrepancy for investigation
rather than asserting which record is correct.

**Rationale:** The discrepancy could be a DNO asset register error (record not updated
after structural change), a field misidentification, or a genuine structural anomaly.
Asserting a resolution without DNO confirmation would be wrong.

**Result:** CORRECT. The conflict is documented in `98_PHASE_4_VERDICT.md` and the route
summary. Formal investigation is a Stage 6D task; premature resolution would undermine
the evidence model.

---

### 3. Stage 4C Timeline Is Days to Weeks, Not Months

**Decision:** Correct the expected timeline from "3–6 months" (as in some briefing
materials) to "days to weeks" for the first milestone.

**Rationale:** The pipeline already exists and runs. Stage 4C is validation hardening
against P_LOCAL_002, not a greenfield build. The difference matters for planning.

**Result:** CORRECT. All Stage 4C M1 tasks are achievable with existing code. No new
modules are required for the first milestone.

---

## Metrics Achieved

| Metric | Result | Assessment |
|---|---|---|
| Poles in P_LOCAL_002 | 12 | — |
| Structural match rate | 12 / 12 = 100% | ✅ |
| Content quality (after fixes) | 12 / 12 = 100% | ✅ |
| Baseline coordinate completeness | 10 / 12 = 83% | ⚠️ Documented gap |
| Conflicts detected | 1 (Pole 06) | ✅ Real conflict found |
| Conservative gaps handled | 2 (Poles 10, 12) | ✅ Integrity maintained |
| Time to complete Phase 4 validation | 1 day (2026-05-17) | ✅ |

---

## Recommendations for Stage 4C

1. **Coordinate closure:** Task 4 — use ENWL FID lookup; 1 hour; unblocks 12/12 claim
2. **Coordinate flag:** Task 2 — add `baseline_coordinate_missing` to `verification_flag_generator.py`; 1 day
3. **Conflict automation:** Task 3 — confirm / extend `conflict_detector/detector.py` for structural rules; 1–2 days
4. **Note content validation:** Add 0-byte and placeholder detection to audit script; 1 day
5. **P_LOCAL_003:** Plan capture after M1 complete; different route type; prove repeatability

---

## Stage 4C Readiness

| Gate | Status |
|---|---|
| Field capture methodology proven | ✅ |
| Baseline matching proven (100% structural) | ✅ |
| Real conflict detection working | ✅ (manual; automation pending) |
| Conservative data handling validated | ✅ |
| Phase 4 verdict issued | ✅ CONDITIONAL GO |
| Stage 4C authorised | ✅ |
| M1 blockers | None — Tasks 1–5 ready to start |
