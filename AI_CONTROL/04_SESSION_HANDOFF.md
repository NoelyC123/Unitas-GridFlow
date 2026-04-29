# Session Handoff

## Date: 2026-04-28

## What happened this session

### Practitioner-review remediation build — implemented

The first remediation pass from the 2026-04-28 practitioner review has now been implemented.

Shipped:

- Forward-facing D2D/Clean Chain language was refocused as Design Chain / Raw Working Audit.
- The review page was reframed as Existing / Proposed Pole Proximity QA while keeping reviewed override behaviour.
- The map now draws basic connected Design Chain spans from `sequenced_route.json`.
- Span distances are available through hover/click detail without permanent label clutter on dense routes.
- The map side panel now includes Review Focus filters for design blockers, review-required records, replacement proximity, and missing height.
- The PDF front-facing issue list is now a structured `Design Review Items` table with record reference, coordinates, status, issue, design consequence, and recommended action.
- Project PDF reports now include Designer Review Status from `review.json`, including review notes and pairing override count.
- Project dashboard desktop rows and mobile cards now show Designer Review status, and review save/reset refreshes the project summary.
- The technical appendix remains in the PDF for raw issue detail.
- The Design Chain and Raw Working Audit CSVs now include first-pass evidence-quality columns showing captured/missing/inferred position, height, notes, replacement, and evidence-gap status.

Validation:

- `pytest -v` — 296 passed.
- `pre-commit run --all-files` — passed.
- Browser smoke check confirmed the span overlay on Gordon `P007/F001`.
- PDF route smoke check returned a valid PDF for `P007/F001`.
- Real project CSV export smoke checks confirmed evidence columns on Gordon `P007/F001` and Bellsprings `P008/F001`.
- Real project map smoke checks confirmed Review Focus controls on Gordon `P007/F001` and Bellsprings `P008/F001`.
- Real project PDF smoke checks returned valid PDFs for Gordon `P007/F001` and Bellsprings `P008/F001`.
- Real project dashboard smoke checks confirmed Gordon `P007/F001` shows reviewed and Bellsprings `P008/F001` shows needs review.
- End-of-day closure smoke check passed for Gordon `P007/F001` and Bellsprings `P008/F001` across project dashboard/API, review page, map page/data, PDF, Design Chain, and Raw Working Audit.

Commits:

- `72c1d35 Refocus D2D outputs as design chain`
- `9e212a7 Improve design handoff map and PDF review`
- `aee2a9d Polish map route visual hierarchy`
- `a2dc426 Add map legend for design chain overlays`
- `9f246c0 Add evidence quality to handoff exports`
- `543a4be Add map review focus filters`
- `ce6f455 Add designer review status to project PDFs`
- `8796e13 Show designer review status on project dashboard`

Additional context captured 2026-04-29:

- `AI_CONTROL/30_FOUNDER_DOMAIN_AND_AI_USAGE_CONTEXT.md` records the founder's repo-safe context on SaaS clarification, AI tooling cost control, telecoms Field Maps experience, OHL/design background, knowledge-capture needs, and iPad trial idea.
- Use that note before broad Stage 4, AI-feature, SaaS, or commercial-model discussion.

Next:

- The remediation build has now been reviewed against real Gordon/Bellsprings outputs at route level.
- The next useful step is either a narrow Claude Desktop product/UX review of the latest remediation result or operational use on the next real job.
- Do not jump into Stage 4, photo upload, tablet capture, PoleCAD export, or DNO submission packs from this remediation work alone.

---

### Practitioner-led full tool review — remediation phase defined

A detailed practitioner-led review was completed using the Bellsprings real-life survey-to-design test.

Reviewed local-only documents:

- `GridFlow_Review_Page_Validation_Notes_With_Photos.docx`
- `Unitas_GridFlow_View_Map_Section_Review.docx`
- `Unitas_GridFlow_Download_PDF_Feature_Final_Review.docx`
- `Unitas_GridFlow_D2D_Features_Review_Only.docx`
- `Unitas_GridFlow_Additional_Improvements_All_4_Features.docx`

Decision:

- Full review folder remains local-only evidence and is ignored by Git.
- Sanitized repo summary added as `AI_CONTROL/29_PRACTITIONER_REVIEW_SUMMARY.md`.
- Current phase is practitioner-review remediation, not Stage 4 implementation.
- First build should start with terminology/wording and D2D-to-Design-Chain refocus before larger functional work.

Prioritised remediation:

1. Terminology and wording pass.
2. Rename/refocus D2D outputs into Design Chain / Raw Working Audit.
3. Reframe EX/PR pairing as proximity QA, without deleting override logic until dependencies are inspected.
4. Add basic map span rendering.
5. Improve PDF findings into a structured issue/action table with coordinates.

Boundary:

- Do not build photo upload, tablet capture, structured field forms, PoleCAD export, or DNO submission packs from this review alone.
- Treat the review as evidence to improve the current Stage 3 handoff surfaces first.

---

### Domain reference integrated — repo-safe summary added

The private `GRIDFLOW_DOMAIN_REFERENCE_1.md` master reference was reviewed and strengthened with:

- claim status labels: practitioner knowledge, validated in GridFlow, research-backed, hypothesis/future, commercial/strategic
- current-versus-future product boundary
- D2D-as-legacy-workaround framing
- validated evidence links from Gordon/NIE/Bellsprings work
- open implementation questions for PoleCAD, design numbering, EXpole interpretation, D2D evidence, and Stage 4 capture
- standards/privacy cautions

Repository boundary:

- The full private reference remains outside Git and should not be copied wholesale into the repository.
- A repo-safe development summary was added as `AI_CONTROL/28_DOMAIN_REFERENCE_SUMMARY.md`.
- Future work should use the summary for day-to-day development and the private master only for strategic/domain review.

---

### Strategic handoff framing correction — D2D is the workaround, not the product

Claude Desktop challenged the wording around D2D and the project direction was clarified.

Decision:

- Manual D2D spreadsheets are the legacy workaround caused by a missing direct bridge between survey output and design tools.
- GridFlow should not be framed as "automating D2D" as the final product model.
- GridFlow should be framed as making the D2D step unnecessary by producing trusted, structured, design-ready handoff outputs from survey evidence.
- The current Clean Chain and D2D Working View CSVs remain valid transitional outputs, because they reduce current manual work and help designers review the route.
- Real D2D spreadsheets are still useful evidence, but only to understand existing manual decisions, missing fields, ordering conventions, EXpole/proposed handling, and PoleCAD/design-handoff requirements.
- The strategic target is design-ready handoff, eventually as close to PoleCAD-direct import as verified evidence allows.

Boundary:

- Do not build a PoleCAD-specific exporter until the actual import format and trust requirements are verified.
- Do not redesign around one company's or one designer's D2D spreadsheet.
- Do not treat D2D as the destination. Treat it as the old process GridFlow is replacing.

---

### Bellsprings EWM285 operational validation — completed

Work-colleague evidence was received, inspected, organised locally, and used for the first real operational validation after Stage 3 closure.

Local-only evidence location:

- `/Users/noelcollins/Desktop/UGF Documentation April 2026/REAL_VALIDATION_EVIDENCE/`

What the files are:

- `01_Bellsprings_EWM285_Design_Package/01_Raw_Survey/Bellsprings_Woodside_Park_11kV_Rebuild_Trimble_Controller_Export.csv` — raw Trimble/controller-style survey export for `Woodside Park 11kV Rebuild`.
- `01_Bellsprings_EWM285_Design_Package/02_Design_Outputs/` — real downstream design deliverables for the same job:
  - pole schedule
  - route map
  - profile
  - technical information sheet
- `01_Bellsprings_EWM285_Design_Package/03_Original_Zip/Sample.zip` — original received Bellsprings archive, retained unchanged.
- `02_EW_Scopes_Workplans/01_Site_Plans_and_Workplans/` — scope/workplan/site-plan DOCX documents, not raw survey files. They show real work-package instructions such as transformer replacement, tee-off pole replacement, inter-pole replacement, H-pole replacement, HV terminal pole replacement, and switching points.
- `02_EW_Scopes_Workplans/02_Original_Zip/Scopes_of_Work.zip` — original received scopes archive, retained unchanged.

How Bellsprings was used:

- Processed in GridFlow as project `P008/F001`.
- Rulepack: `SPEN_11kV`.
- Initial evidence pack: `/Users/noelcollins/Desktop/Unitas_GridFlow_Validation_Run_2026-04-27_143117_Bellsprings_EWM285_Operational_Validation.zip`.
- Initial comparison document: `04_Notes/bellsprings_initial_comparison.md` inside that pack.

Initial findings:

- GridFlow successfully ingested and processed the Bellsprings CSV.
- The pole schedule coordinates matched raw survey points closely enough to prove this is a strong before/after validation sample.
- `Pline` and `110xing` were incorrectly entering the structural/proposed chain.
- Real pole schedule numbering and final design-pole interpretation do not match GridFlow provisional numbering directly.
- Some final design poles use coordinates corresponding to `EXpole` records; this is a future reviewed-design interpretation gap, not an immediate parser bug.

Code fix shipped:

- `Pline`, `110xing`, `33xing`, `11xing`, and `HVxing` are now context records in both intake classification and QA structural filters.
- Focused tests were added for role classification, structural-only QA, and span checks.
- Full validation: `pytest -v` — 287 passed.
- `pre-commit run --all-files` — passed.
- Commit: `eb88bac Classify Bellsprings crossing codes as context`.

After-fix validation:

- Bellsprings reprocessed successfully.
- Issue count changed from 24 to 18.
- Structural/context counts changed from 46/10 to 40/16.
- Replacement signals changed from 9 to 3.
- After-fix evidence pack: `/Users/noelcollins/Desktop/Unitas_GridFlow_Validation_Run_2026-04-27_144746_Bellsprings_EWM285_After_Context_Code_Fix.zip`.

Important boundary:

- Raw colleague files, PDFs, DOCX files, generated `uploads/`, and validation packs remain local-only and are not committed to Git.
- Do not implement EXpole-as-final-design-pole handling, design-number alignment, photo capture, tablet capture, or Stage 4 workflows from this evidence alone.
- The next useful step is another operational comparison/review, not a broad feature build.

---

### Stage 3 closure — operational use phase begins

Stage 3 is now closed for the current evidence set.

Reason:

- Stage 3C, Stage 3B, Stage 3A1, and Stage 3A2 are implemented and validated.
- The Gordon real-file field trial proved protected remote/mobile intake, project dashboard review, map, PDF, D2D Chain, D2D Working View, and Designer Review.
- Mobile intake polish was implemented and validated with iPhone screenshots.
- A validation evidence-pack utility was added and used to create a final Gordon evidence pack with raw input, app outputs, review JSON, PDF/D2D exports, notes, prompt, and 14 iPhone screenshots.
- A final map wording clarity polish now distinguishes mapped records from total survey records, and QA replacement signals from reviewed EXpole assignments.

Decision:

- Stop internal Stage 3 polish.
- Use GridFlow on a real operational survey-to-design job.
- Let real friction define the next build.

Future roadmap preserved:

- Trimble/GNSS remains the coordinate/source-of-position authority.
- Unitas GridFlow remains the structured UK OHL survey-to-design workflow, validation, evidence, field-capture, and handoff layer around Trimble/controller/GIS data.
- Stage 4 tablet/iPad structured field capture, photo evidence, richer surveyor capture, and Trimble/GIS integration remain valid future roadmap.
- Do not implement Stage 4 until operational use evidence identifies the first field-capture requirement worth building.

New control document:

- `AI_CONTROL/27_STAGE_3_CLOSURE_AND_OPERATIONAL_USE.md`

Latest validation:

- `pytest -v` after map clarity polish — 284 passed.
- `pre-commit run --all-files` — passed.

---

### Stage 3 mobile intake polish — implemented

Claude Desktop approved a narrow Stage 3 mobile usability follow-on after the Gordon field trial. Cursor/GPT implemented only the approved scope.

Implemented:

- Homepage wording updated from early "Pre-CAD QA Tool" / DNO compliance framing to survey-to-design project intake, review, and D2D handoff framing.
- Homepage quick-start links now prioritise Projects and New Upload, with Legacy Jobs and Health as secondary links.
- Upload and legacy jobs page navigation now keeps Projects visible and labels upload as New Upload.
- Map viewer legacy "Jobs" back-link changed to Projects for non-project map views.
- Project detail page now keeps the desktop table but adds a mobile-only survey file card layout below 768px.
- Mobile cards show filename, file ID, processing status, intake status, rulepack, record/issue/P/W/F counts, survey day, uploaded-by, surveyor note, office feedback, and Map/Review/PDF/D2D actions.

Not changed:

- No backend logic.
- No processing pipeline.
- No D2D export logic.
- No map sidebar restructure.
- No designer review page redesign.
- No hosted deployment, app accounts, cloud storage, photo upload, tablet capture, or live Trimble sync.

Validation run:

- `pytest -v` — 283 passed.
- `pre-commit run --all-files` — passed.

Next validation:

- Reload the local app/templates and check `https://gridflow.unitasconnect.com` from iPhone/mobile data.
- Confirm `P007` uses the mobile card layout and the action buttons are easy to tap.

---

### First controlled field trial — Gordon real file

The first controlled field trial was run through the protected remote workflow.

Setup:

- Protected URL: `https://gridflow.unitasconnect.com`
- Upload device: iPhone on mobile data
- Survey file: `Gordon_Pt1_-_Original.csv`
- Project: `P007` / `Test with actual survey data`
- File: `F001`

Result:

- Remote upload worked.
- Project dashboard updated.
- Gordon processed successfully:
  - 157 records
  - 39 issues
  - 126 PASS
  - 25 WARN
  - 4 FAIL
  - 102 sequenced proposed supports
  - 24 matched EXpoles
  - 0 unmatched EXpoles
  - 2 sections
- Designer review was marked reviewed without pairing reassignment.
- Map, PDF, D2D Chain, D2D Working View, and Review routes all worked.

Validation conclusion:

- The core remote workflow passed.
- The project dashboard made sense after upload.
- Gordon EXpole pairings were acceptable for this validation run but must remain designer-reviewable.
- D2D Chain and Working View are good enough transitional handoff outputs to reduce manual spreadsheet preparation, while remaining reviewed/provisional outputs rather than final PoleCAD import format.
- Biggest friction is mobile usability: tables and review controls are cramped on phone, and homepage/navigation wording still reflects early QA-tool language.

Recommended next task:

- Decide whether to approve a narrow Stage 3 mobile usability follow-on:
  - mobile-friendly project file cards
  - clearer Map / Review / PDF / D2D action buttons
  - compact mobile review/export summary
  - updated homepage wording around project intake and D2D handoff

Do not jump to hosted deployment, app accounts, cloud storage, photo upload, tablet capture, live Trimble sync, or later-stage features.

---

### Stage 3A2: Cloudflare Access-gated remote trial — complete

The primary Stage 3A2 route was validated using a named Cloudflare Tunnel and Cloudflare Access. Stage 3A2 is closed as a controlled remote-access validation success.

Operational setup completed:

- Cloudflare zone: `unitasconnect.com`
- Tunnel name: `gridflow`
- Tunnel hostname: `gridflow.unitasconnect.com`
- Tunnel origin: local GridFlow app on `http://localhost:5001`
- Cloudflare Access application: `gridflow`
- Access policy: email allow policy for Noel
- Authentication method: Cloudflare Access email / one-time PIN

Validation evidence:

1. iPhone on mobile data opened `https://gridflow.unitasconnect.com`.
2. Cloudflare Access login screen appeared before GridFlow loaded.
3. Email one-time PIN was received and accepted.
4. GridFlow loaded after authentication.
5. `/projects/` loaded remotely.
6. `/upload` loaded remotely.
7. Non-sensitive `sample_data/mock_survey.csv` was uploaded from iPhone.
8. Project dashboard updated with project `P006` / `iPhone Test`.
9. Local stored project metadata confirms:
   - file `F001`
   - filename `mock_survey.csv`
   - status `complete`
   - uploaded by `Noel`
   - surveyor note `Testing`
   - 5 poles
   - 10 issues
   - review status `reviewed`
10. Output routes for `P006/F001` returned successfully:
    - project dashboard
    - Map
    - PDF
    - D2D Chain
    - D2D Working
    - Review

Boundary:

- No real or sensitive survey CSVs were uploaded during the Access-gated test.
- No app accounts, app-level auth, hosted deployment, cloud storage migration, photo upload, tablet capture, or live Trimble sync were built.
- Data at rest remains on the local Mac; Cloudflare provides the protected HTTPS tunnel.
- Remote availability depends on the Mac and `cloudflared tunnel run gridflow` staying online.

Recommended next decision:

- Stage 3A2 is validated for the controlled remote-access trial objective.
- A later stage/decision is needed before always-on hosted deployment, backups, app-level accounts, or wider user rollout.

---

### Stage 3A2: Temporary tunnel connectivity — validated, not accepted

Cursor/GPT installed `cloudflared`, confirmed the local GridFlow app was reachable on `127.0.0.1:5001`, and started a temporary unauthenticated Cloudflare Tunnel using:

```bash
cloudflared tunnel --url http://localhost:5001
```

Temporary URL used:

- `https://basically-movements-morgan-surname.trycloudflare.com`

Phone / external-device validation passed:

1. Home page loaded.
2. `/projects/` loaded.
3. `/upload` loaded.

Important boundary:

- No real or sensitive survey CSVs were uploaded.
- This is **temporary unauthenticated connectivity validation only**.
- This is **not full Stage 3A2 acceptance** because Cloudflare Access is not active.
- Full Stage 3A2 acceptance still requires a Cloudflare domain/zone, named tunnel, and Cloudflare Access gate before any real survey-data workflow validation.

Next proper step:

1. Add a Cloudflare domain/zone.
2. Create a named `gridflow` Cloudflare Tunnel.
3. Add a DNS route such as `gridflow.<domain>`.
4. Configure Cloudflare Access with approved email / one-time PIN.
5. Then validate authenticated remote upload, project dashboard update, Map/PDF/D2D links, and Review.

---

### Stage 3A2: Remote Access Trial — planned

Cursor/GPT converted the Claude Desktop deployment analysis and ChatGPT review into a committed Stage 3A2 plan.

Key decision:

- Use **Cloudflare Tunnel + Cloudflare Access** as the first controlled remote-access trial.
- Use **Tailscale** as the private trusted-device fallback.
- Defer **Render/Railway/full hosted deployment** until the remote workflow proves useful and data handling requirements are clearer.
- Do not build app user accounts, cloud storage migration, photo upload, tablet capture, or live Trimble sync in Stage 3A2.

Files added or changed:

| File | Change |
|------|--------|
| `AI_CONTROL/25_STAGE_3A2_DEPLOYMENT_PLAN.md` | Stage 3A2 remote-access plan |
| `README.md` | Local remote-access trial commands and validation checklist |
| `AI_CONTROL/01_CURRENT_STATE.md` | Current state updated for Stage 3A2 plan |
| `AI_CONTROL/02_CURRENT_TASK.md` | Next task set to remote-access trial |
| `CHANGELOG.md` | Planning/documentation entry |

The next practical validation is to run the existing Flask app locally, expose it through Cloudflare Tunnel + Access, and test upload/dashboard/export/review from a phone or external trusted device.

---

### Stage 3A1: Local Daily Intake MVP — implemented and validated

Cursor/GPT implemented the approved Stage 3A1 local daily intake scope from `AI_CONTROL/23_STAGE_3A_DESIGN_BRIEF.md`.

Files added or changed:

| File | Change |
|------|--------|
| `AI_CONTROL/23_STAGE_3A_DESIGN_BRIEF.md` | New — Stage 3A1 local intake scope and Stage 3A2 cloud boundary |
| `AI_CONTROL/24_STAGE_3A_VALIDATION_ACCEPTANCE.md` | New — validation evidence |
| `app/project_manager.py` | Added intake metadata, office feedback update, and review-aware intake status |
| `app/routes/api_projects.py` | Added intake capture during project presign and office feedback API |
| `app/templates/upload.html` | Added survey day / uploaded-by / surveyor note fields |
| `app/static/js/upload-manager.js` | Sends intake metadata with project uploads |
| `app/templates/project.html` | Shows intake status, survey notes, and office feedback per file |
| `tests/test_project_manager.py` | Added intake metadata and status tests |
| `tests/test_project_integration.py` | Added intake API integration tests |

Focused validation:

- `tests/test_project_manager.py tests/test_project_integration.py` — 41 passing
- Real-file temporary-root validation passed for Gordon and Strabane 474/474c intake flows

Stage 3A1 remains local-only by design. Cloud/remote access is now a Stage 3A2 planning task, not an active implementation task.

---

### Stage 3B: Designer Review & Export Readiness — implemented and validated

Claude Code implemented the Stage 3B MVP across two commits in one work session, following the approved brief at `AI_CONTROL/21_STAGE_3B_DESIGN_BRIEF.md`.

**Commit `a9b3ee2`:** Add Stage 3B design brief

**Commit `7daa5a9`:** Add Stage 3B designer review overlay

Files added or changed:

| File | Change |
|------|--------|
| `app/review_manager.py` | New — review data layer |
| `app/routes/api_review.py` | New — review REST API |
| `app/routes/review_page.py` | New — review page route |
| `app/templates/review.html` | New — Bootstrap 5 review UI |
| `app/routes/d2d_export.py` | Modified — project exports apply review overlay |
| `app/routes/api_intake.py` | Modified — reprocessing clears stale review |
| `app/__init__.py` | Modified — blueprint registration |
| `tests/test_review_manager.py` | New — 20 unit tests |
| `tests/test_review_integration.py` | New — 9 integration tests |

**Test count:** 273 passing (up from 244)

**Pre-commit:** clean

---

### What Stage 3B delivers

A designer can now:

1. Navigate to `/review/project/<project_id>/<file_id>` to see the review page for a processed file.
2. View all auto-detected EXpole pairings in a table.
3. Reassign any EXpole to a different proposed pole using a dropdown, or mark it as unmatched.
4. Enter review notes and mark the file as "Reviewed".
5. Download D2D Chain or D2D Working View exports — reviewed exports show "Designer Reviewed — <timestamp>" in the header; unreviewed exports remain "provisional".
6. Reset the review at any time — deletes `review.json`, exports revert to auto-generated state.

The original `sequenced_route.json` is never modified. The review overlay is applied at export time on a deep copy.

---

### Previous session (Stage 3C — recorded for continuity)

Stage 3C (Project Management / multi-file job support) was implemented and validated in the prior session.

- Commit: `b0b5331`
- Test count at close of 3C: 244

---

## Current state

- Stage 3A1 local daily intake implemented and validated
- Stage 3A2 Cloudflare Tunnel + Access trial complete
- First controlled Gordon field trial complete
- Temporary unauthenticated tunnel page reachability validated from phone/external device
- Access-gated remote upload/dashboard/export/review smoke test passed with non-sensitive data
- Stage 1 complete
- Stage 2A, 2B, 2C implemented and closed
- Stage 3C implemented and validated — commit `b0b5331`
- Stage 3B implemented and validated — commits `a9b3ee2`, `7daa5a9`
- Branch is up to date with `origin/master`

---

## Known caveats (by design — not bugs)

- EXpole pairing review only — section boundary editing deferred
- No route sequence editing, no pole attribute editing, no map-based editing
- No cross-file review — each file is reviewed independently
- Reviewed state affects D2D CSV exports only; PDF update deferred
- `reviewed_by` hardcoded to "Designer" — configurable later
- No multi-user conflict resolution — last-write-wins (single-user local use)
- Sequential P### IDs are not concurrent-safe (acceptable for single-user local use)
- Legacy J##### jobs not auto-migrated into projects

---

## Next steps

1. Decide whether to approve a narrow Stage 3 mobile usability follow-on based on the Gordon field-trial friction.
2. Keep using the named tunnel only for controlled trials while the Mac is online.
3. Keep the field-trial result in `AI_CONTROL/26_STAGE_3A_OPERATIONAL_RUNBOOK.md` as the evidence base.
4. Do not begin Render/Railway/full hosted deployment, app accounts, Stage 4 tablet capture, Stage 5 designer workspace expansion, or Stage 6 submission packs yet.

---

## Tool usage instructions for next chat

Use Cursor/GPT as the default working agent for routine repo work:

- documentation updates
- validation notes
- small scoped implementation
- test/check runs
- commits for agreed, narrow changes
- operational guidance such as starting the app or tunnel

Use Claude Desktop selectively as the project orchestrator:

- stage closure decisions
- next-stage scope decisions
- ambiguous product direction
- commercial/strategic tradeoffs
- deciding whether to move from controlled tunnel trial to broader field trial, hosted deployment, or later-stage work

Do not use Claude Desktop for routine admin, small doc edits, or obvious mechanical updates.

Use Claude Code only when the task is code-heavy, risky, or benefits from autonomous repo-wide implementation:

- multi-file feature implementation
- complex refactors
- substantial test additions
- debugging failures that require broad code inspection
- infrastructure/code changes beyond simple operational setup

Do not use Claude Code for routine docs, small validation records, or simple command guidance.

Use ChatGPT as a second-opinion / analysis tool when useful:

- reviewing strategic options
- challenging assumptions
- commercial framing
- comparing deployment/access approaches
- drafting questions for orchestrator review

Do not treat ChatGPT output as project truth unless it is reviewed and folded into the active control layer.

Source-of-truth order remains:

1. Real validation evidence
2. `AI_CONTROL/` active control files
3. Repo code and tests
4. Documentation
5. AI outputs

Current hard boundary:

- Do not build app accounts, hosted deployment, cloud storage migration, photo upload, tablet capture, live Trimble sync, Stage 4, Stage 5, or Stage 6 work unless explicitly approved as a new stage/task.
