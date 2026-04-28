# Practitioner Review Summary

## Purpose

This is the repo-safe summary of the detailed practitioner-led review completed on 2026-04-28.

The full review folder remains local-only evidence because it contains colleague/practitioner feedback, screenshots, large binary files, and internal review language. Do not commit the full folder. Use this file as the active development record.

---

## Evidence base

Review package:

- `GridFlow_Review_Page_Validation_Notes_With_Photos.docx`
- `Unitas_GridFlow_View_Map_Section_Review.docx`
- `Unitas_GridFlow_Download_PDF_Feature_Final_Review.docx`
- `Unitas_GridFlow_D2D_Features_Review_Only.docx`
- `Unitas_GridFlow_Additional_Improvements_All_4_Features.docx`

Local-only evidence folder:

- `/Users/noelcollins/Unitas-GridFlow/Unitas GridFlow Full Tool Review 28th April 2026/`

Context:

- Review used the Bellsprings real-life survey-to-design test.
- The project owner reviewed the tool as both UK OHL surveyor and designer.
- Colleague/practitioner feedback was incorporated.
- Claude Desktop reviewed the five documents and produced a structured prioritisation.

---

## Overall finding

GridFlow has moved beyond "can the app process survey files?" into "does the interpreted output make sense to a surveyor/designer working on a real OHL job?"

The core processing, evidence gates, map, PDF, review page, and chain exports are useful. The main weakness is not the existence of these features, but their current framing and presentation. Too much language is internal/software-oriented instead of engineering-oriented. Some outputs imply more design certainty than the evidence supports.

The next phase is therefore **practitioner-review remediation**: a narrow Stage 3 follow-on to improve trust, terminology, design-chain clarity, and professional handoff output before any Stage 4 field-capture build.

---

## Repeated themes

1. Terminology must become practitioner-facing.
   Internal terms such as `Auto Match`, `Review Signals`, `Structural`, `Context`, `Anchor`, `Warn`, `Fail`, and `D2D` reduce trust when shown as product language.

2. The map must show a connected OHL circuit.
   Markers alone are not enough. Designers need poles, spans, route direction, and topology.

3. EX/PR pairing is mis-framed.
   The current designer reassignment workflow is too prominent. Proposed pole positions are normally captured on site. The tool should present proximity QA and review flags, not imply designers manually create the route from dropdowns.

4. Evidence quality and provenance need to be visible.
   Values should not look equally reliable when one is measured, one is inferred, one is free text, and one is missing.

5. Missing evidence needs design consequences.
   A finding should explain what it blocks or what action is needed, not only report that a value is outside range.

6. The PDF should become a formal engineering handoff report.
   It is one of the outputs most likely to leave the software, so it needs professional structure, metadata, coordinates, issue actions, and appropriate caveats.

7. D2D should be retired from forward product language.
   The useful part is the design chain / design handoff, not the old D2D workaround.

---

## Classified findings

### Must-fix misleading outputs

| Finding | Why it matters |
|---------|----------------|
| EXpole Pairings framed as designer reassignment | Implies the wrong real-world responsibility and overstates the role of manual dropdown assignment |
| Ambiguous height fields in chain/export outputs | `Height` can mean ground level, pole height, attachment height, or birthmark-derived value |
| Broad EXpole association threshold | A fixed broad radius can create false confidence on RTK-quality survey data |
| Soft readiness wording | Terms like "Partially Ready" may understate missing stay/clearance/stability evidence |
| Issue wording lacks design consequence | Designers need to know what action is required and whether the issue blocks design |

### High-value product improvements

| Improvement | Priority reason |
|-------------|-----------------|
| Span rendering on map | Most important functional gap; converts dots into an OHL route |
| Basic route topology and span labels | Helps designer understand chain/order/distance |
| Map issue filtering | Lets reviewers isolate design blockers and review-required items |
| Overlapping marker handling | EX/PR replacement points are often intentionally close together |
| Structured PDF issue table | Makes the report usable as a professional handoff document |
| PDF coordinates and actions | Converts findings into a worklist |
| Missing-evidence matrix | Shows what is absent pole-by-pole |
| Guided workflow status | Aligns upload, validation, map, chain, PDF, and sign-off |

### Wording and framing replacements

| Current wording | Preferred direction |
|-----------------|---------------------|
| EXpole Pairings | Existing / Proposed Pole Proximity QA |
| Auto Match | Nearby proposed pole |
| Auto Dist (m) | Distance (m) |
| Reviewed Assignment | QA status / action required |
| Seq Range | Design pole range |
| Boundary Point | Section boundary / route break |
| Structural / Context / Anchor | Primary assets / environmental-clearance data / geodetic control |
| Warn / Fail | Review required / design blocker |
| Review Signals | Design review items / compliance anomalies |
| Issue count | Open QA items |
| D2D Working View | Raw Working Audit / Legacy Working View |
| Clean Chain Export | Design Chain Export / Master Design Chain |

### Future Stage 4 ideas to hold

These are valuable but should not be built yet:

- tablet/iPad structured field-capture forms
- photo upload and linking
- structured birthmark capture
- stay anchor/bearing capture
- crossing clearance measurement capture
- conductor identity capture
- field correction loop
- split-screen photo/map review
- automated mechanical/design suggestion engine

### Items not to build yet

- verified PoleCAD exporter without actual import requirements
- app user accounts or role-based auth
- hosted cloud deployment
- cloud storage migration
- DNO submission pack generation
- final compliance certification
- bill of materials / quote preview
- live Trimble sync
- large object-model rebuild

---

## D2D decision

Decision: **rename, reduce, and refocus.**

The old D2D spreadsheet is the workaround GridFlow is replacing. The current D2D-related outputs should be repositioned:

- The Clean Chain Export becomes the primary **Design Chain Export** / **Master Design Chain**.
- The D2D Working View remains short-term as a secondary **Raw Working Audit** or **Legacy Working View** for traceability.
- Forward product language should use **Design Chain**, **Design Handoff**, and **designer working view** rather than D2D.

The strategic idea of D2D elimination remains valid in the control layer because it explains the workflow being replaced. It should not appear as the product destination in the UI.

---

## Prioritised development steps

### Step 1 — Terminology and wording pass

Apply practitioner-facing wording across UI, exports, and PDF text where safe. This is low risk and high trust impact.

Scope:

- product labels
- status labels
- review-table headings
- D2D/download wording
- report section titles
- explanatory text

Do not change backend logic in this step.

### Step 2 — D2D rename/refocus

Rename the primary chain output around **Design Chain / Master Design Chain**. Make the raw working export secondary. Remove forward-facing D2D language where it makes the old workaround look like the product goal.

### Step 3 — EX/PR proximity QA reframing

Reframe the current EXpole pairing page as proximity QA. Do not delete reviewed override logic until the code dependencies and export behaviour are inspected. The first safe step is wording, layout, and emphasis.

### Step 4 — Map span rendering

Draw inferred span lines between sequential design-chain poles and label basic span distances. This is the highest-value functional improvement after wording.

Do not attempt the full three-pane map, side inspector, advanced symbology, or voltage-aware styling in the first map pass.

### Step 5 — PDF structured issue table

Rework the report findings into a structured table with asset/record reference, coordinates, severity/status, description, design consequence, and recommended action.

---

## Control doc implications

The active project state should now record:

- the practitioner-led full tool review is complete
- the full review folder is local-only evidence
- a sanitized summary is committed as this file
- the current phase is practitioner-review remediation, still within the post-Stage-3 operational-use period
- the next build should start with wording/D2D rename/review framing before larger functional work

---

## Implementation boundary

This review does not justify jumping directly into Stage 4. Photo capture, tablet forms, structured birthmarks, stays, crossings, and conductor capture are important future directions, but the immediate evidence points first to trust, terminology, map topology, and handoff/report clarity.
