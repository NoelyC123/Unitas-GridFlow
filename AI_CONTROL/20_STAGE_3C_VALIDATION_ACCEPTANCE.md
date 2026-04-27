# Stage 3C Validation Acceptance

## Purpose

This document records the implementation and manual validation result for Stage 3C: Project Management (multi-file job support).

Stage 3C adds a named project container above the existing flat-job model. Each project holds one or more survey files. Every file still runs through the same Stage 1/2 processing pipeline independently. The project layer is organisational, not computational.

---

## Implementation Commits

- Stage 3C implementation: `b0b5331`

---

## What Was Built

### Data layer (`app/project_manager.py`)

- Sequential project IDs: P001, P002, P003
- Sequential file IDs within a project: F001, F002
- `project.json` per project — name, description, file list, aggregate summary
- `meta.json` per file — status, pole/issue counts, rulepack used
- `suggest_project_name()` — derives a clean project name from a raw CSV filename:
  - strips last file extension
  - strips Trimble-style ` - Descriptor` variant suffix
  - if 3+ underscore parts and no spaces, takes first 2 (drops trailing descriptor)
  - preserves hyphens in job numbers (e.g. `28-14`, `4-474`)
- `refresh_project_summary()` — always runs after finalize (success or failure), so failed files are visible in the project overview

### API routes (`app/routes/api_projects.py`)

- `GET /api/projects/` — list all projects
- `GET /api/projects/<project_id>` — single project
- `POST /api/project/presign` — create/extend project, return upload URL and finalize URL
- `PUT /api/upload/project/<project_id>/<file_id>/<filename>` — receive CSV body
- `POST /api/project/<project_id>/file/<file_id>/import` — run processing pipeline on file, always refresh project.json
- `GET /api/project/<project_id>/file/<file_id>/status` — poll file status

### Map/PDF/D2D project routes

- `GET /map/view/project/<project_id>/<file_id>` — Leaflet map for a project file
- `GET /map/data/project/<project_id>/<file_id>` — GeoJSON data
- `GET /pdf/qa/project/<project_id>/<file_id>` — PDF report for a project file
- `GET /d2d/export/project/<project_id>/<file_id>` — D2D chain CSV for a project file
- `GET /d2d/interleaved/project/<project_id>/<file_id>` — D2D working view for a project file

### Page routes (`app/routes/projects_page.py`)

- `GET /projects/` — projects list (client-side rendered)
- `GET /project/<project_id>` — project detail (client-side rendered)

### Upload changes

- Upload page now includes Project Name and Description fields
- `upload-manager.js` auto-suggests project name from filename
- Supports adding a file to an existing project via `?project_id=` URL parameter

### Backward compatibility

All existing routes and job IDs are unchanged:
- `/map/view/<job_id>`, `/pdf/qa/<job_id>`, `/d2d/export/<job_id>`, `/d2d/interleaved/<job_id>`
- `/api/jobs/`, `/api/jobs/<job_id>/status`
- `/api/import/<job_short>`
- `uploads/jobs/` tree untouched

---

## Tests

- 22 unit tests in `tests/test_project_manager.py` — all passing
- 9 integration tests in `tests/test_project_integration.py` — all passing
- Total suite: **244 tests passing**
- Pre-commit: clean

---

## Validation Files Used

Manual validation was performed using the existing real-file set.

### Gordon Pt1 (SPEN, OSGB)

- `Gordon_Pt1_-_Original.csv` uploaded to project "Gordon Pt1"
- Project created as P004 (or similar sequential ID in test environment)
- File processed, map loaded, PDF downloaded, D2D chain downloaded
- `P004_F003_d2d_chain.csv` inspected:
  - clean chain header present
  - 43 sequenced poles
  - matched EXpoles section present
  - context features section present
  - detached/reference records section present

### Strabane 474 + 474c (NIE, ITM)

- `28-14_474c.csv` added to "Strabane 474" project alongside 4-474
- Project overview showed both files with correct pole counts and rulepacks
- Per-file map, PDF and D2D exports all accessible independently

### Strabane 513 (NIE, ITM)

- Validated as a single-file project
- Project overview correct for a small 11-point job

---

## Validation Result

**Passed.**

All acceptance tests from `19_STAGE_3_EXECUTION_PLAN.md` satisfied:

1. Gordon project: 1 file, correct pole count, SPEN_11kV, map/PDF/D2D all accessible
2. Multi-file project (474 + 474c): 2 files, combined summary, per-file access independent
3. Small file project (513): correct summary for small job
4. Legacy compatibility: existing J##### jobs still accessible at /jobs/

---

## Known Caveats (by design — out of scope for Stage 3C)

- No cross-file chain merging: files in the same project are processed independently
- No combined map showing all project files overlaid
- No project-level combined D2D export
- No designer editing of pairings or section boundaries
- No live sync or cloud deployment
- No file deletion, reprocessing, or reordering
- Sequential P### IDs are not concurrent-safe (acceptable for single-user local use)
- Legacy J##### jobs are not auto-migrated into projects

---

## Acceptance Conclusion

Stage 3C is accepted.

The project container layer is in place. Named projects work. Multi-file projects work. All existing outputs work from the project file table. The foundation for Stage 3B (designer review) is established.

---

## Next Stage

**Stage 3B — Designer Review & Export Readiness**

Designer review should not begin until:

1. Named projects work (✅ now true)
2. Multi-file projects work (✅ now true)
3. Project overview is usable (✅ now true)
4. All existing outputs accessible from project page (✅ now true)
5. At least one real multi-file project validated (✅ now true — 474 + 474c)

Stage 3B scope is to be defined by the project orchestrator before any code work begins.
