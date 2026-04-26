# Stage 3 Execution Plan — Project Management (Multi-File Job Support)

## Prepared by: Claude Desktop (Project Orchestrator)
## Date: April 2026
## Status: Planning — awaiting domain owner approval

---

## Executive Summary

Stage 3 adds a "project" container above the current flat job model. Today every uploaded CSV creates a disconnected job with a random ID (J76076, J28931). Real work involves multiple related files — 474 and 474c cover the same Strabane area; Gordon has a raw file and two manual splits. The tool has no way to group, name, or compare them. Stage 3 fixes this with a minimal project layer: named projects, multiple files per project, per-file processing through the existing pipeline, and a project overview page. No new algorithms, no cloud deployment, no frontend framework change. Each file still runs through the same proven Stage 1/2 pipeline independently. The project layer is organisational, not computational. This is a 1-2 session build that creates the foundation every subsequent stage requires, validated by uploading the Gordon and NIE file sets into named projects and confirming the grouping, overview, and per-file access all work correctly.

---

## A. Execution Plan

### Current Data Model (what exists)

```
uploads/
  jobs/
    J76076/          ← one random ID per upload
      meta.json
      Gordon_Pt1.csv
      issues.csv
      map_data.json
      sequenced_route.json
    J28931/           ← unrelated random ID, same real-world area
      meta.json
      28-14_4-474.csv
      ...
```

No grouping. No naming. No relationship between J76076 and any other job.

### Target Data Model (Stage 3)

```
uploads/
  projects/
    P001_Gordon_Rebuild/
      project.json         ← name, description, created, file list
      files/
        F001/              ← was J76076
          meta.json
          Gordon_Pt1.csv
          issues.csv
          map_data.json
          sequenced_route.json
        F002/              ← second upload to same project
          meta.json
          ...
    P002_Strabane_474/
      project.json
      files/
        F001/
          meta.json
          28-14_4-474.csv
          ...
        F002/
          meta.json
          28-14_474c.csv
          ...
  jobs/                    ← legacy flat jobs remain accessible
    J76076/
    ...
```

### Milestone 1: Project CRUD (data layer)

**What:** Create/read/update projects. A project is a named container with a description and a list of file references.

**Data model — project.json:**
```json
{
  "project_id": "P001",
  "name": "Gordon Pt1 Rebuild",
  "description": "11kV refurbishment, Scottish Borders, SPEN area",
  "created": "2026-04-26T14:00:00Z",
  "updated": "2026-04-26T15:30:00Z",
  "files": [
    {
      "file_id": "F001",
      "filename": "Gordon_Pt1_-_Original.csv",
      "uploaded": "2026-04-26T14:00:00Z",
      "status": "complete",
      "rulepack_id": "SPEN_11kV",
      "pole_count": 157,
      "issue_count": 39,
      "sequence_summary": { ... }
    }
  ],
  "summary": {
    "total_files": 1,
    "total_poles": 157,
    "total_issues": 39,
    "rulepacks_used": ["SPEN_11kV"]
  }
}
```

**Key design decisions:**
- Project IDs are sequential: P001, P002, P003
- File IDs within a project are sequential: F001, F002
- Each file still gets its own meta.json, issues.csv, map_data.json, sequenced_route.json — the existing pipeline is unchanged
- project.json aggregates file-level summaries into a project overview
- Legacy flat jobs under uploads/jobs/ remain accessible (backward compat)

**NOT building:**
- Cross-file chain merging
- Cross-file EXpole matching
- Cross-file section coordination
- Project-level combined exports
- File deletion or reprocessing

### Milestone 2: Upload-to-Project Flow

**What:** Modify the upload page to support creating a new project or adding a file to an existing project.

**UX flow — new project:**
1. User goes to /upload
2. Sees new field: "Project name" (text input, required) and "Description" (optional)
3. Selects CSV file and DNO rulepack as before
4. Clicks "Upload & Validate"
5. System creates project folder, saves file, processes through existing pipeline
6. Redirects to project view page

**UX flow — add file to existing project:**
1. User goes to project view page for an existing project
2. Clicks "Add Survey File"
3. Selects CSV file and DNO rulepack
4. System saves file into existing project folder, processes through pipeline
5. Project overview updates with new file summary

**Backend changes:**
- /api/presign gains optional project_id parameter
- If project_id provided, file goes into that project's files/ folder
- If no project_id, a new project is created automatically from the filename
- The existing finalize route (/api/import/<job_id>) works unchanged — it processes the file wherever it lives
- project.json is updated after each file finalize

**NOT building:**
- Drag-and-drop multi-file upload
- Batch upload of multiple CSVs at once
- Auto-detection of which project a file belongs to

### Milestone 3: Project Overview Page

**What:** A new page at /project/<project_id> showing the project and its files.

**Content:**
- Project name and description (editable inline or via simple form)
- Project summary: total files, total poles, total issues, rulepacks used
- File table: one row per file showing filename, status, rulepack, pole count, issue count, P/W/F counts, actions (Map, PDF, D2D Chain, D2D Working View)
- "Add Survey File" button
- Link back to projects list

**NOT building:**
- Cross-file comparison view
- Combined map showing all files overlaid
- Project-level combined D2D export
- Interactive project editing beyond name/description

### Milestone 4: Projects List Page

**What:** Replace or augment the current /jobs/ page with a /projects/ page.

**Content:**
- Table of all projects: name, file count, total poles, created date, last updated
- Click project name → project overview page
- "Create New Project" button → upload page with project creation flow
- Legacy jobs section at bottom (or a "Legacy Jobs" tab) showing any flat jobs not yet assigned to projects

**NOT building:**
- Project archiving or deletion
- Project search or filtering
- Project tagging or categorisation

### Milestone 5: Backward Compatibility

**What:** Ensure everything that works today still works.

**Rules:**
- All existing /map/view/<job_id>, /pdf/qa/<job_id>, /d2d/export/<job_id>, /d2d/interleaved/<job_id> routes continue to work with the existing J##### job IDs
- The existing /jobs/ page still works
- The API endpoints still work
- The existing upload flow (without project) still works — it auto-creates a project
- 211 existing tests continue to pass unchanged

---

## What We Will NOT Build in Stage 3

- Cross-file chain merging or combined routing
- Cross-file EXpole matching
- Combined project-level D2D exports
- File deletion, reprocessing, or reordering
- Cloud deployment or authentication
- Mobile-specific UI
- Designer review/editing interface
- Photo/image integration
- Tablet field capture
- DNO submission packs
- New QA rules or sequencing algorithms
- Project archiving, deletion, search, or tagging

---

## Edge Cases

**Resurvey fragments:** A surveyor returns to the same route and uploads a second CSV with updated or additional points. For Stage 3, this is simply a second file in the same project. No merging, no conflict resolution. The designer sees both files in the project overview and handles them manually. Future stages may add comparison or merge capabilities.

**Duplicate points:** Two files in the same project may contain overlapping point IDs or coordinates. Stage 3 does not detect or resolve this. Each file is processed independently. The project overview shows both files' summaries side by side.

**Conflicting sectioning:** One file may section at a different point than another. Stage 3 does not coordinate sectioning across files. Each file has its own sequenced_route.json with its own sections.

**Mixed CRS:** One file may be Irish Grid, another OSGB. Stage 3 processes each file independently through the existing CRS detection and conversion pipeline. The project overview shows which rulepack was used for each file.

**Legacy jobs:** Existing J##### jobs remain accessible. They are not automatically migrated into projects. A future migration step could be added but is not part of Stage 3.

---

## Acceptance Tests

### Using existing validation files:

1. **Gordon project test:** Create project "Gordon Pt1 Rebuild". Upload Gordon Pt1 Original. Verify project overview shows 1 file, 157 poles, SPEN_11kV. Click through to map, PDF, D2D exports — all work.

2. **Multi-file project test:** Create project "Strabane 474". Upload 4-474. Verify project shows 1 file. Add 474c to same project. Verify project shows 2 files, combined pole count, both file summaries visible. Each file's map/PDF/D2D exports work independently.

3. **Small file test:** Create project "Strabane 513". Upload 513. Verify project overview shows correct summary for a small 11-point job.

4. **Legacy compatibility test:** Existing J##### jobs at /jobs/ still load. Existing map/PDF/D2D routes still work with J##### IDs.

### Synthetic test scenarios (in pytest):

5. **test_create_project:** POST to create project → project.json exists with correct structure
6. **test_add_file_to_project:** Upload file to existing project → project.json updated with file entry
7. **test_project_summary_aggregation:** 2 files in project → summary shows combined totals
8. **test_project_list:** Multiple projects exist → /api/projects/ returns all with summaries
9. **test_legacy_jobs_still_work:** Existing J##### job routes return correct data
10. **test_project_file_processing:** File in project goes through full pipeline → meta.json, issues.csv, map_data.json, sequenced_route.json all created correctly

---

## B. Handoff Criteria: Stage 3 (C) → Stage 3B (Designer Review)

Designer review is worth building ONLY when all of the following exist:

1. **Named projects work.** Files are grouped and accessible by project name, not random IDs.
2. **Multi-file projects work.** At least 2 files can be uploaded to the same project and accessed independently.
3. **Project overview is usable.** A designer can look at the project page and immediately understand what files they have, what state each is in, and where to access outputs.
4. **All existing outputs still work.** Map, PDF, D2D chain, D2D working view all accessible from the project file list.
5. **At least one real multi-file project has been validated.** The 474 + 474c project should be tested as a real grouped project.

Without these, designer review has nowhere to live — you'd be building an editing interface for disconnected random-ID jobs, which would have to be rebuilt when projects are added.

---

## C. Top 15 Risks and Mitigations (C → B → A)

### Stage 3C (Project Management) Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 1 | **File path refactoring breaks existing routes.** Moving from uploads/jobs/J##### to uploads/projects/P###/files/F### could break every existing route that constructs paths from job_id. | High | Keep uploads/jobs/ working as-is. Project files live in a separate tree. Existing routes use job_id unchanged. Project routes are new endpoints. |
| 2 | **project.json becomes stale if file processing fails mid-way.** If a file upload succeeds but finalize crashes, project.json may reference a file with status "processing" forever. | Medium | project.json is updated AFTER finalize completes. If finalize fails, the file entry shows status "error" with reason. |
| 3 | **Upload page UX becomes confusing with project creation added.** Adding project name, description, and "add to existing" options to the current simple upload form could overwhelm. | Medium | Keep it simple: "Project name" is one text field. "Add to existing" is only available from the project page, not the main upload page. First upload always creates a new project. |
| 4 | **Sequential project IDs collide under concurrent access.** Two simultaneous uploads could generate the same P### ID. | Low (single user now) | Use a simple max-ID-plus-one scan of existing project folders. Acceptable for single-user local use. Proper UUID generation can be added for multi-user deployment later. |
| 5 | **Legacy job migration creates confusion.** Users may not understand why some jobs are in "projects" and others are in "legacy jobs." | Low | Do not migrate automatically. Show legacy jobs in a separate section. Add a manual "Import to Project" option later if needed. |

### Stage 3B (Designer Review) Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 6 | **Scope creep once editing is introduced.** "Edit EXpole pairing" leads to "edit sequence order" leads to "edit section boundaries" leads to "edit pole attributes" leads to a full CAD interface. | High | Define exactly which fields are editable in the Stage 3B task. Start with ONLY: EXpole pairing reassignment and section boundary selection. Nothing else is editable. |
| 7 | **Frontend framework change required.** Interactive editing may push beyond what server-rendered Bootstrap HTML can do cleanly. | Medium | Evaluate whether vanilla JS with fetch() calls is sufficient for the minimal editing scope before committing to React/Vue. The current UI uses Bootstrap + vanilla JS successfully. |
| 8 | **Edited state vs original state confusion.** Once a designer edits pairings or sections, the system has two versions of truth. Which one do exports use? | Medium | Clear state model: "provisional" (auto-generated) → "reviewed" (designer-edited). Exports always use the latest state. Original auto-generated state is preserved for comparison. |
| 9 | **Undo/history complexity.** If the designer makes a mistake, can they revert? | Medium | Stage 3B MVP: no undo history. "Reset to auto-generated" button only. Full undo is Stage 5+. |

### Stage 3A (Live Intake) Risks

| # | Risk | Severity | Mitigation |
|---|------|----------|------------|
| 10 | **Cloud deployment diverts from product work.** Weeks spent on Dockerfiles, nginx, SSL, DNS, hosting provider decisions instead of survey-to-design value. | High | Use a minimal deployment platform (Render, Railway) with automatic SSL and deployment. Do not build custom infrastructure. |
| 11 | **Authentication opens compliance surface.** If the tool stores real survey data on a server, data protection (UK GDPR) and client confidentiality obligations apply. Survey data may include precise coordinates of DNO infrastructure. | High | Stage 3A MVP: single shared-password auth. No user accounts. No PII stored. Clear terms that data is provisional/development-only. Full auth and compliance is a Stage 5+ concern. |
| 12 | **Concurrent uploads create conflicts.** Two surveyors uploading to the same project simultaneously could corrupt project.json. | Medium | File-level locking on project.json writes. Each file goes into its own subfolder — no cross-file write conflicts. project.json updates are atomic read-modify-write with a lockfile. |
| 13 | **Mobile upload on poor connectivity.** Surveyors on rural sites may have intermittent 3G/4G. Large CSV uploads may fail mid-stream. | Medium | Support resumable uploads or at minimum detect and report partial uploads. Stage 3A MVP can require a complete upload — partial/resumable is a refinement. |
| 14 | **Data residency for EU/UK survey data.** If hosting on a US-based cloud provider, survey coordinates of UK infrastructure may cross jurisdictions. | Low-Medium | Host on a UK or EU region. Render and Railway both offer EU regions. Document the data residency choice. |
| 15 | **Surveyor adoption resistance.** Surveyors may resist changing their USB-handover habit if the new tool adds friction or requires steps they don't understand. | Medium | Stage 3A must be SIMPLER than USB handover, not harder. Upload from phone/tablet → one tap → done. If it's more complex than plugging in a USB drive, it won't be adopted. |

---

## D. Naming Scheme and AI_CONTROL Updates

### Proposed naming

Keep the original 6-stage vision numbering. Stage 3 subdivides into:

- **Stage 3C:** Project Management (multi-file job support) — build first
- **Stage 3B:** Designer Review & Export Readiness — build second
- **Stage 3A:** Live Intake / Daily Sync — build third

The C → B → A ordering reflects build sequence (foundation first, features second, deployment third). The letter scheme avoids renumbering the original 6-stage vision.

After Stage 3, the vision continues:
- Stage 4: Structured field capture (tablet/GIS)
- Stage 5: Designer workspace (full editing)
- Stage 6: DNO submission layer

### AI_CONTROL updates needed

**02_CURRENT_TASK.md** — should say:
- Phase: Stage 3C — Project Management
- Goal: named projects, multi-file support, project overview
- Not yet: designer review (3B), live intake (3A)

**04_SESSION_HANDOFF.md** — should record:
- Stage 2 closed (commit b2ce213)
- Stage 3 options analysed (18_STAGE_3_OPTIONS_ANALYSIS.md)
- Stage 3C approved as next build
- Stage 3B and 3A are planned but not started

**New file: AI_CONTROL/19_STAGE_3_EXECUTION_PLAN.md** — this document, saved to repo after approval.

---

## Open Questions for Domain Owner (max 8)

1. **Project naming convention.** Should the tool suggest a project name from the CSV filename, or should the user always type it manually? For example, uploading "Gordon Pt1 - Original.csv" could auto-suggest project name "Gordon Pt1".

2. **Should the upload page change, or should project creation be a separate page?** Option A: add project name field to existing upload page. Option B: new /projects/new page for creating a project, then upload from the project page. Option A is simpler; Option B is cleaner separation.

3. **Legacy job migration.** Do you want existing J##### jobs to remain accessible as legacy, or should we provide a "move to project" option? For now I recommend leaving them as legacy with no migration.

4. **Project-level rulepack.** Should a project have a default rulepack that applies to all files, or should each file keep its own rulepack selection independently? The 474 and 474c files both use NIE_11kV, but the Gordon file uses SPEN_11kV — so different projects would need different defaults.

5. **How many files per project is realistic?** The Gordon job has 1 raw file (plus 2 manual splits). The Strabane area has at least 3 related files (513, 474, 474c). What's the largest number of related files you'd expect for one real project? This affects UI layout decisions.

6. **Should the PR1/PR2 manual split files be uploadable alongside the original?** Or are they only useful as validation evidence? If a designer might want to upload both the original and the splits, the project should handle that.

7. **Project description — what goes in it?** Examples: "11kV refurbishment, Scottish Borders, SPEN area" or "Strabane Main PT.3, NIE Networks, 2025" or just a free text note? Is there a standard job description format in your industry?

8. **Do you want the project overview to show a combined map of all files' points?** This would overlay all files' survey points on one Leaflet map. It's technically straightforward (merge the map_data.json features from each file) but adds visual complexity. Should this be in Stage 3C or deferred?
