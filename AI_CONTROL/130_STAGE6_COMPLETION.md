# Stage 6 Completion Review

## Status

Stage 6 is complete and validated on P_LOCAL_002.

All 10 poles are surveyed, linked to ENWL records, assessed for conflicts, and given a
formal readiness status. The workspace displays three-source evidence and readiness per pole.

---

## What Stage 6 Delivered

### Stage 6A — ENWL Trace Parser and Evidence Classification

- `gridflow/enwl_trace/parser.py`: conservative GeoJSON parser with four relationship
  categories (`direct_pole_identity`, `direct_equipment_linked_to_pole`,
  `route_span_evidence`, `nearby_context_only`)
- Trace inspector CLI
- Established the evidence classification model used by all later stages

### Stage 6B — Three-Source Evidence Combiner and Workspace Display

- `gridflow/evidence_combiner/combiner.py`: combines `pole_notes.md`, ENWL pole/equipment
  records, and ENWL trace GeoJSON into one per-pole evidence record
- `scripts/combine_pole_evidence.py` and survey summary tooling
- `gridflow/workspace/enwl_evidence_adapter.py`: workspace display of DNO evidence by
  relationship level
- Workspace `pole_detail.html` updated with Level 1–4 DNO Evidence card
- Conductor caution wording established: route-level provenance only

### Stage 6C — Formal Pole-to-ENWL Linking

- `gridflow/evidence_combiner/linker.py`: `LinkingResult` dataclass with six linking
  mechanisms in priority order
- `scripts/link_survey_poles.py`: CLI producing markdown linking report
- `AI_CONTROL/126_PLOCAL002_LINKING_REPORT.md`: actual results for all 10 poles

### Stage 6D — Conflict Detection

- `gridflow/conflict_detector/`: detects mismatches between field evidence, ENWL records,
  and trace data
- `scripts/detect_conflicts.py`: CLI for survey-level conflict detection
- Zero conflicts detected across all 10 P_LOCAL_002 poles

### Stage 6E — Design-Readiness Logic Update

- `gridflow/readiness/assessor.py`: four-level readiness assessor consuming Stage 6C
  linking results and Stage 6D conflict reports
- `scripts/assess_readiness.py`: CLI for survey-level readiness assessment
- `gridflow/workspace/readiness_adapter.py`: workspace adapter for readiness display
- Workspace updated with Design Readiness card (green/amber/red/grey badge per pole)
- Workspace job header updated with readiness summary counts
- `design_ready = True` only at `DESIGN_READY` level

---

## P_LOCAL_002 Final Evidence State

| Measure | Count |
|---|---|
| Poles surveyed | 10 / 10 |
| Poles linked to ENWL records | 10 / 10 |
| HIGH confidence links (`fid_polestructure`) | 3 (Poles 03, 05, 06) |
| MEDIUM confidence links (`support_no`) | 7 (Poles 01, 02, 04, 07, 08, 09, 10) |
| Conflicts detected | 0 |
| Poles design-ready | 0 (correct — no span-confirmed conductor) |
| Poles review-required | 3 (Poles 03, 05, 06 — HIGH link + route conductor) |
| Poles not-ready | 7 (MEDIUM link + no conductor evidence) |

Zero design-ready poles is the correct and expected outcome. P_LOCAL_002 is a field
survey prototype. The system correctly identifies that conductor specification has not been
proven per span — a DNO engineering record gap, not a survey failure.

---

## Test Growth

| Stage | Tests |
|---|---|
| Stage 5 baseline | 1368 |
| Stage 6E completion | 1468 |
| New tests added in Stage 6 | 100 |

---

## What Stage 6 Does NOT Do

- **No span-confirmed conductor assignment.** All conductor evidence is Level 3 route/span
  provenance. The exact conductor FID-to-span-to-pole chain is not resolved.
- **No `conductor_spec_missing` clearance from route-level evidence.** This flag remains
  set on all P_LOCAL_002 poles because conductor specification is route-level only.
- **No design calculations.** Stage 6 produces evidence records and readiness status; it
  does not perform engineering calculations.
- **No PoleCAD output.** The PoleCAD import format is out of scope until a verified
  mapping is agreed with DNO.
- **No photo integration.** Field photos are counted and listed; their content is not
  analysed or parsed by code.
- **No mobile capture.** Structured digital field capture is Stage 4.

---

## Key Principles Preserved Throughout Stage 6

**ENWL evidence is provenance, not design clearance.** Every level of Stage 6 treats ENWL
records as network evidence to be displayed, classified, and linked — not as automatic
authorisation for design to proceed.

**`conductor_spec_missing` is not cleared by route-level evidence.** The conductor caution
wording established in Stage 6B is present in the workspace display at every level, and
the readiness assessor explicitly does not clear this flag from Level 3 evidence.

**`design_ready` is only `True` at the `DESIGN_READY` level.** Stage 6E is the only stage
that touches this flag, and it sets it only when all conditions in the readiness spec are
met — which no P_LOCAL_002 pole currently meets.

**Four-level readiness is more honest than a boolean.** `DESIGN_READY_WITH_CAUTIONS`
(amber) for Poles 03, 05, and 06 correctly communicates: high evidence quality, confirmed
linking, no conflicts, but conductor specification unresolved. A binary `design_blocked`
would obscure the real state.

**GPS proximity is never a sole linking basis.** Confirmed across Stage 6C: GPS proximity
was detected as a secondary signal for two poles but never elevated to a primary linking
method.

---

## Stage 7 Recommendation

Stage 6 completes the evidence integration foundation. Stage 7 options in priority order:

### 7A — Workspace maturation

- Photo viewer embedded per pole
- Notes viewer with structured field extracted
- Comparative views across multiple jobs
- Filter by readiness level in job overview

### 7B — Span-level conductor assignment

- Prove the exact conductor FID-to-span-to-pole chain for P_LOCAL_002 spans
- Allow `conductor_spec_missing` to be cleared where proven
- Unlock `DESIGN_READY` status for qualifying poles

### 7C — Export formats

- Route summary export for designer review
- Readiness report export (PDF or structured CSV)
- ENWL evidence provenance export per job

### 7D — Multi-job comparative views

- Compare linking confidence across surveys
- Flag jobs with unusually high conflict counts
- Evidence quality dashboard across active jobs

**Recommended next step:** 7A workspace maturation combined with 7B span conductor
assignment for P_LOCAL_002 as proof case, then 7C export once the readiness model is
stable.
