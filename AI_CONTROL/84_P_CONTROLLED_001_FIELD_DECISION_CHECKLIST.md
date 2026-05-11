# P_CONTROLLED_001 Field Decision Checklist

**For: Noel's per-pole targeting during field capture**

**Date:** 2026-05-11
**Purpose:** Per-pole decision targets and stop conditions for controlled baseline pilot
**Authority:** Documents 73–75 (Prep, Protocol, Decision Template)
**Scope:** Field capture workflow — what to aim for on each of the 30–50 selected poles

---

## Pole Selection Strategy

Codex has selected **P_CONTROLLED_001 baseline** with **40 candidate poles** from real Trimble survey data.

**Recommended capture options:**

- **Full option:** 34 poles (complete job coverage, realistic field conditions, 5–8.5 hours estimated)
- **Fallback option:** 15 poles (if time/access constraints require shorter pilot, 2.5–3.75 hours estimated)

**Both options use the same baseline CSV.** You choose the scale based on field conditions.

---

## Per-Pole Targets

For each pole you capture, aim for these targets:

| Target | Requirement | Why This Matters |
|--------|-------------|------------------|
| **pole_id accuracy** | Exact match to baseline ID or physical label | GO threshold is ≥80% exact match |
| **evidence_status classification** | clear / obscured / proxy / inferred / none | Determines merge-ready vs. review-required |
| **photo count** | ≥1 context shot (required), ≥2 photos optimal | Validator requires ≥90% coverage; auditor verifies your work |
| **pole_type identification** | Visible material: wood, concrete, steel, lattice | Basic asset classification for design |
| **condition assessment** | good / fair / poor / unsafe (visual only) | Structural asset state informs design decisions |
| **verification_required flag** | Mark YES if uncertain about pole_id or any field | Uncertainty is documented, not suppressed |
| **notes field** | Mismatch reason, access constraint, or unclear situation | Audit trail for decision gate |

---

## Decision Logic at Each Pole

### Pole Identification (2–3 min)

1. Use map reference and baseline pole_id list
2. Locate pole physically
3. Read pole label/tag/nameplate if visible
4. **Decide:**
   - **Exact match:** Physical label matches baseline pole_id exactly → mark `verification_required=no` → proceed normally
   - **Format difference:** Same pole, different format (P008-001 vs P008-01) → use baseline ID, mark `verification_required=yes`, document in notes
   - **Worn/missing label:** No visible label; use Trimble location to infer ID → use baseline ID, mark `evidence_status=inferred`, mark `verification_required=yes`
   - **Ambiguous/uncertain:** Cannot confirm pole_id → do NOT invent one; mark `verification_required=yes`, document reason exactly
   - **New pole:** Pole exists but not in baseline → document as new pole, mark `verification_required=yes`

### Template Filling (3–5 min)

Fill one row per pole using the Stage 4 template:

| Field | How to Fill |
|-------|-------------|
| `pole_id` | Exact from baseline or physical label (never invented) |
| `capture_source` | field_manual (for this pilot) |
| `captured_by` | Your name (Noel) |
| `capture_date` | Today's date (YYYY-MM-DD) |
| `pole_type` | wooden, concrete, steel, lattice (based on visible material) |
| `condition` | good, fair, poor, unsafe (observable only) |
| `height_m` | Measured or reasonably estimated (leave blank if uncertain) |
| `stays_count` | Count visible stay wires (leave blank if blocked) |
| `equipment` | transformer, switch, crossarm, other (if present) |
| `voltage` | Mark only if visible on nameplate (do NOT guess) |
| `verification_required` | yes if uncertain about any field or pole_id |
| `evidence_status` | clear, obscured, proxy, inferred, or none |
| `notes` | Reason for verification_required, mismatch details, access issues |

**Golden rule:** Better to mark `verification_required=yes` and leave a field blank than to guess and fill incorrectly.

### Photo Capture (2–5 min)

Minimum 1 photo per pole. More if helpful.

**Naming format (REQUIRED):**
```
<pole_id>_<evidence_type>_<sequence>.jpg
```

Examples:
- `P008-001_clear_01.jpg` — full pole, context visible
- `P008-001_clear_02.jpg` — nameplate or detail shot
- `P008-001_equipment_01.jpg` — transformer, crossarm, or top
- `P008-001_base_01.jpg` — base, stays, or ground condition
- `P008-001_obscured_01.jpg` — vegetation blocks view

**Evidence types:**
- `clear` — full, unobstructed view of pole
- `obscured` — vegetation, buildings, or distance limits visibility
- `proxy` — photo from distance; includes scale reference
- `inferred` — photo taken but pole_id estimated (not visible in photo)
- `none` — no usable photo (too dark, blurry, unusable)

### Photo Organization (1 min)

Move each photo to the appropriate subfolder:
```
real_pilot_data/P_CONTROLLED_001/photos_final/
├── clear/        # unobstructed context photos
├── obscured/     # vegetation-blocked photos
├── proxy/        # distance/angle photos
├── inferred/     # pole_id inferred from location
└── none/         # unusable photos (reference only)
```

### Next Pole

Repeat for the next pole on the baseline list. Target: 10–15 minutes per pole for experienced operator.

---

## Stop Conditions (Do Not Continue If...)

**Immediate stop — halt field work:**

1. **Cannot confirm pole_id on 3+ consecutive poles**
   - Signal: Baseline may not match field reality or capture location error
   - Action: Stop; contact Codex with location details before continuing

2. **Camera not working; no backup available**
   - Signal: Cannot capture evidence
   - Action: Return to base; replace battery or fix equipment; resume when ready

3. **Device storage full**
   - Signal: Cannot save more photos
   - Action: Offload photos to cloud/external backup immediately before continuing

4. **Baseline CSV inaccessible on device**
   - Signal: Cannot verify pole_ids
   - Action: Stop; restore CSV file from backup before continuing (unsafe to guess)

5. **Personal safety concern**
   - Examples: Electrical hazard, steep terrain, hostile animal, private property without permission, unsafe weather
   - Action: Move away immediately; document reason; do not approach pole

6. **Real data accidentally committed to repo**
   - Signal: Security isolation breach (should not happen if you follow git-ignore)
   - Action: Stop immediately; contact Codex for emergency recovery

---

## Full Option: 34-Pole Checklist

If you choose the full option:

| Target | Metric | Threshold |
|--------|--------|-----------|
| Total poles | 34 poles captured | ≥30 (some flexibility for access issues) |
| pole_id accuracy | Exact match rate | ≥80% (≥27 exact matches) |
| Photo coverage | ≥1 photo per pole | 100% (all 34 poles have ≥1 photo) |
| Valid rows | Schema + required fields | ≥90% of 34 rows = ≥31 valid |
| Merge-ready | Confident enough for immediate design use | ≥50% of 34 rows = ≥17 merge-ready |
| Evidence linking | Photos linked to pole_ids | ≥90% (0 missing, 0 orphaned) |
| Time estimate | 34 poles @ 10–15 min each | 5–8.5 hours realistic |

**Decision at 34 poles:** Run validator; assess whether GO / CONDITIONAL GO / NO-GO thresholds are met; fill decision template (doc 75).

---

## Fallback Option: 15-Pole Checklist

If you encounter access constraints or time limits:

| Target | Metric | Threshold |
|--------|--------|-----------|
| Total poles | 15 poles captured (instead of 34) | ≥12 (some flexibility) |
| pole_id accuracy | Exact match rate | ≥80% (≥12 exact matches) |
| Photo coverage | ≥1 photo per pole | 100% (all 15 poles have ≥1 photo) |
| Valid rows | Schema + required fields | ≥90% of 15 rows = ≥14 valid |
| Merge-ready | Confident enough for design use | ≥50% of 15 rows = ≥8 merge-ready |
| Evidence linking | Photos linked to pole_ids | ≥90% (0 missing, 0 orphaned) |
| Time estimate | 15 poles @ 10–15 min each | 2.5–3.75 hours realistic |

**Decision at 15 poles:** Run validator; assess thresholds; document in decision template why full option was not completed (time constraint, access issues, equipment problem, etc.); fill decision template (doc 75).

---

## Critical Reminders

1. **No fuzzy matching:** If pole_id is uncertain, mark `verification_required=yes` rather than guessing. The protocol (doc 74) requires exact matching; uncertainty is handled by human review, not algorithm guessing.

2. **Evidence-first:** If a photo is unclear, take another one. If you cannot take a better photo, mark `evidence_status=obscured` or `inferred` — don't pretend the photo is clear.

3. **One pole per row:** Do not combine two poles into one row. Each pole gets exactly one row with its own pole_id.

4. **Backup early:** Offload photos to cloud/external drive daily. Field data loss is unrecoverable.

5. **No real data in repo:** All captured CSVs and photos stay in `real_pilot_data/` (git-ignored). They never get committed to the repo.

6. **Noel's word is final:** Your signature on the decision template (doc 75) is the formal authorization mechanism for Stage 4C. The thresholds are clear; your assessment is authoritative.

---

## What Happens After Field Capture

1. Run validator: `python scripts/validate_stage4_pilot.py --csv real_pilot_data/P_CONTROLLED_001/csv/P_CONTROLLED_001.csv --evidence-dir real_pilot_data/P_CONTROLLED_001/photos_final/ --pilot-name P_CONTROLLED_001 --out validation_runs/stage4_pilots/P_CONTROLLED_001_FINAL`
2. Review validator output (row counts, match rate, evidence audit)
3. Fill operator decision notes (doc 82) with friction, unknowns, confidence assessment
4. Assess field results against post-field acceptance gate (doc 85)
5. Fill decision template (doc 75) with verdict: GO / CONDITIONAL GO / NO-GO / STOP
6. Sign decision template and submit for gate audit
7. If GO or CONDITIONAL GO: authorization for new Stage 4C implementation task
8. If NO-GO: root-cause investigation and re-pilot planning

---

## Reference

- **Doc 73:** Controlled Baseline Pilot Prep (why this pilot matters)
- **Doc 74:** Pole_ID Match Protocol (exact matching rules and categories)
- **Doc 75:** Controlled Pilot Decision Template (verdict recording)
- **Doc 80:** Controlled Pilot Field Pack (field-day procedure)
- **Doc 81:** Photo and Evidence Rules (detailed photo guidance)
- **Doc 82:** Operator Decision Notes (friction and confidence assessment)
- **Doc 85:** Post-Field Acceptance Gate (GO/CONDITIONAL GO/NO-GO criteria)
