# Stage 6B — Three-source Evidence Combiner Prototype

## Purpose

Stage 6B proves that GridFlow can combine field evidence, ENWL pole/equipment evidence, and ENWL trace evidence into a single inspectable per-pole evidence record.

This is a product-forward evidence integration stage. It is allowed to produce visible, useful outputs, including CLI summaries and read-only workspace evidence panels.

Stage 6B must remain evidence/provenance only. It must not change design readiness.

## Product Goal

For a real P_LOCAL_002 pole, especially Pole 05 / Support 900344, GridFlow should be able to show:

- field/notes identity evidence
- ENWL pole identity evidence
- direct equipment evidence where proven by `fid_polestructure`
- route-level conductor evidence from ENWL trace or notes
- nearby network context
- provenance / contributing files
- uncertainty notes
- design-readiness caution

A reviewer should be able to run one command or open the workspace and understand what GridFlow knows, what is proven, and what remains route-level only.

## Target Poles

Initial Stage 6B validation should focus on the strongest P_LOCAL_002 examples:

| Pole | Support | Reason |
|---|---:|---|
| 03 | 900343 | Direct FSL/switch evidence via `fid_polestructure` |
| 05 | 900344 | Direct ABS / Fault Making Switch evidence via `fid_polestructure` |
| 06 | 900345 | Transformer / HV link / LV way context with direct pole-structure evidence where available |

Other P_LOCAL_002 poles may be shown with Level 1 identity and route-level evidence, but the strongest proof cases are Poles 03, 05, and 06.

## Relationship Model

Stage 6B must preserve the Stage 6A relationship categories:

1. `direct_pole_identity`
2. `direct_equipment_linked_to_pole`
3. `route_span_evidence`
4. `nearby_context_only`
5. `uncertain`

These categories must be visible or preserved in CLI output, combined records, and workspace display.

## Evidence Combiner Inputs

The combiner may use:

- pole folder path
- `notes/pole_notes.md`
- ENWL trace GeoJSON files
- Stage 6A parser output
- explicit FIDs and SPNs written in pole notes
- optional future `enwl_record.json` files

The combiner should not depend on OCR or image parsing.

## Evidence Combiner Output

The combined evidence record should contain:

- `pole_id`
- `support_no`
- `pole_fid`
- `spn`
- `pole_type`
- `pole_class`
- `support_diameter`
- coordinates where present
- `direct_equipment_records`
- `route_conductor_evidence`
- `nearby_context`
- `evidence_quality_summary`
- `design_readiness_caution`
- `contributing_files`
- `uncertainties`

## Hard Rules

Stage 6B must not:

- change `design_ready`
- clear `conductor_spec_missing`
- claim conductor evidence is span-linked unless the span/FID/pole relationship is proven
- use GPS proximity alone as a confirmed direct link
- alter report generation
- alter merge/matching pipeline behaviour
- delete, move, rename, or edit evidence images
- make operational safety claims from ENWL switch status fields

## Direct Equipment Rule

A record may be treated as direct equipment evidence only when:

- the equipment record has `fid_polestructure` matching the pole FID, or
- the pole notes explicitly identify the equipment FID as attached to that pole and the record is classified as equipment, not conductor

Examples:

- Pole 05 ABS / Fault Making Switch FID `73189925` with `fid_polestructure = 16869657`
- Pole 03 FSL/switch evidence with `fid_polestructure = 16869661`
- Pole 06 transformer/HV link evidence where `fid_polestructure = 53427080`

## Route Conductor Rule

Conductor records remain Level 3 route/span evidence unless Stage 6C proves a specific pole/span relationship.

Route conductor evidence may be displayed, but must be labelled clearly:

`ROUTE/SPAN EVIDENCE ONLY — not per-pole design-ready proof`

It must not clear design-readiness blockers.

## Nearby Context Rule

Sleeves, joints, terminations, services, underground transitions, and nearby plant context default to Level 4 unless explicit direct linkage exists.

They may be displayed as nearby context, but not treated as proven attachments.

## CLI Acceptance Criteria

The combiner CLI should support a command like:

```bash
python3 scripts/combine_pole_evidence.py \
  --survey real_pilot_data/P_LOCAL_002 \
  --pole 05_SUPPORT_900344 \
  --trace real_pilot_data/P_LOCAL_002/enwl_trace/enwl_trace_10924865_with_ratings.geojson
