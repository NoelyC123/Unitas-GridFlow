# Current State

## Project phase

**Stage 2 completion review**

Stage 1 is complete.

Stage 2A, Stage 2B and Stage 2C are implemented and validated against the current Gordon/NIE real-file set.

Stage 2 is not formally closed until the completion review decision is made.

---

## What works

- Raw Trimble controller dump intake (tested on 4 real files)
- CRS detection: Irish Grid TM65, ITM, OSGB27700
- Coordinate conversion to WGS84 for map display
- Record-role classification (structural, context, anchor)
- Replacement pair detection (EXpole to Pol matching)
- Evidence gates (7 scoped design gates)
- Confidence-aware severity tiers (PASS/WARN/FAIL)
- Interactive Leaflet map with filtering
- PDF pre-design briefing report
- DNO rulepack inference from geography
- Column/header normalisation for structured CSVs
- Context feature classification (Hedge, Fence, Wall, Gate, Track, Road, Tree, Stream, BTxing, LVxing, Ignore)
- Stage 2 clean route-chain export (`<job_id>_d2d_chain.csv`)
- Stage 2 interleaved D2D working view (`<job_id>_d2d_working_view.csv`)
- Route sequencing from raw controller exports
- EXpole matching to proposed poles
- Span-to-next and deviation-angle calculations
- Section-aware output with section summaries
- Detached / not-required record handling
- Global provisional design pole numbering
- Section-local sequence numbering
- Confidence / sequence-note warning for high-ambiguity files

## Counts

- **Tests passing:** 211
- **DNO rulepacks:** 4 (SPEN, SSEN, NIE, ENWL)
- **Real files validated:** Gordon, 4-474, 513, 474c

## What was just shipped

- Stage 2A: provisional D2D candidate export / clean chain view
- Stage 2B: section-aware sequencing, interleaved D2D working view, detached record handling, global design numbering
- Stage 2B validation bugfix: trailing `not required` annotation preserved and Gordon points 9/10 detached correctly
- Stage 2C: export polish, clearer headers, section summaries, detached wording, sequence-note wording, UI labels and filenames

## Known remaining issues

1. Stage 2 output is still provisional and not a verified PoleCAD import schema.
2. High-ambiguity files such as `2814_4-474_raw_trimble_export.csv` require designer review.
3. No manual section-selection UI yet.
4. No multi-file job merge yet (`4-474` and `474c` remain separate validation files).
5. PDF report still reflects Stage 1/QA style more than final Stage 2 designer workflow.

## Strategic position

- No competing product exists in this space
- Tool validated on real NIE and SPEN survey files
- Project owner has direct survey and design experience
- Full 6-stage vision defined (see 00_PROJECT_CANONICAL.md)
- Next decision is whether Stage 2 is complete enough for now or whether a small further polish pass is needed before Stage 3 planning
