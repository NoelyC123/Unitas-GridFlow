# Stage 3 Closure and Operational Use

## Closure decision

Stage 3 is closed for the current evidence set.

Completed Stage 3 capabilities:

- Stage 3C: named projects and multi-file project support
- Stage 3B: designer review overlay and reviewed/provisional exports
- Stage 3A1: local daily intake MVP
- Stage 3A2: controlled remote access through Cloudflare Tunnel + Access
- Mobile intake polish: updated homepage/navigation and mobile project file cards
- Validation evidence packs: repeatable packaging of raw input, app outputs, review state, screenshots, notes, and AI review prompt
- Map clarity polish: mapped records are distinguished from total survey records, and QA replacement signals are distinguished from reviewed EXpole assignments

The next step is not another internal polish pass. The next step is real operational use.

---

## Product direction preserved

Trimble/GNSS remains the coordinate and source-of-position authority.

Unitas GridFlow is the structured UK OHL survey-to-design workflow, validation, evidence, field-capture, and handoff layer around Trimble/controller/GIS data.

Current GridFlow works after survey data exists:

- ingest raw controller/survey files
- validate and normalise data
- classify records
- detect EX/PR relationships
- produce map, PDF, D2D Chain, D2D Working View, and review outputs
- package validation evidence

Future GridFlow may support structured field capture:

- tablet/iPad surveyor workflow alongside Trimble
- structured pole/support checklists
- stay, crossing, clearance, access, private-land, and condition evidence
- photos linked to pole IDs or feature records
- field completeness prompts before leaving site
- richer office/designer feedback while the job is active

These future capabilities remain valid roadmap. They are not current Stage 3 implementation work.

---

## Operational use objective

Use GridFlow on the next real survey-to-design job as the actual handoff workflow.

The key question is:

> Does GridFlow reduce real D2D/design handoff effort on an actual job?

This is stronger evidence than more internal validation.

---

## Operational use checklist

For the next real job:

1. Start GridFlow locally and expose it through the approved protected access route if remote/mobile access is needed.
2. Upload the real controller CSV into a named project.
3. Confirm the project dashboard shows the correct file, counts, status, intake context, and action links.
4. Open the map and confirm the route is in the correct location with no obvious outliers.
5. Review design-readiness, evidence gates, top risks, and recommended actions.
6. Open Designer Review and check:
   - section summary
   - proposed chain count
   - matched EXpoles
   - unmatched EXpoles
   - any pairing that needs reassignment
7. Mark the file reviewed only if the pairing/review state is acceptable.
8. Export:
   - PDF report
   - Clean Chain CSV
   - D2D Working View CSV
9. Try to use the D2D Working View instead of rebuilding the manual D2D spreadsheet from scratch.
10. Record what still required field notes, notebook pages, photos, designer memory, or manual spreadsheet work.

---

## Evidence to capture from operational use

Record:

- Did upload work reliably?
- Did the map and route sequence match the real route?
- Were EXpole pairings correct enough?
- Did the D2D Working View save time?
- What columns or information were missing for real D2D/PoleCAD preparation?
- What did the designer still need from notebooks, photos, WhatsApp, or memory?
- What would have helped the surveyor capture better data while still on site?
- What failed, confused, or slowed the workflow?

This evidence defines the next development step.

---

## Out of scope until operational evidence justifies it

Do not begin these immediately:

- tablet/iPad structured field capture
- photo upload or photo evidence management
- live Trimble sync
- hosted production deployment
- app user accounts or role-based auth
- cloud storage/database migration
- Stage 5 designer workspace
- Stage 6 DNO submission layer

They remain future roadmap, especially Stage 4 structured field capture around Trimble/controller/GIS data.
