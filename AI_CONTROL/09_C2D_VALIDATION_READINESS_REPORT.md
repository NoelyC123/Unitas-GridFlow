> **HISTORICAL — Stage 2 closure document. Read-only.**
> This document describes completed Stage 2 work. Do not update it.
> For current project state see `01_CURRENT_STATE.md`.

# C2D Validation Readiness Report

Date: 2026-05-05

Source commit: `f42e809 Merge C2D map workspace usability polish`

Task: **C2D-AD validation evidence and readiness consolidation**

## Scope

This pass validates the current C2/D map/review workspace against local real-job evidence and records what is already built so future Codex work does not repeat it.

Out of scope:

- Stage 4/full survey-platform expansion
- New field-capture/mobile/GIS platform work
- New popup/platform features beyond validation and documentation

## Jobs Checked

Runtime route checks used current Flask routes, not only stored fixture JSON.

| Job | Evidence style | Map view | Map data | PDF | Runtime evidence |
| --- | --- | --- | --- | --- | --- |
| `P005/F001` | Gordon-style OSGB controller survey | 200 | 200 | 200 PDF | 155 features, 101 spans, 27 context records, 7 angle highlights |
| `P008/F001` | Bellsprings-style SPEN rebuild | 200 | 200 | 200 PDF | 56 features, 28 spans, 16 context records, 5 third-party records, 3 angle highlights |
| `P009/F001` | Bellsprings-style duplicate/current local validation | 200 | 200 | 200 PDF | 56 features, 28 spans, 16 context records, 5 third-party records, 3 angle highlights |
| `P010/F001` | Gordon-style operational review fixture | 200 | 200 | 200 PDF | 155 features, 101 spans, 27 context records, 7 angle highlights |
| `P009/F002` | Irish Grid/controller-style 2814_474c fixture | 200 | 200 | 200 PDF | 91 features, 63 spans, 24 context records, 8 angle highlights, 4 replacement-pair audit records |

## Confirmed Current Behaviour

- Map workspace routes render with C2/D controls: angle highlights, span controls, PDF links, design-readiness panel hooks, and bounded side-panel scroll styling.
- Runtime map enrichment attaches span features and context/crossing links for the checked real jobs.
- Angle items are now counted and controlled as runtime highlights/subsets; toggling the angle control hides/shows highlight treatment rather than removing structural records.
- Context/crossing records are enriched as context records and carry span-corridor links where relevant: all Gordon-style context records checked had links; Bellsprings had 15 of 16 linked.
- Span/cable electrical ownership remains span/cable-owned. Runtime checks found no point-level voltage/conductor/cable display leaks in the checked jobs.
- Popup truthfulness behaviour is guarded by static tests for context height-evidence exclusion, proposed design-decision wording, equipment/photo absence wording, stay evidence wording, and angle highlight semantics.
- PDF/report routes returned valid PDFs for all checked local jobs, and existing tests cover design-readiness and C2/D evidence-gate wording.

## Built Capabilities To Avoid Repeating

Do not re-implement these as new work:

- Raw controller/GNSS-style CSV parsing and structured CSV intake
- OSGB36, Irish Grid/TM65, and WGS84-derived coordinate handling
- Completeness and design-readiness summaries for newly processed/current pipeline data
- Existing/proposed lifecycle and EX/PR relationship detection
- Route/design-chain sequencing and span feature generation
- Context/crossing enrichment and span-corridor linking
- C2D popup truthfulness/evidence-status wording
- Angle pole highlight semantics from C2D-AC
- Span/cable field-ownership policy for voltage/conductor/cable data
- PDF QA/design-readiness handoff route generation

## Historical Or Stale Evidence Notes

- Some local stored `meta.json` and `map_data.json` files predate the latest C2/D runtime enrichment and do not persist all current metadata fields.
- The checked routes enrich those older fixtures at request time, so route behaviour is stronger than the stored JSON alone suggests.
- Stored validation fixtures should be refreshed in a focused follow-up if they are to be treated as canonical evidence snapshots.

## Remaining Risks And Follow-Ups

- **Fixture refresh:** Regenerate or persist canonical local validation outputs so stored metadata carries current design-readiness, field-ownership, span, and context evidence.
- **Report wording parity:** PDF/report smoke checks confirm route health, but a focused wording review should align report language with C2D popup truthfulness.
- **Browser evidence pack:** Add focused screenshot/browser validation for representative popup examples, layer toggles, and side-panel usability.

## Recommended Next Tasks

1. **C2D-AE validation fixture refresh:** reprocess or persist refreshed canonical outputs for Gordon, Bellsprings, and Irish Grid/controller fixtures.
2. **C2D-AF report wording parity:** tighten PDF/report evidence wording and add focused tests where wording can drift from popup truthfulness.
3. **C2D-AG browser validation pack:** capture a small real-job browser evidence set for map controls, popup examples, and review-panel layout.
