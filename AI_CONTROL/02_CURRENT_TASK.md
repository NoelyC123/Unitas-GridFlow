# Current Task

## Phase

**Stage 2 — D2D Elimination**

We are entering Stage 2 of the product vision.

---

## Immediate next step

**Run all 4 real validation files through the tool after Phase 3A fixes and verify output quality.**

Files to test:
- 28-14 513 (NIE, small job, 11 points)
- 2814_4-474_raw_trimble_export.csv (NIE, dense survey, 83 points)
- 2814_474c_raw_trimble_export.csv (NIE, separate section same area, 91 points)
- Gordon Pt1 Original (SPEN, large job, 157 points)

What to check:
- Span noise reduced (474 should drop from 42 to much fewer)
- BTxing/LVxing classified as context (not structural)
- Location field clean (no "Pol:LAND USE" contamination)
- Overall output quality — would this save a designer time?

---

## After validation confirms Phase 3A

Begin Stage 2 work: **D2D elimination.**

The goal is to make the tool produce PoleCAD-ready output directly from a raw controller dump, eliminating the manual D2D spreadsheet step.

This means:
- Automatic pole sequencing (spatial route order, not file order)
- Correct pole numbering
- Section splitting at sensible points (the Gordon PR1/PR2 split done automatically)
- Coordinate output in the format PoleCAD expects
- EXpole records matched to their route position, not left at the end of the file

---

## What not to do

- Do not add features without validation evidence
- Do not build tablet/field capture (Stage 4) yet
- Do not build commercial packaging
- Do not expand rulepacks without real-file evidence
- Do not redesign architecture

---

## Files likely involved for Stage 2

- `app/controller_intake.py` — route sequencing logic
- `app/qa_engine.py` — span calculations on spatial sequence
- `app/routes/api_intake.py` — output formatting
- New export module for PoleCAD-ready output
- Tests

---

## Success criteria for Stage 2

A raw controller dump goes in. A structured, sequenced, section-split output comes out that a designer could feed into PoleCAD without manually creating a D2D spreadsheet first.
