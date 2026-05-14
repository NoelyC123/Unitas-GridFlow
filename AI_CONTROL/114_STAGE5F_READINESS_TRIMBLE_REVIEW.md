# Stage 5F Readiness and Trimble Truthfulness Review

**Date:** 2026-05-14
**Branch:** `claude-code/stage5f-readiness-trimble-review`
**Pipeline used:** `scripts/run_pipeline.py` with `--register --overwrite-registration`

---

## 1. Executive Summary

**Design readiness:** The 0/10 design-ready result on P_LOCAL_001 is correct behaviour. Both `conductor_verification_required` and `pole_class_verification_required` are unconditionally `True` by design — conductor spec and pole class are never available from survey data alone and always require DNO engineering records. Every pole on every survey will be design-blocked until a designer obtains and confirms those records. This is not a bug. The logic is correct, the docstrings say so explicitly, and the 0/10 result accurately describes the state of the data. No code changes were made to design readiness logic. Four new tests were added to lock this behaviour explicitly.

**Trimble match rate:** The reported 100% match rate on the Trimble fixture was a calculation bug. `MatchRegister.compute_stats()` counted `EXTRA_FIELD` entries (field poles with no baseline partner) as matched because the filter excluded only `UNMATCHED` but not `EXTRA_FIELD`. This inflated `matched` from 9 to 10 and reported 100% instead of 90%. A one-line fix to `gridflow/matching/models.py` corrects the denominator exclusion. The Trimble fixture now correctly reports 9/10 matched at 90%. Two new regression tests were added.

---

## 2. Design Readiness Investigation

### 2.1 How design readiness is determined

The full code path:

1. `gridflow/merge/verification_flag_generator.py:32` — `VerificationFlagGenerator.generate_flags()` runs six checks on a `MergedPole`.
2. `verification_flag_generator.py:73–75` — `_check_conductor_verification()` unconditionally returns `True`. Docstring: *"Always True — conductor spec requires DNO data records."*
3. `verification_flag_generator.py:77–79` — `_check_pole_class_verification()` unconditionally returns `True`. Docstring: *"Always True — pole class requires DNO data records."*
4. `verification_flag_generator.py:116–122` — `_compute_design_status()` sets `design_blocked = True` if any verification flag is set. Since conductor and pole class are always `True`, `design_blocked` is always `True`.
5. `verification_flag_generator.py:123` — `design_ready = not design_blocked and pole.match_confidence == "HIGH"`. Since `design_blocked` is always `True`, `design_ready` is always `False`.
6. `gridflow/merge/data_merger.py:92–93` — the merged dataset counts `design_ready` and `design_blocked` poles across all merged records.

### 2.2 Blockers found on P_LOCAL_001 ENWL clean run

| Pole # | Support Number | Confidence | Voltage | Blockers | All legitimate? |
|---|---|---|---|---|---|
| 1 | 903203 | HIGH | LV (known) | conductor, pole class | Yes |
| 2 | 903202 | LOW | LV (known) | conductor, pole class, identity | Yes |
| 3 | 903201A | HIGH | HV (known) | conductor, pole class | Yes |
| 4 | 903201 | HIGH | HV (known) | conductor, pole class | Yes |
| 5 | 902204 | HIGH | HV (known) | conductor, pole class | Yes |
| 6 | 903101 | HIGH | LV (known) | conductor, pole class | Yes |
| 7 | 903503 | HIGH | LV (known) | conductor, pole class | Yes |
| 8 | 900346 | MEDIUM | HV (known) | conductor, pole class, identity | Yes |
| 9 | 900347 | LOW | HV (known) | conductor, pole class, identity | Yes |
| 10 | 902206 | LOW | HV (known) | conductor, pole class, identity | Yes |

Observation: `voltage_verification_required = False` for all 10 poles because the ENWL fixture contains voltage values (`LV`/`HV`). The universal blockers are conductor and pole class — both genuine DNO engineering gaps.

### 2.3 What "design-ready" should mean

For a real OHL designer, a pole is design-ready when they have enough confirmed data to begin producing PoleCAD or AutoCAD design outputs: specifically the conductor specification (type, size, material — needed for sag calculations, thermal limits, and mechanical loading), the pole class (structural rating — needed to verify the pole can take the intended load at the intended height), and sufficient location and identity certainty. A Trimble survey or ENWL field-capture delivers GPS coordinates, photos, site notes, and identity evidence. It does not deliver conductor specifications or pole class ratings. Those remain in DNO engineering asset records and must be confirmed through a formal DNO data request. Until they are confirmed, no designer should commit to a design, because the wrong conductor size or an underrated pole creates a safety and compliance failure.

### 2.4 Decision

**0/10 design-ready is: CORRECT BEHAVIOUR**

The `conductor_verification_required` and `pole_class_verification_required` flags are always `True` by deliberate design. The codebase comment says so and the logic implements it correctly. A survey produces GPS positions, evidence quality, photos, and notes. It does not produce DNO conductor specifications or pole class ratings. GridFlow correctly identifies this gap and blocks design until those records are confirmed. The 0/10 result is the right answer for any survey dataset that has not been supplemented with DNO engineering data. When a real DNO baseline CSV with conductor and pole class records is available, those fields could potentially allow a different result — but no such dataset is currently validated.

---

## 3. Design Readiness Changes

No code changes — current behaviour is correct.

Four tests were added to `tests/merge/test_verification_flag_generator.py` to lock the behaviour:

- `test_design_blocked_even_with_perfect_match_and_voltage` — proves that HIGH confidence + known voltage still yields `design_blocked=True` because conductor and pole class are always required.
- `test_design_blocked_count_all_poles_in_survey_without_dno_data` — runs all 10 P_LOCAL_001 support numbers through the flag generator and asserts every pole is design-blocked.

(Two tests already existed: `test_conductor_flag_always_true`, `test_pole_class_flag_always_true`.)

---

## 4. Trimble Match Rate Investigation

### 4.1 Match register vs merge output

| Metric | Before fix | After fix |
|---|---|---|
| Register entries | 11 | 11 |
| Match type EXACT | 9 | 9 |
| Match type UNMATCHED (blank Point Name) | 1 | 1 |
| Match type EXTRA_FIELD (field pole 902204) | 1 | 1 |
| `register.matched` reported | 10 ← **wrong** | 9 ✓ |
| `register.match_rate` reported | 100.0% ← **wrong** | 90.0% ✓ |
| Merged poles produced | 9 | 9 |

Root cause of fixture issue: the Trimble fixture CSV contains one row where the Point Name column is blank. The CSV parser reads it as `nan`. The support number normaliser cannot extract a valid ID from `nan`, so the pole goes through matching as support number `""` or `nan`. No field folder name matches this, so it exits as `UNMATCHED`. The corresponding field pole (`902204`) has no baseline partner and exits as `EXTRA_FIELD`.

### 4.2 How match rate is calculated

The match rate is set in `gridflow/matching/models.py:60–68`:

```python
def compute_stats(self) -> None:
    # ...
    matched = sum(1 for e in self.entries if e.match_type != "UNMATCHED")  # BUG: includes EXTRA_FIELD
    self.matched = matched
    if self.baseline_total > 0:
        self.match_rate = (matched / self.baseline_total) * 100
```

`compute_stats()` is called at `gridflow/matching/register_builder.py:82`, immediately after the `MatchRegister` is constructed. `RegisterBuilder.build()` had already correctly calculated `matched = 9` at line 72 using `not in ("UNMATCHED", "EXTRA_FIELD")`, passed it to the constructor at line 77 — but `compute_stats()` overwrites `self.matched` with the inflated value 10. The local variable logged by the `RegisterBuilder` logger ("Register built: 9 matched…") used the local value before overwrite, so the log line was correct but `register.matched` was not.

### 4.3 Root cause

**Type: CALCULATION BUG**

`MatchRegister.compute_stats()` used `match_type != "UNMATCHED"` as the "is matched" predicate. The correct predicate is `match_type not in ("UNMATCHED", "EXTRA_FIELD")`, since `EXTRA_FIELD` means a field pole that found no baseline partner — the opposite of a match. Counting it as matched was a logic error that inflated the count by exactly the number of extra field entries.

### 4.4 Decision

Fixed. One line changed in `gridflow/matching/models.py:65`.

```python
# Before (bug):
matched = sum(1 for e in self.entries if e.match_type != "UNMATCHED")

# After (fix):
matched = sum(1 for e in self.entries if e.match_type not in ("UNMATCHED", "EXTRA_FIELD"))
```

---

## 5. Trimble Match Rate Changes

**File changed:** `gridflow/matching/models.py` line 65 — `compute_stats()` predicate corrected.

**Effect on ENWL runs:** None. When all poles match (no `EXTRA_FIELD` entries), the result is identical.

**Effect on Trimble Fixture run:** `register.matched` now correctly reports 9; `register.match_rate` correctly reports 90.0%; Stage 3 print now reads "Matched: 9/10 poles, Match rate: 90.0%".

**pipeline_summary.json** now records the accurate value.

---

## 6. Tests Added or Updated

### New in `tests/matching/test_register_builder.py`

| Test | What it proves |
|---|---|
| `test_match_rate_excludes_extra_field_entries` | End-to-end: 9 matched + 1 UNMATCHED + 1 EXTRA_FIELD → `matched=9`, `match_rate=90.0%` |
| `test_compute_stats_extra_field_not_counted_as_matched` | Unit: `compute_stats()` directly with a mix of EXACT, UNMATCHED, EXTRA_FIELD entries → only EXACT counted |

### New in `tests/merge/test_verification_flag_generator.py`

| Test | What it proves |
|---|---|
| `test_design_blocked_even_with_perfect_match_and_voltage` | HIGH confidence + known voltage → still design-blocked; conductor + pole class are always required |
| `test_design_blocked_count_all_poles_in_survey_without_dno_data` | All 10 P_LOCAL_001 support numbers pass through flag generator → every pole design-blocked; locks the 0/10 correct result |

---

## 7. Validation Commands Run

```bash
# ENWL primary run (design readiness investigation)
python scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/enwl_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/stage5f_readiness_review \
  --job-id STAGE5F_READINESS_REVIEW \
  --register --overwrite-registration
# Result: 10/10 matched, 100%, 0/10 design-ready — CORRECT

# Trimble run before fix
python scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/trimble_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/stage5f_trimble_review \
  --job-id STAGE5F_TRIMBLE_REVIEW \
  --register
# Result: 10/10 matched (WRONG), 100% (WRONG), 9 merged — BUG CONFIRMED

# Trimble run after fix
python scripts/run_pipeline.py \
  --baseline tests/baseline/fixtures/trimble_sample.csv \
  --field real_pilot_data/P_LOCAL_001/enwl_enrichment_clean \
  --output /tmp/stage5f_trimble_fixed \
  --job-id STAGE5F_TRIMBLE_FIXED \
  --register
# Result: 9/10 matched, 90.0%, 9 merged — CORRECT

# Targeted tests
pytest tests/matching/test_register_builder.py tests/merge/test_verification_flag_generator.py -v
# Result: 26 passed

# Full suite
pytest -q
# Result: 1355 passed, 1 skipped
```

---

## 8. Pilot-Use Recommendation

The tool is ready to show to an OHL designer for a structured walkthrough — not a production handoff. The 0/10 design-ready result on P_LOCAL_001 should be the *opening point* of that walkthrough, not a thing to apologise for. It is the most honest and useful output the tool produces: it tells a designer exactly what they need to request from the DNO (conductor spec and pole class for all 10 poles, voltage confirmation for 4, identity confirmation for 4 low/medium-confidence matches) before they can begin. The designer should be shown Report 06 (`06_dno_data_request.md`) first, because it names the blockers per pole in designer-readable language. Then Reports 07 and 08 as supporting context. The workspace at `/workspace/view/<job_id>` gives a filterable pole-by-pole view. The Trimble fix is not visible to a designer but removes a number that was objectively wrong from any report they might read.

---

## 9. Remaining Risks

1. **Only fixture baselines validated.** The ENWL fixture (`enwl_sample.csv`) was built to match the P_LOCAL_001 field evidence. A real DNO baseline CSV for that site, if it contained conductor and pole class data, would produce a different design-readiness result. That result has not been tested.

2. **Blank-name Trimble fixture row is a known caveat, not a general Trimble issue.** Real Trimble exports do not have blank Point Name rows; this is a fixture artefact. The fix ensures it is correctly accounted for, but the row cannot merge and the field pole it corresponds to appears as unmatched. This should be documented when using the Trimble fixture as a compatibility check.

3. **`equipment_conflict_flag` is not included in `_compute_design_status()`.** It is generated and reported but does not block design. If a real DNO baseline had conflicting equipment records, those would show in Report 06 but would not block the `design_ready` field. This may or may not be intentional — worth confirming before a pilot with real conflicting data.

4. **Single real-site dataset.** All Stage 5 validation evidence comes from one controlled local evidence pack (P_LOCAL_001). Gordon, Bellsprings, P010, and P011 still lack compatible Stage 4C field evidence folders. Until at least one of those is usable, the validation scope remains narrow.

5. **Report 07 footer still says `Stage 5A.1`** (noted in `AI_CONTROL/112_STAGE5_PLOCAL_VALIDATION_FINDINGS.md`). Not a readiness blocker but a polish gap visible to any designer who reads it.
