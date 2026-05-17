# P0 Issue Code Locations

Date: 2026-05-17
Scope: Stage 4C M1 P0 issues only

## Issue 1 — Blank Coordinates Silently Dropped

### Primary files
- `gridflow/baseline/csv_parser.py`
- `scripts/run_pipeline.py`

### Exact functions / classes
- `CSVParser._parse_generic()`
- `CSVParser._parse_enwl()`
- `CSVParser._parse_trimble()`
- `run_stage1()` in `scripts/run_pipeline.py`

### Why these matter
- In `CSVParser._parse_generic()` rows are skipped on:
  - `if easting is None or northing is None: continue`
- Equivalent skip logic exists in `_parse_enwl()` and `_parse_trimble()`.
- That means rows with valid identity but blank coordinates disappear before any warning or flag can be surfaced.
- `run_stage1()` reports only `dataset.pole_count` and `report.error_count`; it does not compare parsed rows to source rows in a way that would fail or warn loudly for dropped poles.

### P0 conclusion
This is the direct code path responsible for dropping supports `903101` and `903203`.

## Issue 4 — Matching Failure

### Primary files
- `gridflow/matching/support_number_matcher.py`
- `gridflow/matching/register_builder.py`
- `gridflow/baseline/csv_parser.py`
- `scripts/run_pipeline.py`

### Exact functions / classes
- `SupportNumberMatcher.match()`
- `SupportNumberMatcher._try_match()`
- `SupportNumberMatcher._normalize()`
- `CSVParser._parse_generic()`
- `run_stage3()` in `scripts/run_pipeline.py`

### Why these matter
- `SupportNumberMatcher.match()` uses:
  - `b_key = self._normalize(bp.support_no or "")`
- For the P_LOCAL_002 generic baseline import, `CSVParser._parse_generic()` mapped:
  - `id = pole_id`
  - `support = None`
- That leaves `BaselinePole.support_no = None` for every imported baseline row.
- The matcher therefore normalizes every baseline support to `""` and cannot match the field support numbers at all.
- `SupportNumberMatcher._try_match()` only attempts:
  1. exact normalized support match
  2. stripped trailing letter suffix match
- There is no fallback to `pole_id` when `support_no` is missing but `pole_id` clearly contains the support identifier.

### P0 conclusion
The matching failure is not random. It is a direct interaction between generic baseline parsing and matcher assumptions.

## Issue 8 — False PASS Status

### Primary files
- `scripts/run_pipeline.py`

### Exact functions / classes
- `main()`
- `_write_summary()`
- `run_stage3()`
- `run_stage4()`

### Why these matter
- In `main()`, `overall_status` is initialised to `PASS`.
- It is only changed to `FAILED` when an exception is thrown in a stage.
- No post-stage gate checks for operational failure conditions such as:
  - `0%` match rate
  - `0` merged poles
  - baseline rows dropped without error
  - notes parsed `0/12`
- As a result:
  - `pipeline_summary.json` records `"overall_status": "PASS"`
  - console output prints `Overall status: PASS`
- `_write_summary()` simply persists the already-set status; it does not derive health independently.

### P0 conclusion
Status logic is exception-driven only. It does not model degraded-but-completed runs.

## Related P1 Locations Already Exposed by P0 Review

### Notes detection
- `gridflow/field/folder_scanner.py`
  - `_has_notes()`
  - `_get_notes_path()`
  - `_read_notes_content()`
- Current implementation recognises only `.txt`.
- P_LOCAL_002 uses `notes/pole_notes.md`.

### Evidence quality collapse
- `gridflow/field/evidence_quality_scorer.py`
  - `EvidenceQualityScorer.score()`
  - depends on `notes_present`, which is currently false for all poles because `.md` notes are ignored

### QA percentage bug
- `gridflow/merge/qa_report_generator.py`
  - `generate_confidence_table()`
- Uses `total = dataset.total_matched or 1`, then divides unmatched count by `total`, which yields impossible percentages when matched count is `0`.

### Baseline identity loss in QA
- `gridflow/merge/qa_report_generator.py`
  - `generate_unmatched_section()`
- Uses `support_no` only, while unmatched baseline records produced by the current parse path preserve `pole_id` but not `support_no`.

## Recommended P0 Fix Order

1. `gridflow/baseline/csv_parser.py`
   - preserve blank-coordinate rows
   - map `pole_id` into a usable support identity when no separate support column exists
2. `gridflow/matching/support_number_matcher.py`
   - allow fallback matching from `pole_id` when `support_no` is missing
3. `scripts/run_pipeline.py`
   - downgrade overall status to `PARTIAL` or `FAILED` for catastrophic-but-non-exception outcomes
