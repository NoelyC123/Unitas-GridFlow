# Stage 2B Decision Checklist

## Purpose

This checklist converts the Stage 2 validation evidence into explicit domain decisions before any Stage 2B implementation task is written.

No Stage 2B coding should begin until these decisions are reviewed and approved by the domain owner.

---

## Current Context

Stage 2A implemented a provisional D2D replacement candidate export.

It proved:

- route sequencing is possible from raw controller dumps
- EXpole matching can work from spatial proximity
- span-to-next and deviation angle calculations are useful
- a designer-readable D2D candidate CSV is achievable

Validation then showed Stage 2A is not enough to replace D2D because real working files are section-aware and interleaved.

Evidence:

- `AI_CONTROL/10_STAGE_2B_DESIGN_BRIEF.md`
- `AI_CONTROL/11_STAGE_2_VALIDATION_SUMMARY.md`
- Gordon manual PR1/PR2 split files
- NIE validation files

---

## Decision 1 — Keep Two Output Views

### Proposed Decision

Stage 2B should support two views:

1. **Clean Proposed Chain View**
   - proposed/structural route chain
   - EXpoles shown as replacement references
   - context features separated
   - useful for QA, span/angle review, and design-readiness analysis

2. **Interleaved D2D Working View**
   - proposed poles, EXpoles and context features shown inline within sections
   - closer to the manual PR1/PR2 working files
   - useful as a D2D replacement candidate

### Reason

Stage 2A's clean chain view is useful, but Gordon PR1/PR2 evidence shows the real working files keep EXpoles and context inline.

### Domain Owner Decision

- [ ] Approved
- [ ] Reject
- [ ] Needs discussion

---

## Decision 2 — Detached / Not-Required Records

### Proposed Decision

Records marked `not required`, or clearly separated from the main route by a large spatial gap, should:

- be retained for traceability
- be excluded from the main design chain
- not influence span calculations
- not influence section membership
- not influence design pole numbering
- appear in a separate `Detached / Reference Points` section

### Reason

Gordon points `9` and `10` are retained in the manual files after blank rows, but should not be treated as normal next poles.

### Domain Owner Decision

- [ ] Approved
- [ ] Reject
- [ ] Needs discussion

---

## Decision 3 — Section Split Candidates

### Proposed Decision

Stage 2B should treat `Angle` records as primary section split candidates.

Deviation angle should remain a supporting signal only.

Do not rely on a fixed `30 degree` threshold as the main sectioning rule.

Stage 2B should mark all `Angle` records as candidate split points, then use a provisional heuristic to suggest section boundaries that produce manageable/balanced section sizes.

Do not build manual section selection UI yet.

### Reason

The Gordon manual split happens at point `4` / pole 12, an `Angle` record with approximately 25.6 degrees deviation. The largest angle candidate was not the real PR1/PR2 split.

### Domain Owner Decision

- [ ] Approved
- [ ] Reject
- [ ] Needs discussion

---

## Decision 4 — Overlapping Section Boundaries

### Proposed Decision

Stage 2B should support shared boundary records.

The boundary record may appear as:

- the last record of Section N
- the first record of Section N+1

### Reason

Gordon PR1 ends around point `4` / pole 12, and PR2 starts again at the same shared point. This overlap makes each working chunk stand alone while maintaining route continuity.

### Domain Owner Decision

- [ ] Approved
- [ ] Reject
- [ ] Needs discussion

---

## Decision 5 — EXpole Handling In Working View

### Proposed Decision

In the clean proposed-chain view:

- EXpoles stay outside the main chain
- matched EXpoles appear as replacement references

In the interleaved D2D working view:

- EXpoles should appear inline in their original capture/file-order position within each section
- added columns should show their matched proposed pole, replacement relationship and role

### Reason

Stage 2A's EXpole matching is useful for analysis. Manual PR1/PR2 files show EXpoles are kept inline in working chunks.

### Domain Owner Decision

- [ ] Approved
- [ ] Reject
- [ ] Needs discussion

---

## Decision 6 — Context Feature Handling

### Proposed Decision

In the clean proposed-chain view:

- context features remain separated for reference

In the interleaved D2D working view:

- context features appear inline in their original file/capture order within each section
- each record has a clear `Role` or `Record_Type` column

### Reason

Manual PR1/PR2 files keep walls, fences, gates, tracks, trees and streams inline because they explain route and construction context.

### Domain Owner Decision

- [ ] Approved
- [ ] Reject
- [ ] Needs discussion

---

## Decision 7 — Design Pole Numbering

### Proposed Decision

Stage 2B may add a provisional `design_pole_number` field.

This value should:

- preserve original point IDs
- preserve original survey remarks
- be clearly marked provisional/editable
- not overwrite raw survey data
- be based on section-aware route order where possible
- use the simplest possible numbering rule at first: sequential structural-record counter within each section
- avoid attempting to exactly replicate the Gordon manual renumbering pattern until more evidence exists

### Reason

Manual PR1/PR2 files show design-style relabelling happened, but final numbering rules are not fully confirmed.

### Domain Owner Decision

- [ ] Approved
- [ ] Reject
- [ ] Needs discussion

---

## Decision 8 — Stage 2B Scope Boundary

### Proposed Decision

Stage 2B should be limited to:

- detached/not-required record separation
- Angle-aware section candidates
- section membership
- overlapping section boundary support
- interleaved D2D working view
- provisional design pole numbering
- tests and validation outputs

Stage 2B should not include:

- final PoleCAD-specific export format
- photo integration
- tablet capture
- live sync
- designer workspace
- DNO submission layer
- new QA rule expansion unless directly required by sectioning

### Reason

Stage 2 must remain focused on D2D elimination. Later roadmap stages should not be pulled forward.

### Domain Owner Decision

- [ ] Approved
- [ ] Reject
- [ ] Needs discussion

---

## Decision 9 — Validation Standard

### Proposed Decision

Stage 2B should be judged against real files, not abstract correctness.

Minimum validation set:

- Gordon raw file
- Gordon manual PR1 file
- Gordon manual PR2 file
- `2814_474c_raw_trimble_export.csv`
- `2814_4-474_raw_trimble_export.csv`
- `28-14 513 (2).csv`

Success means:

- Gordon output reflects the known PR1/PR2 style better than Stage 2A
- detached/not-required records are not in the main chain
- EXpoles and context can be reviewed inline in working view
- NIE files do not collapse into misleading route chains
- ambiguity is surfaced rather than hidden

High-ambiguity outputs should still be produced where possible, but the export must make confidence visible and warn the designer when a job has many medium/low-confidence records.

### Domain Owner Decision

- [ ] Approved
- [ ] Reject
- [ ] Needs discussion

---

## Recommended Approval

Recommended answer:

Approve Decisions 1-9.

Then ask Claude Desktop to review this checklist and confirm whether it is ready to become a narrow Stage 2B Claude Code task.

Do not ask Claude Code to implement until Claude Desktop has reviewed the checklist and the domain owner has approved the task.
