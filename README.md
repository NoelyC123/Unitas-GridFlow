# GridFlow

**Survey-to-design workflow tool for UK electricity distribution overhead line infrastructure.**

GridFlow sits between field survey output and office design work. It ingests raw DNO baseline data and structured field evidence, matches them pole-by-pole, identifies what engineering specifications are still missing, and produces a clear QA report telling a designer exactly what they need to request from the DNO before design can proceed.

```
DNO Baseline CSV ──► Baseline Ingest ──┐
                                        ├──► Matching ──► Merge ──► QA Report
Field Evidence ──────► Field Import ───┘
```

## Quick Start

### Prerequisites

- Python 3.12+
- Install dependencies:

```bash
pip install -r requirements.txt
```

### Run the Pipeline

```bash
python scripts/run_pipeline.py \
  --baseline path/to/baseline.csv \
  --field path/to/field_evidence/ \
  --output path/to/output/
```

This runs all four stages and produces a timestamped output directory containing:

- `01_baseline_dataset.json` — parsed and validated baseline
- `02_field_dataset.json` — scanned field evidence with quality scores
- `03_match_register.json` + `.csv` — pole-by-pole match results
- `04_merged_dataset.json` + `.csv` — combined evidence per pole
- `05_qa_report.md` — designer QA report with specific DNO action items
- `pipeline_summary.json` — machine-readable run summary

### Run Tests

```bash
pytest tests/ -v
```

### Test with Sample Data

```bash
python scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/enwl_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/gridflow_output/
```

## Pipeline Stages

### Stage 4C.1 — Baseline Ingest (`gridflow/baseline/`)

Parses DNO Network Asset Viewer CSV exports. Supports ENWL, Trimble, and generic formats
with automatic detection. Validates data quality, transforms OSGB36 coordinates to WGS84,
normalizes support numbers, and reconstructs route sequences.

```bash
python scripts/ingest_baseline.py \
  --input baseline.csv --output baseline.json \
  --validate --transform-coords
```

### Stage 4C.2 — Field Evidence Import (`gridflow/field/`)

Scans structured field evidence folders (`NN_SUPPORT_*` pattern), parses observation notes,
counts photos and screenshots, detects special cases (NO_POLE_POPUP, JOINT_USER, variant
support numbers), and scores evidence quality (HIGH/MEDIUM/LOW).

```bash
python scripts/import_field_evidence.py \
  --input evidence_folder/ --output field.json \
  --validate --score
```

### Stage 4C.3 — Matching Engine (`gridflow/matching/`)

Matches baseline poles to field evidence using support number comparison with normalization
(handles prefix stripping, variant suffixes). Scores each match HIGH/MEDIUM/LOW/UNMATCHED.
Detects voltage and equipment conflicts between baseline records and field observations.

```bash
python scripts/run_matching.py \
  --baseline baseline.json --field field.json \
  --output register.json --csv register.csv
```

### Stage 4C.4 — Merge Engine (`gridflow/merge/`)

Combines all three inputs into unified pole records. Applies verification flags (voltage,
conductor, pole class, condition, identity). Identifies design blockers. Generates QA report
with specific action items per pole.

```bash
python scripts/run_merge.py \
  --baseline baseline.json --field field.json --register register.json \
  --output merged.json --report qa_report.md
```

## Validated Results — P_LOCAL_001

Real field pilot validation against 10 ENWL poles in the Sheernest Lane area:

| Metric | Result |
|--------|--------|
| Poles in baseline | 10 |
| Poles surveyed | 10 |
| Match rate | 100% |
| HIGH confidence | 6 |
| MEDIUM confidence | 1 (pole 08, NO_POLE_POPUP) |
| LOW confidence | 3 (VOLTAGE_CONFLICT in notes) |
| Design ready | 0 (DNO specs not yet obtained) |
| Design blocked | 10 (expected — conductor/pole class required from DNO) |

Special cases correctly handled:
- `903201A` — variant support number (A suffix)
- `903503` — joint user pole (telecoms co-attachment)
- `903101` — OH/UG transition pole
- `900346` — HV link pole with no map popup

## Project Status

| Stage | Component | Status |
|-------|-----------|--------|
| Stage 1 | Post-survey QA gate | ✅ Complete |
| Stage 2 | Design-ready handoff / Design Chain | ✅ Complete |
| Stage 4C.1 | Baseline Ingestion Engine | ✅ Complete |
| Stage 4C.2 | Field Evidence Importer | ✅ Complete |
| Stage 4C.3 | Matching Engine | ✅ Complete |
| Stage 4C.4 | Merge Engine | ✅ Complete |
| Pipeline CLI | Unified four-stage pipeline | ✅ Complete |
| Stage 3 | Live intake platform | 🔲 Planned |
| Stage 4 (full) | Structured field capture (tablet) | 🔲 Planned |
| Stage 5 | Designer workspace | 🔲 Planned |
| Stage 6 | DNO submission layer | 🔲 Planned |

## Documentation

| Document | Description |
|----------|-------------|
| `AI_CONTROL/00_PROJECT_CANONICAL.md` | Full 6-stage vision and project identity |
| `AI_CONTROL/01_CURRENT_STATE.md` | What is true right now |
| `AI_CONTROL/02_CURRENT_TASK.md` | Active task record |
| `gridflow/baseline/README.md` | Baseline Ingestion Engine reference |
| `gridflow/merge/README.md` | Merge Engine reference |
| `docs/BASELINE_INGESTION_SPECIFICATION.md` | Technical specification for Stage 4C.1 |

## Test Coverage

```
tests/baseline/    —  49 tests  (CSV parsing, validation, coordinate transform, route reconstruction)
tests/field/       —  47 tests  (folder scanning, notes parsing, quality scoring)
tests/matching/    —  21 tests  (support number matching, confidence scoring, register building)
tests/merge/       —  45 tests  (data merging, verification flags, QA report, conflict detection)
tests/             —  11 tests  (pipeline end-to-end)
─────────────────────────────────────────────────────────────────────────────────────────
Total              — 202 tests
```

Run with coverage:

```bash
pytest tests/ --cov=gridflow --cov-report=html
```

## Limitations

**DNO data still required.** GridFlow identifies what is needed but cannot substitute for
official DNO engineering records. Conductor specifications, pole class, and strength ratings
must be obtained from the network operator before design can proceed. All merged output will
show `design_blocked=true` until DNO data is ingested.

**CLI-only.** No web UI or API in the current release. All interactions are via command-line
scripts.

**10-pole validation.** The pipeline has been validated against a 10-pole ENWL dataset
(P_LOCAL_001). Performance at scale (1,000+ poles) has not been measured in production.

**Coordinate accuracy.** OSGB36 to WGS84 transformation via pyproj achieves ±0.01° accuracy
— sufficient for display and rough geolocation, but not for precise survey-grade work.

**No live DNO connectivity.** GridFlow reads exported CSV files. It does not connect to live
DNO GIS systems.

## Architecture

GridFlow is **validation-led, not feature-led**. Every component is designed to answer:

> *Does this improve the reliability, clarity, and design-readiness of real survey data?*

It does not replace Trimble, PoleCAD, AutoCAD, or engineering designers. It is a pre-design
intelligence layer that sits between field survey output and design input.

---

*Built for UK overhead line infrastructure. Validated against ENWL Network Asset Viewer data.*
