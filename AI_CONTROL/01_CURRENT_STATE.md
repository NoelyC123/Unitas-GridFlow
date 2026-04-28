# Current State

## Project phase

**Stage 3 complete — practitioner-review remediation**

Stage 1 is complete.

Stage 2A, Stage 2B and Stage 2C are implemented and validated. Stage 2 is formally closed.

Stage 3C (Project Management / multi-file job support) is implemented and manually validated.

Stage 3B (Designer Review & Export Readiness) is implemented and validated.

Stage 3A1 (Local Daily Intake MVP) is implemented and validated.

Stage 3A2 (Remote Access Trial) is complete. The primary Cloudflare route was validated with a named Cloudflare Tunnel for `gridflow.unitasconnect.com` protected by Cloudflare Access email one-time PIN. A phone on mobile data authenticated through Access, loaded the app, uploaded non-sensitive `sample_data/mock_survey.csv`, updated the project dashboard, and opened Map/PDF/D2D/Review outputs. Tailscale remains the private fallback. Render/Railway/full hosted deployment is deferred.

Stage 3 mobile validation is complete. The real Gordon file was uploaded through the protected remote workflow as `P007/F001`, reviewed, exported, captured in a validation evidence pack, and used to drive a final map wording clarity polish.

The project is now in a **practitioner-review remediation phase** after Stage 3 closure. A detailed review of the Validation page, Map, PDF, D2D/chain exports, and cross-feature workflow has defined the next narrow improvement pass.

Strategic framing: D2D is the legacy workaround GridFlow is eliminating, not the future product model. Current Clean Chain / D2D Working View CSVs are transitional design-handoff outputs. The Clean Chain should now be reframed as the primary Design Chain / Design Handoff Export, while the old D2D Working View becomes a secondary Raw Working Audit / Legacy Working View. The real destination is a trusted design-ready handoff, eventually as close to PoleCAD-direct import as verified evidence allows.

---

## What works

- Raw Trimble GNSS controller dump intake (tested on 4 real files)
- CRS detection: Irish Grid TM65, ITM, OSGB27700
- Coordinate conversion to WGS84 for map display
- Record-role classification (structural, context, anchor)
- Replacement pair detection (EXpole to Pol matching)
- Evidence gates (7 scoped design gates)
- Confidence-aware severity tiers (PASS/WARN/FAIL)
- Interactive Leaflet map with filtering and basic Design Chain span overlay
- PDF pre-design briefing report with structured design review issue/action table
- DNO rulepack inference from geography
- Column/header normalisation for structured CSVs
- Context feature classification (Hedge, Fence, Wall, Gate, Track, Road, Tree, Stream, Pline, 110xing, 33xing, 11xing, BTxing, HVxing, LVxing, Ignore)
- Design Chain export (`<job_id>_design_chain.csv`) as a transitional design-handoff output with evidence-quality columns
- Raw Working Audit export (`<job_id>_raw_working_audit.csv`) for file-order traceability with evidence-quality columns
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
- **Stage 3A2: closed as a controlled remote-access validation success**
- **Stage 3 mobile polish: homepage/navigation/project-file cards validated with Gordon iPhone screenshots**
- **Stage 3 validation evidence pack utility: packages raw input, app outputs, review JSON, screenshots, notes, and AI review prompt**
- **Stage 3 map clarity polish: distinguishes mapped records from total survey records and QA replacement signals from reviewed EXpole assignments**
- **Practitioner review summary: repo-safe summary of the full 2026-04-28 review added at `AI_CONTROL/29_PRACTITIONER_REVIEW_SUMMARY.md`**
- **Practitioner review remediation: terminology, D2D-to-Design-Chain refocus, EX/PR proximity wording, basic map span rendering, and structured PDF issue/action table implemented**

## Counts

- **Tests passing:** 291
- **DNO rulepacks:** 4 (SPEN, SSEN, NIE, ENWL)
- **Real files validated:** Gordon, 4-474, 513, 474c, Bellsprings EWM285

## What was just shipped

- Practitioner-review remediation builds
  - Forward-facing D2D/Clean Chain wording has been refocused around Design Chain and Raw Working Audit.
  - The review page now presents Existing / Proposed Pole Proximity QA while preserving reviewed override logic.
  - Map data now exposes basic Design Chain spans from `sequenced_route.json`, and the Leaflet map renders connected route lines.
  - PDF Design Review Items now use a structured table with record reference, coordinates, status, issue, design consequence, and recommended action.
  - Design Chain and Raw Working Audit CSVs now expose position, height, notes, replacement, and evidence-gap status derived from the existing sequence output.
  - Validation: `pytest -v` — 291 passed; `pre-commit run --all-files` — passed.

- Practitioner-led full tool review
  - Five local-only review documents were created from the Bellsprings real-life survey-to-design test, including practitioner and colleague feedback.
  - Reviewed areas: Validation/Review page, View Map, Download PDF, D2D/chain exports, and cross-feature additional improvements.
  - Claude Desktop produced a structured product review from those documents.
  - Sanitized repo summary added: `AI_CONTROL/29_PRACTITIONER_REVIEW_SUMMARY.md`.
  - Full review folder remains local-only and ignored by Git: `/Users/noelcollins/Unitas-GridFlow/Unitas GridFlow Full Tool Review 28th April 2026/`.
  - Remediation sequence now shipped: terminology/wording pass, D2D-to-Design-Chain rename/refocus, EX/PR proximity QA reframing, basic map span rendering, and PDF structured issue table.

- Bellsprings EWM285 operational validation and fix
  - Work-colleague evidence was organised locally as a real validation package: raw Bellsprings Trimble/controller CSV, pole schedule, route map, profile, TIS, and separate scope/workplan/site-plan documents.
  - Bellsprings was processed as project `P008/F001` against `SPEN_11kV`.
  - Initial comparison showed `Pline` and `110xing` were being treated as proposed/structural records even though they are route/crossing context.
  - Narrow operational fix shipped: `Pline`, `110xing`, `33xing`, `11xing`, and `HVxing` are context records in both intake classification and structural-only QA.
  - Before/after result: issue count dropped from 24 to 18; structural/context counts changed from 46/10 to 40/16.
  - New after-fix validation pack: `/Users/noelcollins/Desktop/Unitas_GridFlow_Validation_Run_2026-04-27_144746_Bellsprings_EWM285_After_Context_Code_Fix.zip`.
  - Real design-numbering and EXpole-as-final-design-pole interpretation remain documented as future evidence gaps, not code changes.

- Stage 3 closure
  - Stage 3C, Stage 3B, Stage 3A1, Stage 3A2, mobile intake polish, validation evidence packs, and map clarity polish are complete for the current evidence set.
  - Controlled remote access validated with Cloudflare Tunnel + Cloudflare Access.
  - Real Gordon field-trial evidence pack generated with raw input, generated outputs, review JSON, PDF/D2D exports, notes, prompt, and iPhone screenshots.
  - No app accounts, hosted deployment, cloud storage migration, photo upload, tablet capture, or live Trimble sync were introduced.
  - Next step is operational use on a real job.

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
3. No section boundary editing.
4. Stage 3A2 uses the local Mac as the origin, so remote access depends on the Mac and `cloudflared` tunnel staying online.
5. Stage 2 output is still provisional and not a verified PoleCAD import schema.
6. Evidence-quality export columns are a first-pass visibility layer only; field-note/photo/provenance capture remains future Stage 4 work.
7. The map now shows basic connected spans, but not advanced topology controls, section editing, voltage styling, or combined project-level map overlay.
8. EX/PR pairing is currently too prominent as a reassignment workflow and should be reframed as proximity QA before deeper workflow changes.
9. PDF report now has a structured issue/action table, but it is not yet a formal DNO submission pack.
10. Reviewed state affects Design Chain / Raw Working Audit CSV exports only — reviewed-state PDF integration remains future work.
11. Stage 4 structured field capture/tablet/photo workflows remain future roadmap and require operational evidence before design.
12. The old D2D spreadsheet should be used as evidence of current manual decisions and conventions, not as the target product shape. The strategic target is design-ready handoff/PoleCAD-ready evidence once actual import requirements are known.

## Strategic position

- No competing product exists in this space
- Tool validated on real NIE and SPEN survey files
- Project owner has direct survey and design experience
- Full 6-stage vision defined (see 00_PROJECT_CANONICAL.md)
- Stage 3 complete — next work is a narrow practitioner-review remediation pass before Stage 4
- Stage 4 remains the future structured field-capture layer around Trimble/GNSS/controller/GIS data, not a replacement for Trimble positioning
- Repo-safe domain reference summary added at `AI_CONTROL/28_DOMAIN_REFERENCE_SUMMARY.md`; the full private domain reference remains outside Git and should not be copied wholesale into the repository.
- Repo-safe practitioner review summary added at `AI_CONTROL/29_PRACTITIONER_REVIEW_SUMMARY.md`; the full review folder remains local-only evidence and ignored by Git.
