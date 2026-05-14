# Stage 5 Validation Discovery

Date: 2026-05-14

Branch: `codex/stage5-validation-discovery`

Purpose: identify which local datasets can actually run through `scripts/run_pipeline.py` for Stage 5 validation.

## Summary

Discovery found one primary immediately runnable validation job:

- `P_LOCAL_001` using `tests/baseline/fixtures/enwl_sample.csv` and `real_pilot_data/P_LOCAL_001/enwl_enrichment_clean`

Two additional runnable checks are useful but should be treated as secondary:

- `P_LOCAL_001` using `tests/baseline/fixtures/enwl_sample.csv` and the older non-clean `real_pilot_data/P_LOCAL_001/enwl_enrichment`
- `P_LOCAL_001` using `tests/baseline/fixtures/trimble_sample.csv` and `real_pilot_data/P_LOCAL_001/enwl_enrichment_clean`

Most other local real-pilot folders are partial for Stage 5 validation because they have either baseline CSVs without Stage 4C `SUPPORT_*` evidence folders, or field/photo CSVs without a compatible Stage 4C baseline.

## Discovery Commands Used

```bash
find real_pilot_data -maxdepth 2 -type d | sort
find tests/baseline/fixtures -type f -name '*.csv' | sort
find real_pilot_data -path '*/archive/*' -prune -o -type f -iname '*.csv' -print | sort
find real_pilot_data -path '*/archive/*' -prune -o -type d \( -iname '*evidence*' -o -name 'enwl_enrichment_clean' -o -name 'field_evidence' -o -name 'photos_final' -o -name 'map_screenshots' -o -name 'field_photos' -o -name 'notes' \) -print | sort
find real_pilot_data -path '*/archive/*' -prune -o -type d -name '*SUPPORT*' -print | sort
find real_pilot_data uploads validation_data -path '*/archive/*' -prune -o \( -type d -name 'P010*' -o -type d -name 'P011*' -o -type f -iname '*P010*' -o -type f -iname '*P011*' \) -print 2>/dev/null | sort
find real_pilot_data uploads validation_data -path '*/archive/*' -prune -o \( -type f -iname '*gordon*' -o -type f -iname '*bellsprings*' -o -type d -iname '*gordon*' -o -type d -iname '*bellsprings*' \) -print 2>/dev/null | sort
```

## Discovered Job And Data Folders

| Folder | Type | Stage 5 status | Notes |
| --- | --- | --- | --- |
| `real_pilot_data/P_LOCAL_001` | Field evidence + local CSVs | Runnable with fixture baseline | Contains `enwl_enrichment_clean` with 10 `SUPPORT_*` folders, each with `field_photos`, `map_screenshots`, and `notes`. |
| `real_pilot_data/P_LOCAL_001/enwl_enrichment` | Original field evidence | Runnable secondary check | Contains 10 `SUPPORT_*` folders, but quality is lower and there is an extra notes folder; use clean folder first. |
| `real_pilot_data/P_CONTROLLED_001` | Controlled baseline/capture prep | Partial / not runnable | Has `baseline/baseline.csv` and capture CSVs, but no Stage 4C `SUPPORT_*` evidence folder. |
| `real_pilot_data/P_CONTROLLED_LOCAL_001` | ENWL trace export | Partial / not runnable | Has baseline export only; `field_photos` and `screenshots` folders are present but no structured `SUPPORT_*` evidence folders were found. |
| `real_pilot_data/P_BASELINE_SURVEY_PACK` | Baseline conversion pack | Partial / not runnable | Bellsprings/Gordon starter CSVs and raw CSVs exist, but no same-site Stage 4C field evidence folders were found. |
| `real_pilot_data/P_REAL_001_MINI` | Field-capture CSV/photos | Partial / not runnable | Has Stage 4-style pilot CSV and photos, but not Stage 4C `SUPPORT_*` evidence folders and no matching baseline. |
| `real_pilot_data/P_REAL_001` | Field-capture CSV | Partial / not runnable | Has pilot CSV/evidence folder but no compatible Stage 4C baseline/evidence structure found. |
| `uploads/projects/P010` | Uploaded project CSV | Partial / not runnable | Exists locally with `Gordon_Pt1_-_Original.csv`; no Stage 4C field evidence folder found. |
| `uploads/projects/P011` | Uploaded project CSV | Partial / not runnable | Exists locally with `messy_test.csv`; no Stage 4C field evidence folder found. |

## Candidate Baseline Files

### Immediately useful for Stage 5 runs

| Path | Format observed | Notes |
| --- | --- | --- |
| `tests/baseline/fixtures/enwl_sample.csv` | ENWL fixture | Matches P_LOCAL_001 support numbers. Primary runnable baseline. |
| `tests/baseline/fixtures/trimble_sample.csv` | Trimble fixture | Mostly matches P_LOCAL_001 support numbers with `SP` prefixes; one row has blank point name, creating an unmatched/merge caveat. |

### Baseline-only or partial

| Path | Status | Notes |
| --- | --- | --- |
| `real_pilot_data/P_CONTROLLED_001/baseline/baseline.csv` | Partial | Raw survey-style header begins with job metadata, not immediately paired with Stage 4C field evidence. |
| `real_pilot_data/P_CONTROLLED_LOCAL_001/baseline_exports/trace_001_sheernest_bridge_lv_transformer.csv` | Partial | ENWL trace export with asset rows; no structured same-site `SUPPORT_*` evidence folder found. |
| `real_pilot_data/P_BASELINE_SURVEY_PACK/csv/bellsprings_stage4_starter.csv` | Partial | Stage 4 starter/capture shape, not Stage 4C baseline schema, and no matching field evidence folder found. |
| `real_pilot_data/P_BASELINE_SURVEY_PACK/csv/gordon_original_stage4_starter.csv` | Partial | Starter CSV only; no matching field evidence folder found. |
| `real_pilot_data/P_BASELINE_SURVEY_PACK/csv/gordon_pr1_stage4_starter.csv` | Partial | Starter CSV only; previous notes indicate duplicate point identity issue. |
| `real_pilot_data/P_BASELINE_SURVEY_PACK/csv/gordon_pr2_stage4_starter.csv` | Partial | Starter CSV only; no matching field evidence folder found. |
| `real_pilot_data/P_BASELINE_SURVEY_PACK/raw/Sample/Bellsprings - CSV File.csv` | Partial | Raw Trimble/controller-style CSV; no matching Stage 4C field evidence folder found. |
| `real_pilot_data/P_BASELINE_SURVEY_PACK/raw/gordon_original.csv` | Partial | Raw Gordon baseline/survey CSV; no Stage 4C field evidence folder found. |
| `uploads/projects/P010/files/F001/Gordon_Pt1_-_Original.csv` | Partial | P010 exists in `uploads`, but not in `real_pilot_data`; no Stage 4C field evidence folder found. |
| `uploads/projects/P011/files/F001/messy_test.csv` | Partial | P011 exists in `uploads`, but not in `real_pilot_data`; no Stage 4C field evidence folder found. |

## Candidate Field Evidence Folders

| Path | Support folders | Evidence shape | Status |
| --- | ---: | --- | --- |
| `real_pilot_data/P_LOCAL_001/enwl_enrichment_clean` | 10 | Each support folder has `field_photos`, `map_screenshots`, and `notes`. | Primary runnable field evidence. |
| `real_pilot_data/P_LOCAL_001/enwl_enrichment` | 10 | Same general structure but older/non-clean; includes an extra duplicate notes folder. | Runnable secondary check, not preferred. |
| `real_pilot_data/P_CONTROLLED_LOCAL_001/field_photos` | 0 | No `SUPPORT_*` subfolders found. | Not runnable for Stage 4C pipeline. |
| `real_pilot_data/P_CONTROLLED_LOCAL_001/screenshots` | 0 | No `SUPPORT_*` subfolders found. | Not runnable for Stage 4C pipeline. |
| `real_pilot_data/P_CONTROLLED_001/photos_final` | 0 | Flat photo folder/no `SUPPORT_*` structure found. | Not runnable for Stage 4C pipeline. |
| `real_pilot_data/P_REAL_001_MINI/photos_final` | 0 | Flat final photo folder/no `SUPPORT_*` structure found. | Not runnable for Stage 4C pipeline. |

## Pipeline Runs Attempted

The local shell does not provide a `python` command, so discovery used:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13
```

### 1. P_LOCAL_001 ENWL Fixture + Clean Evidence

Command used:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/enwl_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/gridflow_validation_discovery/P_LOCAL_001_enwl_clean
```

Result: PASS.

| Metric | Result |
| --- | --- |
| Baseline format | ENWL |
| Baseline poles | 10 |
| Field poles | 10 |
| Evidence quality | 9 HIGH / 1 MEDIUM / 0 LOW |
| Matched | 10/10 |
| Match rate | 100.0% |
| Merged poles | 10 |
| Design-ready | 0 |
| Design-blocked | 10 |
| Unmatched baseline | 0 |
| Unmatched field | 0 |
| Confidence | 6 HIGH / 1 MEDIUM / 3 LOW |
| Reports generated | `00`, `05`, `06`, `07`, `08`, `09`, `10` |

Notes: This is the primary validation candidate.

### 2. P_LOCAL_001 Trimble Fixture + Clean Evidence

Command used:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/trimble_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/gridflow_validation_discovery/P_LOCAL_001_trimble_clean
```

Result: PASS with caveat.

| Metric | Result |
| --- | --- |
| Baseline format | TRIMBLE |
| Baseline poles | 10 |
| Field poles | 10 |
| Evidence quality | 9 HIGH / 1 MEDIUM / 0 LOW |
| Matched | 10/10 reported by matching summary |
| Match rate | 100.0% |
| Merged poles | 9 |
| Design-ready | 0 |
| Design-blocked | 9 |
| Unmatched baseline | 1 |
| Unmatched field | 1 |
| Confidence | 8 HIGH / 1 MEDIUM / 0 LOW in merged dataset |
| Reports generated | `00`, `05`, `06`, `07`, `08`, `09`, `10` |

Notes: Useful parser/matching check, but not a primary validation run because one Trimble fixture row has no `Point Name`, which causes an unmatched/merge discrepancy.

### 3. P_LOCAL_001 ENWL Fixture + Original Non-Clean Evidence

Command used:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/enwl_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment \
  --output /tmp/gridflow_validation_discovery/P_LOCAL_001_enwl_original
```

Result: PASS with quality caveat.

| Metric | Result |
| --- | --- |
| Baseline format | ENWL |
| Baseline poles | 10 |
| Field poles | 10 |
| Evidence quality | 7 HIGH / 1 MEDIUM / 2 LOW |
| Matched | 10/10 |
| Match rate | 100.0% |
| Merged poles | 10 |
| Design-ready | 0 |
| Design-blocked | 10 |
| Unmatched baseline | 0 |
| Unmatched field | 0 |
| Confidence | 4 HIGH / 1 MEDIUM / 5 LOW |
| Reports generated | `00`, `05`, `06`, `07`, `08`, `09`, `10` |

Notes: Useful as a regression check for non-clean evidence. Not preferred for pilot validation because the clean evidence folder has better quality and deterministic naming.

## Valid Runnable Jobs

| Recommended order | Candidate | Baseline | Field evidence | Status |
| ---: | --- | --- | --- | --- |
| 1 | P_LOCAL_001 clean ENWL | `tests/baseline/fixtures/enwl_sample.csv` | `real_pilot_data/P_LOCAL_001/enwl_enrichment_clean` | Runnable / primary |
| 2 | P_LOCAL_001 clean Trimble fixture | `tests/baseline/fixtures/trimble_sample.csv` | `real_pilot_data/P_LOCAL_001/enwl_enrichment_clean` | Runnable / parser compatibility check |
| 3 | P_LOCAL_001 original evidence | `tests/baseline/fixtures/enwl_sample.csv` | `real_pilot_data/P_LOCAL_001/enwl_enrichment` | Runnable / lower-quality evidence regression |

## Partial Or Non-Runnable Jobs

| Candidate | Why not immediately runnable |
| --- | --- |
| P_CONTROLLED_001 | Baseline and capture CSVs exist, but no Stage 4C `SUPPORT_*` evidence folder found. |
| P_CONTROLLED_LOCAL_001 | ENWL trace export exists, but no structured `SUPPORT_*` field evidence folder found. |
| P_BASELINE_SURVEY_PACK Bellsprings | Starter/raw baseline CSVs and PDFs exist, but no same-site Stage 4C field evidence folder found. |
| P_BASELINE_SURVEY_PACK Gordon original/PR1/PR2 | Starter/raw baseline CSVs exist, but no same-site Stage 4C field evidence folder found. |
| P_REAL_001_MINI | Field-capture CSV/photos exist, but no compatible baseline or Stage 4C `SUPPORT_*` evidence folder found. |
| P_REAL_001 | Field-capture CSV/evidence folder exists, but no compatible baseline or Stage 4C `SUPPORT_*` evidence folder found. |
| uploads/projects/P010 | Exists locally with `Gordon_Pt1_-_Original.csv`, but no Stage 4C field evidence folder found. Not present under `real_pilot_data`. |
| uploads/projects/P011 | Exists locally with `messy_test.csv`, but no Stage 4C field evidence folder found. Not present under `real_pilot_data`. |

## Exact Commands For Valid Candidates

Primary:

```bash
python scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/enwl_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/gridflow_validation/P_LOCAL_001_enwl_clean
```

Secondary Trimble fixture check:

```bash
python scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/trimble_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/gridflow_validation/P_LOCAL_001_trimble_clean
```

Secondary original-evidence check:

```bash
python scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/enwl_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment \
  --output /tmp/gridflow_validation/P_LOCAL_001_enwl_original
```

If `python` is not available in the local shell, use the Python 3.13 binary that was used for discovery:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/enwl_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/gridflow_validation/P_LOCAL_001_enwl_clean
```

## Recommended Validation Order

1. Run full validation on P_LOCAL_001 clean ENWL.
2. Check all generated reports `00`, `05`, `06`, `07`, `08`, `09`, and `10`.
3. Copy or symlink the run output into a workspace-compatible job location if needed, then validate:
   - `/workspace/view/<job_id>`
   - `/workspace/pole/<job_id>/<support_number>`
   - `/map/overlay/<job_id>`
   - overlay JSON endpoint.
4. Run the Trimble fixture pairing as a parser/matching compatibility check and document the one unmatched/merge caveat.
5. Run the original evidence folder only as a regression comparison against the clean folder.
6. Do not spend validation time on Gordon/Bellsprings/P010/P011 until same-site Stage 4C field evidence folders are created or located.

## Missing Baselines Or Missing Field Evidence

- P_LOCAL_001 has field evidence but uses fixture baselines for Stage 5 validation.
- Gordon and Bellsprings have baseline/starter CSVs but no discovered same-site Stage 4C field evidence folders.
- P010/P011 exist under `uploads/projects`, not `real_pilot_data`, and no Stage 4C field evidence folders were found.
- P_CONTROLLED_001 and P_CONTROLLED_LOCAL_001 are not currently runnable through `scripts/run_pipeline.py` because their available evidence is not in `NN_SUPPORT_*` folder form.

## Suggested Next Validation Step

Create `AI_CONTROL/111_STAGE5_VALIDATION_FINDINGS.md` from a focused validation of the primary candidate:

```text
P_LOCAL_001 clean ENWL:
baseline = tests/baseline/fixtures/enwl_sample.csv
field = real_pilot_data/P_LOCAL_001/enwl_enrichment_clean
```

The validation should inspect generated reports, workspace routes, pole detail route for at least one support number, preview map overlay, and overlay JSON. It should also record the Trimble fixture caveat separately as a compatibility issue rather than a pilot blocker.
