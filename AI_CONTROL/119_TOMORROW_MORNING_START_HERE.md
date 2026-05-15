# GridFlow — Tomorrow Morning Starting Point

**Date created:** 2026-05-14 (end of session)
**Read this first tomorrow.**
**Full vision:** See `118_GRIDFLOW_VISION_AND_ROADMAP.md`

---

## Where We Are

Stage 5 is fully complete. Tag: `stage5-complete`. Tests: 1368 passed, 1 skipped. Master is clean.

Last session uncovered something significant: the ENWL Network Asset Viewer at `https://enwl.gis-cdn.net/network-asset-viewer/` is a publicly accessible DNO tool that provides exactly the authoritative engineering records that Stage 5F identified as the missing piece for design-readiness. This changes the strategic picture for Stage 6.

---

## The Full Vision (Captured)

The user has stated GridFlow should become:

1. **Field survey evidence** — captured on iPad, GPS, photos, condition notes
2. **DNO baseline records** — pulled from ENWL Network Asset Viewer per pole
3. **DNO network trace evidence** — pulled as GeoJSON from the same tool
4. **Survey analysis tool** — making survey data design-ready as much as possible
5. **Eventually a design tool** — doing what PoleCAD and AutoCAD do today

All five are captured in the roadmap document. They are staged so each gets the engineering rigour it deserves at the right time:

- Points 1-3 are Stage 6
- Point 4 is Stages 7-8
- Point 5 is Stages 9-10+ with appropriate engineering review and possibly certification

---

## What Stage 6 Looks Like

Five sub-stages. Each ships and is validated on a real Unitas job before the next begins.

| Stage | Scope | Effort |
|-------|-------|--------|
| 6A | ENWL trace GeoJSON capture, parsing, storage, workspace display | 1-2 weeks |
| 6B | Per-pole ENWL record capture format and storage | 1-2 weeks |
| 6C | FID-to-pole linking (geometry + support_no + manual confirm) | 2-3 weeks |
| 6D | Three-source conflict detection and reporting | 2-3 weeks |
| 6E | Updated design-readiness logic using three sources | 1-2 weeks |

Total Stage 6: roughly 2-3 months.

**Critical rule for Stage 6A through 6C:** Do NOT change `design_ready` logic. ENWL trace and baseline are stored as evidence, displayed in workspace, but do not yet drive design-readiness decisions. That change happens in Stage 6E, after linking is proven in Stage 6C.

---

## First Decision Tomorrow

**Do a second local survey BEFORE starting Stage 6A?**

The argument for: Stage 6A needs real validation data. A paired field + trace + baseline dataset for a different short local route would give 6A a real target to build against. Maybe half a day in the field plus ENWL capture.

The argument against: You already have P_LOCAL_001 trace files saved. Stage 6A could be built and validated against the existing trace data.

**Recommendation:** Survey first.

Pick a short route of 5-8 poles near home that is different from P_LOCAL_001. Survey them with the iPad. Then capture matching ENWL trace data and per-pole records for the same route. Come back with a fully paired dataset. Total time: roughly half a day. Gives Stage 6A a complete real-world dataset to test against, not a synthetic one.

The reason: Stage 6 onwards is about three-source evidence. Building it against incomplete data risks baking in assumptions that the next real survey will break. A paired dataset upfront protects against that.

**Decision to make tomorrow morning:** survey first, or build first?

---

## Stage 6A Scope (When Ready to Start)

When you decide to start Stage 6A, the work splits naturally between Codex and Claude Code:

**Codex task (parallel):**
- New module: `gridflow/enwl_trace/` with GeoJSON parser
- Store traces under `uploads/jobs/<job_id>/enwl_evidence/traces/`
- Trace metadata: source FID, settings used, date captured
- CLI flag or pipeline integration to ingest a trace file
- Tests for parser and storage

**Claude Code task (parallel):**
- Workspace display for trace evidence in pole detail page
- New template section showing trace conductor data
- Add trace evidence indicator to Report 00 Quick Actions
- Read-only display, no design_ready changes
- Tests for workspace display

**Both:**
- Do NOT touch `design_ready` logic
- Do NOT modify match register or merge logic
- Both branches off master
- Merge sequentially after both validated

---

## What is Saved Locally Already

ENWL trace files captured in last session:

- `real_pilot_data/P_LOCAL_001/enwl_trace/enwl_trace_75754085_11kv_entire_feeder.geojson` (30 features, no ratings)
- `real_pilot_data/P_LOCAL_001/enwl_trace/enwl_trace_75754085_hv_to_lv_with_ratings.geojson` (30 features, with ratings — 115A / 190A / 284A observed)
- `real_pilot_data/P_LOCAL_001/enwl_trace/TRACE_INVENTORY.txt`
- `real_pilot_data/P_LOCAL_001/enwl_trace/README_ENWL_TRACE_NOTES.md`

Also backed up on Desktop: `GridFlow_ENWL_Trace_Backup_2026-05-14`

Per-pole record observed in last session (not yet saved, just screenshot):
- Pole FID 16788440, support 902203, Terminal, Stub Pole, Medium diameter
- SPN 61090H02203

Tools used:
- ENWL Network Asset Viewer at `https://enwl.gis-cdn.net/network-asset-viewer/`
- Start FID 75754085, HV Conductor, 11kV
- Both "Trace Entire Feeder" and "Trace HV to LV with ratings" tested
- Both HTML/table output and GeoJSON output formats confirmed working

---

## Hard Rules for Stage 6

1. **No design_ready logic changes until Stage 6E.** Evidence is stored and displayed but does not yet drive readiness logic.

2. **No native design calculations.** Stage 10+ territory, with engineering review.

3. **Real Unitas job between each sub-stage.** 6A is not complete until used on real work. Same for 6B, 6C, 6D, 6E.

4. **Wording discipline.** GridFlow is a "design preparation tool" through Stage 8. "Design assistance tool" through Stage 9. Not a "design tool" until Stage 10 ships with engineering review.

5. **Provenance is mandatory.** Every piece of evidence tracks where it came from, when it was captured, and what version of the source produced it.

6. **The ENWL trace is not authoritative for every pole.** It is authoritative for traced assets. The chain `trace FID → baseline asset → pole/support → merged record` must be proven before trace data can drive design decisions. That proof comes in Stage 6C.

---

## Long-Term Arc Reminder

- **Stage 6** — Three-source evidence engine (2-3 months) — vision points 1-3
- **Stage 7** — Workspace and reporting maturation (3-6 months) — supporting infrastructure
- **Stage 8** — Design-readiness analytics (6-9 months) — vision point 4 fully realised
- **Stage 9** — Design assistance / PoleCAD-ready outputs (9-15 months) — vision point 5 begins
- **Stage 10+** — Selected native design calculations with engineering review (Year 2+) — vision point 5 fully realised

Each stage builds on the previous one being validated on real work.

---

## Start Here Tomorrow

1. Read this document (you are doing it now).
2. Read `118_GRIDFLOW_VISION_AND_ROADMAP.md` if you want the full picture.
3. Decide: survey first, or build Stage 6A first?
4. Execute the chosen path.
5. After completion, update `01_CURRENT_STATE.md` and `02_CURRENT_TASK.md`.

The roadmap document does not change with sprints. It changes only when the strategic picture genuinely shifts.

---

**Good place to stop tonight. Tomorrow we build on a clearer foundation than ever.**
