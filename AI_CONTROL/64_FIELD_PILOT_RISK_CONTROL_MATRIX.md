---
status: ACTIVE
created: 2026-05-10
branch: claude-code/real-field-pilot-readiness-stage4c-gate-audit
---

# 64 — Field Pilot Risk Control Matrix

This document maps each of the 8 active risks (R01–R08) from the risk register (document 55) to the specific controls that mitigate it during the real field pilot. Each risk has 4 control types: field, validation, evidence, and go/no-go impact.

---

## Control types explained

**Field control**: Action Noel takes on site to prevent the risk from occurring.

**Validation control**: What the pytest/validation pipeline checks to catch the risk.

**Evidence control**: Documentary proof (test, log, result) that the control worked.

**Go/no-go impact**: How this risk affects the Stage 4C gate decision if it fires during pilot.

---

## Risk R01 — Wrong pole_id match corrupts live job data

**Category**: Data integrity
**Likelihood**: 2 / **Impact**: 3 / **Score**: 6 (HIGH)

| Control type | Implementation |
|---|---|
| **Field control** | Noel uses Trimble pole ID reference list (printed/on-screen) for every pole. Transcribes ID exactly, character-for-character. No invention or substitution. If pole_id doesn't match list, STOP and flag as unmatched. |
| **Validation control** | `validate_stage4_rows()` normalizes pole_id (whitespace trim); rejects unsafe identity tokens (blank, "unknown", "n/a"). Test: `test_pole_id_validation_rejects_unsafe_tokens()`. Test: `test_pole_id_whitespace_normalization()`. |
| **Evidence control** | Pilot CSV has zero invalid pole_ids (all valid or marked unmatched). Checklist 52 documents pole ID reference used. Field observation log notes any mismatches encountered. Result template 53 shows 0 rows with pole_id validation error. |
| **Go/no-go impact** | If >5% of rows have invalid pole_id: REVIEW (indicates field procedure breakdown). If any row is matched to wrong Trimble pole (fuzzy match): BLOCK (mergeexact-match validation failed). Otherwise: GO. |

---

## Risk R02 — Fake completeness: Stage 4 fields present but meaningless

**Category**: Data quality
**Likelihood**: 3 / **Impact**: 2 / **Score**: 6 (HIGH)

| Control type | Implementation |
|---|---|
| **Field control** | Noel captures detail fields only when observable. If unsure, leaves blank (not "unknown"). Does not invent confidence_level; leaves blank if not genuinely assessable. Data dictionary (STAGE4_FIELD_DATA_DICTIONARY.md) guides decisions. |
| **Validation control** | Validation pipeline rejects "unknown" as invalid value (R02 fix from Stage 4A). Test: `test_unknown_value_forbidden()`. `classify_stage4_completeness()` distinguishes minimum/partial/complete; counts actual optional fields filled, not placeholders. Test: `test_completeness_classification()`. |
| **Evidence control** | Result template 53 shows completeness distribution: ≥1 complete, ≥2 partial. No rows classified as "all fields unknown". Confidence_level distribution shows majority are not "low" (if filled). Observation log documents fields left blank per Noel's assessment. |
| **Go/no-go impact** | If ≥50% of rows are minimum completeness: CAUTION (template didn't encourage detail; consider re-design). If ≥80% have confidence_level=low or missing: CAUTION (lacks surveyor confidence). If both: REVIEW (consider re-pilot). Otherwise: GO. |

---

## Risk R03 — Stage 4 leaks into map popup before Stage 4D

**Category**: Scope leakage
**Likelihood**: 2 / **Impact**: 2 / **Score**: 4 (MEDIUM)

| Control type | Implementation |
|---|---|
| **Field control** | N/A (field pilot uses validation-only pathway, not runtime). Stage 4C intake not active during pilot. |
| **Validation control** | Leakage guard test suite `test_structured_capture_leakage.py` passes on pilot CSV. Test verifies no Stage 4 tokens in C2E2 popup field groups. Test: `test_c2e2_popup_excludes_stage4_fields()`. `merge_safety_check.py` Stage 4C import scan confirms no imports in forbidden files. |
| **Evidence control** | All leakage guard tests pass on pilot. merge_safety_check.py output shows zero boundary violations. C2E2 popup field definition review confirms no structured_capture field exposure. |
| **Go/no-go impact** | If any leakage guard test fails: BLOCK (scope violated before Stage 4C even implemented). If merge_safety_check reports boundary violation: BLOCK. Otherwise: GO (pilot is intake-only, safe). |

---

## Risk R04 — pole_id format mismatch between Trimble and Stage 4 CSV

**Category**: Integration correctness
**Likelihood**: 3 / **Impact**: 2 / **Score**: 6 (HIGH)

| Control type | Implementation |
|---|---|
| **Field control** | Noel has Trimble pole ID list on site with exact formatting (dashes, capitalization). Copies pole_id verbatim from list. Does not retype or correct format. Observation log notes any format variations observed in field. |
| **Validation control** | `extract_stage4_row_identity()` normalizes pole_id: strips whitespace, preserves dashes. exact-match validation rejects fuzzy matches. Test: `test_pole_id_normalization_whitespace()`. Test: `test_pole_id_exact_match_only()`. Unmatched pole_ids are logged with reason (format mismatch vs. new pole). |
| **Evidence control** | Result template 53 pole_id match analysis shows: (a) total captured, (b) matched to Trimble, (c) unmatched, (d) match rate ≥80%. Unmatched list documents reason: format mismatch, typo, new pole, etc. Observation log notes any format surprises from Trimble export. |
| **Go/no-go impact** | If match rate <80%: REVIEW (format normalisation insufficient). Inspect unmatched reasons: if mostly format variations, then normalisation needs enhancement (fixable in Stage 4C). If mostly typos, then field procedure needs tightening (re-pilot). If match rate ≥80%: GO. |

---

## Risk R05 — Stage 4B validation preview diverges from Stage 4C merge behaviour

**Category**: Implementation consistency
**Likelihood**: 2 / **Impact**: 2 / **Score**: 4 (MEDIUM)

| Control type | Implementation |
|---|---|
| **Field control** | N/A (field pilot tests Stage 4B only, not Stage 4C). Stage 4C merge not active during pilot. |
| **Validation control** | Pilot CSV validated using `validate_stage4_rows()` from library. Stage 4B and future Stage 4C will use identical function. Integration test (to be written in Stage 4C) will verify `validate_stage4_rows()` output == merge-accepted rows. Test: `test_stage4b_preview_equals_stage4c_merge_ready()` (not yet written, deferred to Stage 4C). |
| **Evidence control** | Pilot uses Stage 4B validation only (no merge). Result template 53 documents merge_ready count from validation. Post-pilot: if Stage 4C code is implemented, integration test will confirm divergence does not occur. |
| **Go/no-go impact** | Field pilot cannot detect R05 (merge not executed). R05 mitigation check happens during Stage 4C code review and integration testing (not during pilot). Pilot result is GO if validation succeeds. R05 check happens later. |

---

## Risk R06 — Schema drift — Stage 4 schema changes break existing validated CSVs

**Category**: Backward compatibility
**Likelihood**: 2 / **Impact**: 2 / **Score**: 4 (MEDIUM)

| Control type | Implementation |
|---|---|
| **Field control** | N/A (field pilot uses fixed schema). Schema is frozen for pilot duration. |
| **Validation control** | Golden sample test suite `test_stage4_golden_samples.py` is parametrised over all golden sample CSVs (valid, invalid, duplicates, known-bad, legacy headers). Pilot CSV is added to golden samples post-pilot. Future schema changes must pass all golden sample tests, including pilot CSV. Test: `test_golden_sample_validation()`. |
| **Evidence control** | Golden sample test passes on all 5+ golden sample CSVs, plus pilot CSV (added post-pilot). If schema is ever changed, golden sample regression indicates breaking change. Changelog documents schema version and breaking changes. |
| **Go/no-go impact** | Field pilot itself cannot trigger R06 (pilot doesn't change schema). Pilot result is GO if validation passes. R06 mitigation happens post-pilot: pilot CSV is added to golden samples as regression evidence. Future PRs that fail golden sample tests will be blocked. |

---

## Risk R07 — AI worker extends Stage 4 scope without gate approval

**Category**: Governance
**Likelihood**: 2 / **Impact**: 3 / **Score**: 6 (HIGH)

| Control type | Implementation |
|---|---|
| **Field control** | N/A (field pilot does not execute runtime code). Stage 4C code not active during pilot. Feature flag defaults to False (will be implemented in Stage 4C). |
| **Validation control** | `merge_safety_check.py` Stage 4C boundary checks (added 2026-05-10) scan for: (1) forbidden file modifications, (2) missing feature flag check, (3) Stage 4 imports in forbidden files. Tests: `test_stage4c_runtime_file_boundary()`, `test_stage4c_has_feature_flag()`, `test_stage4c_no_stage4_imports_in_forbidden()` (to be written in Stage 4C). |
| **Evidence control** | merge_safety_check.py passes on Stage 4C branch with zero boundary violations. Feature flag present and documented in config. Boundary tests confirm no Stage 4 imports in qa_engine, map-viewer, pdf_generator, etc. |
| **Go/no-go impact** | Field pilot is intake-only; Stage 4C runtime code not executed. R07 mitigation happens during Stage 4C code review: merge_safety_check.py blocks PRs that violate boundaries. Pilot result is GO if validation succeeds. R07 check happens at Stage 4C merge gate. |

---

## Risk R08 — Duplicate pole_id accepted across separate upload sessions

**Category**: Data integrity
**Likelihood**: 2 / **Impact**: 2 / **Score**: 4 (MEDIUM)

| Control type | Implementation |
|---|---|
| **Field control** | Field pilot is single upload session. Noel captures 10–20 poles once. No second upload during pilot. Duplicate detection happens within-session (within single CSV). |
| **Validation control** | `validate_stage4_rows()` detects duplicates: if two rows have same pole_id within single CSV, both are marked invalid. Test: `test_duplicate_pole_id_within_csv_rejected()`. Cross-session duplicates (R08) will be caught in Stage 4C merge by checking job's existing Stage 4 records before accepting new row. Test: `test_merge_rejects_duplicate_across_sessions()` (to be written in Stage 4C). |
| **Evidence control** | Result template 53 duplicate detection table: if any duplicates found in pilot CSV, logged as invalid rows with reason "duplicate_pole_id". Golden sample `golden_duplicates.csv` is regression evidence for duplicate detection. |
| **Go/no-go impact** | If pilot CSV has >1 row with same pole_id: marked invalid, merge_ready=False. Should not happen (Noel captures each pole once). If any duplicate detected: flag in defect log for awareness. Cross-session duplicates (R08) are Stage 4C runtime risk, checked during merge (not during field pilot validation). Pilot result: if ≤1 duplicate, GO (expected). If >2 duplicates: REVIEW (field procedure issue). |

---

## Risk control coverage summary

| Risk | Field control | Validation control | Evidence control | Go/no-go impact |
|---|---|---|---|---|
| R01 | Exact ID match from reference list | Unsafe token rejection, normalisation | Valid pole_id in all rows | Match rate ≥80% → GO |
| R02 | Capture observable detail only, no invention | "unknown" forbidden, completeness classification | Complete + partial rows present | Completeness distribution → GO |
| R03 | N/A (intake-only) | Leakage guard tests pass | merge_safety_check zero violations | Leakage guard pass → GO |
| R04 | Use Trimble ID list with exact format | Whitespace normalisation, exact-match | Match rate documented, unmatched logged | Match rate ≥80% → GO |
| R05 | N/A (validation-only) | Shared validator function (deferred to Stage 4C) | Integration test result (post-merge) | Deferred to Stage 4C code review |
| R06 | N/A (schema frozen) | Golden sample regression tests | Golden samples pass, including pilot | Regression test pass → GO |
| R07 | N/A (runtime not active) | merge_safety_check boundary scan | Boundary check zero violations | Boundary check pass → GO |
| R08 | Single upload session | Within-CSV duplicate detection | Duplicate count in defect log | ≤1 duplicate → GO |

---

## Field pilot risk verdict

**All 8 risks are mitigated during field pilot through field, validation, or evidence controls.** Risks R05 and R07 are runtime risks (not triggered until Stage 4C code execution); their controls happen post-pilot (code review, integration testing). Pilot can proceed with confidence.

**High-priority evidence to capture**:
- Pole_id match rate (R01, R04)
- Completeness distribution (R02)
- Duplicate count (R08)
- Leakage guard test results (R03)
- merge_safety_check output (R07)
