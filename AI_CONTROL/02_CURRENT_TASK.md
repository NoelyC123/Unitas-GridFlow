# Current Task

## Phase

**Stage 3 closed — practitioner-review remediation**

Stage 3A1 (Local Daily Intake MVP) is implemented and validated. It is closed.

Stage 3A2 planning is documented in `AI_CONTROL/25_STAGE_3A2_DEPLOYMENT_PLAN.md`.

The Cloudflare Tunnel + Access route has been validated from a phone on mobile data. Stage 3A2 is closed as a controlled remote-access trial. The first controlled field trial has now been run with the real Gordon file through the protected remote workflow. Claude Desktop approved a narrow Stage 3 mobile usability follow-on, and the scoped homepage/navigation/project-file-card polish has been implemented and validated with an iPhone evidence pack. A final map wording clarity polish was also completed.

Validation completed:

- Home page loaded through a temporary `trycloudflare.com` tunnel.
- `/projects/` loaded remotely.
- `/upload` loaded remotely.
- No real or sensitive survey CSVs were uploaded.
- Named tunnel `gridflow` created for `gridflow.unitasconnect.com`.
- Cloudflare Access email one-time PIN prompt appeared before app access.
- iPhone on mobile data authenticated successfully through Access.
- Non-sensitive `mock_survey.csv` uploaded remotely into project `P006` / `iPhone Test`.
- Project dashboard updated remotely.
- Map, PDF, D2D Chain, D2D Working, and Review routes responded successfully for `P006/F001`.
- Real Gordon file uploaded remotely as project `P007` / `F001`.
- Gordon processed successfully: 157 records, 39 issues, 126 PASS, 25 WARN, 4 FAIL.
- Gordon review marked reviewed with 24 matched EXpoles and 0 unmatched EXpoles.
- Gordon Map/PDF/D2D Chain/D2D Working/Review routes all worked.
- Field-trial finding: core workflow passed; biggest friction is mobile table/review layout and outdated homepage wording.
- Homepage wording updated from Stage 1 QA/compliance framing to survey-to-design project intake and D2D handoff framing.
- Navigation updated so Projects and New Upload are primary, with Legacy Jobs secondary.
- Project detail page now renders mobile file cards with status, intake context, key counts, office feedback, and Map/Review/PDF/D2D actions.
- Validation evidence pack generated for `P007/F001` with raw input, app outputs, review JSON, PDF/D2D exports, 14 iPhone screenshots, validation notes, and AI review prompt.
- Map wording now distinguishes mapped records from total survey records.
- Replacement wording now distinguishes QA replacement signals from reviewed EXpole assignments.
- Bellsprings EWM285 work-colleague evidence package was organised locally and used for the first operational validation pass after Stage 3 closure.
- Bellsprings processed as project `P008/F001`; initial validation exposed `Pline` and `110xing` as context/crossing records that were incorrectly entering the structural chain.
- Narrow context-code fix shipped for `Pline`, `110xing`, `33xing`, `11xing`, and `HVxing`; after rerun, issues dropped from 24 to 18 and structural/context counts moved from 46/10 to 40/16.
- After-fix evidence pack generated: `/Users/noelcollins/Desktop/Unitas_GridFlow_Validation_Run_2026-04-27_144746_Bellsprings_EWM285_After_Context_Code_Fix.zip`.
- Full practitioner review completed on 2026-04-28 using the Bellsprings real-life workflow. Reviewed Validation/Review page, View Map, Download PDF, D2D/chain exports, and cross-feature improvements.
- Sanitized review summary added: `AI_CONTROL/29_PRACTITIONER_REVIEW_SUMMARY.md`.
- Full review folder remains local-only evidence and is ignored by Git: `/Users/noelcollins/Unitas-GridFlow/Unitas GridFlow Full Tool Review 28th April 2026/`.

---

## Stage 3A1 is closed

- Design brief: `AI_CONTROL/23_STAGE_3A_DESIGN_BRIEF.md`
- Validation acceptance: `AI_CONTROL/24_STAGE_3A_VALIDATION_ACCEPTANCE.md`
- Focused tests: `tests/test_project_manager.py tests/test_project_integration.py` — 41 passing
- Real-file validation: Gordon single-day intake and Strabane 474/474c multi-file intake passed
- Stage 3A2 plan: `AI_CONTROL/25_STAGE_3A2_DEPLOYMENT_PLAN.md`

---

## Current task

The first practitioner-review remediation pass is implemented and validated.

Completed remediation:

1. Terminology and wording pass across UI/export/PDF surfaces.
2. Rename/refocus D2D outputs:
   - Clean Chain / route-chain output became Design Chain / Master Design Chain.
   - D2D Working View became secondary Raw Working Audit.
3. Reframe EX/PR pairing as Existing / Proposed Pole Proximity QA without deleting reviewed override logic.
4. Add basic map span rendering between sequenced design-chain poles.
5. Improve PDF findings into a structured issue/action table with coordinates, status, design consequence, and recommended action.
6. Add first-pass evidence-quality visibility to Design Chain and Raw Working Audit CSV exports.
7. Add map Review Focus filters for design blockers, review-required records, replacement proximity, and missing height.
8. Add project designer review status to PDF reports.

Next useful step:

- Review the remediation build against real Gordon/Bellsprings outputs in the browser, generated PDF, and Design Chain / Raw Working Audit CSVs.
- If the user wants external review, give Claude Desktop the latest commit and ask for a narrow product/UX review of the remediation result.
- Do not begin Stage 4 or PoleCAD export until this remediation pass has been reviewed against real outputs.

Stage 3 proved:

- app reachable from a phone or external trusted device
- Cloudflare Access prompts for authentication before app access
- upload into a project works remotely with non-sensitive test data
- project dashboard updates remotely
- Map/PDF/D2D/Review links work remotely
- real Gordon survey data can be uploaded, reviewed, exported, and packaged as validation evidence
- mobile project intake is usable enough to stop internal polish and begin operational use
- Stage 2/3 handoff outputs are transitional replacements for the manual D2D workaround, not the future product model.
- The practitioner review proved the next priority is trust, terminology, connected map topology, and professional handoff/report clarity.

Evidence boundary:

- For Bellsprings, do not change EXpole/design-numbering logic yet. The real pole schedule shows some final design poles at EXpole coordinates, but that requires a separate reviewed-design interpretation step before implementation.
- Evidence-quality export columns are derived from existing sequence fields only; do not treat them as structured field capture, photo provenance, or final engineering certification.
- Keep Stage 4 structured field capture/tablet/photo/Trimble-GIS integration as future roadmap, not current implementation.
- Do not implement PoleCAD export until actual PoleCAD import requirements are verified.

---

## What not to do before the next stage is defined

- Do not begin section boundary editing
- Do not begin Render/Railway/full hosted deployment
- Do not build app user accounts or role-based auth
- Do not redesign architecture
- Do not begin Stage 4 tablet capture, photo upload, or structured field forms before operational use evidence
- Do not begin Stage 5 or 6 work
- Do not add new QA rules or sequencing algorithms
- Do not implement photo upload, tablet capture, or live Trimble sync in Stage 3A2
- Do not redesign outputs around the legacy D2D spreadsheet as if it is the destination. Use real D2D spreadsheets only to identify current manual decisions, missing data, and PoleCAD/design-handoff requirements.

---

## Relevant files

- `AI_CONTROL/23_STAGE_3A_DESIGN_BRIEF.md`
- `AI_CONTROL/24_STAGE_3A_VALIDATION_ACCEPTANCE.md`
- `AI_CONTROL/25_STAGE_3A2_DEPLOYMENT_PLAN.md`
- `AI_CONTROL/26_STAGE_3A_OPERATIONAL_RUNBOOK.md`
- `AI_CONTROL/27_STAGE_3_CLOSURE_AND_OPERATIONAL_USE.md`
- `AI_CONTROL/28_DOMAIN_REFERENCE_SUMMARY.md`
- `AI_CONTROL/29_PRACTITIONER_REVIEW_SUMMARY.md`
- `README.md`
- `app/project_manager.py`
- `app/routes/api_projects.py`
- `app/templates/project.html`
- `app/templates/upload.html`
- `app/static/js/upload-manager.js`
- `tests/test_project_manager.py`
- `tests/test_project_integration.py`
