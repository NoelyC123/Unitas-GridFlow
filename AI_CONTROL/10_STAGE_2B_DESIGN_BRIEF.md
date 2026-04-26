# Stage 2B — Validation and Design Brief

## Purpose

This document records what Stage 2A got right, what it got wrong, what the manual PR1/PR2 files reveal about real D2D workflow, and what Stage 2B should do. It is a design brief, not a code task. No implementation should begin until this brief is reviewed and approved by the domain owner.

---

## 1. What Stage 2A Got Right

**Route sequencing works.** The nearest-neighbour chain correctly followed the spatial progression of the Gordon Pt1 route from point 1 (Angle, pole 1) through 102 proposed poles to point 5 (Angle, pole 2/20). The sequence matches the raw file's spatial pattern and the manual PR1/PR2 files confirm the same ordering.

**EXpole matching works.** All 24 EXpoles were correctly matched to their nearest proposed pole within the 15m threshold. Zero unmatched. The out-of-sequence EXpoles (points 67-72, captured after point 66 in the file but spatially located earlier in the route) were correctly matched by spatial position, not file position. The EXpole REMARK values ("pole 2", "pole 5", "pole 7" etc.) confirm the pairings are correct.

**Span and angle calculations work.** Spans are mostly in the 14-18m range, consistent with a refurbishment survey. Deviation angles correctly identify the major direction changes (39.9° at seq 7, 25.6° at seq 60, 47.4° at seq 102).

**Context feature separation works.** 27 context features (Wall, Fence, Gate, Track, Tree, Stream) correctly excluded from the structural chain.

**Confidence scoring works.** 102 of 104 records got "high" confidence (file order matched spatial order). The 2 "medium" records are points 9 and 10 (the detached "not required" points), which is correct.

**Graceful handling works.** The sequencer produced valid output, saved sequenced_route.json, populated meta.json summary, and the D2D export link appeared on the map page.

---

## 2. What Stage 2A Got Wrong or Only Partially Right

**Section break detection missed the real split point.** Stage 2A flagged two section breaks:
- Seq 7 (point 38): 39.9° deviation — a valid angle candidate but NOT where the real PR split happened
- Seq 102 (point 5): 47.4° deviation with 1,052m gap — the jump to the detached "not required" points

The actual PR1/PR2 split in the manual files is at **point 4 (Angle, "pole 11/12")**, which is seq 60 in the Stage 2A chain. This point has a 25.6° deviation angle — below the 30° threshold. The real split criterion is not "large angle" but "Angle-type structural point that represents a meaningful route junction or section boundary."

**Points 9 and 10 should not be in the main chain.** Stage 2A keeps them as seq 103-104 with a 1,052m span to the previous pole. The manual split files confirm they are retained after blank rows as reference, but they are not part of the main design chain. They should be separated into a "detached/not-required" section.

**EXpoles are separated from the chain, but the manual files keep them inline.** Stage 2A correctly excluded EXpoles from the proposed-pole chain for analysis purposes. However, the manual PR1/PR2 files show that the working D2D output keeps EXpoles interleaved in file order among the proposed poles. Stage 2B needs to support both views: a clean proposed chain (for analysis) and an interleaved working view (for D2D replacement).

**Context features are separated, but the manual files keep them inline too.** Same pattern — the manual splits preserve the surveyor's full capture order including walls, fences, tracks, gates, trees, streams. A working D2D view should include them.

**No section membership or section-aware output.** Stage 2A produces one flat chain. The manual files show the output should be section-aware: PR1 (poles 1-12) and PR2 (poles 12-20) with an overlapping boundary record.

---

## 3. What the Manual PR1/PR2 Files Reveal

### Split point location
The PR1/PR2 split is at point 4 (Angle, "pole 11" in the original, relabelled "pole 12" in the split). This is an Angle-type record at a meaningful route junction — the point where the line changes direction significantly (25.6° deviation). The split is NOT at the largest angle or the largest gap. It is at a named Angle point that the surveyor/designer chose as a logical section boundary.

### Overlap at boundary
PR1 ends with point 4 (Angle, pole 12). PR2 starts with point 4 (Angle, pole 12). The same physical point appears in both files. This is not a hard cut — it is a shared anchor record that lets each section file stand alone while maintaining continuity.

### EXpoles inline
Both PR1 and PR2 include EXpoles in their original file-order position among the proposed poles. EXpole 29 appears between points 28 and 30. EXpole 32 appears between points 31 and 33. The out-of-sequence EXpoles (67-72) appear at the same position as in the original file — after point 66. They are not moved to sit next to their matched proposed pole.

### Context features inline
Walls, fences, gates, tracks, trees, streams all remain in file order. They are not separated or removed.

### Design renumbering
The manual splits show that pole REMARKs were modified. In PR1, the trailing column has been edited to show sequential design pole numbers: "pole 1" through "pole 12". In PR2, the numbering continues: "pole 12" (shared start) through "pole 20". The original surveyor used angle numbering (1, 2, 3, 4, 5) which was replaced with sequential design numbers.

Additionally, the EXpole numbering was adjusted. In the original, EXpole 123 has REMARK "pole 13". In PR1, the trailing column shows "pole 12" — the design pole number, not the original REMARK. Similarly in PR2, EXpole 130 has REMARK "pole 14" in original but "pole 13" in the trailing column. This suggests the splitter was assigning design numbers to EXpoles based on their position in the route sequence.

### "Not required" handling
Points 9 and 10 appear after blank rows in both PR1 and PR2. They are retained as reference records but clearly separated from the main data by blank rows. Their REMARK includes "not required" as a trailing annotation.

---

## 4. What "Section-Aware Sequencing" Should Mean

Section-aware sequencing means the tool should:

1. Identify the full route chain (as Stage 2A does)
2. Detect candidate section split points — primarily at Angle-type records, not just at large deviations
3. Allow the user (or a heuristic) to select which candidates become actual section boundaries
4. Assign section membership to each record (Section 1, Section 2, etc.)
5. Support overlapping boundary records — the last record of Section N is also the first record of Section N+1
6. Produce section-level output files or sections within a single CSV

The current 30° threshold is not the right criterion. The real criterion appears to be: "an Angle-type record at a position where splitting would produce manageable section sizes." The Gordon file has 5 Angle points (1, 2, 3, 4, 5). The split was made at Angle 4, which divides the route roughly in half (poles 1-12 and 12-20).

A provisional heuristic might be: suggest splits at Angle points that divide the route into sections of roughly 40-80 poles each. But this needs validation on more files before we hard-code it.

---

## 5. How Detached / "Not Required" Records Should Be Handled

Records should be classified as "detached" if:
- They are separated from the main route by a gap significantly larger than any normal span (e.g. >500m)
- Their REMARK contains "not required" or similar disqualifying language
- They appear after blank rows in the raw file (if detectable)

Detached records should:
- NOT appear in the main route chain
- NOT be counted in section membership
- NOT influence span calculations or section splitting
- Appear in a separate "Detached / Reference Points" section of the CSV export
- Include a reason for classification ("large spatial gap", "remark: not required", etc.)

---

## 6. How EXpoles and Context Features Should Appear in D2D-Style Export

Stage 2B should support two export views:

### View 1: Clean Proposed Chain (analysis view)
This is what Stage 2A currently produces. Proposed poles only, in route order, with EXpoles as matched references and context features listed separately. Useful for route analysis, span/angle review, and design-readiness assessment.

### View 2: Interleaved Working View (D2D replacement view)
This mirrors the manual PR1/PR2 format. ALL records — proposed poles, EXpoles, and context features — in file order within each section. This is the output that most closely replaces the manual D2D spreadsheet because it preserves the surveyor's full capture sequence.

In the interleaved view:
- EXpoles appear at their original file-order position (NOT moved to sit beside their matched proposed pole)
- Context features appear at their original file-order position
- Each record has a "Role" column: Proposed / Existing / Context / Detached
- Section boundaries are marked with a clear indicator

The interleaved view is what a designer would actually use as a PoleCAD working file. The clean chain view is what the QA/completeness analysis uses.

---

## 7. What an Overlapping Section Boundary Means

When the route is split into sections, the boundary record (typically an Angle point) appears as:
- The LAST record in Section N
- The FIRST record in Section N+1

This means:
- Section N's span_to_next for the boundary record should show the span to the first record of Section N+1 (confirming continuity)
- Section N+1's first record should match the coordinates, feature code, and attributes of Section N's last record
- In the CSV export, this can be represented either by duplicating the record or by marking it as "Section Boundary (shared with Section N+1)"

---

## 8. What Design Pole Renumbering May Need to Do

The manual splits show that pole identifiers were relabelled from the surveyor's numbering (angle numbers 1-5, point IDs 1-173) to sequential design pole numbers (pole 1 through pole 20).

This is a significant transformation:
- The surveyor's Angle 1 becomes Design Pole 1
- The surveyor's Angle 2 becomes Design Pole 3
- EXpoles get design numbers too (EXpole near pole 2 becomes "pole 2" in the design numbering)
- Each section restarts or continues numbering depending on the split

Stage 2B should NOT hard-code a renumbering scheme. Instead it should:
- Preserve original point IDs and feature codes
- Add an optional "design_pole_number" column
- Use a provisional numbering heuristic: sequential from 1, counting only structural records in route order
- Mark this as provisional and editable by the designer

---

## 9. What Should Be Validated Before Coding Stage 2B

Before writing the Stage 2B Claude Code task:

1. **Run the NIE files (474, 474c, 513) through Stage 2A** and check whether the sequencing, EXpole matching, and section break detection work on Irish Grid files too. The Gordon file is OSGB — we need to confirm the sequencer works across CRS.

2. **Check whether the NIE files have natural section split points.** The 474 and 474c files are separate surveys of the same wider job area. Do they need splitting? Are they already sections?

3. **Confirm the "interleaved view" concept with your domain knowledge.** The manual splits keep everything in file order — is that what you would want from a D2D replacement, or would you prefer EXpoles grouped beside their matched proposed pole?

4. **Confirm whether design renumbering is a priority.** The manual splits show it happened, but is it something the tool should do automatically, or is it better left to the designer?

5. **Consider whether the 30° angle threshold should be replaced entirely.** The real split criterion appears to be "Angle-type record at a logical section boundary," which is more about pole type and section size than deviation angle.

---

## 10. Proposed Stage 2B Scope (Not a Code Task Yet)

Stage 2B should add:

1. **Detached record separation** — remove "not required" and large-gap records from the main chain into a separate section
2. **Angle-point-aware section detection** — identify Angle records as primary section split candidates instead of relying on deviation angle threshold alone
3. **Section membership** — assign each record to a section (Section 1, Section 2, etc.)
4. **Overlapping boundary records** — duplicate the boundary Angle point as last-of-previous and first-of-next
5. **Interleaved D2D view** — a second CSV export mode showing all records (proposed, existing, context) in file order within each section
6. **Provisional design pole numbering** — optional sequential numbering of structural records in route order
7. **Updated tests** covering detached separation, section assignment, overlap, and interleaved output

Stage 2B should NOT add:
- Final PoleCAD export format
- Photo integration
- Tablet capture
- Live sync
- Designer workspace
- DNO submission
- New QA rules

---

## Summary

Stage 2A proved the route sequencing concept works. The manual PR1/PR2 files give us clear evidence for what Stage 2B needs to do differently. The key insight is that the real D2D output is not a clean proposed-pole chain — it is a section-aware, interleaved working file that preserves the surveyor's full capture context while adding section structure and design numbering on top.

Stage 2B bridges the gap between "useful analysis output" (Stage 2A) and "actual D2D replacement" (the real goal of Stage 2).
