# Stage 3B Planning Brief — Designer Review & Export Readiness

## Prepared by: Claude Desktop (Project Orchestrator)
## Date: April 2026
## Status: Planning brief — no implementation until approved

---

## Executive Summary

Stage 3B adds the ability for a designer to review, correct, and sign off on the auto-generated processing outputs before using them. Currently, every D2D export is provisional and auto-generated — the designer must either accept it as-is or revert to manual spreadsheet work to fix problems. Stage 3B closes this gap with a minimal review capability: a per-file review page showing EXpole pairings and section assignments, the ability to reassign EXpole pairings, a designer sign-off flag, and exports that respect reviewed decisions. This is the smallest step that makes the tool trustworthy enough for a designer to use the D2D output directly rather than treating it as a suggestion. It does NOT build a full design workspace, CAD editing, interactive map editing, or pole attribute editing. It adds exactly one editable decision (EXpole pairing reassignment) plus a sign-off mechanism.

---

## 1. Purpose (one paragraph)

Stage 3B exists because auto-generated output without designer review creates a trust gap. The tool currently produces EXpole pairings by spatial proximity, section boundaries by heuristic, and design pole numbering by sequential count — all provisional, all potentially wrong. A designer who receives this output has no way to say "I've checked this and it's correct" or "this pairing is wrong, pair EXpole 67 with Pol 40 instead of Pol 38." Without that capability, the tool remains a useful suggestion engine but not a trusted workflow replacement. Stage 3B adds the minimum review and correction capability needed for a designer to trust and use the D2D exports directly.

### Domain clarification: EXpole / PRpole relationship

`EXpole` means **existing pole**. `PRpole` means **proposed pole**. They are commonly close together on the map because the proposed pole is replacing the existing pole nearby. The reason for replacement may be pole defect/damage, land ownership or access constraints, or a design requirement to move the support slightly while keeping it in the same general location.

Stage 3B does not exist to explain this relationship. The tool already uses proximity to detect likely replacement pairings. Stage 3B exists so the designer can confirm or correct the automatic EXpole-to-proposed-pole match when multiple nearby poles or messy field data make the automatic pairing ambiguous.

---

## 2. Smallest Useful Stage 3B MVP

The MVP is three things:

**A. EXpole pairing review and reassignment.** The designer sees a list of all auto-detected EXpole-to-Pol pairings. For each pairing, they can confirm it, reassign the EXpole to a different proposed pole, or mark it as "unmatched / no replacement." This is the single most impactful edit because wrong pairings directly corrupt the D2D export — a designer who sees the wrong existing pole matched to the wrong proposed pole will immediately distrust the entire output.

**B. Designer sign-off flag.** A per-file "Reviewed" / "Not Reviewed" status. When the designer marks a file as reviewed, the exports carry a "Designer Reviewed" header instead of "Provisional — for designer review only." This is a trust signal, not a legal sign-off.

**C. Export readiness summary.** A review page showing: chain summary, EXpole pairings (with edit controls), section boundaries (read-only for now), confidence warnings, and the sign-off button. This page is the place where the designer does their review before exporting.

That's it. No section boundary editing, no pole attribute editing, no sequence reordering, no interactive map editing.

---

## 3. What should be reviewable/editable

**Editable in Stage 3B:**
- EXpole-to-Pol pairing assignment (reassign which proposed pole an existing pole is matched to)
- EXpole "unmatched" status (mark an EXpole as having no replacement — e.g. it's being recovered, not replaced)
- Designer review status (reviewed / not reviewed)
- Designer review notes (free text — "Checked pairings against notebook page 3, all correct" or "EXpole 67 reassigned — field notes confirm it replaces Pol 40 not Pol 38")

**Visible but read-only in Stage 3B:**
- Route chain sequence
- Section boundaries and section assignments
- Span distances and deviation angles
- Design pole numbering
- Confidence indicators
- Detached records
- Context features

---

## 4. Recommended starting point

**Option D: A very small combination — EXpole pairing review + sign-off.**

Reasoning:

- **Not Option A (EXpole only)** because pairing review without a sign-off mechanism leaves the output permanently marked "provisional" even after the designer has checked everything. The sign-off flag is trivial to implement and completes the workflow.

- **Not Option B (section boundary only)** because the auto-selected section boundaries from Stage 2B are reasonable enough for most files. The Gordon PR1/PR2 split was validated. Section boundary editing is more complex (requires chain recalculation, section renumbering, interleaved view regeneration) and less urgently needed.

- **Not Option C (export readiness checklist only)** because a read-only checklist with no edit capability doesn't reduce manual work — it just shows the designer what they already see in the CSV. The value comes from being able to fix the one thing most likely to be wrong (pairings).

- **Option D (pairings + sign-off)** is the sweet spot: one meaningful edit action, one trust signal, no architectural complexity. It can be built with the current Bootstrap/Flask stack using vanilla JS form submissions. No React, no drag-and-drop, no interactive map editing needed.

---

## 5. What must remain read-only

- Original uploaded CSV data (never modified)
- Auto-generated sequenced_route.json (preserved as the "original" auto-generated state)
- Route chain sequence order (editing sequence is Stage 5 territory)
- Section boundary positions (deferring to Stage 3B+ or 5)
- Design pole numbering (auto-regenerated from chain — not independently editable)
- Span distances and deviation angles (computed from coordinates — not editable)
- QA issues and evidence gates (Stage 1 output — not editable)
- meta.json original processing results
- Context features and detached records

---

## 6. Data model for reviewed decisions

The core principle: **never modify the original source records.** Store designer decisions as a separate overlay.

### New file: `review.json` (per file, alongside meta.json)

```json
{
  "file_id": "F001",
  "review_status": "reviewed",
  "reviewed_by": "designer",
  "reviewed_at": "2026-04-27T14:30:00Z",
  "review_notes": "Checked pairings against field notebook. EXpole 67 reassigned.",
  "pairing_overrides": [
    {
      "expole_point_id": "67",
      "original_matched_to": "38",
      "original_distance_m": 1.5,
      "reviewed_matched_to": "40",
      "reviewed_distance_m": 8.3,
      "reason": "Field notes confirm EXpole 67 is being replaced by Pol 40"
    },
    {
      "expole_point_id": "72",
      "original_matched_to": "71",
      "original_distance_m": 3.2,
      "reviewed_matched_to": null,
      "reviewed_distance_m": null,
      "reason": "EXpole 72 is being recovered, not replaced"
    }
  ],
  "version": 1
}
```

### How exports use reviewed decisions

When generating D2D exports:
1. Load sequenced_route.json (original auto-generated state)
2. Load review.json (if exists)
3. Apply pairing_overrides: for each override, replace the matched_expole references in the chain and matched_expoles lists
4. If review_status == "reviewed", change export header from "Provisional — for designer review only" to "Designer Reviewed — <reviewed_at>"
5. Original auto-generated pairings are always preserved in sequenced_route.json — never overwritten

### State transitions

```
uploaded → processed (auto-generated) → reviewed (designer confirmed/corrected)
                                       ↓
                                  reset to auto-generated (designer can undo all overrides)
```

"Reset to auto-generated" simply deletes review.json. The original sequenced_route.json is untouched.

---

## 7. Acceptance tests and validation

### Automated tests (pytest):

1. **test_create_review:** POST review with sign-off → review.json created with correct structure
2. **test_pairing_override:** POST override for one EXpole → review.json contains the override
3. **test_export_uses_override:** D2D export after override → CSV shows reassigned pairing, not original
4. **test_export_header_reviewed:** After sign-off → CSV header says "Designer Reviewed" not "Provisional"
5. **test_export_header_provisional:** Before sign-off → CSV header says "Provisional"
6. **test_reset_review:** DELETE review → review.json removed, exports revert to auto-generated
7. **test_original_preserved:** After override → sequenced_route.json is unchanged
8. **test_review_with_no_overrides:** Sign-off without any pairing changes → valid, just marks as reviewed
9. **test_mark_expole_unmatched:** Override matched_to to null → EXpole appears in unmatched section of export

### Manual validation with real files:

1. Upload Gordon Pt1 Original into a project
2. Go to review page → verify all 24 EXpole pairings are shown
3. Reassign one EXpole to a different proposed pole
4. Download D2D chain export → verify the reassigned pairing appears
5. Download D2D working view → verify the reassigned pairing appears
6. Click "Mark as Reviewed" → verify export headers change
7. Click "Reset to Auto-Generated" → verify exports revert to original pairings
8. Upload 4-474 → verify review page shows medium-confidence warning and correct pairings for NIE file

---

## 8. Risks and scope boundaries

### Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | **Scope creep: "let me also edit the sequence order."** Once editing is introduced, every auto-generated field becomes a candidate for editing. | High | Stage 3B scope is ONLY pairing reassignment + sign-off. Everything else is read-only. Enforce in code review. |
| 2 | **Frontend complexity: interactive pairing UI.** A dropdown or reassignment control for 24 EXpoles needs to work cleanly in the existing Bootstrap/Flask stack. | Medium | Use a simple HTML table with a dropdown `<select>` per EXpole row showing all proposed poles. No drag-and-drop, no React, no map-based interaction. |
| 3 | **review.json / sequenced_route.json desync.** If the file is reprocessed (re-uploaded or pipeline changes), the review.json overrides may reference point IDs that no longer exist. | Medium | When loading review.json, validate that all referenced point_ids still exist in sequenced_route.json. If any are stale, flag a warning on the review page: "Some reviewed pairings reference points that no longer exist in the current processing output. Please re-review." |
| 4 | **Multiple reviewers.** Two designers review the same file and overwrite each other's decisions. | Low (single user now) | Stage 3B: single reviewer, last-write-wins. review.json has a version counter. Multi-user conflict resolution is a deployment-stage concern. |
| 5 | **Designer signs off on wrong data.** The designer marks "reviewed" without actually checking, creating false confidence. | Low | The sign-off is a workflow signal, not a legal certification. The export still shows the data; the header just changes. The designer's name and timestamp are recorded. |

### Scope boundaries (hard limits)

Stage 3B will NOT include:
- Section boundary editing (defer to Stage 3B+ or Stage 5)
- Route sequence reordering
- Pole attribute editing (height, material, type)
- Interactive map-based editing (click-to-reassign on map)
- Design pole renumbering override
- Cross-file operations (reviewing pairings across multiple files)
- Batch review (reviewing all files in a project at once)
- Review history or undo beyond "reset to auto-generated"
- PoleCAD-specific export adjustments
- Cloud deployment, authentication, or multi-user
- Photo integration
- Tablet capture

---

## 9. Should Claude Code create the design brief document first?

**Yes.** Claude Code should create `AI_CONTROL/21_STAGE_3B_DESIGN_BRIEF.md` containing this brief, committed to the repo, before any implementation begins. This ensures:
- The brief is version-controlled and traceable
- Cursor/GPT can review it
- The domain owner can approve or amend it
- The implementation task references a committed document, not a conversation

This is a documentation-only task — no code changes, no tests, no pipeline modifications.

---

## Recommended Stage 3B MVP — Summary

| Component | What | Editable? |
|-----------|------|-----------|
| Review page | Shows chain summary, pairings, sections, confidence | — |
| EXpole pairings | List of auto-detected pairs with reassignment controls | Yes |
| EXpole unmatched | Mark an EXpole as "no replacement" | Yes |
| Designer sign-off | Reviewed / Not Reviewed flag with notes | Yes |
| D2D exports | Respect reviewed pairings, show reviewed/provisional header | Auto |
| Section boundaries | Shown for reference | Read-only |
| Route chain | Shown for reference | Read-only |
| Original data | Preserved in sequenced_route.json | Never touched |

---

## Non-Goals (explicit)

- This is not a designer workspace (Stage 5)
- This is not a CAD editing tool
- This is not a PoleCAD exporter
- This is not a multi-user review system
- This is not a section editor
- This does not touch the processing pipeline
- This does not change how files are uploaded or processed
- This does not add new QA rules

---

## Open Questions for Domain Owner (max 8)

1. **EXpole reassignment UI:** Should reassignment be a dropdown showing all proposed poles sorted by distance? Or a text field where the designer types the point ID? Dropdown is safer (no typos) but could be long for large files (100+ proposed poles). Recommendation: dropdown sorted by distance, showing top 10 nearest + "other" option.

2. **Should "Mark as Reviewed" require all pairings to be explicitly confirmed?** Or is it enough that the designer has seen the page and clicked the button? Recommendation: clicking "Mark as Reviewed" is sufficient — the designer is not forced to confirm each pairing individually. But the sign-off notes field should prompt "Have you verified pairings against field notes?"

3. **Should the review page be accessible from the map viewer or from the project overview?** Recommendation: from the project overview page, as a new "Review" action button per file, alongside Map/PDF/D2D.

4. **What should happen to the sign-off if the file is reprocessed?** If the same CSV is re-uploaded to the project and reprocessed, should the review be cleared? Recommendation: yes — reprocessing invalidates the review. review.json is deleted on reprocess. The designer must re-review.

5. **Should the PDF report reflect the reviewed state?** If the designer has reviewed and corrected pairings, should the PDF show the corrected pairings or the original auto-generated ones? Recommendation: defer PDF updates to a later polish pass. Stage 3B MVP only affects the D2D CSV exports.

6. **Is "designer" the right role name?** In your workflow, is the person reviewing the D2D output always called a "designer"? Or could they be a "D2D operator," "QA lead," or "project engineer"? The sign-off will say "Reviewed by: <role>." Recommendation: use "Designer" for now, make it configurable later.

7. **How many pairing reassignments are realistic per file?** Is it typically 0-2 corrections on a well-captured file, or could it be 10+ on a messy file? This affects whether the review page needs bulk operations or whether individual row-level edits are sufficient.

8. **Should the review page show the EXpole's REMARK value alongside the pairing?** For example: "EXpole 67 (remark: 'pole 5') → Pol 38 (3.2m)". The remark often contains the surveyor's pole number, which helps the designer verify the pairing against field notes. Recommendation: yes, always show the remark.

---

## Domain Owner Decisions — Approved Defaults

These decisions are approved for the first Stage 3B implementation task unless superseded by a later domain-owner note.

1. **EXpole reassignment UI:** use a dropdown/select control, not free text. Show the current match first, then nearby proposed poles sorted by distance. Include enough identifying detail to avoid confusion: point ID, feature code, design pole number if available, distance, and remark/location where available. For large files, start with nearby candidates and include an "other proposed pole" option if needed.

2. **Mark as Reviewed requirement:** do not require the designer to manually confirm every pairing one by one. The designer can review the page and mark the file reviewed. The review notes prompt should make clear that the designer is confirming they have checked the pairings as needed.

3. **Review page entry point:** add the review page from the project overview as a new per-file `Review` action, beside `Map`, `PDF`, `D2D Chain`, and `D2D Working`. Do not make the map viewer the primary review entry point in the MVP.

4. **Reprocessing rule:** if a file is reprocessed, any existing `review.json` is no longer valid and should be cleared or marked invalid. The designer must re-review against the new auto-generated output.

5. **PDF reviewed state:** defer PDF changes. Stage 3B MVP applies reviewed pairings and reviewed/provisional status to D2D CSV exports only. PDF can continue to show the current QA/reporting view until a later polish pass.

6. **Role label:** use `Designer` for now. This is a practical workflow label, not a legal approval role. It can be made configurable later if the workflow needs `D2D Operator`, `QA Lead`, or `Project Engineer`.

7. **Expected reassignment volume:** assume most files need zero to two manual corrections. The UI should support more, but the MVP does not need bulk operations.

8. **Show EXpole remark:** yes. Always show the EXpole remark/location value where available. It helps the designer connect the automatic pairing to field notes and surveyor pole references.

## Implementation Readiness Decision

Stage 3B may proceed to a scoped Claude Code implementation task after this brief is committed and reviewed. The first coding task should implement only:

- `review.json` overlay storage per file
- project-file review page
- EXpole pairing reassignment / unmatched status
- designer reviewed/not-reviewed flag with notes
- D2D CSV exports applying reviewed pairing overrides

Everything else remains out of scope for the first Stage 3B build.
