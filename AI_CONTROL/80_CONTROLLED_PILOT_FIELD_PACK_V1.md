# Controlled Pilot Field Pack v1

**For use by Noel after Codex selects the baseline candidate (P_CONTROLLED_001)**

**Date:** 2026-05-11
**Purpose:** Simple operator field pack for capturing 30–50 poles against a real Trimble baseline
**Authority:** Documents 73–75 (Controlled Baseline Pilot Prep, Pole_ID Match Protocol, Decision Template)
**Scope:** Field capture workflow only (baseline selection done by Codex separately)

---

## Before You Leave

Noel's pre-field checklist:

- [ ] Codex has selected the baseline job and extracted the Trimble CSV
- [ ] Baseline CSV is on device (iPad or laptop) — pole_ids, coordinates documented
- [ ] Stage 4 template is loaded on device or printed (use `templates/structured_capture_template.csv`)
- [ ] Field bag packed: camera battery charged, device charged, backup battery, notebook, pen
- [ ] Evidence folder created on device: `real_pilot_data/P_CONTROLLED_001/photos_final/`
- [ ] Subdirectories created: `clear/`, `obscured/`, `proxy/`, `inferred/`, `none/`
- [ ] Physical map prepared: poles marked, access points noted, hazards identified
- [ ] Baseline pole_ids reviewed: you know what to expect on-site
- [ ] Test capture completed for 1 pole: format correct, file naming works, folder structure confirmed

---

## The Baseline Pole List

Codex selected **~30–50 poles** from the baseline job.

**On-site reference:**
- Check the baseline pole_id against the pole label/tag visible on the pole
- If the pole label matches baseline, fill `pole_id` exactly as shown in the baseline
- If the label differs from baseline or is unclear, document the mismatch reason and mark `verification_required=yes`
- If the pole is inaccessible or unmarked, use the Trimble ID from the baseline as your best reference, but flag `verification_required=yes`

**No guessing:** If you cannot verify the pole_id with confidence, do not invent one. Mark the row as uncertain and document your reasoning.

---

## Per-Pole Capture Workflow

For each of the 30–50 selected poles:

### Step 1: Locate and Identify (2–3 min)

1. Use map reference to find pole location
2. Read the pole label/plate if visible
3. Compare against baseline pole_id from Codex's list
4. **Decide:** Can I confirm this is the pole in the baseline?
   - **YES → continue to Step 2**
   - **NO or UNCERTAIN → mark `verification_required=yes` and document reason**

### Step 2: Fill the Template Row (3–5 min)

Open the Stage 4 template CSV on your device. Fill one row per pole:

| Field | How to fill | Examples |
|-------|-------------|----------|
| `pole_id` | EXACT match from baseline or pole label | P008-001, P-SPEN-042, P010.005 |
| `capture_source` | Select: surveyor_tablet or field_manual | surveyor_tablet |
| `captured_by` | Your name | Noel |
| `capture_date` | Today's date (YYYY-MM-DD) | 2026-05-15 |
| `pole_type` | Visible material: wooden, concrete, steel, lattice | wooden |
| `condition` | Good, fair, poor, unsafe (based on visible damage) | fair |
| `height_m` | Measured or estimated (meters) | 11.5 |
| `stays_count` | Number of stay wires visible | 2 |
| `equipment` | What's attached: transformer, switch, crossarm, other | transformer |
| `voltage` | Marked or known (kV) | 11kV, 230V |
| `verification_required` | yes/no — flag uncertain rows | yes |
| `evidence_status` | clear, obscured, proxy, inferred, or none | clear |
| `notes` | Free text for non-standard situations | pole label worn; matches baseline ID P008-001 |

**What NOT to guess:**
- ❌ Don't invent a `height_m` if you can't measure or reasonably estimate it
- ❌ Don't fill `voltage` unless you see it marked on the pole or equipment
- ❌ Don't assume `stays_count` if visibility is poor — mark `evidence_status=obscured` instead
- ❌ Don't fill optional fields unless confident

**What IS expected:**
- ✅ `pole_id` — required, must match baseline or document mismatch
- ✅ `capture_date`, `captured_by` — metadata for audit trail
- ✅ `condition` — observable, you can always say good/fair/poor/unsafe
- ✅ `evidence_status` — required, describes photo quality
- ✅ `verification_required` — if uncertain about any field, mark yes

### Step 3: Take Evidence Photos (2–5 min)

Minimum 1 photo per pole. More if helpful.

**Photo naming format (REQUIRED):**
```
<pole_id>_<evidence_type>_<sequence>.jpg
```

Examples:
- `P008-001_clear_01.jpg` — full pole view
- `P008-001_clear_02.jpg` — nameplate/ID detail
- `P008-001_equipment_01.jpg` — transformer or crossarm
- `P008-001_base_01.jpg` — base condition
- `P008-001_obscured_01.jpg` — if vegetation blocked view

**Evidence types:**
- `clear` — full, unobstructed view of pole
- `obscured` — vegetation, buildings, or distance limits visibility
- `proxy` — photo from distance/angle; includes reference object for scale
- `inferred` — photo taken but pole_id estimated (not visible)
- `none` — no usable photo (too dark, blurry, etc.)

**Photo content guidance (see doc 81 for detail):**
- Include pole ID/plate if visible
- Include top of pole if safe
- Include base/defects if relevant
- Include context (surroundings, scale reference)

### Step 4: Organize Photos Locally (1 min)

Move each photo to the appropriate subfolder on device:
```
real_pilot_data/P_CONTROLLED_001/photos_final/
├── clear/          # full view photos
├── obscured/       # vegetation-blocked photos
├── proxy/          # distance/angle photos
├── inferred/       # pole_id not visible in photo
└── none/           # unusable photos (for reference only)
```

**Check before moving:**
- Filename starts with the pole_id you just captured
- Filename matches the evidence_type you selected in the template
- Filename ends with .jpg (not HEIC, not PNG unless specifically needed)

### Step 5: Next Pole

Repeat for the next pole on the baseline list.

---

## End-of-Day Workflow

After capturing 6–8 poles (or at end of day):

### Check 1: No Blank pole_ids

```
grep -c '^[^,]*,[^,]*$' real_pilot_data/P_CONTROLLED_001/csv/P_CONTROLLED_001.csv
```

If this returns any matches, you have rows with blank pole_id. Go back and fill them or document why.

### Check 2: Evidence Folder Structure

```
ls -la real_pilot_data/P_CONTROLLED_001/photos_final/
```

You should see 5 subdirectories: `clear/`, `obscured/`, `proxy/`, `inferred/`, `none/`.

### Check 3: Photo Count

```
find real_pilot_data/P_CONTROLLED_001/photos_final -name '*.jpg' | wc -l
```

Should be at least equal to number of poles captured. If much lower, you have missing photos.

### Check 4: Backup CSV

Copy today's CSV to a separate backup location (cloud, external drive, or email to yourself):
```
cp real_pilot_data/P_CONTROLLED_001/csv/P_CONTROLLED_001.csv ~/backup/P_CONTROLLED_001_$(date +%Y%m%d_%H%M%S).csv
```

---

## Post-Field: Validation

When field capture is complete (all 30–50 poles captured, all photos organized):

### Run the validator

```bash
python scripts/validate_stage4_pilot.py \
  --csv real_pilot_data/P_CONTROLLED_001/csv/P_CONTROLLED_001.csv \
  --evidence-dir real_pilot_data/P_CONTROLLED_001/photos_final/ \
  --pilot-name P_CONTROLLED_001 \
  --out validation_runs/stage4_pilots/P_CONTROLLED_001_FINAL
```

### Review validator output

The command will output:
- **Terminal verdict:** PASS / PARTIAL / NO-GO
- **Row summary:** valid, merge-ready, review-required, blocked, invalid counts
- **Evidence summary:** missing, orphaned, duplicates, invalid patterns
- **Warning profile:** verification_required, low confidence, evidence status verification warnings

### Key files created

- `validation_runs/stage4_pilots/P_CONTROLLED_001_FINAL/pilot_validation_report.json` — machine-readable
- `validation_runs/stage4_pilots/P_CONTROLLED_001_FINAL/pilot_validation_report.md` — human-readable
- `validation_runs/stage4_pilots/P_CONTROLLED_001_FINAL/evidence_audit.json` — photo linking audit

### Proceed to decision board

Open `AI_CONTROL/75_STAGE4C_CONTROLLED_PILOT_DECISION_TEMPLATE.md`.

Fill the template using:
- Validator output (row counts, match rate)
- Evidence audit results (photo coverage, missing, orphaned)
- Your field notes (document 82, if you used it)
- Your manual pole_id comparison against the Trimble baseline

---

## Stop Conditions (Go Home If...)

**Immediate stop:** Do not proceed to the next pole if:

- ❌ Camera not working (no photos possible) → safe to continue after fixing equipment
- ❌ Baseline CSV not accessible → cannot verify pole_ids; unsafe to guess
- ❌ Device storage full → must offload photos before continuing
- ❌ Personal safety concern (electrical, traffic, terrain, private property) → never risk safety
- ❌ Multiple consecutive poles marked `verification_required=yes` with unresolved reasons → stop and contact Codex for clarification

**Do not force it:** If you encounter 3+ poles in a row where pole_id cannot be confirmed, that's a signal. Contact Codex before continuing.

---

## Critical Reminders

1. **No fuzzy matching:** If the pole_id is uncertain, mark `verification_required=yes` rather than guessing. The protocol (doc 74) requires exact matching; uncertainty is handled by human review, not algorithm guessing.

2. **Evidence-first:** If a photo is unclear, take another one. If you cannot take a better photo, mark `evidence_status=obscured` or `inferred` — don't pretend the photo is clear.

3. **One pole per row:** Do not combine two poles into one row. If you capture two poles with similar pole_ids, they get separate rows.

4. **Backup early:** Offload photos to cloud/backup daily. Field data loss is unrecoverable.

5. **No real data in repo:** All captured CSVs and photos stay in `real_pilot_data/` (git-ignored). They never get committed to the repo.

6. **Use document 82:** After the pilot, use `AI_CONTROL/82_CONTROLLED_PILOT_OPERATOR_DECISION_NOTES.md` to record operator friction, unknown fields, confidence notes. These notes inform your decision board verdict.

---

## Reference

- **Doc 73:** Controlled Baseline Pilot Prep (why this pilot matters)
- **Doc 74:** Pole_ID Match Protocol (exact matching rules and thresholds)
- **Doc 75:** Controlled Pilot Decision Template (where you record your verdict)
- **Doc 81:** Photo and Evidence Rules (detailed photo guidance)
- **Doc 82:** Operator Decision Notes (for recording friction and confidence)
