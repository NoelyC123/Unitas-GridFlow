# P_LOCAL_002 Pipeline Run — 2026-05-17

## Command Executed

```bash
/usr/bin/time -l ./.venv312/bin/python scripts/run_pipeline.py \
  --baseline real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv \
  --field real_pilot_data/P_LOCAL_002/enwl_enrichment_clean \
  --output validation_runs/P_LOCAL_002 \
  --log-level INFO
```

## Inputs Provided

- Baseline CSV: `real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv`
- Field evidence root: `real_pilot_data/P_LOCAL_002/enwl_enrichment_clean`
- Output root: `validation_runs/P_LOCAL_002`
- Python runtime: `./.venv312/bin/python`

## Outputs Generated

Run directory:

- `validation_runs/P_LOCAL_002/pipeline_run_2026-05-17_181047/`

Generated files:

- `00_pilot_output_pack_index.md`
- `01_baseline_dataset.json`
- `02_field_dataset.json`
- `03_match_register.csv`
- `03_match_register.json`
- `04_merged_dataset.csv`
- `04_merged_dataset.json`
- `05_qa_report.md`
- `06_dno_data_request.md`
- `07_design_readiness_summary.md`
- `08_match_confidence_analysis.md`
- `09_verification_flags_breakdown.md`
- `10_evidence_provenance_log.md`
- `pipeline_summary.json`
- `validation_runs/P_LOCAL_002/pipeline_console_2026-05-17.txt`

## Validation Results

- Poles declared in baseline CSV: `12`
- Poles parsed by baseline ingest: `10`
- Poles scanned in field evidence: `12`
- Poles matched by pipeline: `0/10` processed baseline poles
- Effective declared-job match rate: `0/12`
- Coordinate gaps detected: `NO explicit pipeline check`
- Coordinate gaps observed indirectly: `YES` — two baseline rows were silently dropped
- Conflicts flagged by pipeline: `0`
- Known conflict surfaced automatically: `NO` — Pole 06 did not appear in generated QA output
- Design-ready poles: `0/10` processed baseline poles
- Design-blocked poles: `0/10` processed baseline poles
- Issues generated: `0` explicit issue records; see silent checks below

## Errors Encountered

No hard runtime exception occurred. The pipeline exited `PASS`.

The run is still operationally invalid for P_LOCAL_002 because:

1. baseline ingest processed `10` poles from a `12`-row CSV without surfacing a named missing-coordinate warning
2. field import reported `Notes parsed: 0/12` even though notes files exist for all `12` poles
3. matching returned `0/10`
4. merge produced `0` merged poles

## Silent / Missing Checks Identified

1. **Blank-coordinate baseline rows are silently dropped**
   - `P_LOCAL_002_baseline.csv` contains `12` rows.
   - `01_baseline_dataset.json` metadata shows `parsed_poles = 10`.
   - Supports `903101` and `903203` disappeared from the parsed baseline instead of being preserved with a visible `baseline_coordinate_missing` flag.

2. **Field notes existence is not being recognised**
   - `02_field_dataset.json` reports `notes_present: false` and `notes_path: null` for all `12` poles.
   - Console output reports `Notes parsed: 0/12`.
   - This is incorrect for the current evidence pack.

3. **Evidence quality scoring is effectively broken for this dataset**
   - Console output reports `0 HIGH / 0 MEDIUM / 12 LOW`.
   - That result does not reflect the actual `12/12` complete evidence structure or the completed pole notes.

4. **Matching does not bridge baseline IDs to the current field folder pattern**
   - Baseline poles use plain support IDs such as `902202`.
   - Field folders use `01_SUPPORT_902202` style names.
   - The matcher returned `0/10` even though Phase 4 structural validation already proved `12/12` support identity coverage.

5. **Stage 5 pilot reports collapse to merged-only zero data**
   - `00_pilot_output_pack_index.md` reports:
     - `Baseline poles | 0`
     - `Field evidence captured | 0`
   - `07_design_readiness_summary.md` reports:
     - `Total baseline poles: 0`
     - `Field evidence captured: 0`
   - This hides the upstream pipeline failure mode.

6. **QA report percentage calculation bug**
   - `05_qa_report.md` shows `UNMATCHED | 10 | 1000.0%`.
   - The correct percentage should not exceed `100%`.

7. **QA report loses baseline support identity**
   - Unmatched baseline poles are listed as `**None** — Easting: ...`
   - The baseline `pole_id` exists and should have been surfaced even when `support_no` is null.

8. **Overall pipeline status remains PASS despite unusable matching outcome**
   - `pipeline_summary.json` reports:
     - `"overall_status": "PASS"`
     - `"match_rate": 0.0`
     - `"design_ready_count": 0`
     - `"design_blocked_count": 0`
   - A `PASS` status with `0` merged poles on a real 12-pole job is too weak as a validation gate.

## Performance Metrics

- Pipeline runtime (reported): `0.08s`
- Shell real time: `0.37s`
- User CPU time: `0.29s`
- System CPU time: `0.05s`
- Max resident set size: `97,435,648`
- Peak memory footprint: `71,205,464`

## Console Output (Full Text)

```text
2026-05-17 18:10:48,000 gridflow.baseline.csv_parser INFO Using generic format parser
2026-05-17 18:10:48,000 gridflow.baseline.csv_parser INFO Parsing baseline CSV: real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv
2026-05-17 18:10:48,001 gridflow.baseline.csv_parser INFO Using generic format parser
2026-05-17 18:10:48,002 gridflow.baseline.csv_parser INFO Loaded 12 rows from CSV
2026-05-17 18:10:48,002 gridflow.baseline.csv_parser INFO Parsing generic format: GENERIC
2026-05-17 18:10:48,002 gridflow.baseline.csv_parser INFO Generic format mapping: id=pole_id, easting=easting, northing=northing, support=None
2026-05-17 18:10:48,003 gridflow.baseline.csv_parser INFO Parsed 10 poles from generic format (0 errors)
2026-05-17 18:10:48,003 gridflow.baseline.schema_validator INFO Validating dataset with 10 poles
2026-05-17 18:10:48,030 gridflow.baseline.coordinate_transformer INFO CoordinateTransformer initialized
2026-05-17 18:10:48,030 gridflow.baseline.schema_validator INFO Validation complete: 10 valid, 0 with errors, 10 with warnings
2026-05-17 18:10:48,050 gridflow.baseline.coordinate_transformer INFO CoordinateTransformer initialized
2026-05-17 18:10:48,050 gridflow.baseline.coordinate_transformer INFO Transformed 10 poles to WGS84 (0 errors)
2026-05-17 18:10:48,050 gridflow.baseline.route_reconstructor INFO Reconstructing pole sequences
2026-05-17 18:10:48,050 gridflow.baseline.route_reconstructor INFO Grouped 10 poles into 1 routes
2026-05-17 18:10:48,050 gridflow.baseline.route_reconstructor INFO Assigned sequence to 10 poles
2026-05-17 18:10:48,051 gridflow.field.folder_scanner INFO Scanning field dataset: real_pilot_data/P_LOCAL_002/enwl_enrichment_clean
2026-05-17 18:10:48,069 gridflow.field.folder_scanner INFO Scan complete: 12 poles found
2026-05-17 18:10:48,069 gridflow.field.evidence_quality_scorer INFO Scored 12 poles: 0 HIGH, 0 MEDIUM, 12 LOW
2026-05-17 18:10:48,070 gridflow.matching.support_number_matcher INFO Matched 0/10 baseline poles to field evidence
2026-05-17 18:10:48,070 gridflow.matching.register_builder INFO Register built: 0 matched, 10 unmatched baseline, 12 extra field | rate 0.0%
2026-05-17 18:10:48,070 gridflow.matching.register_builder INFO CSV exported to validation_runs/P_LOCAL_002/pipeline_run_2026-05-17_181047/03_match_register.csv (22 rows)
2026-05-17 18:10:48,070 gridflow.merge.data_merger INFO Merging: 10 baseline, 12 field, 22 register entries
2026-05-17 18:10:48,071 gridflow.merge.data_merger INFO Merge complete: 0 merged, 0 design_ready, 0 design_blocked
2026-05-17 18:10:48,071 gridflow.merge.qa_report_generator INFO CSV exported to validation_runs/P_LOCAL_002/pipeline_run_2026-05-17_181047/04_merged_dataset.csv (0 rows)
2026-05-17 18:10:48,071 __main__ INFO ============================================================
2026-05-17 18:10:48,071 __main__ INFO Stage 5A — Generating Pilot Reports
2026-05-17 18:10:48,071 __main__ INFO ============================================================
2026-05-17 18:10:48,071 __main__ INFO Generating 00_pilot_output_pack_index.md...
2026-05-17 18:10:48,074 __main__ INFO ✓ Report: 00_pilot_output_pack_index.md (2919 chars)
2026-05-17 18:10:48,074 __main__ INFO Generating 06_dno_data_request.md...
2026-05-17 18:10:48,074 __main__ INFO ✓ Report: 06_dno_data_request.md (894 chars)
2026-05-17 18:10:48,074 __main__ INFO Generating 07_design_readiness_summary.md...
2026-05-17 18:10:48,074 __main__ INFO ✓ Report: 07_design_readiness_summary.md (2169 chars)
2026-05-17 18:10:48,074 __main__ INFO Generating 08_match_confidence_analysis.md...
2026-05-17 18:10:48,074 __main__ INFO ✓ Report: 08_match_confidence_analysis.md (1926 chars)
2026-05-17 18:10:48,074 __main__ INFO Generating 09_verification_flags_breakdown.md...
2026-05-17 18:10:48,074 __main__ INFO ✓ Report: 09_verification_flags_breakdown.md (1028 chars)
2026-05-17 18:10:48,074 __main__ INFO Generating 10_evidence_provenance_log.md...
2026-05-17 18:10:48,074 __main__ INFO ✓ Report: 10_evidence_provenance_log.md (1388 chars)
2026-05-17 18:10:48,074 __main__ INFO Stage 5A reports generated successfully
======================================================================
GRIDFLOW PIPELINE — SURVEY-TO-DESIGN WORKFLOW
======================================================================
Run ID:  2026-05-17_181047
Baseline: real_pilot_data/P_LOCAL_002/csv/P_LOCAL_002_baseline.csv
Field:    real_pilot_data/P_LOCAL_002/enwl_enrichment_clean
Output:   validation_runs/P_LOCAL_002/pipeline_run_2026-05-17_181047/
======================================================================

Stage 1/4 — Baseline Ingest...
  Format detected: GENERIC
  Poles loaded: 10
  Validation: 10 valid, 0 errors
  Coordinates: OSGB36 → WGS84 transformed
  ✓ Complete (0.05s)

Stage 2/4 — Field Evidence Import...
  Poles scanned: 12
  Evidence quality: 0 HIGH / 0 MEDIUM / 12 LOW
  Notes parsed: 0/12
  Special flags: VARIANT_SUPPORT_NO(1)
  ✓ Complete (0.02s)

Stage 3/4 — Baseline-to-Field Matching...
  Matched: 0/10 poles
  Match rate: 0.0%
  Confidence: 0 HIGH / 0 MEDIUM / 0 LOW
  ✓ Complete (0.00s)

Stage 4/4 — Merge + QA Analysis...
  Merged poles: 0
  Design ready: 0 poles
  Design blocked: 0 poles
  Verification required:
  ✓ Complete (0.00s)
  Stage 5A reports: 6 files

======================================================================
PIPELINE COMPLETE — 0.08s
======================================================================
Overall status:  PASS
Match rate:      0.0%
Design ready:    0/10 poles
Design blocked:  0/10 poles (DNO data required)

Output files:
  00_pilot_output_pack_index.md
  01_baseline_dataset.json
  02_field_dataset.json
  03_match_register.csv
  03_match_register.json
  04_merged_dataset.csv
  04_merged_dataset.json
  05_qa_report.md
  06_dno_data_request.md
  07_design_readiness_summary.md
  08_match_confidence_analysis.md
  09_verification_flags_breakdown.md
  10_evidence_provenance_log.md
  pipeline_summary.json

Next steps: Review 05_qa_report.md for required DNO actions.
======================================================================
        0.37 real         0.29 user         0.05 sys
            97435648  maximum resident set size
                   0  average shared memory size
                   0  average unshared data size
                   0  average unshared stack size
               12810  page reclaims
                  83  page faults
                   0  swaps
                   0  block input operations
                   0  block output operations
                   0  messages sent
                   0  messages received
                   0  signals received
                 102  voluntary context switches
                 148  involuntary context switches
          3822746126  instructions retired
          1425977046  cycles elapsed
            71205464  peak memory footprint
```
