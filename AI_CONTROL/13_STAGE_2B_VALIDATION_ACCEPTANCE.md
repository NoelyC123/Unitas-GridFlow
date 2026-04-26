# Stage 2B Validation Acceptance

## Purpose

This document records the first real-file acceptance pass after Stage 2B implementation and the follow-up validation bugfix.

It confirms whether Stage 2B now provides a useful D2D replacement baseline.

---

## Current Confirmed State

- Stage 1: complete
- Stage 2A: implemented in commit `5f99bf0`
- Stage 2B: implemented in commit `54417ba`
- Stage 2B validation bugfix: implemented in commit `e51d0ee`
- Current tests: 211 passing
- Branch: `master`

Stage 2B is accepted as a strong working baseline, but Stage 2 is not declared fully complete until the next product decision is made.

---

## What Stage 2B Added

Stage 2B added:

- detached / `not required` record handling
- section-aware sequencing
- Angle records as section candidates
- `sections` metadata
- global `design_pole_number`
- section-local `section_sequence_number`
- interleaved D2D working view
- `/d2d/interleaved/<job_id>` endpoint
- confidence warnings for high-ambiguity files
- clean-chain export preserved and extended

---

## Validation Files Reviewed

### Gordon / OSGB

- `validation_data/gordon_pt1/raw/Gordon Pt1 - Original.csv`
- downloaded clean chain export: `J65371_d2d_candidate.csv`
- downloaded interleaved working view: `J65371_d2d_working_view.csv`
- manual split references:
  - `Gordon Pt1 - POLES 1-12 - PR1.csv`
  - `Gordon Pt1 - POLES 12-20- PR2.csv`

### NIE / Irish Grid

- `validation_data/2814_474/raw/2814_4-474_raw_trimble_export.csv`
- downloaded exports: `J63835_d2d_candidate.csv`, `J63835_d2d_working_view.csv`
- `validation_data/2814_513/raw/28-14 513 (2).csv`
- downloaded exports: `J85546_d2d_candidate.csv`, `J85546_d2d_working_view.csv`
- `validation_data/2814_474/raw/2814_474c_raw_trimble_export.csv`
- downloaded exports: `474c_d2d_candidate.csv.csv`, `474c_d2d_working_view.csv`

---

## Gordon Acceptance Result

Gordon is the strongest validation case because it has:

- raw Trimble export
- manual PR1/PR2 working splits
- known detached/not-required records

Validation result: **passed**.

Confirmed:

- Points `9` and `10` are no longer in the main chain.
- Points `9` and `10` appear in detached/reference output.
- Their remark now includes `pole not required`.
- The main chain contains 102 records.
- Section boundary is at point `4`, sequence `60`.
- This matches the manual PR1/PR2 split evidence.
- There are 2 sections.
- Global design numbering continues across the route.
- Interleaved working view keeps EXpoles and context inline.
- Clean chain view remains available for analysis.

Important note:

The interleaved view is not a final PoleCAD import format. It is a designer-readable D2D working view and remains provisional.

---

## NIE 4-474 Acceptance Result

Validation result: **passed with expected warning**.

Confirmed:

- Output is produced successfully.
- EXpoles are matched.
- Context features remain visible in the working view.
- Confidence warning appears:
  - `42/43` records are medium or low confidence.
- The tool does not hide ambiguity.

Interpretation:

This file is a useful warning case. The output is useful, but the designer must review route order against field notes or map context.

This is expected and correct.

---

## NIE 513 Acceptance Result

Validation result: **passed**.

Confirmed:

- Simple file behaves cleanly.
- 8 route records are sequenced.
- 1 EXpole is matched.
- 2 Hedge context records are preserved.
- No detached records.
- No confidence warning.
- Interleaved working view keeps proposed/context/existing records inline.

Interpretation:

This is a clean small-job sanity check. Stage 2B handles it properly.

---

## NIE 474c Acceptance Result

Validation result: **passed**.

Confirmed:

- Output is produced successfully.
- One section.
- No detached records.
- EXpoles are matched.
- Context features are preserved, including Hedge, Road and Ignore.
- Interleaved view keeps records inline.
- Clean chain view has route sequence, design pole numbers, section candidates and confidence.
- No high-ambiguity warning appears.

Note:

Downloaded filenames were accidentally swapped:

- `474c_d2d_candidate.csv.csv` contained the interleaved working view.
- `474c_d2d_working_view.csv` contained the clean chain candidate export.

The contents were still valid for review.

---

## Acceptance Conclusion

Stage 2B is accepted as a strong D2D replacement baseline.

It now does the key things the real validation files require:

- produces a clean analysis route chain
- produces a D2D-style interleaved working view
- separates detached/not-required records
- supports section-aware output
- preserves EXpole and context evidence
- adds global design pole numbering
- warns on high ambiguity
- works across OSGB and Irish Grid files

---

## What Stage 2B Still Is Not

Stage 2B is not:

- a final PoleCAD importer/exporter
- a final engineering design tool
- a tablet capture system
- a live-sync platform
- a designer workspace
- a DNO submission generator

It remains a provisional survey-to-design handoff output designed to reduce or replace manual D2D cleanup.

---

## Recommended Next Decision

The next project decision is whether to:

1. Do a small **Stage 2C polish pass**, focused on output clarity and validation reporting, or
2. Move to a **Stage 2 completion review**, deciding whether the current D2D replacement baseline is good enough to close Stage 2 for now.

Recommended direction:

Do a small Stage 2C polish pass before declaring Stage 2 complete.

Potential Stage 2C scope:

- clearer CSV titles/labels for clean chain vs working view
- clearer confidence and ambiguity explanation in exports
- explicit section summary rows
- clearer detached/reference section wording
- update README / AI_CONTROL current state / handover pack
- no new algorithmic work unless validation exposes a bug

Do not start Stage 3 until Stage 2 is deliberately closed.
