# P_CONTROLLED_001 Readiness Gate

**Date:** 2026-05-11
**Purpose:** Confirm P_CONTROLLED_001 baseline is ready for Noel's field capture
**Authority:** Documents 50, 73–75 (Go/No-Go Gate, Prep, Protocol, Template)
**Status:** Ready for field work (conditional on local inputs being present)

---

## Readiness Verdict

### ✅ READY FOR FIELD WORK

**If all required pre-field checks pass, P_CONTROLLED_001 is cleared to proceed.**

P_CONTROLLED_001 has been selected as the controlled baseline candidate with 40 support rows extracted from the real GridFlow/Trimble baseline. Codex's subset analysis recommends:
- **Full option:** 34 poles (complete job coverage, realistic field conditions)
- **Fallback option:** 15 poles (if time/access constraints require shorter pilot)

**Stage 4C remains blocked.** This pilot must prove exact pole_id matching (≥80%) before Stage 4C runtime integration is authorized.

---

## Pre-Field Checks

### Required Local Inputs

Before Noel leaves for the field, verify these files exist and are accessible:

| Input | Location | Status | Notes |
|-------|----------|--------|-------|
| Baseline CSV (40 rows) | `sample_data/P_CONTROLLED_001_baseline.csv` | ✓ Required | Trimble pole_ids, coordinates, baseline attributes |
| Starter CSV (template) | `templates/structured_capture_template.csv` | ✓ Required | Empty Stage 4 template for capture |
| Baseline pole_id extract | `sample_data/P_CONTROLLED_001_pole_ids.txt` | ✓ Required | 40 pole_ids for on-site reference |
| Field subset plan | `sample_data/P_CONTROLLED_001_subset_plan.md` | ✓ Required | Codex's 34-row or 15-row recommendation with rationale |
| Evidence folder structure | `real_pilot_data/P_CONTROLLED_001/photos_final/` | ✓ Required | Subdirs: clear/, obscured/, proxy/, inferred/, none/ |
| Pre-field checklist | Doc 84 | ✓ Required | Noel's checklist before leaving |

### Readiness Checks

**Baseline Selection:**
- [ ] P_CONTROLLED_001 selected by Codex after suitability audit
- [ ] 40 candidate poles reviewed; 34-row or 15-row subset approved
- [ ] Baseline CSV contains pole_id, latitude, longitude, reference_frame
- [ ] Optional baseline fields (voltage, pole_class, structure_type) present if available

**Protocol Understanding:**
- [ ] Noel has read doc 74 (Pole_ID Match Protocol) — exact matching rules
- [ ] Noel understands no fuzzy matching; ≥80% exact match is GO threshold
- [ ] Noel knows what to do if pole_id uncertain (mark verification_required=yes)

**Field Pack Reviewed:**
- [ ] Noel has read doc 80 (Field-Day Procedure) — capture workflow
- [ ] Noel has read doc 81 (Photo/Evidence Rules) — photo naming and organization
- [ ] Noel has read doc 82 (Operator Decision Notes) — post-field notes template
- [ ] Noel has read doc 84 (Field Decision Checklist) — exact per-pole targets

**Equipment & Logistics:**
- [ ] Camera battery charged; backup battery available
- [ ] Device (iPad/laptop) charged; backup charger available
- [ ] Baseline CSV and template loaded on device
- [ ] Pole_id reference list printed or accessible on device
- [ ] Physical map marked with 34 (or 15) selected poles
- [ ] Evidence folder structure created locally (`real_pilot_data/P_CONTROLLED_001/photos_final/`)
- [ ] Test capture completed for 1 pole (verify format, naming, file movement works)

**Safety & Access:**
- [ ] Job location verified; no active electrical hazards noted
- [ ] Access permissions confirmed for private land poles (if any)
- [ ] Weather conditions suitable for field work
- [ ] Estimated field duration (34 poles @ 10–15 min each = 5–8.5 hours realistic)

---

## Expected Field Outputs

After field capture, Noel will produce:

| Output | Location | Expected Content | Validator Checks |
|--------|----------|------------------|------------------|
| **Captured CSV** | `real_pilot_data/P_CONTROLLED_001/csv/P_CONTROLLED_001.csv` | 34 or 15 poles, all required fields filled | No blank pole_ids, no duplicates, ≥90% valid |
| **Evidence photos** | `real_pilot_data/P_CONTROLLED_001/photos_final/` | ≥1 photo per pole, named per doc 81 | 100% reference coverage, 0 missing/orphaned/duplicates |
| **Validator report** | `validation_runs/stage4_pilots/P_CONTROLLED_001_FINAL/` | pilot_validation_report.json + .md | Terminal verdict (PASS/PARTIAL/NO-GO), row-level classification |
| **Pole_ID match report** | Manual comparison table (in doc 85) | Captured vs. Trimble baseline, match rate % | ≥80% exact match = GO; 75–80% = CONDITIONAL GO; <75% = NO-GO |
| **Decision template** | Filled doc 75 (Controlled Pilot Decision Template) | Operator verdict (GO/CONDITIONAL GO/NO-GO/STOP) | Signed by Noel, authorized by gate auditor |

**All outputs remain local (git-ignored).** Only the decision verdict (on doc 75) becomes a permanent project record.

---

## What Happens After Field Work

1. **Validation** – Noel runs validator command (doc 80 specifies exact command)
2. **Decision notes** – Noel fills doc 82 (friction log, unknown fields, confidence assessment)
3. **Pole_ID analysis** – Manual comparison: captured vs. baseline, match rate calculation
4. **Acceptance gate** – Doc 85 checks (quantitative: match rate, duplicates, coverage; qualitative: operator confidence)
5. **Verdict** – Noel signs GO / CONDITIONAL GO / NO-GO / STOP on doc 75
6. **Gate audit** – Independent reviewer confirms verdict matches thresholds
7. **Authorization** – GO verdict authorizes NEW Stage 4C implementation task (runtime integration)

**Stage 4C runtime integration remains blocked until signed verdict exists.**

---

## Critical Reminders

- **No fuzzy matching:** If pole_id is uncertain, mark verification_required=yes and document reason
- **Exact matching only:** Pole_id must match Trimble baseline exactly (after normalisation: strip whitespace, uppercase)
- **Evidence-first:** If photo is unclear, take another one; don't pretend visibility is better than it is
- **No real data in repo:** All captured CSV and photos stay in `real_pilot_data/` (git-ignored)
- **Decision board is the gate:** Noel's signed verdict on doc 75 is the formal authorization mechanism
- **Stage 4C stays blocked:** GO verdict authorizes implementation task only; does NOT auto-merge, does NOT approve Stage 4D

---

## Reference Documents

- **Doc 50:** Stage 4C Go/No-Go Gate (criterion G4)
- **Doc 73:** Controlled Baseline Pilot Prep
- **Doc 74:** Pole_ID Match Protocol (exact matching rules)
- **Doc 75:** Controlled Pilot Decision Template (verdict recording)
- **Doc 80:** Controlled Pilot Field Pack (field-day procedure)
- **Doc 81:** Photo and Evidence Rules
- **Doc 82:** Operator Decision Notes
- **Doc 84:** Field Decision Checklist (this task's detailed per-pole guide)
- **Doc 85:** Post-Field Acceptance Gate (verdict criteria)
