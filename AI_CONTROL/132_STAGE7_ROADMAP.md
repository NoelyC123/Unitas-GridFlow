# Stage 7 Roadmap — Workspace Maturation

**Date:** 2026-05-18
**Reference:** `AI_CONTROL/130_STAGE6_COMPLETION.md`, `AI_CONTROL/131_STAGE7A_PHOTO_INTEGRATION_SPEC.md`

---

## Overview

Stage 6 proved that GridFlow can combine field evidence, ENWL pole/equipment records, and
ENWL trace evidence into a conservative, linked evidence record. The pipeline runs, the
workspace displays evidence relationships, and design-readiness is correctly assessed.

Stage 7 makes that evidence genuinely easy to review in practice. The current workspace
shows text records and flags. A designer reviewing P_LOCAL_002 cannot see photos, cannot
compare jobs side-by-side, and cannot export anything useful for downstream tools.

Stage 7 closes the gap between "evidence exists" and "evidence is reviewable."

---

## Sub-stages

### 7A — Photo Integration (Current)

**Goal:** Make field photos accessible from the workspace and CLI.

**Backend (Codex — `codex/stage7a-photo-integration`):**
- `gridflow/photos/loader.py`: `PhotoSet`/`PhotoFile` schemas, `load_pole_photos()`,
  `load_survey_photos()`
- `scripts/list_pole_photos.py`: CLI listing per pole and all poles
- Update `gridflow/evidence_combiner/combiner.py` with `photo_count`,
  `photo_types_present`, `photos_available`
- `tests/test_photo_loader.py`

**Workspace display (Stage 7B — see below):**
Photo display is split from the backend because workspace display requires a photo-serving
strategy decision first (see `AI_CONTROL/131` Architectural Note).

**Acceptance:** All 12 P_LOCAL_002 poles return photo counts; combined evidence includes
photo fields; `pytest -q` passes.

---

### 7B — Workspace Photo Display (Next, 1–2 weeks)

**Goal:** Show field photos in the workspace pole detail page.

**Prerequisites:**
- Stage 7A backend complete
- Photo-serving strategy chosen (Flask route vs copy vs symlink — see 131)

**What it adds to the workspace:**

```
┌─ Field Photos (9) ─────────────────────┐
│                                        │
│  Full Pole (1)                         │
│  [thumbnail]                           │
│                                        │
│  Equipment (2)                         │
│  [thumbnail] [thumbnail]               │
│                                        │
│  [+ 6 more photos]                     │
└────────────────────────────────────────┘
```

- Photo section in `pole_detail.html` after Design Readiness card
- Group by photo type; one thumbnail per type visible by default
- Click → open full size in new tab (no lightbox for now)
- Lazy-load images (only fetch when section is visible)
- Limit initial load to 6 photos; "Show all" expands to grid
- Job overview page shows photo count per pole in the table

**Worker split:**
- Claude Code: template changes, CSS, lazy loading
- Codex: Flask route for serving photos from evidence path

---

### 7C — Export Formats (2–3 weeks)

**Goal:** Allow designers to export evidence for downstream tools.

**Formats:**
- CSV: per-pole evidence table (support_no, match confidence, verification flags, photo count)
- JSON bundle: combined evidence + ENWL records + photos as a single exportable package
- PDF summary: per-job readiness report (printable for site visits)

**Non-goals for 7C:**
- Excel (complex format, low priority)
- PoleCAD import (out of scope until format verified with DNO)

**Worker:** Codex (report generators already follow the existing pattern in `gridflow/reports/`)

---

### 7D — Multi-job and Comparison Views (2–3 weeks)

**Goal:** Allow reviewers to compare evidence across jobs and track history.

**What it adds:**
- Job overview dashboard: all registered jobs in a single table (match rate, photo count,
  readiness status, last run date)
- Cross-job search: find a support number across all jobs
- Evidence quality dashboard: summary of HIGH/MEDIUM/LOW counts across jobs

**Non-goals:**
- Per-pole history / change tracking (depends on storage model not yet defined)
- Timeline or audit trail (Stage 7E or later)

---

### 7E — Search and Filter Enhancements (1–2 weeks)

**Goal:** Make it faster to find specific poles in large jobs.

**Adds to the workspace:**
- Free-text search across support numbers and notes content
- Filter by readiness level (Design Blocked / Review Required / Ready)
- Filter by evidence quality (HIGH / MEDIUM / LOW)
- Filter by pole type or equipment presence (has transformer, has ABS, etc.)
- Filter by coordinate completeness (flag poles with `coordinate_status=MISSING`)

**Non-goals:**
- Full-text search across ENWL records (Stage 8 if needed)
- Map-based filtering (already partially handled by Stage 5C map overlay)

---

## What Stage 7 Does NOT Include

| Out of scope | Reason |
|---|---|
| Photo upload or editing | Out of scope — GridFlow is read-only for survey evidence |
| Thumbnail generation | Requires image processing dependency; deferred to Stage 7B |
| EXIF metadata extraction | Low priority; filenames are sufficient for now |
| PoleCAD export | Out of scope until format verified with DNO |
| Mobile field capture | Separate track; requires mobile dev decision |
| GIS integration | Beyond current scope |
| Design calculations | Out of scope — GridFlow is pre-design |
| Live ENWL data sync | Requires DNO API access not yet available |

These belong in Stage 8 or later, after Stage 7 proves the workspace is useful to designers.

---

## Worker Coordination

Each sub-stage should be assigned clearly before starting:

| Sub-stage | Backend (Codex) | Workspace/docs (Claude Code) |
|---|---|---|
| 7A | `gridflow/photos/loader.py` + CLI + tests | Spec (131) + workspace photo display design |
| 7B | Photo-serving Flask route | Template changes, lazy loading CSS/JS |
| 7C | Report generators | Export format spec |
| 7D | Job comparison data layer | Dashboard template |
| 7E | Search/filter route handlers | Filter UI components |

Do not run Codex and Claude Code on the same files simultaneously.

---

## Stage 7 Success Criteria

Stage 7 is complete when all of the following hold:

- A designer reviewing P_LOCAL_002 in the workspace can see photos for any pole without
  opening the file system
- Photos are organised by type (or shown as unclassified when filenames carry no signal)
- Evidence can be exported in at least one format usable in downstream work
- Multiple jobs are visible in a single dashboard view
- Basic search and filter works on the pole list
- `pytest -q` passes with no regressions after each sub-stage

Stage 7 does not require `design_ready = True` for any pole. The correct expected state
remains `DESIGN_BLOCKED` for P_LOCAL_002 until conductor specification is confirmed per span.

---

## Dependency on Stage 7A

Sub-stages 7B onwards depend on Stage 7A being complete. Do not start 7B workspace display
until:
1. `gridflow/photos/loader.py` is merged and tests pass
2. The photo-serving strategy (Flask route vs copy) is decided and implemented
3. At least one job has been registered with its evidence root path stored in metadata
