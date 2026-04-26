# Current Task

## Phase

**Stage 2 — Completion Review**

Stage 2A, Stage 2B and Stage 2C are implemented and validated against the current real-file evidence set.

The next task is to decide whether Stage 2 can be formally marked complete for now.

---

## Immediate next step

**Run the Stage 2 completion review.**

Primary review document:

- `AI_CONTROL/16_STAGE_2_COMPLETION_REVIEW.md`

Question to answer:

> Is Stage 2 complete as a validated provisional D2D replacement baseline for the current evidence set?

---

## Current Stage 2 capability

The tool can now produce structured D2D replacement outputs directly from raw controller dumps.

Current outputs:

- clean route-chain export: `<job_id>_d2d_chain.csv`
- interleaved working view: `<job_id>_d2d_working_view.csv`
- `sequenced_route.json`

Current capabilities:

- route sequencing
- EXpole matching
- span and angle calculations
- section-aware output
- detached/not-required record handling
- global provisional design pole numbering
- section-local sequence numbering
- confidence/sequence notes for ambiguous files

---

## What not to do

- Do not add features without validation evidence
- Do not build tablet/field capture (Stage 4) yet
- Do not build commercial packaging
- Do not expand rulepacks without real-file evidence
- Do not redesign architecture
- Do not begin Stage 3 until Stage 2 closure is explicitly approved

---

## Relevant files

- `AI_CONTROL/13_STAGE_2B_VALIDATION_ACCEPTANCE.md`
- `AI_CONTROL/14_STAGE_2C_POLISH_PLAN.md`
- `AI_CONTROL/15_STAGE_2C_VALIDATION_ACCEPTANCE.md`
- `AI_CONTROL/16_STAGE_2_COMPLETION_REVIEW.md`
- `app/route_sequencer.py`
- `app/routes/d2d_export.py`
- `tests/test_route_sequencer.py`

---

## Success criteria for Stage 2

Stage 2 can be marked complete if the domain owner accepts:

- raw controller dumps produce structured D2D replacement outputs
- clean route-chain and interleaved working views are both useful
- current real-file validation has passed
- remaining limitations are clearly documented
- final PoleCAD import format remains out of scope until verified with additional evidence
