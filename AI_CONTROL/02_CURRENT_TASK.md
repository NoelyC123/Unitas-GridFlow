# Current Task

## Immediate task

The immediate task is:

**Validate the designer summary layer and narrative outputs on real survey files, then decide the next development step from that evidence.**

---

## Why this is the current task

Fifteen validation batches and one documentation batch have been completed:

- Batch 2: raw GNSS controller dump intake + completeness reporting
- Batch 3: coord_consistency fix for non-OSGB grids + QA noise suppression
- Batch 4: NIE_11kV rulepack auto-detection from Irish Grid CRS + completeness surfacing in map and PDF
- Batch 5: design readiness verdict + survey coverage categories + enhanced map popups
- Batch 6: issue-text popup explanation + interactive pass/fail filter + Records label + overlap detection
- Batch 7: feature-aware QA (Hedge skipped in span checks) + record inspection panel
- Batch 8: strict structural_only height scoping + issue deduplication
- Batch 9: record-role classification (structural/context/anchor) + anchor chain-reset in span checks + Gate/Track/Stream as context + role breakdown in UI and PDF
- Batch 10: record count consistency, span threshold decimal precision, coverage label fix, expanded design readiness what_this_supports
- Batch 11: EX/PR replacement cluster detection — EXpole + nearby structural emits WARN instead of false span-too-short FAIL; relationship metadata in map popup
- Batch 12: angle/stay evidence logic — angle structures with no proximate stay evidence emit cautious WARN
- Batch 13: confidence-aware QA — short span tiers (very short/unusual/borderline, all WARN); EXpole height-below-min downgraded to WARN; strong summary when material absent
- Batch 14: EX/PR narrative linking — asset_intent labels (Existing asset / Proposed support) in GeoJSON and UI; warn_count/warn_texts correctly serialised
- Batch 15: designer summary layer — circuit summary, top design risks, replacement narratives; map and PDF now present a pre-design briefing rather than a raw QA dump
- Batch 16: project vision documentation aligned — "survey-to-design workflow intelligence tool" framing established across all control files

**121 tests passing.**

The tool now produces a structured pre-design briefing from real survey data. The next uncertainty is whether that briefing is genuinely useful to a designer or QA lead receiving a real survey handoff.

---

## What this task means

This task means:

- obtain one or more real survey files (ideally from recent jobs)
- run them through the current intake and QA pipeline
- review the map view, side panel, and PDF output as a designer or QA lead would
- log what the designer summary actually says on real data
- log whether the circuit summary, top design risks, and replacement narratives are accurate and useful
- identify what the tool misses, overflags, or misframes
- use that evidence to define the next development step

---

## What success looks like

This task is successful when we can answer:

- Does the designer summary layer accurately describe the job from real data?
- Do the top design risks surface real concerns or produce noise?
- Do the replacement narratives correctly identify EX→PR pairs?
- Is the design readiness verdict accurate?
- Is the output something a designer or QA lead would trust and act on?

---

## What not to do during this task

Do NOT:

- add new features without evidence from real-file testing
- broaden the product into a larger platform
- add more rulepacks just for coverage
- assume the designer summary layer is good because it passed synthetic test data

---

## Approved focus areas

The most likely files involved in any follow-on work are:

- `app/controller_intake.py` — build_circuit_summary, build_top_design_risks, build_design_readiness
- `app/routes/api_intake.py` — finalize route, _build_replacement_narratives
- `app/qa_engine.py` — QA rules and severity calibration
- `app/routes/pdf_reports.py` — PDF pre-design briefing
- `app/templates/map_viewer.html` — map side panel and designer summary sections

---

## Strategic note

The external AI review completed on 2026-04-22 concluded:

- continue the project
- keep the scope narrow
- treat the project primarily as an internal tool / consultancy asset for now
- shift to validation-led development

The project has followed that direction through Batches 2–16. The vision is now:

**A survey-to-design workflow intelligence tool for UK electricity network projects.**

Its purpose is to act as the trusted gate between survey and design — interpreting, validating, and explaining digital survey data so designers receive a clearer, more trustworthy handoff.

It does NOT replace Trimble, PoleCAD, AutoCAD, engineering designers, or surveyors. It is not yet a full DNO compliance engine.

---

## Likely next reference task

After real-file validation findings are gathered, a likely next task is:

**Produce a real-world survey workflow reference document** — a structured description of what a real survey file from a UK overhead line job should contain, what is typically missing, and what the tool currently surfaces vs misses. This would help define the next rule and output improvements from real evidence.

---

## When to update this file

Update when:

- real survey files have been tested against the current designer summary layer
- validation findings materially change project direction
- the next development phase becomes clearer from evidence
