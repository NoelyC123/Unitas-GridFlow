# GridFlow Developer Onboarding Guide

**Date:** 2026-05-17
**Codebase state:** Commit 8afeee0 — 4 critical bugs fixed, 1464 tests passing

GridFlow is a survey-to-design validation platform for UK overhead line networks. It sits
between field survey evidence and office design work. This guide covers everything needed
to contribute.

---

## Quick Start (Under 10 Minutes)

### 1. Clone and set up

```bash
git clone https://github.com/NoelyC123/Unitas-GridFlow.git
cd Unitas-GridFlow

python3 -m venv .venv312
source .venv312/bin/activate          # macOS/Linux
# .venv312\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 2. Verify tests pass

```bash
pytest -q
# Expected: 1464 passed, 9 skipped
```

### 3. Run the pipeline against the validation job

```bash
python scripts/run_pipeline.py \
  --baseline real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv \
  --field    real_pilot_data/P_LOCAL_002/enwl_enrichment_clean \
  --output   /tmp/gridflow_test_run

# Expected:
#   Stage 1: 12 poles loaded
#   Stage 2: 12 notes detected, 12 HIGH quality
#   Stage 3: 12/12 matched (100%)
#   Stage 4: 12 poles merged, design blocked (correct)
#   Overall: PARTIAL
```

If those numbers match, the environment is correct.

---

## Project Structure

```
Unitas-GridFlow/
│
├── gridflow/                       ← Stage 4C+ pipeline (core library)
│   ├── baseline/
│   │   ├── csv_parser.py           ← Parse DNO baseline CSVs (ENWL/Trimble/Generic)
│   │   ├── models.py               ← BaselinePole, BaselineDataset (Pydantic)
│   │   ├── coordinate_transformer.py  ← OSGB36/ITM/TM65 → WGS84
│   │   ├── schema_validator.py
│   │   ├── support_number_normalizer.py
│   │   └── route_reconstructor.py
│   ├── field/
│   │   ├── folder_scanner.py       ← Scan NN_SUPPORT_* evidence folders
│   │   ├── models.py               ← FieldPole, FieldDataset (Pydantic)
│   │   ├── notes_parser.py         ← Extract fields from pole_notes.md
│   │   └── evidence_quality_scorer.py
│   ├── matching/
│   │   ├── support_number_matcher.py  ← Match baseline ↔ field by support number
│   │   ├── confidence_scorer.py
│   │   ├── register_builder.py
│   │   └── models.py               ← MatchResult, MatchRegister
│   ├── merge/
│   │   ├── data_merger.py          ← Produce MergedPole per matched pair
│   │   ├── models.py               ← MergedPole, MergedDataset (Pydantic)
│   │   ├── verification_flag_generator.py
│   │   ├── conflict_detector.py
│   │   └── qa_report_generator.py
│   ├── reports/                    ← 10 standard report generators
│   ├── readiness/
│   │   └── assessor.py             ← Stage 6E design-readiness assessment
│   ├── enwl_trace/
│   │   └── parser.py               ← Stage 6A ENWL trace GeoJSON parser
│   ├── evidence_combiner/
│   │   ├── combiner.py             ← Stage 6B three-source evidence combiner
│   │   └── linker.py               ← Stage 6C formal pole-to-ENWL linking
│   ├── conflict_detector/
│   │   └── detector.py             ← Stage 6D conflict detection
│   └── workspace/
│       ├── review_data_provider.py ← Feed merged data to workspace routes
│       ├── enwl_evidence_adapter.py ← Stage 6B workspace evidence display
│       └── readiness_adapter.py    ← Stage 6E workspace readiness display
│
├── app/                            ← Stage 1/2 QA pipeline (Trimble GNSS)
│   ├── qa_engine.py                ← 1250-line QA engine using pandas
│   ├── routes/                     ← Flask blueprints (17 files)
│   └── templates/                  ← Jinja2 HTML templates
│
├── scripts/
│   ├── run_pipeline.py             ← Main pipeline CLI
│   ├── validate_phase4_matching.py ← Lightweight structural gate
│   ├── link_survey_poles.py        ← Stage 6C CLI
│   ├── assess_readiness.py         ← Stage 6E CLI
│   ├── detect_conflicts.py         ← Stage 6D CLI
│   └── combine_pole_evidence.py    ← Stage 6B CLI
│
├── tests/                          ← 1464 tests
│   ├── baseline/
│   ├── field/
│   ├── matching/
│   ├── merge/
│   ├── workspace/
│   ├── test_pipeline.py            ← Integration tests
│   └── test_enwl_trace_parser.py
│
├── real_pilot_data/                ← Gitignored survey data (local only)
│   └── P_LOCAL_002/                ← 12-pole ENWL validation job
│       ├── csv/P_LOCAL_002_baseline.csv
│       ├── enwl_enrichment_clean/  ← 12 pole evidence folders
│       └── route_notes/            ← Audit and review reports
│
└── AI_CONTROL/                     ← Project governance and docs (30+ files)
    ├── 00_PROJECT_CANONICAL.md     ← What the project is
    ├── 01_CURRENT_STATE.md         ← Authoritative current state
    ├── 02_CURRENT_TASK.md          ← Active task
    ├── 45_GRIDFLOW_PRODUCTION_ARCHITECTURE.md
    ├── 46_GRIDFLOW_API_REFERENCE.md
    └── ...
```

**Important:** `app/` (Stage 1/2) and `gridflow/` (Stage 4C+) are separate pipeline
tracks. `app/qa_engine.py` processes Trimble GNSS controller dumps. `gridflow/` processes
DNO baseline CSVs + organised field evidence. They share the web layer but have different
data models and entry points.

---

## Key Concepts

### Two Pipeline Tracks

**Track 1 — Stage 1/2 (Trimble GNSS → QA report):**
- Entry: file upload via web UI or `app/routes/api_intake.py`
- Engine: `app/qa_engine.py` (pandas-based, 1250 lines)
- Input: Trimble GNSS controller dump CSV
- Output: Issues list, design-readiness flags, PDF report

**Track 2 — Stage 4C+ (Baseline CSV + field evidence → merged dataset):**
- Entry: `scripts/run_pipeline.py`
- Engine: `gridflow/` modules
- Input: DNO baseline CSV + organised evidence folders
- Output: Merged dataset, 10 report files, workspace-ready job

### Evidence Folder Structure

Every field evidence folder follows:
```
NN_SUPPORT_{support_no}[_DESCRIPTOR]/
  field_photos/       ← JPEG/PNG field survey photos
  enwl_screenshots/   ← ENWL Network Asset Viewer screenshots
  map_screenshots/    ← Map screenshots with GPS pin
  notes/
    pole_notes.md     ← Structured markdown notes (or .txt)
```

The `support_no` is extracted from the folder name (`parts[2]` of `_`-split).

### Design-Readiness Is a Four-Level Concept

| Level | Meaning | `design_ready` |
|---|---|---|
| `ready` | All evidence confirmed, conductor span-linked | `True` |
| `review_required` | Evidence present, conductor route-level only | `False` |
| `not_ready` | Missing pole class, photos, or conductor evidence | `False` |
| `insufficient_evidence` | Identity unclear or linking failed | `False` |

`design_ready = True` only when conductor specification is confirmed per span. All
P_LOCAL_002 poles are `not_ready` or `review_required` — correct, not a failure.

### The `support_no` / `pole_id` Distinction

DNO baseline CSVs use different column names:
- ENWL: `ENID` (becomes `pole_id`) + `Support No` (becomes `support_no`)
- P_LOCAL_002 generic: `pole_id` column only (used as both `pole_id` and `support_no` fallback)

The `_normalize()` function strips prefixes (`SP`, `EN`) and uppercases to create a
consistent matching key.

---

## Development Workflow

### Standard flow

```bash
git checkout -b claude-code/your-feature   # or codex/ or cursor/ depending on tool
# Make changes
pytest -q                    # must pass before commit
pre-commit run --all-files   # ruff lint, whitespace, yaml checks
git commit -m "Clear description"
```

### Run specific tests

```bash
pytest tests/baseline/test_csv_parser.py -v
pytest tests/matching/test_support_number_matcher.py::test_match_with_pole_id_fallback -v
pytest tests/test_pipeline.py -v -s    # -s shows print output
```

### Run the structural gate (fast, no model stack)

```bash
python scripts/validate_phase4_matching.py \
  --baseline-csv real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv \
  --field-evidence-dir real_pilot_data/P_LOCAL_002/enwl_enrichment_clean
# Expected: 12/12, 100.00%
```

### Debug a pipeline run

```bash
python scripts/run_pipeline.py \
  --baseline real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv \
  --field    real_pilot_data/P_LOCAL_002/enwl_enrichment_clean \
  --output   /tmp/debug_run \
  --log-level DEBUG 2>&1 | tee /tmp/debug.log
```

---

## Common Tasks

### Add support for a new DNO baseline format

1. Add format detection in `gridflow/baseline/csv_parser.py`:

```python
def detect_format(self, csv_path: Path) -> str:
    # ...existing ENWL, TRIMBLE checks...
    if "NEW_DNO_COL_A" in columns and "NEW_DNO_COL_B" in columns:
        return "NEW_DNO"
    return "GENERIC"
```

2. Add a `_parse_new_dno(self, df, csv_path) -> BaselineDataset` method following the
   pattern of `_parse_enwl`. Critical: always set `support_no = support_col_value or pole_id`
   so the `pole_id` fallback is preserved.

3. Add tests in `tests/baseline/test_csv_parser.py`.

### Add a new conflict detection rule

1. Add a detection method in `gridflow/conflict_detector/detector.py`
2. Add it to the main `detect_pole()` call sequence
3. Add tests in `tests/test_conflict_detector.py`

Use `ConflictResult(severity="CRITICAL"|"WARNING"|"INFO", description="...")`.

### Add a new verification flag

1. Add the field to `gridflow/merge/models.py`:`MergedPole`
2. Set it in `gridflow/merge/verification_flag_generator.py`
3. Display it in `app/templates/workspace/pole_detail.html` Verification Flags card
4. Add tests

### Start the web workspace

```bash
export FLASK_APP=run.py
flask run
# Then: http://127.0.0.1:5000/workspace/view/<job_id>
```

Register a job first with `--register --job-id <name>` in `run_pipeline.py`.

---

## Code Patterns

### Pydantic models throughout `gridflow/`

```python
from pydantic import BaseModel, Field
from typing import Optional

class MyModel(BaseModel):
    required_field: str
    optional_field: Optional[str] = None
    list_field: list[str] = Field(default_factory=list)
```

### Conservative error handling in parsers

All parsers catch per-row exceptions and log warnings rather than raising. A row error
never kills the whole parse. Return a partial result with an error log instead.

### Never modify `design_ready` in `gridflow/` outside `gridflow/readiness/assessor.py`

The merger sets `design_ready = False` by default. Only the assessor may set it `True`,
and only when all readiness conditions in `assess_from_records()` are met. No other
module should touch this field.

### `coordinate_status` lives in `metadata`

Blank-coordinate poles are included in `BaselineDataset` with `easting=None`,
`northing=None`, and `metadata["coordinate_status"] = "MISSING"`. Do not add a
top-level `coordinate_status` field to `BaselinePole` without a migration plan.

---

## AI_CONTROL Layer

The `AI_CONTROL/` directory contains the project's governance layer. Key files to read:

| File | Read when |
|---|---|
| `00_PROJECT_CANONICAL.md` | Starting any work — project identity |
| `01_CURRENT_STATE.md` | Understanding the active state |
| `02_CURRENT_TASK.md` | Starting a session |
| `45_GRIDFLOW_PRODUCTION_ARCHITECTURE.md` | Architecture questions |
| `46_GRIDFLOW_API_REFERENCE.md` | API/signature questions |
| `39_STAGE4C_SILENT_FAILURES.md` | Understanding what was fixed and what remains |
| `42_MATCHING_ENGINE_ANALYSIS.md` | Root cause for the 0/10 matching bug (historical) |

Documents prefixed with numbers in the 80s–100s are Stage 4 planning documents. Documents
in the 120s–130s are Stage 6 ENWL evidence integration documents.

---

## What Stays Local-Only

`real_pilot_data/` is gitignored. Never commit survey photos, screenshots, or CSVs.
Control documents in `AI_CONTROL/` that reference `real_pilot_data/` paths are tracked;
the data itself is not.

`validation_runs/` and `uploads/` are also gitignored.
