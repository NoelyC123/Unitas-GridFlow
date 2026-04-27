# Current State

## Project phase

**Stage 3B complete — next decision pending**

Stage 1 is complete.

Stage 2A, Stage 2B and Stage 2C are implemented and validated. Stage 2 is formally closed.

Stage 3C (Project Management / multi-file job support) is implemented and manually validated.

Stage 3B (Designer Review & Export Readiness) is implemented and validated.

---

## What works

- Raw Trimble GNSS controller dump intake (tested on 4 real files)
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
- **Stage 3C: named project container above flat-job model**
- **Stage 3C: multi-file projects (P001/F001, P001/F002...)**
- **Stage 3C: project.json with aggregate summary across files**
- **Stage 3C: project-aware upload, map, PDF, D2D routes**
- **Stage 3C: project overview and projects list pages**
- **Stage 3C: backward-compatible — all legacy J##### routes unchanged**
- **Stage 3B: review.json overlay per project file**
- **Stage 3B: per-file designer review page**
- **Stage 3B: EXpole pairing reassignment / mark unmatched**
- **Stage 3B: designer reviewed/not-reviewed flag with notes**
- **Stage 3B: D2D Chain and D2D Working exports apply reviewed pairing overrides**
- **Stage 3B: reviewed/provisional export headers**
- **Stage 3B: reset to auto-generated deletes review.json; original seq unchanged**

## Counts

- **Tests passing:** 273
- **DNO rulepacks:** 4 (SPEN, SSEN, NIE, ENWL)
- **Real files validated:** Gordon, 4-474, 513, 474c

## What was just shipped

- Stage 3B: designer review overlay
  - `app/review_manager.py` — data layer
  - `app/routes/api_review.py` — review API (GET/POST/DELETE)
  - `app/routes/review_page.py` — review page route
  - `app/templates/review.html` — Bootstrap 5 review UI
  - `app/routes/d2d_export.py` — project exports apply review overlay
  - `app/routes/api_intake.py` — reprocessing clears stale review
  - `app/__init__.py` — blueprint registration
  - 20 unit tests + 9 integration tests
  - commits `a9b3ee2`, `7daa5a9`

## Known remaining issues

1. No cross-file chain merging or combined exports within a project.
2. No combined project-level map overlay.
3. No section boundary editing (Stage 3B+ scope).
4. No live sync or cloud deployment (Stage 3A scope).
5. Stage 2 output is still provisional and not a verified PoleCAD import schema.
6. High-ambiguity files such as `2814_4-474_raw_trimble_export.csv` require designer review.
7. PDF report still reflects Stage 1/QA style more than final Stage 2 designer workflow.
8. Reviewed state affects D2D CSV exports only — PDF update deferred.

## Strategic position

- No competing product exists in this space
- Tool validated on real NIE and SPEN survey files
- Project owner has direct survey and design experience
- Full 6-stage vision defined (see 00_PROJECT_CANONICAL.md)
- Stage 3B complete — designers can now review and sign off EXpole pairings before export
