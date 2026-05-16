# GridFlow Delivery Style — Product-Forward Control Rule

## Purpose

This document records the preferred delivery style for GridFlow going forward.

GridFlow should not become trapped in over-cautious micro-steps. The project now has:

- a strong test suite
- active control files
- real P_LOCAL_002 evidence
- Stage 6A parser/classifier foundation
- Stage 6B evidence combiner, export utilities, survey summary, and read-only workspace display
- clean audit and provenance records

Future work should favour useful, visible, end-to-end progress while still protecting truthfulness and design-readiness boundaries.

## Core Principle

Prefer bigger vertical slices when they are read-only, evidence-only, and well tested.

Avoid unnecessary delay where a prototype can safely prove value without changing design readiness or production decisions.

## What Bolder Means

GridFlow workers may take larger, product-forward tasks when the work is isolated and validated.

Allowed examples:

- parser plus CLI inspector in one stage
- schema plus loader plus real sample records
- evidence combiner prototype for real poles
- read-only workspace evidence panel
- real P_LOCAL_002 validation scripts
- evidence export bundles and survey summaries
- visible summaries that help a designer understand the evidence
- broader Codex / Claude Code tasks where files do not overlap

The goal is to produce things that can be run, inspected, and shown.

## What Bolder Does Not Mean

Do not become reckless.

The following remain hard boundaries:

- Do not change `design_ready` logic until the approved Stage 6E work.
- Do not clear `conductor_spec_missing` from route-level evidence alone.
- Do not claim conductor evidence is span-linked unless the span/FID/pole relationship is proven.
- Do not use GPS proximity alone as a confirmed link.
- Do not commit photos, large zip files, or accidental evidence dumps.
- Do not let two workers edit the same files at the same time.
- Do not delete, rename, or move real evidence files unless the task explicitly requires it.
- Do not use archive folders as source of truth.
- Do not make operational safety claims from ENWL status fields.

## Preferred Delivery Pattern

Use this pattern for future stages:

1. Build a useful vertical slice.
2. Keep it read-only if the evidence model is still developing.
3. Validate against real P_LOCAL_002 data.
4. Add tests.
5. Keep design-readiness mutation out until explicitly approved.
6. Merge only after `pytest -q` and `git diff --check` pass.

## Stage 6 Delivery Guidance

Stage 6 should be treated as a product-forward evidence integration phase.

### Stage 6A — Completed Foundation

Stage 6A established:

- ENWL trace parser/classifier
- evidence relationship categories
- trace inspector CLI
- conservative route/span wording

### Stage 6B — Current Foundation

Stage 6B established:

- three-source evidence combiner prototype
- Pole 05 combined evidence output
- evidence export bundle
- all-poles survey evidence summary
- read-only DNO Evidence workspace display
- Stage 6B combiner spec

Stage 6B evidence may be displayed, classified, combined, exported, and inspected.

Stage 6B must not change design readiness.

### Stage 6C — Linking

Stage 6C should formalise linking rules:

- support number
- pole FID
- SPN
- `fid_polestructure`
- route topology
- GPS proximity as supporting evidence only
- manual confirmation where needed

### Stage 6D — Conflict Detection

Stage 6D should compare field evidence, ENWL records, and trace records.

Examples:

- record says intermediate but field shows terminal/equipment context
- visible transformer/switch not represented as expected
- support number mismatch
- GPS mismatch
- LV and 11kV context mixed incorrectly
- conductor evidence present but not span-linked

### Stage 6E — Readiness Logic

Only Stage 6E should update design-readiness logic.

Before Stage 6E:

- evidence may be displayed
- evidence may be classified
- evidence may be combined
- evidence may be flagged
- evidence must not automatically clear design blockers

## Worker Coordination Rule

Codex and Claude Code can work in parallel when they touch different files.

Recommended split:

- Codex: backend modules, parsers, loaders, CLIs, tests
- Claude Code: control documents, workspace wording, review reports, read-only display

Do not run both workers on the same file unless one is explicitly read-only.

## Control Source of Truth

Active control files are source of truth.

Before starting significant work, workers should read:

- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/121_PLOCAL002_LINKING_FEASIBILITY_SPIKE.md`
- relevant Stage 6 control documents
- `AGENTS.md`

Do not use archive folders as source of truth.

## Evidence Relationship Model

All Stage 6 work should preserve these categories:

1. `direct_pole_identity`
2. `direct_equipment_linked_to_pole`
3. `route_span_evidence`
4. `nearby_context_only`
5. `uncertain`

Use these categories consistently in parsers, CLIs, combined records, workspace display, exports, and reports.

## Product-Forward Rule

When choosing between a tiny infrastructure-only step and a safe vertical slice, prefer the safe vertical slice.

Good:

- “Run this on Pole 05 and show combined evidence.”
- “Open the workspace and see DNO evidence.”
- “Inspect trace file and see relationship counts.”
- “Generate a per-pole evidence summary with provenance.”
- “Export a combined evidence bundle for review.”

Less useful:

- “Create a schema that is not used yet.”
- “Write a loader with no real data.”
- “Document a future process without producing an inspectable result.”

Infrastructure is allowed, but it should quickly lead to visible, testable product behaviour.

## Non-Negotiable Validation

Before merge:

```bash
git diff --check
pytest -q
git status --short
