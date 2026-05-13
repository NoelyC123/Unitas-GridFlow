# Stage 4B Manual Review Workflow

## Purpose

Guide manual review of automated match confidence scores to validate baseline-to-field correlation accuracy.

This workflow reviews identity correlation and evidence sufficiency. It does not approve engineering design values or remove DNO verification requirements.

## Prerequisites

- ✅ `baseline_field_match_register.csv` generated (automated scoring complete)
- ✅ `pole_summary.csv` available (reference data)
- ✅ `enwl_enrichment_clean/` dataset validated (100% compliance)

## Review Scope

**Total poles to review:** 10

**Expected time:** 30-60 minutes (3-6 min per pole)

## Review Process

### For Each Pole:

#### 1. Open Evidence Files

Navigate to pole folder:

```text
real_pilot_data/P_LOCAL_001/enwl_enrichment_clean/NN_SUPPORT_XXXXXX_*/
```

Review:

- `field_photos/` — All photos (typically 3-11 per pole)
- `map_screenshots/` — Map popup screenshots (1-7 per pole)
- `notes/identity_notes.txt` — Surveyor observations

#### 2. Verify Identity Match

Check if field evidence matches baseline:

**Support Number Verification:**

- [ ] Map popup shows support number clearly
- [ ] Support number matches folder name
- [ ] No conflicting support numbers visible

**Location Verification:**

- [ ] Map marker location matches field photo context
- [ ] Street/landmark context consistent
- [ ] No evidence this is wrong pole

**Result:** `identity_verified` → yes / no / uncertain

#### 3. Assess Photo Coverage

Check field photo quality:

**Pole Top Coverage:**

- [ ] Crossarms visible (if present)
- [ ] Insulators visible
- [ ] Conductor attachment points visible
- [ ] Equipment mountings visible

**Result:** `top_visible` → yes / partial / no

**Pole Base Coverage:**

- [ ] Ground level visible
- [ ] Base condition assessable
- [ ] Stay anchor visible (if applicable)
- [ ] Foundation/soil visible

**Result:** `base_visible` → yes / partial / no

#### 4. Equipment Verification

Check equipment consistency:

**Warning Signs:**

- [ ] Warning sign visible in photos
- [ ] Voltage indication readable (if present)
- [ ] DNO markings visible

**Result:** `warning_sign_visible` → yes / no / unclear

**Equipment Match:**

Compare field photos vs map popup/folder name:

- Transformer presence matches description
- Streetlight matches description
- HV/LV designation consistent
- Joint-user equipment matches

**Result:** `equipment_match` → yes / partial / no / unknown

#### 5. Score Match Confidence

Based on evidence reviewed, assign final confidence:

**HIGH Confidence Criteria:**

- ✅ Support number verified from map popup
- ✅ Location clearly matches field context
- ✅ Equipment configuration consistent
- ✅ No conflicting evidence
- ✅ Photos cover top, base, and equipment

**MEDIUM Confidence Criteria:**

- ⚠️ Support number likely correct but minor uncertainties
- ⚠️ Location matches but some ambiguity
- ⚠️ Equipment partially consistent
- ⚠️ Photo coverage has gaps

**LOW Confidence Criteria:**

- ❌ Support number unclear or conflicting
- ❌ Location match uncertain
- ❌ Equipment inconsistent with description
- ❌ Insufficient photo evidence

**Result:** Confirm or update `match_confidence` → HIGH / MEDIUM / LOW

#### 6. Flag Review Requirements

Determine if additional verification needed:

**Review Required = YES if:**

- Match confidence = MEDIUM or LOW
- Identity verification = uncertain
- Equipment match = partial or unknown
- Conflicting evidence between sources
- Photo coverage insufficient for design

**Review Required = NO if:**

- Match confidence = HIGH
- All verifications = yes
- No conflicting evidence
- Photo coverage complete

**Result:** Confirm or update `review_required` → yes / no

## Review Recording

### Update Match Register

After reviewing each pole, update `baseline_field_match_register.csv`:

**Before:**

```csv
903203,01_SUPPORT_903203_LV_TERMINAL_STREETLIGHT,5,5,yes,HIGH,,,,,,,yes,no
```

**After manual review:**

```csv
903203,01_SUPPORT_903203_LV_TERMINAL_STREETLIGHT,5,5,yes,HIGH,yes,yes,yes,yes,yes,yes,no
```

### Use Review Script (Optional)

If `scripts/score_match_confidence.py` is available:

```bash
python scripts/score_match_confidence.py
```

### Manual CSV Editing (Alternative)

Open in Excel/Numbers/VS Code and fill columns 7-13 for each pole.

## Review Completion Checklist

After reviewing all 10 poles:

- [ ] All `identity_verified` fields completed
- [ ] All `top_visible` fields completed
- [ ] All `base_visible` fields completed
- [ ] All `warning_sign_visible` fields completed
- [ ] All `equipment_match` fields completed
- [ ] All `match_confidence` scores reviewed/updated
- [ ] All `review_required` flags set appropriately
- [ ] `baseline_field_match_register.csv` saved

## Uncertainty and Limitations

- Manual review confirms whether the baseline asset and field folder appear to describe the same support.
- Manual review does not certify voltage, conductor size, pole class, transformer rating, load, or compliance status.
- If field photos are obstructed, distant, backlit, or access-constrained, record the limitation instead of forcing a high-confidence conclusion.
- If a support number is missing or contradictory, keep the row in manual review until the conflict is resolved.
- Future datasets with underground transitions, multi-circuit assets, EHV equipment, or sparse photos may require longer review than P_LOCAL_001.

## Quality Check

Before proceeding to match rate calculation:

**Verify:**

- No blank cells in columns 7-13 (all manual review fields completed)
- Match confidence distribution reasonable (expect mostly HIGH for good dataset)
- Review required flags consistent with confidence scores
- Support numbers unique (no duplicates)

**If quality check passes:** Proceed to match rate calculation

**If issues found:** Re-review flagged poles

## Next Step

After manual review complete → Run match rate calculator:

```bash
python scripts/calculate_match_rate.py
```

This generates Stage 4B match rate analysis and verdict recommendation.

## Note for P_LOCAL_001

Since all 10 poles received automated HIGH identity-match confidence scores with 0 requiring manual review, detailed manual review requirements were low for P_LOCAL_001 specifically. However, the workflow remains required guidance for future datasets with lower automated confidence scores, different evidence structures, or unresolved uncertainty.
