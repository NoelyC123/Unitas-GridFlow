# GridFlow

GridFlow is a survey-to-design reconciliation platform for overhead line infrastructure workflows.

It sits between field survey evidence and design preparation. It ingests baseline asset data, imports structured field evidence, matches the two sources pole by pole, merges the records, and produces QA outputs showing what still requires DNO engineering data before design can proceed.

GridFlow is not an autonomous design tool, a DNO records replacement, a compliance certifier, or a production multi-user SaaS platform.

## What GridFlow Is

GridFlow helps project teams answer practical survey-to-design questions:

- Which baseline poles have field evidence?
- Which field evidence folders match which support numbers?
- How confident is the baseline-to-field identity match?
- Which poles have evidence gaps or conflicts?
- What DNO engineering data is still required before design?
- What should the designer request from the DNO?

The current backend pipeline is complete through Stage 4C.

## Pipeline Diagram

```text
DNO / Survey Baseline CSV
        |
        v
Baseline Ingest
        |
        v
Field Evidence Import  <--- field photos, map screenshots, notes
        |
        v
Baseline-to-Field Matching
        |
        v
Merge + QA
        |
        v
Structured Outputs
```

Operational sequence:

```text
Baseline -> Field -> Matching -> Merge -> QA
```

## Operational Workflow

1. Export or obtain a baseline CSV containing support numbers, coordinates, and asset context.
2. Capture field evidence in structured `NN_SUPPORT_*` folders.
3. Run the unified GridFlow pipeline.
4. Review match confidence and evidence quality.
5. Review merged pole records and verification flags.
6. Use the QA report to prepare a structured DNO data request.
7. Proceed with design only after DNO engineering data and designer review are complete.

## Stage 4C Overview

Stage 4C is complete and operational.

### Stage 4C.1 - Baseline Ingestion

Module:

- `gridflow/baseline/`

CLI:

- `scripts/ingest_baseline.py`

Capabilities:

- CSV parsing.
- ENWL, Trimble, and generic format detection.
- Schema validation.
- OSGB36 <-> WGS84 coordinate transformation.
- Support number normalization.
- Route reconstruction.

### Stage 4C.2 - Field Evidence Import

Module:

- `gridflow/field/`

CLI:

- `scripts/import_field_evidence.py`

Capabilities:

- Scans `NN_SUPPORT_*` evidence folders.
- Parses notes.
- Counts field photos and map screenshots.
- Scores evidence quality.
- Detects special flags such as `NO_POLE_POPUP`, `JOINT_USER`, `VARIANT_SUPPORT_NO`, `OH_UG_TRANSITION`, and `HV_LINK`.

### Stage 4C.3 - Baseline-to-Field Matching

Module:

- `gridflow/matching/`

CLI:

- `scripts/run_matching.py`

Capabilities:

- Normalized support number matching.
- Variant support number handling.
- Match confidence scoring.
- Conflict detection.
- Match register generation.

### Stage 4C.4 - Merge + QA

Module:

- `gridflow/merge/`

CLI:

- `scripts/run_merge.py`

Capabilities:

- Merged pole records.
- Verification flags.
- DNO action reporting.
- Design blocker analysis.
- QA report generation.

### Unified Pipeline CLI

CLI:

- `scripts/run_pipeline.py`

The unified pipeline runs baseline ingest, field import, matching, merge, and QA in one command.

It produces timestamped structured outputs, including baseline dataset, field dataset, match register, merged dataset, QA report, and machine-readable summary.

## Quick Start

### Prerequisites

- Python 3.12+.
- Project dependencies installed.

```bash
pip install -r requirements.txt
```

### Run the Unified Pipeline

```bash
python scripts/run_pipeline.py \
  --baseline path/to/baseline.csv \
  --field path/to/enwl_enrichment_clean \
  --output path/to/output
```

Expected output package:

- `01_baseline_dataset.json`
- `02_field_dataset.json`
- `03_match_register.json`
- `03_match_register.csv`
- `04_merged_dataset.json`
- `04_merged_dataset.csv`
- `05_qa_report.md`
- `pipeline_summary.json`

### Run Individual Stages

```bash
python scripts/ingest_baseline.py \
  --input baseline.csv \
  --output baseline.json \
  --validate \
  --transform-coords
```

```bash
python scripts/import_field_evidence.py \
  --input evidence_folder \
  --output field.json \
  --validate \
  --score
```

```bash
python scripts/run_matching.py \
  --baseline baseline.json \
  --field field.json \
  --output match_register.json \
  --csv match_register.csv
```

```bash
python scripts/run_merge.py \
  --baseline baseline.json \
  --field field.json \
  --register match_register.json \
  --output merged_dataset.json \
  --report qa_report.md \
  --csv merged_dataset.csv
```

### Run Tests

```bash
pytest -v
```

Current verified test result:

```text
1,277 tests passing
```

## P_LOCAL_001 Validation Results

Validated dataset:

- `real_pilot_data/P_LOCAL_001/enwl_enrichment_clean`

Current verified outcomes:

| Metric | Result |
| --- | --- |
| Poles matched | 10/10 |
| Match rate | 100% |
| HIGH evidence quality | 9 |
| MEDIUM evidence quality | 1 |
| Design blocked | 10/10 |
| Unified pipeline | Operational |
| QA reports | Generated successfully |
| Tests | 1,277 passing |

The `design_blocked=True` result for all 10 poles is correct. It means GridFlow has reconciled baseline and field evidence, but DNO engineering data is still required before final design.

GridFlow does not certify:

- voltage,
- conductor size or type,
- pole class,
- equipment rating,
- inspection history,
- design approval.

## Current Architecture

```text
gridflow/
  baseline/
  field/
  matching/
  merge/

scripts/
  ingest_baseline.py
  import_field_evidence.py
  run_matching.py
  run_merge.py
  run_pipeline.py
```

## Limitations

GridFlow currently has these limitations:

- No designer review UI yet.
- ENWL-focused validation to date.
- No PoleCAD export yet.
- No production multi-user workflow yet.
- No live DNO API integration.
- No production deployment layer.
- No autonomous engineering design.

P_LOCAL_001 proves the Stage 4C backend pipeline on a controlled ENWL evidence set. Larger jobs, other DNO formats, and production contractor workflows still require pilot validation.

## Current Roadmap

### Complete

- Stage 4C.1 Baseline Ingestion.
- Stage 4C.2 Field Evidence Import.
- Stage 4C.3 Baseline-to-Field Matching.
- Stage 4C.4 Merge + QA.
- Unified Pipeline CLI.

### Current Next Phase

- Stage 5 - Pilot Hardening & Operational Review Workflow.

### Planned Stage 5 Focus

- Review workspace UI.
- Evidence/photo viewer.
- Merged record explorer.
- Blocker/action dashboard.
- DNO request export packaging.
- Multi-job validation.
- ICP/Tier-1 pilot preparation.

## Stage 5 Preview

Stage 5 will not replace the completed backend pipeline. It will make the pipeline usable in real pilot workflows.

Planned outcomes:

- Designers can review merged pole records without reading raw JSON.
- Evidence can be navigated alongside baseline and match data.
- DNO data request packs can be generated from verification flags.
- Review states can be tracked across poles and jobs.
- Pilot teams can evaluate GridFlow on real survey-to-design handoffs.

## Documentation

Useful project references:

- `AI_CONTROL/01_CURRENT_STATE.md`
- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/108_STAGE4C_COMPLETION_REPORT.md`
- `AI_CONTROL/109_STAGE5_PILOT_HARDENING_SPEC.md`
- `PRODUCT_SPEC.md`
- `GRIDFLOW_DOMAIN_REFERENCE.md`
- `docs/SURVEYOR_GUIDE.md`
- `docs/DESIGNER_GUIDE.md`
- `docs/DNO_DATA_REQUEST_TEMPLATE.md`
- `docs/ICP_PILOT_BRIEFING.md`

## Governance Position

GridFlow is validation-led and evidence-based.

It is designed to improve the reliability, clarity, and traceability of survey-to-design handoff. It does not replace DNO records, designer judgement, statutory requirements, or engineering approval.
