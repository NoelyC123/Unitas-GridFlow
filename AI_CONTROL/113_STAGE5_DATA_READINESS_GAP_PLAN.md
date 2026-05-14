# Stage 5 Data Readiness Gap Plan

**Date:** 2026-05-14
**Branch:** `claude-code/stage5-data-readiness-plan`
**Source:** Derived from `AI_CONTROL/111_STAGE5_VALIDATION_DISCOVERY.md` and direct code inspection. All findings based on actual local files — nothing invented.

---

## 1. Executive Summary

`P_LOCAL_001` is currently the only candidate that can run end-to-end through `scripts/run_pipeline.py` without any data preparation work. This is because it is the only candidate with both a compatible baseline source *and* a structured field evidence folder containing `NN_SUPPORT_*` subfolders — the exact format the `FolderScanner` requires.

All other candidates are blocked by one or both of:
- A missing or incompatible field evidence folder (most common gap).
- No same-site baseline CSV in a supported format.

This plan documents the exact required pipeline input structure, what each candidate actually has locally, what is missing, and the smallest set of actions that would unblock additional validation candidates.

The single-job validation risk is real but not critical at this stage. P_LOCAL_001 proves the pipeline is functionally correct. The next validation priority is adding at least one second candidate using real site data, not synthetic fixtures, to build confidence before any Stage 6 planning.

---

## 2. Required Pipeline Input Structure

Confirmed by inspecting `scripts/run_pipeline.py` and `gridflow/field/folder_scanner.py`. Not assumed.

### 2.1 CLI Arguments

```bash
python scripts/run_pipeline.py \
  --baseline <path-to-baseline.csv> \
  --field    <path-to-field-evidence-root/> \
  --output   <path-to-output-directory/>
  [--baseline-format AUTO|ENWL|TRIMBLE|GENERIC]
  [--report]
```

`--baseline-format` defaults to `AUTO`. The parser supports ENWL export format, Trimble GNSS controller dump format, and a generic fallback.

### 2.2 Baseline CSV

A flat CSV file with one row per pole. Exact required fields depend on the detected format. The ENWL and TRIMBLE parsers accept the native export layouts; the GENERIC parser attempts best-effort extraction. A support/asset number column is required for matching.

### 2.3 Field Evidence Root Folder — Exact Structure

The `FolderScanner` scans the root folder and accepts **only** subdirectories whose names match this pattern:

```
NN_SUPPORT_<support_number>[_<voltage>][_<descriptor>]
```

Where:
- `NN` = two-digit integer sequence number (e.g. `01`, `09`)
- `SUPPORT` = literal string (case-insensitive comparison in `_is_pole_folder`)
- `<support_number>` = pole/asset number containing at least one digit (e.g. `903203`, `900346A`)
- `_<voltage>` = optional voltage tag (`LV`, `HV`, `EHV`)
- `_<descriptor>` = optional free-text suffix (e.g. `TERMINAL_STREETLIGHT`)

Folders starting with `.` or `_DUPLICATE_` are skipped silently.
**Any folder that does not match this pattern is skipped with a warning.** This means flat photo folders (`photos_final/`, `field_photos/`) produce zero poles even if photos are present.

Within each `NN_SUPPORT_*` folder, the scanner looks for:

```
field_evidence_root/
└── 01_SUPPORT_903203_LV_TERMINAL/        ← NN_SUPPORT_* required
    ├── field_photos/                      ← optional; .jpeg/.jpg/.heic counted
    │   └── IMG_001.jpeg
    ├── map_screenshots/                   ← optional; .png/.jpg/.jpeg counted
    │   └── screenshot_001.png
    └── notes/                             ← optional; first .txt file parsed
        └── notes.txt
```

**Minimum viable SUPPORT folder:** an empty `NN_SUPPORT_<number>/` directory is accepted and produces a `LOW` evidence quality pole with zero photos/screenshots and no notes.

### 2.4 Pipeline Output Structure

The pipeline writes all outputs into a timestamped subfolder:

```
<--output argument>/
└── pipeline_run_<YYYYMMDD_HHMMSS>/
    ├── 01_baseline_dataset.json
    ├── 02_field_dataset.json
    ├── 03_match_register.json
    ├── 03_match_register.csv
    ├── 04_merged_dataset.json
    ├── 04_merged_dataset.csv
    ├── 05_qa_report.md
    ├── 00_pilot_output_pack_index.md
    ├── 06_dno_data_request.md
    ├── 07_design_readiness_summary.md
    ├── 08_match_confidence_analysis.md
    ├── 09_verification_flags_breakdown.md
    ├── 10_evidence_provenance_log.md
    └── pipeline_summary.json
```

The workspace routes and map overlay route read from `uploads/jobs/<job_id>/`. These paths are independent — see Section 5.

---

## 3. Per-Candidate Gap Analysis

### 3.1 Summary Table

| Candidate | Baseline CSV | Field Root Folder | `NN_SUPPORT_*` subfolders | Runnable now | Effort to fix |
|---|---|---|---|---|---|
| P_LOCAL_001 | ✅ fixture | ✅ `enwl_enrichment_clean` | ✅ 10 folders | ✅ | — |
| P_LOCAL_001 (Trimble fixture) | ✅ fixture | ✅ `enwl_enrichment_clean` | ✅ 10 folders | ✅ (caveat) | — |
| P_LOCAL_001 (original evidence) | ✅ fixture | ✅ `enwl_enrichment` | ✅ 10 folders | ✅ (lower quality) | — |
| P_CONTROLLED_001 | ✅ `baseline/baseline.csv` | ❌ `photos_final/` (flat) | ❌ 0 | ❌ | HIGH |
| P_CONTROLLED_LOCAL_001 | ✅ ENWL trace export | ❌ `field_photos/` (flat) | ❌ 0 | ❌ | HIGH |
| Bellsprings (P_BASELINE_SURVEY_PACK) | ✅ `bellsprings_stage4_starter.csv` | ❌ none | ❌ 0 | ❌ | HIGH |
| Gordon (P_BASELINE_SURVEY_PACK) | ✅ multiple starter CSVs | ❌ none | ❌ 0 | ❌ | HIGH |
| P_REAL_001 | ❌ no compatible baseline | ❌ no SUPPORT_* structure | ❌ 0 | ❌ | HIGH |
| P_REAL_001_MINI | ❌ no compatible baseline | ❌ `photos_final/` (flat) | ❌ 0 | ❌ | HIGH |
| P010 (`uploads/projects/P010`) | ✅ `Gordon_Pt1_-_Original.csv` | ❌ none | ❌ 0 | ❌ | HIGH |
| P011 (`uploads/projects/P011`) | ✅ `messy_test.csv` | ❌ none | ❌ 0 | ❌ | HIGH |

**Note on Trimble fixture caveat:** One Trimble fixture row has a blank `Point Name`, producing one unmatched pole. Reports and workspace still generate; this is a fixture deficiency, not a pipeline failure.

### 3.2 Candidate Detail

**P_LOCAL_001** — Fully runnable. Primary validation candidate. Uses `tests/baseline/fixtures/enwl_sample.csv` as baseline because no real ENWL baseline CSV for this specific site is available locally. The field evidence folder `enwl_enrichment_clean` contains 10 `NN_SUPPORT_*` subfolders with photos, screenshots, and notes. This is the only candidate where both halves exist and are structurally compatible with the pipeline.

**P_CONTROLLED_001** — Has `real_pilot_data/P_CONTROLLED_001/baseline/baseline.csv` and `csv/stage4_controlled_capture_completed.csv`. Has `photos_final/` folder but it is a flat photo dump — no `NN_SUPPORT_*` subfolders found. The capture CSV is a Stage 4-style controller output rather than a Stage 4C structured evidence folder. To run this through the pipeline, the photos and any notes would need to be reorganised into `NN_SUPPORT_<number>/field_photos/`, `notes/` subfolders for each pole. This is a significant manual data preparation task given the number of poles involved. Effort: HIGH.

**P_CONTROLLED_LOCAL_001** — Has `real_pilot_data/P_CONTROLLED_LOCAL_001/baseline_exports/trace_001_sheernest_bridge_lv_transformer.csv` (ENWL trace export). Has `field_photos/` and `screenshots/` folders, but both are flat — no `NN_SUPPORT_*` subfolders. Same gap as P_CONTROLLED_001: the field data exists in an earlier (pre-Stage 4C) format. Restructuring into `NN_SUPPORT_*` form is required before the pipeline can ingest it. Effort: HIGH.

**Bellsprings (P_BASELINE_SURVEY_PACK)** — Has `real_pilot_data/P_BASELINE_SURVEY_PACK/csv/bellsprings_stage4_starter.csv` and the raw `Bellsprings - CSV File.csv`. Has accompanying DNO documents (PDFs: route map, pole schedule, profile, TIS). No field evidence folder of any kind was found. Bellsprings needs a structured `NN_SUPPORT_*` field evidence folder to be created from scratch — ideally from a real field evidence capture session on that site. Effort: HIGH (no field data exists).

**Gordon (P_BASELINE_SURVEY_PACK)** — Has multiple CSVs: `gordon_original_stage4_starter.csv`, `gordon_pr1_stage4_starter.csv`, `gordon_pr2_stage4_starter.csv`, and the raw `gordon_original.csv`. The PR1 CSV has a known duplicate point identity issue noted in the discovery discovery. A Gordon `_Original.csv` also exists in `uploads/projects/P010` under `uploads/jobs/J16535`, `J17251`, `J20932`, `J23769`, `J43309`, `J44360`, `J44727`, `J58417`, `J60152`, `J65371`, `J75086`, `J76076`, `J78297`, `J85182`, `J85925`, `J94106` (all Stage 1 QA jobs). No field evidence folder for Gordon was found anywhere locally. Effort: HIGH (no field data exists).

**P_REAL_001 and P_REAL_001_MINI** — Both have field-capture CSVs and a flat `photos_final/` folder. Neither has a compatible Stage 4C baseline or a `NN_SUPPORT_*` evidence folder. The photos and any capture data would need to be reorganised before the pipeline can run. No same-site baseline for matching was found. Effort: HIGH (missing both halves in compatible form).

**P010 (`uploads/projects/P010`)** and **P011 (`uploads/projects/P011`)** — Exist as uploaded Stage 1/2/3 QA jobs under `uploads/projects`. P010 has `Gordon_Pt1_-_Original.csv` and P011 has `messy_test.csv`. Neither has any field evidence structure. These are single-CSV QA jobs — the Stage 1 map viewer pipeline applies, not the Stage 4C reconciliation pipeline. To run them through `scripts/run_pipeline.py` they would each need a compatible `NN_SUPPORT_*` evidence folder, which does not exist. Effort: HIGH.

---

## 4. Standard Validation Pack Template

Future validation jobs should be structured as follows before running through `scripts/run_pipeline.py`:

```
<job_name>/
├── baseline.csv                         ← required, ENWL/TRIMBLE/GENERIC format
└── field_evidence/                      ← required, root folder for FolderScanner
    ├── 01_SUPPORT_<number>_<voltage>/   ← one subfolder per pole
    │   ├── field_photos/                ← optional but recommended
    │   │   └── IMG_001.jpeg
    │   ├── map_screenshots/             ← optional, drives evidence quality score
    │   │   └── screenshot.png
    │   └── notes/                       ← optional, parsed for structured data
    │       └── notes.txt
    ├── 02_SUPPORT_<number>_<voltage>/
    │   └── ...
    └── ...
```

Rules:
- Subfolder sequence numbers (`01`, `02`…) must be two digits.
- `SUPPORT` must appear as the second `_`-delimited token.
- Support number must contain at least one digit.
- Voltage tag (`LV`, `HV`, `EHV`) is optional but aids evidence quality scoring.
- Photos must be `.jpeg`, `.jpg`, or `.heic`.
- Screenshots must be `.png`, `.jpg`, or `.jpeg`.
- Notes must be `.txt` files inside a `notes/` subfolder.

For validation packs prepared from real sites:
- Match support numbers in the folder name exactly to the baseline CSV's asset/support number column.
- Differences in capitalisation, leading zeros, or spacing between baseline and folder name will result in unmatched poles.

---

## 5. Workspace and Map Route Gap

### 5.1 The gap

The pipeline (`scripts/run_pipeline.py`) writes all outputs to a caller-specified path:

```
<--output argument>/pipeline_run_<YYYYMMDD_HHMMSS>/
```

The workspace routes read from a fixed path:

```
uploads/jobs/<job_id>/
```

The map overlay route (`/map/overlay/<job_id>`) reads the same `uploads/jobs/<job_id>/` path for `01_baseline_dataset.json`, `02_field_dataset.json`, `03_match_register.json`, and `04_merged_dataset.json`.

There is no automatic registration step. After a pipeline run, the output folder at `<--output>/pipeline_run_<run_id>/` is not accessible via either the workspace or map overlay routes until the files are copied or linked into `uploads/jobs/<job_id>/`.

### 5.2 Current workaround (P_LOCAL_001 validation practice)

Copy the pipeline output into `uploads/jobs/<job_id>/`:

```bash
job_id="P_LOCAL_001_enwl_clean"
cp -r /tmp/gridflow_validation/P_LOCAL_001_enwl_clean/pipeline_run_<run_id>/ \
       uploads/jobs/${job_id}/
```

Then access:
- `/workspace/view/P_LOCAL_001_enwl_clean`
- `/workspace/pole/P_LOCAL_001_enwl_clean/<support_number>`
- `/map/overlay/P_LOCAL_001_enwl_clean`

### 5.3 Simplest permanent resolution

Add a `--register` flag (or default behaviour) to `scripts/run_pipeline.py` that copies or symlinks the `pipeline_run_*` output folder into `uploads/jobs/<job_id>/` automatically, where `job_id` is the run ID. This is a one-line path copy and removes the manual step entirely.

This is a small, well-scoped pipeline enhancement, not a new feature. It does not affect any existing route or test.

---

## 6. Risks of Proceeding with Limited Validation Data

**Risk 1 — Overclaiming from single-job validation.**
All current Stage 5 validation evidence comes from one job (P_LOCAL_001) using synthetic fixture baselines (`enwl_sample.csv`), not the real ENWL baseline for that site. Pipeline results are internally consistent but the real-world matching behaviour on a genuine DNO baseline/field evidence pair has not yet been exercised. Reports and workspace should not be described as production-validated until at least one real baseline-to-real-field-evidence run is complete.

**Risk 2 — Mismatched baseline and field data.**
P_LOCAL_001 uses a fixture baseline whose support numbers were built to match the evidence folder names. In a real job, support number formats between the DNO baseline and the field capture may differ (leading zeros, capitalisation, dash vs underscore). The matching pipeline handles some normalisation but the real-world failure modes have not been stress-tested.

**Risk 3 — Old Stage 4 CSVs treated as Stage 4C evidence.**
Several candidate jobs (`P_CONTROLLED_001`, `P_REAL_001`, Gordon/Bellsprings starters) have Stage 4-style capture CSVs. These are *not* compatible with the Stage 4C `FolderScanner` — they require a different ingestion path (or restructuring). Attempting to pass them as `--field` input would produce a `FieldDataset` with zero poles, which would then generate reports showing 0 matches and 0 merged poles. This could be misread as a pipeline failure when it is actually a data structure mismatch.

**Risk 4 — Design-blocked result misread as pipeline failure.**
The expected output for P_LOCAL_001 is `design_blocked=True` for all poles because the fixture baseline contains no engineering data (voltage, conductor, pole class). This is correct and expected. On a real job with a genuine DNO baseline, some poles should become `design_ready=True`. If the first real-job run also returns all-blocked, this could indicate a baseline schema gap or mapping issue rather than a field evidence problem — and would need to be investigated before reporting.

**Mitigations:**
- Run at least one real baseline CSV against a same-site field evidence folder before any Stage 6 planning.
- Document support number normalisation behaviour explicitly in `111_STAGE5_VALIDATION_FINDINGS.md`.
- Add a clear warning in pipeline output when `FieldDataset.total_poles == 0` and the evidence root exists but contains no matching folders.
- Never use Stage 4-era CSVs as a `--field` argument without first restructuring into `NN_SUPPORT_*` folders.

---

## 7. Recommended Next Actions (Priority Order)

**1. Add a `--register` step to `scripts/run_pipeline.py` (or document a copy step).**
This is the smallest action that unblocks workspace and map overlay validation for any pipeline run without manual copy steps. Write the output directly into `uploads/jobs/<job_id>/` or add a flag to auto-register after the run. Effort: LOW. Unblocks: every future validation candidate immediately after they become runnable.

**2. Restructure one non-P_LOCAL_001 candidate's field evidence into `NN_SUPPORT_*` form.**
P_CONTROLLED_001 is the best target because it has both a baseline CSV and a flat photo folder — the photos just need to be moved into `NN_SUPPORT_*/field_photos/` subfolders. If the support numbers from the baseline can be matched to the photos (by filename, capture metadata, or site notes), this can be done with a simple folder-reorganisation script. This would produce the second independent validation run. Effort: MEDIUM (half day). Unblocks: one additional real-site validation candidate.

**3. Create `AI_CONTROL/111_STAGE5_VALIDATION_FINDINGS.md` from the P_LOCAL_001 clean ENWL run.**
The discovery work and three pipeline runs have already been completed and documented in `111_STAGE5_VALIDATION_DISCOVERY.md`. The findings document should record workspace and overlay route verification, report quality observations, and the design-blocked caveat. This must exist before any Stage 6 planning begins.

**4. Investigate whether any Gordon or Bellsprings site visit has produced field photos that could be structured.**
Gordon and Bellsprings both have baseline CSVs. If any field photos from those sites exist locally (in a non-`real_pilot_data` location) or can be created via a low-cost site revisit, structuring them into `NN_SUPPORT_*` folders would produce a second full real-world validation candidate with a genuine DNO-style baseline rather than a fixture.

**5. Add a zero-pole warning to `FolderScanner.scan()`.**
When a field evidence root folder exists but contains no `NN_SUPPORT_*` matching subfolders, the scanner currently logs individual folder warnings but does not raise a clear high-level error. Adding a single warning or raising a `ValueError` when `total_poles == 0` would prevent silent empty-dataset runs and protect against the Stage 4 CSV misuse risk described in Section 6. Effort: LOW. No test changes required for the basic warning; a specific test for the zero-pole case would add coverage.

---

## 8. Decision Gate

**Before Stage 6 feature implementation begins, the following must be true:**

1. `AI_CONTROL/111_STAGE5_VALIDATION_FINDINGS.md` exists and is complete, covering:
   - P_LOCAL_001 clean ENWL pipeline run results.
   - All seven Stage 5A reports verified as generated and readable.
   - Workspace routes (`/workspace/view/` and `/workspace/pole/`) verified as loading correctly.
   - Map overlay route (`/map/overlay/`) verified as loading with correct baseline and field layers.
   - The design-blocked result documented as expected (not a failure).

2. At least one non-fixture validation run has been attempted:
   - Either a real baseline CSV against a real field evidence folder (preferred), or
   - P_CONTROLLED_001 or a similar candidate restructured into `NN_SUPPORT_*` form and run through the pipeline.

3. The workspace/map routing gap (Section 5) is resolved either by documentation or by a `--register` pipeline step, so that future validation runs do not require manual file copying.

**Evidence needed to justify expanding validation scope to Gordon, Bellsprings, or real DNO baselines:**

- A site visit or existing photo archive that can be structured into `NN_SUPPORT_*` form for at least one of those jobs.
- Confirmation that the DNO baseline CSV for that site is available in an ENWL or TRIMBLE-compatible format.
- A successful pipeline run with non-zero matched poles and at least some `design_ready=True` results (to prove the pipeline handles real engineering data, not only blocked-by-missing-data runs).

**Stage 6 implementation must not begin until both criteria above are met.**
