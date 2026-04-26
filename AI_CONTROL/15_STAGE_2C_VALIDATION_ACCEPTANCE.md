# Stage 2C Validation Acceptance

## Purpose

This document records the validation result after the Stage 2C polish pass.

Stage 2C was a clarity and usability polish pass for the Stage 2 D2D exports. It did not change route sequencing, EXpole matching, detached detection, section detection or design numbering logic.

---

## Current Confirmed State

- Stage 2A implemented: `5f99bf0`
- Stage 2B implemented: `54417ba`
- Stage 2B validation bugfix: `e51d0ee`
- Stage 2B validation acceptance: `3c06184`
- Stage 2C polish plan: `d45be3d`
- Stage 2C implementation: `4ca6bc0`
- Validation file rename clarification: `23bb64a`
- Current tests after Stage 2C: 211 passing

---

## Stage 2C Changes

Stage 2C improved:

- CSV export headers
- clean chain vs working view naming
- section summary comments
- detached/reference record wording
- confidence warning wording
- map page download button labels
- export filenames

Stage 2C changed export filenames to:

- `<job_id>_d2d_chain.csv`
- `<job_id>_d2d_working_view.csv`

---

## Validation Files Reviewed

### Gordon

- `J17251_d2d_chain.csv`
- `J17251_d2d_working_view.csv`

### NIE 4-474

- `J57530_d2d_chain.csv`
- `J57530_d2d_working_view.csv`

### NIE 513

- `J85546_d2d_candidate.csv`
- `J85546_d2d_working_view.csv`

Note: 513 was validated before the final filename polish, but its content remained valid and the filename logic was verified by Gordon and 4-474 after Stage 2C.

### NIE 474c

- `J12946_d2d_chain.csv`
- `J12946_d2d_working_view.csv`

---

## Gordon Validation Result

Result: **passed**.

Confirmed:

- clean chain filename is correct
- working view filename is correct
- export headers are clearer
- section summary appears
- Section 1: seq 1-60, boundary point `4`, overlaps Section 2
- Section 2: seq 61-102
- point `4` remains the section boundary
- points `9` and `10` remain detached/reference records
- detached section wording is clear
- working view retains original file order with proposed, existing and context records inline

---

## 4-474 Validation Result

Result: **passed with expected sequence note**.

Confirmed:

- clean chain filename is correct
- working view filename is correct
- section summary appears
- one section is shown
- Sequence note appears:
  - `file order and spatial order differ for 42 of 43 chain records`
- context features remain visible, including LVxing, BTxing and Road
- output does not hide ambiguity

This is the expected high-ambiguity validation case.

---

## 513 Validation Result

Result: **passed**.

Confirmed:

- simple file behaves cleanly
- no warning required
- EXpole is matched
- Hedge context features are preserved
- working view keeps proposed, existing and context records inline

---

## 474c Validation Result

Result: **passed**.

Confirmed:

- clean chain filename is correct
- working view filename is correct
- section summary appears
- one section is shown
- 64 poles in the clean chain
- no high-ambiguity warning
- context features remain visible, including Road, Ignore and Hedge
- working view preserves inline records

---

## Acceptance Conclusion

Stage 2C is accepted.

Stage 2 now has:

- a clean route-chain export for analysis
- a D2D working view for designer review
- improved export naming
- clearer headers
- clearer section summaries
- clearer detached/reference wording
- clearer confidence/sequence note wording
- validated outputs across Gordon, 4-474, 513 and 474c

The next project decision should be a Stage 2 completion review.

---

## Recommended Next Action

Do not begin Stage 3 yet.

Run a Stage 2 completion review to decide whether D2D elimination / PoleCAD-ready output is complete enough for now.

The review should decide:

1. Whether Stage 2 can be marked complete for the current evidence set.
2. Whether any remaining Stage 2 polish is required.
3. What evidence would be needed later to strengthen Stage 2.
4. Whether the project should next move to Stage 3 planning.
