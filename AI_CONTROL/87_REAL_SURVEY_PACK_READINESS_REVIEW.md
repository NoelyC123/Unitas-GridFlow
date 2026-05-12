# Real Survey Pack Readiness Review

**For: Understanding what real Trimble baseline and design-pack files support for Stage 4**

**Date:** 2026-05-12
**Purpose:** Independent readiness review of real survey files as Stage 4 baseline conversion inputs
**Authority:** Documents 73–85 (Controlled Baseline Pilot framework, exact pole_id protocol, acceptance gates)
**Scope:** Baseline file suitability, design-pack utility, field-evidence distinction, Stage 4C authorization status

---

## What This Review Covers

This review examines:
- Bellsprings raw Trimble controller CSV
- Gordon Pt1 original, PR1, PR2 CSVs
- Associated design PDFs (pole schedules, route maps, profiles, TIS documents)
- Noel's local pole_survey_2026-05-11_complete.csv (field observation summary)

**What this review does NOT do:**
- Does not commit real survey files to repo
- Does not implement baseline conversion logic
- Does not enable Stage 4C runtime code
- Does not approve Stage 4C without field evidence

---

## Real Survey Baseline Files: What They Support

### Bellsprings & Gordon Raw Controller Exports

**What they are:**
- Raw GNSS controller dumps from Trimble survey equipment
- Multiple rows per structural point (sometimes 10–50 observation records per pole location)
- Raw coordinate systems (may be Irish Grid TM65, ITM, OSGB27700, or local UTM)
- Raw point numbers (e.g., `1001`, `1002`) that may or may not match field pole labels
- Optional: voltage, equipment type, structure-type comments from surveyor notes

**What they can support:**

✅ **Baseline CSV generation:**
- Extract unique pole locations by grouping raw observations
- Apply coordinate transformation (TM65 → OSGB27700, ITM → WGS84, etc.)
- De-duplicate point numbers by aggregating multi-observation records
- Generate structured baseline: pole_id, latitude, longitude, reference_frame, optional voltage/structure_type
- Output a starter CSV for Stage 4 field-capture template

✅ **Pole identification:**
- Map raw point numbers to field pole labels (if pole label records exist in design pack)
- Cross-reference Trimble coordinates against design PDF pole locations to confirm matches
- Document pole numbering conventions (which system is authoritative: Trimble point numbers or physical labels)

✅ **Design context:**
- Route geometry (WGS84 coordinates from Trimble → compare against design PDF route geometry)
- Pole sequence (Trimble point order vs. design schedule order)
- Equipment asset list (transformer types, switch types, conductor types from notes)

**What they cannot support without field evidence:**

❌ **Pole condition assessment:**
- Raw survey does not capture pole condition (good/fair/poor/unsafe)
- Field photos + operator assessment required

❌ **Photo evidence linking:**
- Raw baseline has no photos
- Field capture required to link photos to pole_ids

❌ **Verification of pole_id match:**
- Baseline point numbers may differ from physical pole labels
- Field confirmation required (Noel walks to pole, reads label, confirms match)

❌ **Current electrical attributes:**
- Baseline voltage/equipment may be outdated (survey could be months or years old)
- Field confirmation + design handoff required

❌ **Structural condition / defect detection:**
- Raw survey cannot detect rot, cracks, corrosion, leaning, or safety hazards
- Field observation required

---

## Design PDFs: What They Support

### Pole Schedules, Route Maps, Profiles, TIS Documents

**What they are:**
- Design-pack outputs from PoleCAD or engineering office work
- Documented pole locations, coordinates, equipment assignments
- Pole labels (if different from Trimble point numbers)
- Equipment lists and electrical attributes
- Route profiles and span geometry
- Design constraints and change notes

**What they can support:**

✅ **Pole labeling authority:**
- Design PDF typically defines the authoritative pole label (P008-001, P-SPEN-042, etc.)
- Cross-reference: Trimble point number → Design pole label
- Identify which system is the source of truth

✅ **Equipment baseline:**
- Documented transformer types, voltage, switch types
- Use as reference to verify field observations match design intent

✅ **Route context:**
- Pole sequence and span distances
- Route geometry for map reference
- Access points and terrain notes

✅ **Design change history:**
- PR1, PR2 records show what changed from original design
- Understand why pole locations, equipment, or structure types changed

**What they cannot support without field evidence:**

❌ **Current field condition:**
- Design PDF is historical; does not reflect field condition today
- Field photos required to confirm current state matches design intent

❌ **Pole_id matching to physical labels:**
- Design PDF has the label; field confirmation required
- Cannot assume physical pole label exactly matches PDF (labels fade, get replaced, get removed)

❌ **Field accessibility:**
- Design PDF does not note if pole is behind fence, in muddy field, on private property
- Field reconnaissance required

❌ **Equipment on-site confirmation:**
- Design PDF says "transformer P008-001 = 11/0.433 kV, 100 kVA"
- But transformer may have been replaced, removed, or nameplate may be illegible
- Field photos required

---

## Field Evidence: What Real Survey Files Cannot Replace

### Noel's Local Survey CSV (pole_survey_2026-05-11_complete.csv)

**What it is:**
- Noel's hand-captured observations from local field survey
- Structure: pole_id, observed_type, observed_condition, observed_equipment, photo_count, notes

**What it demonstrates:**
- Field capture workflow is feasible (Noel captured ~30–50 poles)
- Template schema works in practice
- Operator can fill in observations without freezing
- Photo evidence can be organized by pole

**What it does NOT demonstrate:**
- Exact pole_id matching against a real Trimble baseline
- Pole_id match rate (no baseline comparison yet)
- How merge algorithm handles inferred vs. exact-match pole_ids
- Stage 4C runtime acceptance criteria

**Why it matters:**
- Proves field-capture workflow, not baseline-field alignment
- Next step: compare Noel's local CSV against Bellsprings/Gordon baseline
- If they can be matched with ≥80% exact pole_id accuracy → valuable dataset for baseline-field integration
- If match rate is <75% → indicates pole_id system mismatch between baseline and field

---

## Recommended Classification

### Baseline Conversion Evidence ✅

**Suitable for:**
- Extracting a starter CSV from raw Trimble baseline
- Generating baseline CSV with poles, coordinates, reference_frame
- Mapping point numbers to design pole labels
- Building a reference set of 30–50 poles for controlled pilot

**Bellsprings baseline readiness:**
- ✅ Raw Trimble controller export available
- ✅ Multiple observation records per pole (typical; requires de-duplication)
- ✅ Coordinate system present (TM65 or ITM; transformation required)
- ✅ Design PDF available for pole-label cross-reference
- ✅ Can support 30–50 pole controlled pilot

**Gordon baseline readiness:**
- ✅ Multiple CSVs (original, PR1, PR2) provide change history
- ✅ Demonstrates how to handle design changes over time
- ✅ Can support baseline-variant comparison
- ✅ Suitable for lesson-learning about design evolution

---

### Field-Photo Evidence ❌

**NOT suitable for:**
- Bellsprings/Gordon raw CSVs do not contain photos
- Design PDFs do not contain photos
- Noel's local survey CSV notes photo_count but provides no actual photos

**To support field evidence:**
- Noel must capture photos on-site (context, ID/nameplate, equipment, base)
- Photos named by pole_id and evidence_type
- Photos organized into folder structure (clear/, obscured/, proxy/, inferred/, none/)
- Validator must confirm ≥90% evidence linking (all poles have photos)

---

### Automatic Stage 4C Approval ❌

**These files alone do NOT authorize Stage 4C runtime integration.**

Why:
- Baseline CSV alone proves only that surveyor data exists
- Field CSV alone proves only that field capture workflow exists
- Baseline + field CSV alone does NOT prove exact pole_id matching works
- No validator pass/PARTIAL decision
- No signed decision template verdict
- No independent gate auditor confirmation

**What IS required for Stage 4C approval:**
1. Baseline CSV (Bellsprings or equivalent) ready for Noel to capture against
2. Noel captures 30–50 poles with field photos against baseline
3. Validator runs on captured CSV + evidence folder
4. Match rate ≥80% (GO) or 75–80% (CONDITIONAL GO) on exact pole_ids
5. Valid rows ≥90%, merge-ready rows ≥50%, evidence coverage ≥90%
6. Noel fills operator decision notes (friction, unknowns, confidence)
7. Noel signs decision template (GO / CONDITIONAL GO / NO-GO)
8. Independent gate auditor reviews and confirms verdict
9. THEN Stage 4C implementation task is authorized

---

## Risks and Mitigation

### Risk 1: Raw File Schema Variation

**Risk:** Bellsprings, Gordon, other survey jobs may have different raw CSV formats (different column names, different point-number systems, different coordinate systems)

**Impact:** Baseline extraction logic must be flexible; cannot hard-code column positions

**Mitigation:**
- Document expected column names for each baseline source
- Build baseline extractor with configurable column mapping
- Validate extracted starter CSV schema before proceeding
- Document any schema deviations in extraction notes

---

### Risk 2: Coordinate System Ambiguity

**Risk:** Raw survey may be in TM65, ITM, UTM, or other CRS; design PDF may use different CRS; field GPS (WGS84) may differ

**Impact:** Pole locations may not align; hard to match baseline pole to field observation

**Mitigation:**
- Document source CRS for each baseline (ask surveyor or infer from coordinates)
- Implement coordinate transformation (proj4 library or similar)
- Store source CRS in baseline CSV metadata
- Require manual verification of 5–10 pole locations after transformation
- Design PDF comparison to confirm transformation is correct

---

### Risk 3: Confusing Survey Baseline with Live Field Condition

**Risk:** Bellsprings baseline is from survey date (unknown; possibly months old); current field condition may have changed (equipment replaced, pole damaged, structure dismantled)

**Impact:** Field observation conflicts with baseline; confusion about what "baseline" means

**Mitigation:**
- Clearly label baseline CSV with survey date
- Document in decision template if field condition does not match baseline (e.g., "3 poles marked unsafe; not in baseline")
- Use baseline as *reference*, not as *ground truth*
- Field evidence takes precedence for current condition

---

### Risk 4: Overfilling Engineering Fields from Baseline

**Risk:** Baseline CSV contains voltage/equipment; temptation to pre-fill these in starter template

**Impact:** Operator may not verify field; creates false confidence in outdated attributes

**Mitigation:**
- Leave optional fields (voltage, equipment) blank in starter template
- Require operator to fill these from field observation
- Document in field-pack: "Do not copy baseline voltage; verify on-site"
- Mark baseline attributes as reference-only in design handoff

---

### Risk 5: Committing Sensitive Data

**Risk:** Real survey files contain property information, structure locations, equipment details from live DNO network

**Impact:** Sensitive DNO/utility data exposed in public repo

**Mitigation:**
- **Never commit real survey CSVs, PDFs, or photos to repo**
- Keep real_pilot_data/, uploads/, validation_runs/ in .gitignore
- Use anonymized/subset fixtures for tests (P_REAL_001_MINI, pilot samples)
- Document that real baseline conversion happens locally only
- Control file records (AI_CONTROL docs) document suitability and lessons; do not contain real data

---

## Recommended Controls

### Before Baseline Conversion

1. ✅ **Confirm baseline source:** Bellsprings CSV exists, is readable, has expected schema
2. ✅ **Identify survey date:** When was this baseline captured? (Affects interpretation of field observations)
3. ✅ **Identify CRS:** What coordinate system? (Affects transformation logic)
4. ✅ **Classify sensitivity:** Is this data sensitive/proprietary? (Affects handling rules)
5. ✅ **Design PDF review:** Does design PDF match baseline location/labeling? (Informs pole-label mapping)

### During Baseline Conversion

1. ✅ **Document extraction logic:** Which columns map to pole_id, lat, lon, voltage, type? (Enables repeatability)
2. ✅ **Validate de-duplication:** If multiple observations per pole, confirm merge logic (Prevents duplicates)
3. ✅ **Verify transformation:** After CRS conversion, spot-check 5–10 poles against design PDF (Confirms coordinates)
4. ✅ **Record metadata:** Survey date, source CRS, extraction notes in starter CSV header
5. ✅ **Generate extraction report:** List unique poles, any dropped/merged observations, quality flags

### Before Field Capture

1. ✅ **Baseline CSV review:** Inspect starter CSV for schema, row count, any blanks (Prevents surprises in field)
2. ✅ **Design PDF cross-reference:** Confirm baseline pole_ids match design labels (Clarifies naming authority)
3. ✅ **Field accessibility assessment:** Can Noel safely access all poles? (Identifies fallback options)
4. ✅ **Noel pre-brief:** Explain baseline source, CRS transformation, pole-label matching rules (Enables confident field work)
5. ✅ **Test capture:** Noel captures 1–2 poles as dry-run before full pilot (Validates workflow)

### After Field Capture

1. ✅ **Validator run:** Official validation pass/PARTIAL/NO-GO verdict (Informs decision)
2. ✅ **Pole_id matching:** Manual comparison of captured vs. baseline pole_ids (Calculates match rate)
3. ✅ **Decision template:** Noel documents verdict (GO / CONDITIONAL GO / NO-GO) (Gates Stage 4C)
4. ✅ **Gate auditor review:** Independent confirmation of verdict (Adds governance rigor)
5. ✅ **Real data purge:** After decision recorded, delete real_pilot_data/, validation_runs/, uploads/ locally (Protects sensitive data)

---

## Classification Summary

| Item | Classification | Supports | Does NOT Support |
|------|---|---|---|
| Bellsprings raw CSV | Baseline conversion evidence | Starter CSV generation, pole-label mapping | Field photo evidence, current condition, Stage 4C approval |
| Gordon original/PR1/PR2 | Baseline conversion evidence + change history | Design evolution, multi-version baseline | Field photo evidence, Stage 4C approval |
| Design PDFs (schedule, route, profile) | Reference/validation only | Pole-label authority, equipment baseline, design intent | Field photo evidence, current condition, Stage 4C approval |
| Noel's local field CSV | Field-capture workflow proof | Demonstrates field capture is feasible, schema works | Baseline-field matching without baseline CSV, Stage 4C approval |
| Controlled pilot (baseline + field) | Full Stage 4C evidence | Everything: baseline, field photos, exact matching, validator pass, signed verdict | Anything less than full triple-evidence combination |

---

## Conclusion

**Real survey files (Bellsprings, Gordon baseline + design pack) are valuable for:**
- Demonstrating baseline extraction workflow
- Testing coordinate transformation logic
- Understanding pole-labeling conventions
- Planning controlled baseline pilot

**They are NOT sufficient alone for Stage 4C authorization.**

**What IS required:**
- Baseline CSV + field evidence from same accessible job
- Exact pole_id matching (≥80%)
- Validator pass/PARTIAL with accepted thresholds
- Noel's signed decision template (GO or CONDITIONAL GO)
- Independent gate auditor confirmation

**Next steps:**
- Codex: Baseline conversion from real survey files
- Noel: Field evidence from local survey
- Combined: Baseline-field matching analysis
- Result: Decision memo (doc 88) recommending next pilot sequence

---

## Reference

- **Doc 73:** Controlled Baseline Pilot Prep (why baseline pilot matters)
- **Doc 74:** Pole_ID Match Protocol (exact matching rules and thresholds)
- **Doc 75:** Controlled Pilot Decision Template (verdict recording mechanism)
- **Doc 80:** Controlled Pilot Field Pack (field-day procedure)
- **Doc 82:** Operator Decision Notes (post-field assessment)
- **Doc 83:** P_CONTROLLED_001 Readiness Gate (baseline readiness verdict)
- **Doc 85:** P_CONTROLLED_001 Post-Field Acceptance Gate (GO/NO-GO criteria)
