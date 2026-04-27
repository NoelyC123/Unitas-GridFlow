# Current State

## Project phase

**Stage 3A1 complete — local daily intake MVP**

Stage 1 is complete.

Stage 2A, Stage 2B and Stage 2C are implemented and validated. Stage 2 is formally closed.

Stage 3C (Project Management / multi-file job support) is implemented and manually validated.

Stage 3B (Designer Review & Export Readiness) is implemented and validated.

Stage 3A1 (Local Daily Intake MVP) is implemented and validated. Cloud/remote access is deferred to Stage 3A2 planning.

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
- **Stage 3A1: survey day / visit label per project file**
- **Stage 3A1: uploaded-by and surveyor note intake metadata**
- **Stage 3A1: office feedback note per project file**
- **Stage 3A1: derived intake status on project overview**
- **Stage 3A1: project dashboard shows intake context alongside existing outputs**

## Counts

- **Tests passing:** 281
- **DNO rulepacks:** 4 (SPEN, SSEN, NIE, ENWL)
- **Real files validated:** Gordon, 4-474, 513, 474c

## What was just shipped

- Stage 3A1: local daily intake layer
  - `app/project_manager.py` — intake metadata and derived intake status
  - `app/routes/api_projects.py` — intake metadata capture and office feedback API
  - `app/templates/upload.html` / `app/static/js/upload-manager.js` — survey-day upload fields
  - `app/templates/project.html` — intake dashboard row with office feedback
  - `AI_CONTROL/23_STAGE_3A_DESIGN_BRIEF.md` — approved scope
  - `AI_CONTROL/24_STAGE_3A_VALIDATION_ACCEPTANCE.md` — validation evidence

## Known remaining issues

1. No cross-file chain merging or combined exports within a project.
2. No combined project-level map overlay.
3. No section boundary editing (Stage 3B+ scope).
4. No cloud deployment or remote authentication yet (Stage 3A2 scope).
5. Stage 2 output is still provisional and not a verified PoleCAD import schema.
6. High-ambiguity files such as `2814_4-474_raw_trimble_export.csv` require designer review.
7. PDF report still reflects Stage 1/QA style more than final Stage 2 designer workflow.
8. Reviewed state affects D2D CSV exports only — PDF update deferred.

## Strategic position

- No competing product exists in this space
- Tool validated on real NIE and SPEN survey files
- Project owner has direct survey and design experience
- Full 6-stage vision defined (see 00_PROJECT_CANONICAL.md)
- Stage 3A1 complete — projects can now act as local daily-intake dashboards before cloud access
