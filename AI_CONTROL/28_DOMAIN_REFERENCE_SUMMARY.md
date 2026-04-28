# Domain Reference Summary

## Purpose

This file is the repo-safe development summary of the private GridFlow domain reference.

The full master reference is a private working document and should not be copied wholesale into Git. It contains practitioner knowledge, market research, commercial thinking, named target organisations, and future product hypotheses. Use this summary for day-to-day development guidance.

---

## Claim status labels

Use these labels when turning domain knowledge into product decisions:

| Label | Meaning | Development use |
|-------|---------|-----------------|
| Practitioner knowledge | Direct field/design experience and experienced-practitioner review | Strong product input, but validate with real files before changing behaviour |
| Validated in GridFlow | Observed in real GridFlow runs or protected by tests | Safe to treat as current product truth |
| Research-backed | Based on standards, public DNO material, or vendor/market research | Check current source before encoding exact values |
| Hypothesis / future | Plausible future need or inferred workflow gap | Do not implement until operational evidence supports it |
| Commercial / strategic | Buyer, market, competitor, pricing, procurement, or positioning context | Keep private; do not expose in public UI or routine docs |

---

## Current product boundary

GridFlow currently provides:

- post-survey QA and design-readiness checks
- raw Trimble/controller CSV intake
- CRS detection and map conversion
- structural/context/anchor role classification
- EX/PR replacement signal detection
- confidence-aware QA gates
- named projects and multi-file intake
- designer review of EXpole pairings
- PDF, map, transitional Clean Chain / Design Chain, and D2D Working View / Raw Working Audit outputs
- protected remote/mobile intake validated through Cloudflare Access
- validation evidence-pack capture

GridFlow does not yet provide:

- final verified Optimal PoleCAD import
- tablet/iPad structured field capture
- photo evidence upload/linking
- app user accounts or cloud storage
- full DNO submission pack generation
- final engineering certification or DNO compliance sign-off

---

## D2D framing

Manual D2D spreadsheets are the legacy workaround caused by a missing direct bridge between survey evidence and design tools.

GridFlow should not be built as a perfect clone of one old D2D spreadsheet. The long-term goal is to make the manual D2D step unnecessary by producing trusted, structured, design-ready handoff outputs from survey evidence.

Current Clean Chain and D2D Working View CSVs are still valid transitional outputs because they reduce manual rebuilding and give designers something practical to review today.

The 2026-04-28 practitioner review confirmed the next product framing:

- Clean Chain should become the primary **Design Chain Export** / **Master Design Chain**.
- D2D Working View should become a secondary **Raw Working Audit** / **Legacy Working View**.
- The D2D concept should be retired from forward-facing product language, while the strategic idea of eliminating the old workaround remains valid.

Real D2D spreadsheets remain useful evidence. They should be used to understand:

- what manual decisions designers currently make
- what fields are missing from raw survey exports
- how final design numbering is assigned
- how EXpoles, proposed poles, retained poles, and not-required records are represented
- what PoleCAD/design-handoff inputs are still missing

They should not define the future product shape by themselves.

---

## Evidence-quality model

The core product principle is not "is the field present?" It is:

**What evidence exists, how strong is it, is it structured or inferred, and does a designer need to review it?**

| Domain | Strong evidence | Weak evidence | GridFlow treatment |
|--------|-----------------|---------------|--------------------|
| Coordinates | Known CRS, sane converted location | ambiguous columns or swapped values | detect and warn |
| EX/PR pairing | close offset plus matching code/remark/sequence | distance only | probable signal, designer review |
| Pole height | measured/read with source | number with unknown source | present but source unknown |
| Birthmark | visible, measured, photographed | not recorded | missing structural evidence |
| Stay direction | surveyed anchor or numeric bearing | free-text "stay" only | classify evidence level |
| Crossing | category plus measured clearance | generic Road/BT/LV code | crossing present, clearance incomplete |
| Conductor | confirmed from records/measured | assumed or absent | missing design evidence |
| Photos | attached to record and evidence type | loose folder/camera roll | unlinked unless manually attached |
| Ground level | known datum and GNSS quality | raw elevation only | provisional vertical evidence |
| Section boundary | explicit terminal/branch evidence | inferred from gap/angle | candidate, require confirmation |

---

## Validated evidence so far

- Real Gordon, NIE, and Bellsprings/SPEN files have been processed through GridFlow.
- Stage 3 remote/mobile validation proved protected Cloudflare Access intake, project dashboard review, map, PDF, D2D exports, review workflow, and evidence-pack capture.
- Bellsprings EWM285 showed that `Pline`, `110xing`, `33xing`, `11xing`, and `HVxing` are context/crossing evidence, not structural poles.
- The Bellsprings context-code fix is implemented in both intake classification and QA structural filtering, with tests.
- Bellsprings also showed a future gap: real pole schedules may use different design numbering and may treat some `EXpole` records as final design pole coordinates. That needs a reviewed-design interpretation step before implementation.
- The 2026-04-28 practitioner review identified terminology, Design Chain framing, EX/PR proximity QA framing, map span rendering, and PDF issue-table structure as the next narrow remediation priorities.

---

## Current domain rules for development

- Feature code is a clue, not final truth.
- Context features such as roads, hedges, fences, streams, tracks, BT/LV/HV crossings, and power-line/crossing observations must not enter the main structural chain unless reviewed evidence says otherwise.
- A probable EX/PR replacement relationship is a QA/design prompt, not a confirmed engineering decision.
- Absence of evidence is not evidence that something is safe or complete.
- "Crossing identified" is different from "clearance measured and design-ready."
- "Pole height present" is different from "pole height source verified."
- A photo is only useful design evidence when it is linked to a pole, stay, crossing, issue, or explicit evidence type.
- GNSS elevation is useful for route/profile context, but raw elevation alone is not enough for final clearance compliance.
- Retain/replace decisions depend on condition, pole age/class, loading, equipment, route/stay/clearance constraints, and client/DNO instruction; they cannot be inferred from feature code alone.

---

## Future implementation candidates

These are not current tasks. They are candidate directions once real operational evidence justifies them:

- reviewed-design interpretation for design pole numbering and EXpole-as-final-design-pole cases
- verified PoleCAD input/export once a real import template or designer walkthrough is obtained
- structured birthmark and pole-height-source capture
- stay anchor/bearing capture and stay evidence grading
- crossing clearance category and measured-clearance capture
- manual photo linking to pole/stay/crossing/evidence records
- structured conductor evidence and confidence level
- explicit section/branch boundary review
- DNO submission-pack evidence only after designer workspace maturity

---

## Open evidence questions

Before building the next major capability, answer as many of these as possible from real work:

- What exact input format does Optimal PoleCAD accept in the user's real distribution workflow?
- Which PoleCAD fields are imported, and which are manually keyed by designers?
- How do different designers assign final design pole numbers?
- When does an `EXpole` become the final design pole rather than a replaced reference point?
- What do real D2D spreadsheets show about current manual decisions?
- Which missing field most often forces the designer back to notes, photos, WhatsApp messages, or a re-survey?
- Which Stage 4 capture item would remove the most real rework first: photos, birthmarks, stay anchors/bearings, crossing clearances, conductor identity, or access/wayleave notes?

---

## Standards caution

Standards and DNO policy references are working context, not legal or engineering certification. Exact values, issue numbers, and DNO-specific requirements must be checked against current official documents before they are encoded as rules or shown in client-facing outputs.
