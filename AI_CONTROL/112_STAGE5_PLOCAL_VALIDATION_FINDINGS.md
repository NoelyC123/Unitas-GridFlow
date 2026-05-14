# Stage 5 P_LOCAL_001 Validation Findings

Date: 2026-05-14

Branch: `codex/stage5-plocal-validation-findings`

## 1. Executive Summary

Stage 5 validation confirms that P_LOCAL_001 can run end-to-end through the current GridFlow pilot pack: baseline ingest, field import, matching, merge, QA, and reports `00`, `05`, `06`, `07`, `08`, `09`, and `10`. The primary ENWL clean run matched 10/10 poles and generated a complete output pack, with 0/10 poles design-ready because DNO engineering records are missing. This proves the Stage 5 pilot pack can package a controlled P_LOCAL_001 validation run into designer-readable outputs; it does not prove wider real-job readiness because Gordon, Bellsprings, P010, and P011 do not yet have matching Stage 4C `SUPPORT_*` field evidence folders.

## 2. Validation Scope and Limitations

Available runnable validation scope:

- P_LOCAL_001 with ENWL fixture baseline and clean field evidence.
- P_LOCAL_001 with Trimble fixture baseline and clean field evidence.
- P_LOCAL_001 with ENWL fixture baseline and original non-clean field evidence.

Unavailable or partial scope:

- Gordon and Bellsprings have starter/raw CSV material but no discovered same-site Stage 4C `SUPPORT_*` field evidence folders.
- P010 and P011 exist under `uploads/projects`, not `real_pilot_data`, and no Stage 4C field evidence folders were found during discovery.
- Wider validation is currently limited by local data readiness, not by the pipeline command surface.

P_LOCAL_001 represents a controlled real field-evidence reference set for Stage 5 validation. It includes real local evidence structured into the expected Stage 4C evidence shape, but it is still one controlled dataset and should not be treated as multi-DNO or production-scale proof.

## 3. Run Comparison Table

| Run | Baseline | Field | PASS/FAIL | Poles | Match Rate | Design Ready |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Run 1 - Primary ENWL clean | `tests/baseline/fixtures/enwl_sample.csv` | `real_pilot_data/P_LOCAL_001/enwl_enrichment_clean` | PASS | 10 baseline / 10 field / 10 merged | 100.0% | 0/10 |
| Run 2 - Trimble compatibility | `tests/baseline/fixtures/trimble_sample.csv` | `real_pilot_data/P_LOCAL_001/enwl_enrichment_clean` | PASS with caveat | 10 baseline / 10 field / 9 merged | 100.0% reported; 1 unmatched baseline and 1 unmatched field | 0/9 merged |
| Run 3 - Original field data | `tests/baseline/fixtures/enwl_sample.csv` | `real_pilot_data/P_LOCAL_001/enwl_enrichment` | PASS with quality caveat | 10 baseline / 10 field / 10 merged | 100.0% | 0/10 |

## 4. Detailed Findings — Run 1 (Primary)

Command used:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/enwl_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/gridflow_validation/P_LOCAL_001_enwl_clean
```

Result: PASS.

Output directory:

```text
/tmp/gridflow_validation/P_LOCAL_001_enwl_clean/pipeline_run_2026-05-14_134920
```

Metrics:

- Baseline format: ENWL.
- Baseline pole count: 10.
- Field pole count: 10.
- Merged pole count: 10.
- Match rate: 100.0%.
- Matched records: 10/10.
- Unmatched baseline records: 0.
- Unmatched field records: 0.
- Match confidence: 6 HIGH / 1 MEDIUM / 3 LOW.
- Evidence quality: 9 HIGH / 1 MEDIUM / 0 LOW.
- Design-ready: 0.
- Design-blocked: 10.
- Review-required count: 4.
- Verification flags: conductor spec missing 10, pole class missing 10, identity confirmation required 4, equipment conflict flag 4, condition verification 0, voltage verification 0.
- Warnings/errors printed: no runtime errors. The pipeline reported `VOLTAGE_CONFLICT(4)` during matching and expected DNO-data blockers during merge.

Reports generated:

- `00_pilot_output_pack_index.md`
- `05_qa_report.md`
- `06_dno_data_request.md`
- `07_design_readiness_summary.md`
- `08_match_confidence_analysis.md`
- `09_verification_flags_breakdown.md`
- `10_evidence_provenance_log.md`

This is the strongest available Stage 5 validation run. The all-blocked design result is legitimate because the fixture does not contain DNO-confirmed conductor specification or pole class data.

## 5. Detailed Findings — Run 2 (Trimble Baseline)

Command used:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/trimble_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/gridflow_validation/P_LOCAL_001_trimble_clean
```

Result: PASS with caveat.

Output directory:

```text
/tmp/gridflow_validation/P_LOCAL_001_trimble_clean/pipeline_run_2026-05-14_134920
```

Metrics:

- Baseline format: TRIMBLE.
- Baseline pole count: 10.
- Field pole count: 10.
- Merged pole count: 9.
- Match rate: 100.0% reported by pipeline summary.
- Match register rows: 11.
- Matched merged records: 9.
- Unmatched baseline records: 1.
- Unmatched field records: 1.
- Match confidence in merged dataset: 8 HIGH / 1 MEDIUM / 0 LOW.
- Match register confidence including unmatched rows: 8 HIGH / 1 MEDIUM / 0 LOW / 2 UNMATCHED.
- Evidence quality: 9 HIGH / 1 MEDIUM / 0 LOW.
- Design-ready: 0.
- Design-blocked: 9.
- Review-required count: 1.
- Verification flags: voltage verification 9, conductor spec missing 9, pole class missing 9, identity confirmation required 1, equipment conflict 0, condition verification 0.
- Warnings/errors printed: no runtime errors. The output has a reporting caveat: matching summary prints 10/10 and 100.0%, while the merge output correctly shows 9 merged records plus one unmatched baseline and one unmatched field record.

Reports generated:

- `00_pilot_output_pack_index.md`
- `05_qa_report.md`
- `06_dno_data_request.md`
- `07_design_readiness_summary.md`
- `08_match_confidence_analysis.md`
- `09_verification_flags_breakdown.md`
- `10_evidence_provenance_log.md`

Difference from Run 1: the Trimble fixture exercises parser compatibility and support-number normalization but is not as clean as the ENWL primary run. One fixture row is not mergeable, so this should remain a compatibility check rather than the primary validation evidence.

## 6. Detailed Findings — Run 3 (Original Field Data)

Command used:

```bash
/Library/Frameworks/Python.framework/Versions/3.13/bin/python3.13 scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/enwl_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment \
  --output /tmp/gridflow_validation/P_LOCAL_001_enwl_original
```

Result: PASS with quality caveat.

Output directory:

```text
/tmp/gridflow_validation/P_LOCAL_001_enwl_original/pipeline_run_2026-05-14_134920
```

Metrics:

- Baseline format: ENWL.
- Baseline pole count: 10.
- Field pole count: 10.
- Merged pole count: 10.
- Match rate: 100.0%.
- Matched records: 10/10.
- Unmatched baseline records: 0.
- Unmatched field records: 0.
- Match confidence: 4 HIGH / 1 MEDIUM / 5 LOW.
- Evidence quality: 7 HIGH / 1 MEDIUM / 2 LOW.
- Notes parsed: 9/10.
- Design-ready: 0.
- Design-blocked: 10.
- Review-required count: 6.
- Verification flags: conductor spec missing 10, pole class missing 10, identity confirmation required 6, equipment conflict flag 5, condition verification 0, voltage verification 0.
- Warnings/errors printed: no runtime errors. The pipeline reported lower evidence quality, one unparsed notes file, and `VOLTAGE_CONFLICT(5)`.

Reports generated:

- `00_pilot_output_pack_index.md`
- `05_qa_report.md`
- `06_dno_data_request.md`
- `07_design_readiness_summary.md`
- `08_match_confidence_analysis.md`
- `09_verification_flags_breakdown.md`
- `10_evidence_provenance_log.md`

Difference from Run 1: the original evidence folder still runs, but the clean evidence folder materially improves confidence and evidence quality. This validates the value of evidence normalization before pilot review.

## 7. Report Review (Run 1)

### `00_pilot_output_pack_index.md`

- Job name appears as `2026-05-14_134920`, not `GridFlow Pipeline`.
- Quick Actions are present for `/map/view/2026-05-14_134920`, `/workspace/view/2026-05-14_134920`, `05_qa_report.md`, and `06_dno_data_request.md`.
- Input Sources are correct for the primary run: baseline `enwl_sample.csv`, field evidence `enwl_enrichment_clean`, output directory under `/tmp/gridflow_validation/P_LOCAL_001_enwl_clean/...`.
- The report clearly distinguishes pipeline success from design blocking caused by missing DNO asset records.

### `06_dno_data_request.md`

- Flags missing conductor specification for all 10 poles.
- Flags missing pole class for all 10 poles.
- Flags voltage conflicts or uncertain voltage for 4 poles: `903202`, `900346`, `900347`, `902206`.
- Flags identity confirmation for the same 4 poles.
- Wording is actionable for a real DNO request because it lists affected support numbers, requested DNO data, design impact, and standards references.
- Main wording risk: the heading `Voltage Conflicts` covers both actual conflicts and missing or uncertain voltage. That is defensible in the body text, but the title may overstate some cases as conflicts.

### `07_design_readiness_summary.md`

- Reports 0 design-ready and 10 design-blocked poles.
- The blockers are legitimate for this test data: conductor specification and pole class are not available, and 4 poles need voltage/identity confirmation.
- The summary is useful for a designer because it separates field evidence quality from DNO engineering-data readiness and explicitly says the result is not a survey failure or pipeline error.
- Minor wording issue: footer still says `Stage 5A.1` while surrounding enhanced reports say `Stage 5A.2`.

### `08_match_confidence_analysis.md`

- Confidence breakdown is consistent with merged data: 6 HIGH, 1 MEDIUM, 3 LOW.
- LOW confidence poles are listed clearly: `903202`, `900347`, `902206`.
- MEDIUM confidence pole is listed clearly: `900346`.
- The analysis is useful because it provides reviewer actions and risk context; it is more than a number dump.
- The normalization section is clean and says no variants were detected.

### `09_verification_flags_breakdown.md`

- Flag types raised: `conductor_spec_missing`, `pole_class_missing`, `voltage_conflict`, and `identity_confirmation_required`.
- Counts are accurate for the primary merged output: 10, 10, 4, and 4 respectively.
- Standards references are present as guidance: ENA G7/4, BS EN 50341-1, ETR 132, ESQCR 2002, and ENA P28.
- The report correctly identifies that one DNO data request can resolve multiple flags for the same poles.

### `10_evidence_provenance_log.md`

- Provenance is present for all 10 merged poles.
- It clearly distinguishes baseline-sourced identity/coordinates from field-sourced photos/notes and DNO-required conductor/pole-class data.
- It accurately reports photo counts per pole and confirms field notes are captured.
- It reports structured condition and equipment observations as missing or unparsed, even though source notes/photos may contain broader observational context. This is useful as a parser limitation but should not be read as proof that the evidence contains no condition/equipment information.

### `pipeline_summary.json`

- Contains run ID, run date, baseline source, field source, detected baseline format, duration, per-stage status, per-stage counts, overall status, match rate, design-ready count, design-blocked count, and output directory.
- It is machine-readable and sufficient for automation at the current validation level.
- It does not include the Stage 5A report list or per-report generation status. That is acceptable for current CLI validation but would be useful for a future report-pack audit.

## 8. Route and Workspace Observations

Report 00 Quick Actions point to:

- `/workspace/view/2026-05-14_134920`
- `/map/overlay/2026-05-14_134920`
- `/map/view/2026-05-14_134920`

These routes are not directly usable from the `/tmp/gridflow_validation/...` pipeline run output. The Flask workspace and map overlay routes look under `uploads/jobs/<job_id>` for job data such as `04_merged_dataset.json`, `pipeline_summary.json`, and related job files. The validation output exists only under `/tmp/gridflow_validation/P_LOCAL_001_enwl_clean/pipeline_run_2026-05-14_134920`.

To make the links usable, one of the following is needed:

1. Copy or symlink the pipeline run output into `uploads/jobs/2026-05-14_134920`.
2. Add a pipeline publish/import step that registers a completed run under `uploads/jobs/<job_id>`.
3. Configure workspace/map routes to accept or resolve pipeline output directories, if that is chosen as the supported workflow.

This is primarily a pipeline routing/import gap, with a documentation gap in the report output. The report links assume the run ID is registered as an app job, but `scripts/run_pipeline.py --output /tmp/...` does not currently register that job with the app.

## 9. Bugs and Wording Issues Found

1. Report 00 route links are not directly usable for `/tmp` pipeline outputs unless the run is copied, symlinked, or imported into `uploads/jobs/<job_id>`.
2. Run 2 has a metric consistency issue: the pipeline summary reports `match_rate: 100.0` and Stage 3 prints `Matched: 10/10`, while the register/merge output includes one unmatched baseline and one unmatched field record and only 9 merged poles. This is likely fixture-specific, but it is confusing for validation.
3. `Voltage Conflicts` wording is slightly broad. Report bodies clarify that the flag can mean missing, uncertain, or conflicting voltage, but the section title may imply all flagged poles have a hard source conflict.
4. `07_design_readiness_summary.md` footer says `Stage 5A.1` while the enhanced output pack is otherwise labelled `Stage 5A.2`.
5. `10_evidence_provenance_log.md` reports `Equipment observations parsed for 0/10 poles` and structured condition missing for all poles. This appears to reflect parser extraction limits rather than absence of visual evidence, so reviewer wording should be read cautiously.

## 10. Data Gaps Preventing Wider Validation

Gordon/Bellsprings need:

- Same-site Stage 4C field evidence folders using the `NN_SUPPORT_*` structure.
- Per-support `field_photos/`, `map_screenshots/`, and `notes/` subfolders.
- Baseline CSVs compatible with Stage 4C support-number matching.
- A known mapping between support numbers in the baseline and evidence folders.

P010/P011 need:

- Confirmation of usable baseline files under `uploads/projects/P010` and `uploads/projects/P011`.
- Stage 4C `SUPPORT_*` field evidence folders for the same sites.
- Job registration or copy/import into `uploads/jobs/<job_id>` if workspace and map route validation is required.

P_LOCAL_001 needs:

- No additional data for pipeline report validation.
- A copy/import step into `uploads/jobs/<job_id>` for route validation of workspace and map overlay links generated in Report 00.

## 11. Recommended Next Actions (Priority Order)

1. Add or document a supported copy/import workflow that makes `/tmp` pipeline outputs available under `uploads/jobs/<job_id>` so Report 00 links resolve in the app.
2. Validate P_LOCAL_001 workspace and map overlay routes after the run output is registered under `uploads/jobs/<job_id>`.
3. Fix or explain the Trimble fixture metric inconsistency where matching reports 100.0% while merge produces 9 merged poles and unmatched records.
4. Tighten report wording around `Voltage Conflicts` so it distinguishes actual source conflicts from missing or uncertain voltage.
5. Update the `07_design_readiness_summary.md` footer from `Stage 5A.1` to the current report-pack label.
6. Improve provenance wording so parser gaps are clearly separated from absence of evidence in photos or notes.
7. Build Stage 4C field evidence packs for Gordon and Bellsprings before attempting broader validation.

## 12. Stage 6 Recommendation

Recommended option: **B. Build pipeline output import so workspace links work from `/tmp` runs.**

Reason: the strongest observed blocker is not a new feature gap in matching or reporting; it is that the generated pilot-pack links point to app routes that expect registered jobs under `uploads/jobs/<job_id>`, while validation runs are written to `/tmp`. A small, explicit import or publish step would make existing Stage 5 reports, workspace pages, and map overlay reviewable from the same run ID. After that, the next evidence-based step is data readiness work for wider jobs, especially creating Stage 4C field evidence packs for Gordon and Bellsprings.

Do not start broad Stage 6 implementation until the route/import gap and wider validation data gaps are resolved or explicitly accepted.
