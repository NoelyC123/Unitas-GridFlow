# Current State

## Project phase

**Stage 3A2 access-gated remote trial validated**

Stage 1 is complete.

Stage 2A, Stage 2B and Stage 2C are implemented and validated. Stage 2 is formally closed.

Stage 3C (Project Management / multi-file job support) is implemented and manually validated.

Stage 3B (Designer Review & Export Readiness) is implemented and validated.

Stage 3A1 (Local Daily Intake MVP) is implemented and validated.

Stage 3A2 (Remote Access Trial) has validated the primary Cloudflare route: a named Cloudflare Tunnel for `gridflow.unitasconnect.com` protected by Cloudflare Access email one-time PIN. A phone on mobile data authenticated through Access, loaded the app, uploaded non-sensitive `sample_data/mock_survey.csv`, updated the project dashboard, and opened Map/PDF/D2D/Review outputs. Tailscale remains the private fallback. Render/Railway/full hosted deployment is deferred.

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
- **Stage 3A2: remote-access trial plan documented**
- **Stage 3A2: temporary unauthenticated tunnel connectivity validated for home, projects, and upload pages**
- **Stage 3A2: named Cloudflare Tunnel + Access validated from iPhone/mobile data**
- **Stage 3A2: protected remote upload/dashboard/Map/PDF/D2D/Review smoke test passed with non-sensitive mock CSV**

## Counts

- **Tests passing:** 281
- **DNO rulepacks:** 4 (SPEN, SSEN, NIE, ENWL)
- **Real files validated:** Gordon, 4-474, 513, 474c

## What was just shipped

- Stage 3A2: Cloudflare Access-gated remote validation
  - Named tunnel `gridflow` created for `gridflow.unitasconnect.com`.
  - Cloudflare Access email one-time PIN prompt validated from iPhone/mobile data.
  - After authentication, GridFlow loaded remotely.
  - Non-sensitive `mock_survey.csv` uploaded from iPhone as project `P006` / `iPhone Test`.
  - Project dashboard updated: 1 file, 5 poles, 10 issues.
  - Map, PDF, D2D Chain, D2D Working, and Review routes all returned successfully for `P006/F001`.

- Stage 3A2: temporary tunnel connectivity validation
  - A `trycloudflare.com` temporary tunnel loaded successfully from a phone/external device.
  - Home page, `/projects/`, and `/upload` all loaded remotely.
  - No real or sensitive survey CSVs were uploaded.
  - This is not full Stage 3A2 acceptance because Cloudflare Access is not active.

- Stage 3A2: remote access trial plan
  - `AI_CONTROL/25_STAGE_3A2_DEPLOYMENT_PLAN.md` — Cloudflare Tunnel + Access first, Tailscale fallback, hosted deployment deferred
  - `README.md` — local remote access trial commands and validation checklist

## Known remaining issues

1. No cross-file chain merging or combined exports within a project.
2. No combined project-level map overlay.
3. No section boundary editing (Stage 3B+ scope).
4. Stage 3A2 uses the local Mac as the origin, so remote access depends on the Mac and `cloudflared` tunnel staying online.
5. Stage 2 output is still provisional and not a verified PoleCAD import schema.
6. High-ambiguity files such as `2814_4-474_raw_trimble_export.csv` require designer review.
7. PDF report still reflects Stage 1/QA style more than final Stage 2 designer workflow.
8. Reviewed state affects D2D CSV exports only — PDF update deferred.

## Strategic position

- No competing product exists in this space
- Tool validated on real NIE and SPEN survey files
- Project owner has direct survey and design experience
- Full 6-stage vision defined (see 00_PROJECT_CANONICAL.md)
- Stage 3A2 primary route validated — next decision is whether the controlled tunnel is sufficient for the near-term trial or whether always-on hosting should be planned later
