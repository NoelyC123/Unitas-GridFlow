# Stage 2C Polish Plan

## Purpose

Stage 2C is a small polish pass after Stage 2B validation acceptance.

The goal is to make the current D2D replacement outputs easier for a designer/domain reviewer to understand, without changing the core algorithms.

This is not a feature expansion stage.

---

## Current State

Stage 2B is implemented and validated as a strong working baseline.

Key commits:

- Stage 2A: `5f99bf0`
- Stage 2B: `54417ba`
- Stage 2B validation bugfix: `e51d0ee`
- Stage 2B validation acceptance: `3c06184`

Current tests: 211 passing.

Current outputs:

- clean D2D candidate export
- interleaved D2D working view
- detached/reference record handling
- section-aware sequencing
- EXpole matching
- context records retained in working view
- global design pole numbering
- confidence warnings

---

## Stage 2C Scope

Stage 2C should improve clarity, wording and reviewer confidence.

It should not change route sequencing, EXpole matching, detached detection, section detection or design numbering logic unless a validation bug is found.

---

## Proposed Stage 2C Tasks

### 1. Export Header Clarity

Improve CSV header comments so a designer immediately understands:

- which export they are viewing
- whether it is the clean analysis chain or interleaved working view
- that it is provisional and not final PoleCAD format
- what each warning means
- what “detached/reference” means

### 2. Section Summary In Exports

Add a compact section summary near the top of both exports:

- section count
- section IDs
- start / end sequence
- boundary point ID
- pole count
- whether overlap is present

This should make PR1/PR2-style behaviour easier to review.

### 3. Detached / Reference Section Wording

Make the detached section clearer:

- label records as `Detached / Reference / Not Required`
- include `Detach_Reason`
- explain that these records are retained for traceability but excluded from main design chain logic

### 4. Confidence Warning Wording

Improve high-ambiguity warning wording so it is useful but not alarming.

Suggested meaning:

> Route sequence was produced, but file order and spatial order differ significantly. Designer review is recommended before using this output for design.

### 5. UI Label Clarity

Review map page download button labels.

Current labels should clearly distinguish:

- clean chain export
- D2D working/interleaved export

Suggested labels:

- `Download Clean Chain Export`
- `Download D2D Working View`

### 6. Validation Guide

Add a short markdown guide explaining how to validate Stage 2 outputs.

Possible file:

- `AI_CONTROL/15_STAGE_2_EXPORT_VALIDATION_GUIDE.md`

Guide should explain:

- which real files to upload
- which exports to download
- what to check for Gordon
- what to check for `4-474`
- what to check for `513`
- what to check for `474c`
- what “pass” looks like

### 7. Current State Documentation

Update project source-of-truth docs after Stage 2C:

- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/04_SESSION_HANDOFF.md`
- `README.md` if needed
- `CHANGELOG.md`
- `AI_HANDOVER_PACK/`

Only do this after Stage 2C implementation/validation is complete.

---

## Out Of Scope

Stage 2C must not add:

- final PoleCAD-specific export
- manual section selection UI
- photo handling
- tablet capture
- live sync
- designer workspace
- DNO submission layer
- new QA rule expansion
- new route sequencing heuristics unless a bug is found

---

## Success Criteria

Stage 2C is successful when:

- exports are easier to understand without needing code knowledge
- clean chain vs working view is obvious
- section summaries are visible
- detached/reference records are clearly explained
- confidence warnings are clear and useful
- validation steps are documented
- all tests still pass
- no Stage 3-6 scope has been pulled forward

---

## Recommended Next Action

Ask Claude Desktop for a light orchestration review of this Stage 2C scope.

If approved, ask Claude Code to implement Stage 2C as a narrow output/documentation polish task.
