# Stage 3 Options Analysis

## Prepared by: Claude Desktop (Project Orchestrator)
## Date: April 2026
## Status: Planning only — no implementation

---

## Context

Stage 2 is closed. The tool now takes raw controller dumps and produces structured D2D replacement outputs: clean chain exports, interleaved working views, section-aware sequencing, EXpole matching, and provisional design numbering. 211 tests passing. Validated on 4 real files across OSGB and Irish Grid.

The question is: what delivers the most value next?

---

## The Three Options

### Option A: Live Intake / Daily Sync

**What it means:** Deploy the tool to a server. Give the surveyor a way to upload/sync controller data daily or during fieldwork. The office sees the job building up while the survey is still active. Validation catches missing information earlier — potentially while the surveyor is still on site or nearby.

**What it requires:**
- Cloud deployment (the docker/deploy infrastructure exists but is minimal — nginx.conf and a Dockerfile stub)
- Authentication (currently none — anyone who can reach the URL can upload)
- A persistent "project" or "ongoing job" concept (currently each upload creates a disconnected job with a random ID like J76076)
- Network connectivity for the surveyor (on-site or end-of-day)
- A concept of "incremental upload" — adding data to an existing job rather than creating a new one
- Mobile-friendly upload interface (the current upload page is desktop-oriented)

**Honest assessment:** This is architecturally the biggest change. It moves the tool from a local development Flask app to a deployed production service. The code changes are not trivial — authentication, persistent storage, incremental job updates, deployment configuration, and mobile-responsive UI. The real risk is not that it's technically impossible — it's that it pulls the project into DevOps and infrastructure work that is far from the domain value. You'd spend weeks on deployment, auth, and server management before adding any survey-to-design value.

### Option B: Designer Review & Export Readiness

**What it means:** Add the ability for a designer to review the tool's sequencing output, correct mistakes (wrong EXpole pairings, wrong sequence order, wrong section boundaries), approve the chain, and then export a designer-approved version. The tool becomes a review workspace, not just a one-shot processor.

**What it requires:**
- An interactive review UI (the current map viewer is read-only — the designer can view but not edit)
- Editable EXpole matches (currently fixed by spatial proximity)
- Editable section boundaries (currently auto-selected by heuristic)
- Editable design pole numbering (currently auto-generated)
- An "approved" vs "provisional" state for each job
- Probably a more sophisticated frontend (React or similar) rather than the current server-rendered Bootstrap HTML

**Honest assessment:** This is essentially a partial Stage 5 (Designer Workspace) brought forward. The value is real — without designer editing, the output is "take it or leave it," which limits trust and adoption. But building a good interactive review interface is significant UI/UX work. The current frontend is server-rendered HTML with minimal JavaScript. Moving to an interactive editing interface is a step change in frontend complexity. The risk is scope creep — once you start building an editable workspace, the feature list grows fast.

### Option C: Multi-File Job Support / Stage 2.5

**What it means:** Allow multiple survey CSV files to be uploaded and managed as one project. The 474 and 474c files are currently separate disconnected jobs. In reality they're two surveys of the same area, done at different times or covering different sections. The tool should let you group them, compare them, and produce combined or coordinated outputs.

**What it requires:**
- A "project" layer above individual file jobs (currently the data model is one file = one job with a random ID)
- Upload multiple CSVs to the same project
- Per-file processing (each file gets its own chain, EXpole matching, sections)
- Project-level overview (how many files, total poles, combined coverage, overlapping areas)
- Possibly merged output across files (combined chain if the files cover sequential route sections)
- Project naming/labelling (currently jobs have random IDs with no human-readable name)

**Honest assessment:** This is the most natural extension of Stage 2. The data structures already exist — each file produces a sequenced_route.json and meta.json. What's missing is the container that groups them. This is primarily a data management and UI change, not an algorithmic one. The risk is relatively low because it doesn't require new sequencing logic, cloud deployment, or interactive editing — it's organising what already works.

---

## Analysis Against Your 10 Criteria

### 1. Which option gives the most value next?

**Option C (Multi-File)** gives the most immediate practical value.

Here's why: right now, if you upload the Gordon file and then want to upload the 474 and 474c files for a different job, you have three disconnected random-ID jobs with no way to tell which is which or which belong together. The jobs page shows J76076, J28931, J39991 — meaningless labels. A real designer managing 5-10 active projects would be lost immediately.

The ability to create a named project ("Gordon Pt1 Rebuild" or "Strabane 474"), upload multiple files to it, and see them grouped together is basic usability that makes the tool genuinely usable beyond validation testing.

Option A (Live Intake) gives the biggest eventual value but requires the most infrastructure work before any survey-to-design value is delivered. Option B (Designer Review) gives high value but requires significant UI complexity.

### 2. Which option is lowest risk?

**Option C (Multi-File)** is clearly lowest risk.

It builds on existing proven code. Each file still gets processed through the same pipeline. The new layer is data organisation, not new algorithms. No cloud deployment. No authentication. No complex frontend framework. No architectural changes to the processing pipeline.

Option A is highest risk (infrastructure, deployment, auth, mobile). Option B is medium risk (significant UI work, frontend framework change likely needed).

### 3. Which option best follows from Stage 2?

**Option C (Multi-File)** follows most naturally.

Stage 2 proved the tool can process individual files and produce useful D2D output. The immediate gap is that real jobs involve multiple files (474 + 474c, Gordon Original + future survey additions) and the tool has no concept of grouping them. This is the missing piece that makes Stage 2's output practically usable across a portfolio of work.

Option B follows well conceptually (process → review → approve → export) but requires a significant UI leap. Option A is a different axis entirely (deployment, not functionality).

### 4. Which option best supports the long-term six-stage vision?

**Option C (Multi-File)** supports all future stages.

Every future stage needs the concept of a named project with multiple files:
- Stage 3 (Live Intake): the surveyor syncs data to a project, not a random job ID
- Stage 4 (Tablet Capture): structured data is captured against a project
- Stage 5 (Designer Workspace): the designer reviews a project, not individual files
- Stage 6 (DNO Submission): submission packs are per project

If you build multi-file project support now, every subsequent stage has a foundation to build on. If you skip it and go to live intake first, you'd have to retrofit the project concept later.

Option B is Stage 5 brought forward. Option A is Stage 3 as originally planned but without the project foundation.

### 5. What should remain out of scope?

For ALL three options, these remain out of scope:
- Final PoleCAD-specific export format
- Photo/image integration into the processing pipeline
- AI/ML features (OCR, image analysis)
- DNO submission pack generation
- Commercial packaging (pricing, multi-tenant, billing)
- Integration with external GIS platforms
- New QA rule expansion unless driven by new validation files

For Option C specifically, also out of scope:
- Merging chains across files into one combined route (too complex for first version)
- Cross-file EXpole matching (file A's EXpoles matched to file B's proposed poles)
- Automated file-to-section mapping (deciding which file covers which route section)

### 6. What real-world evidence do we need before building?

**For Option C:** We already have the evidence. The 474 and 474c files are two real surveys of the same job area that are currently processed as separate disconnected jobs. The Gordon file has the PR1/PR2 splits showing how one survey is divided into sections. The evidence for needing project-level grouping is already in hand.

**For Option A:** We would need evidence of what "daily sync" actually means in practice. Does the surveyor have mobile data on site? Do they sync from the van at end of day using WiFi? Do they email the file? Do they use a cloud drive? This varies by company and site. We don't have this evidence yet.

**For Option B:** We would need a real designer to attempt to use the current output and tell us specifically what they would want to edit. We have your domain knowledge, but we haven't observed someone actually trying to use the D2D export as a working file.

### 7. What would a minimal first version look like?

**Option C minimal version:**
- Add a "projects" concept: named container for related files
- Create project page: name, description, list of uploaded files
- Upload multiple files to a project
- Each file still processes independently through the existing pipeline
- Project overview: total files, total poles, combined coverage summary
- Project-level jobs list (instead of the current flat random-ID list)
- Human-readable project names instead of J76076-style random IDs

That's it for a minimal version. No merging, no cross-file analysis, no combined exports. Just organisation.

**Option A minimal version:**
- Deploy to a cloud server (Render, Railway, or similar)
- Add basic authentication (even just a shared password)
- Make the upload page mobile-friendly
- Add the project concept from Option C (you'd need it anyway)
- Allow "add file to existing project" workflow

Even the minimal Option A requires deployment + auth + mobile + project concept.

**Option B minimal version:**
- Add editable EXpole pairings (drag-and-drop or dropdown reassignment)
- Add editable section boundaries (click to set/unset)
- Add an "approve" button that marks the chain as designer-reviewed
- Keep it within the current Flask/Bootstrap UI

Even minimal Option B needs interactive frontend components that don't exist yet.

### 8. What would be the success criteria?

**Option C:**
- 474 and 474c can be uploaded to the same named project
- The project page shows both files with their individual summaries
- The jobs list shows project names instead of random IDs
- A designer looking at the project page immediately understands what files they have and what state each is in
- No existing functionality breaks

**Option A:**
- The tool is accessible from a mobile device over the internet
- A surveyor can upload a file from their phone/tablet at end of day
- The office can see the uploaded file and its validation results without waiting for a USB drive
- No existing functionality breaks

**Option B:**
- A designer can review the chain and correct at least one type of error (e.g. wrong EXpole pairing)
- The corrected version can be exported
- The designer can see the difference between "provisional" and "reviewed" output
- No existing functionality breaks

### 9. What risks should we avoid?

**For all options:**
- Do not start deployment/infrastructure work before the core product value is proven
- Do not build a complex frontend framework change unless the feature requires it
- Do not merge files across projects without explicit domain evidence for how that should work
- Do not assume PoleCAD import format is known
- Do not build features that only make sense in a deployed multi-user environment when the tool is still used locally by one person

**Option-specific risks:**
- Option A: risk of spending weeks on DevOps instead of product value
- Option B: risk of scope creep once editing capability is opened up
- Option C: risk of over-engineering the project data model before understanding real usage patterns

### 10. What is my recommendation?

**Build Option C (Multi-File Job Support) as Stage 3.**

Rationale:

1. It gives immediate practical value — the tool becomes usable for managing real work, not just validation testing
2. It's the lowest risk — builds on existing code, no deployment, no complex UI
3. It follows naturally from Stage 2 — organises what already works
4. It's a prerequisite for everything else — Stages 4, 5, and 6 all need the project concept
5. The evidence already exists — the 474/474c files prove the need
6. It can be built and validated in 1-2 sessions
7. It doesn't require cloud deployment, authentication, or frontend framework changes

**Rename it from "Stage 2.5" to "Stage 3: Project Management."** The original Stage 3 (Live Intake) becomes Stage 4, and everything else shifts by one. The six-stage vision becomes:

1. Post-survey QA gate ✅
2. D2D elimination ✅
3. Project management (multi-file, named projects) ← NEW CURRENT
4. Live intake platform (was Stage 3)
5. Structured field capture (was Stage 4)
6. Designer workspace (was Stage 5)
7. DNO submission layer (was Stage 6)

Or alternatively, keep the original numbering and call this "Stage 2.5" or "Stage 3A" to avoid renumbering everything. Your call.

**After Option C is built and validated**, Option A (Live Intake) and Option B (Designer Review) both become much easier to build because they have the project foundation to build on.

---

## What I Would NOT Do

I would not build Option A (Live Intake) next. The tool is still a local Flask app used by one person for validation. Deploying it to the cloud before the project management layer exists would mean deploying a tool that can't even group related files together. Get the product right locally first, then deploy.

I would not build Option B (Designer Review) next. It's valuable but premature — the tool needs to be organisationally usable (projects, named jobs, grouped files) before adding interactive editing. Building an editing interface for a tool that can't even tell you which files belong to which project is putting polish before structure.

---

## Summary

| Criterion | Option A: Live Intake | Option B: Designer Review | Option C: Multi-File |
|---|---|---|---|
| Immediate value | Medium (needs infrastructure first) | High (but needs complex UI) | **High (solves real gap now)** |
| Risk | High | Medium | **Low** |
| Follows from Stage 2 | Loosely | Well | **Most naturally** |
| Supports future stages | Yes (but needs project concept anyway) | Partially (Stage 5 early) | **Yes (foundation for all)** |
| Evidence available | Weak (no sync workflow evidence) | Medium (domain knowledge only) | **Strong (474/474c prove it)** |
| Build effort | 3-5 sessions | 2-4 sessions | **1-2 sessions** |
| Recommendation | Later | Later | **Now** |
