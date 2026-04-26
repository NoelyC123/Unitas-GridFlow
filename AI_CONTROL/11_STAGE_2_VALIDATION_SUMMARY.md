# Stage 2 Validation Summary

## Purpose

This document records the first validation pass after Stage 2A implementation.

Stage 2A implemented a provisional D2D replacement candidate output:

- route sequencing
- EXpole matching
- span-to-next calculation
- deviation angle calculation
- candidate section breaks
- D2D candidate CSV export
- `sequenced_route.json` per job

This summary is not a coding task. It records what the real validation files show and what should shape Stage 2B.

---

## Current Confirmed State

- Stage 1: complete
- Stage 2A: implemented
- Stage 2A commit: `5f99bf0`
- Current tests after Stage 2A: 186 passing
- Stage 2B design brief: `AI_CONTROL/10_STAGE_2B_DESIGN_BRIEF.md`
- Stage 2 validation direction commit: `6b027d1`

Stage 2 is not complete yet.

The current phase is validation and Stage 2B refinement.

---

## Files Reviewed

### Gordon / OSGB Evidence

- `validation_data/gordon_pt1/raw/Gordon Pt1 - Original.csv`
- `validation_data/gordon_pt1/split_for_polecad/Gordon Pt1 - POLES 1-12 - PR1.csv`
- `validation_data/gordon_pt1/split_for_polecad/Gordon Pt1 - POLES 12-20- PR2.csv`
- `validation_data/gordon_pt1/notes/source_note.txt`
- generated `J76076_d2d_candidate.csv`

### NIE / Irish Grid Evidence

- `validation_data/2814_474/raw/28-14 474c.csv`
- `validation_data/2814_474/raw/28-14 4-474.csv`
- `validation_data/2814_513/raw/28-14 513 (2).csv`

---

## Gordon Validation Findings

### What Worked

Stage 2A produced a useful first D2D candidate export for the Gordon file.

It successfully:

- produced a coherent route chain
- sequenced 104 proposed/structural route records
- matched all 24 EXpoles
- produced zero unmatched EXpoles
- separated context features into a reference section
- calculated span-to-next values
- calculated deviation angles
- flagged candidate section breaks
- produced a designer-readable CSV clearly marked as provisional

The EXpole matching looked sensible. Most offsets were only a few metres, which matches the real replacement-pole pattern.

### What Needed Refinement

The Gordon output also exposed that Stage 2A is not yet enough to replace D2D.

The largest issue is section logic.

Stage 2A flagged:

- a 39.9 degree angle at point `38`
- a large 1052.8 m jump before detached points `9` and `10`

However, the manual PR1/PR2 files show the real working split was around point `4` / pole 12, not point `38`.

This proves that sectioning is not simply:

> split at the largest angle

or:

> split at any angle above 30 degrees

The real split appears to be a practical/design section boundary around an Angle-type record that allows the route to be worked in useful chunks.

---

## Manual PR1/PR2 Evidence

The Gordon manual split files are the strongest evidence currently available for Stage 2B.

They show:

1. **PR1 and PR2 are manually split working chunks**
   - They are not abstract concepts.
   - They are real working CSV chunks used to make the route manageable.

2. **The split uses an overlap point**
   - PR1 ends around point `4` / pole 12.
   - PR2 starts again around point `4` / pole 12.
   - The shared point acts as a section anchor.

3. **EXpoles are kept inline**
   - Manual split files do not remove EXpoles from the working file.
   - They appear among the other survey records.
   - This means Stage 2B likely needs a D2D-style interleaved view, not only a clean proposed-chain view.

4. **Context features are kept inline**
   - Walls, fences, gates, tracks, trees and streams remain in the working chunks.
   - They provide useful route/design context.

5. **Detached / not-required records are retained separately**
   - Points `9` and `10` are marked `not required`.
   - They appear after blank rows.
   - They should not be treated as normal next poles in the main route chain.

6. **Manual design numbering/relabeling happened**
   - The split files show design-style pole numbering such as pole 1 through pole 20.
   - Original point IDs and survey feature codes are not the same as final design numbering.
   - Any tool-generated design numbering must be provisional and editable.

---

## NIE Validation Findings

The Stage 2A sequencer was run read-only against the three NIE/Irish Grid validation files.

### `28-14 474c.csv`

Result:

- CRS detected: `EPSG:29900`
- rows: 91
- structural records: 67
- context records: 24
- sequenced chain: 64
- matched EXpoles: 3
- unmatched EXpoles: 0
- candidate section breaks: 8
- confidence: 32 high, 32 medium

Interpretation:

The sequencer works technically, but this file shows route/section complexity.

There are many Angle records and several very short spans. The high number of medium-confidence records means simple nearest-neighbour sequencing is not enough to fully understand this job.

Stage 2B should handle this by adding section-aware logic rather than trying to make nearest-neighbour smarter in isolation.

### `28-14 4-474.csv`

Result:

- CRS detected: `EPSG:29900`
- rows: 83
- structural records: 48
- context records: 35
- sequenced chain: 43
- matched EXpoles: 5
- unmatched EXpoles: 0
- candidate section breaks: 2
- confidence: 1 high, 42 medium

Interpretation:

This is the strongest warning case.

The sequencer can produce an output, and EXpole matching works, but nearly the entire chain is medium-confidence. This suggests the file may include branch/section complexity, capture-order differences, very close features, or non-linear route structure.

Stage 2B must not assume a single greedy nearest-neighbour chain is always enough.

### `28-14 513 (2).csv`

Result:

- CRS detected: `EPSG:29900`
- rows: 11
- structural records: 9
- context records: 2
- sequenced chain: 8
- matched EXpoles: 1
- unmatched EXpoles: 0
- candidate section breaks: 0
- confidence: 8 high

Interpretation:

This file is simple and clean.

Stage 2A works well here. It confirms the sequencer can handle small Irish Grid jobs properly.

---

## What Stage 2A Proves

Stage 2A proves that Unitas GridFlow can move beyond QA-only output.

It can now produce a first structured survey-to-design handoff output:

- readable route chain
- replacement references
- spans
- angles
- context separation
- exportable CSV

This is a major step toward replacing manual D2D work.

---

## What Stage 2A Does Not Solve Yet

Stage 2A does not yet solve:

- real section splitting
- overlapping section boundaries
- detached / not-required record separation
- branch/tee/section complexity
- D2D-style interleaved working output
- design pole numbering
- editable designer approval of section boundaries
- final PoleCAD import formatting

These are Stage 2B / later Stage 2 concerns.

---

## Stage 2B Direction

Stage 2B should be planned around evidence from both Gordon and NIE validation.

Recommended Stage 2B scope:

1. **Detached record handling**
   - Detect records marked `not required`.
   - Detect records separated by very large route gaps.
   - Move them out of the main route chain into a detached/reference section.

2. **Angle-aware section candidates**
   - Treat Angle-type records as primary section split candidates.
   - Use deviation angle as a supporting signal only.
   - Do not rely on a fixed 30 degree threshold as the main split rule.

3. **Section-aware output**
   - Assign records to candidate sections.
   - Support shared/overlapping boundary records.
   - Allow sections such as PR1 / PR2 style working chunks.

4. **Interleaved D2D working view**
   - Keep proposed poles, EXpoles and context features together within each section.
   - Preserve original capture order where useful.
   - Add role/status columns to make the working file clearer than the legacy split.

5. **Clean analysis view remains**
   - Keep the Stage 2A proposed-chain output as an analysis view.
   - Do not replace it with only the interleaved view.

6. **Provisional design numbering**
   - Add generated design pole numbers only as provisional/editable values.
   - Preserve original point IDs and original survey remarks.

---

## Risks To Avoid

Do not:

- overfit the product to Stevie's legacy workflow
- treat the manual D2D split as the ideal design
- assume final PoleCAD format is known
- treat nearest-neighbour sequencing as final truth
- hide ambiguity behind false confidence
- jump to tablet/photo/designer workspace work yet
- build Stage 3-6 features before Stage 2 is validated

The goal is not to copy the old D2D process exactly.

The goal is to build a clearer, more structured, more auditable survey-to-design handoff.

---

## Current Recommendation

Do not start Stage 2B coding yet until the domain owner confirms the following decisions:

1. Stage 2B should support both:
   - clean proposed-chain analysis view
   - interleaved D2D working view

2. Detached/not-required records should be retained for traceability but excluded from main route chain logic.

3. Angle records should be primary section split candidates.

4. Design pole numbering should be provisional/editable, not final truth.

5. Stage 2B should be limited to section-aware sequencing and D2D candidate export refinement.

Once these decisions are confirmed, a narrow Stage 2B Claude Code task can be written.
