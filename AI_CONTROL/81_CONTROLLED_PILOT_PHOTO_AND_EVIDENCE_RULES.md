# Controlled Pilot Photo and Evidence Rules

**For: Noel's field capture of 30–50 poles against real Trimble baseline**

**Date:** 2026-05-11
**Purpose:** Detailed photo requirements and evidence linking protocol
**Authority:** Document 73–75 (Pilot Prep, Match Protocol, Decision Template)
**Scope:** Photo capture, naming, organization, and evidence audit

---

## Photo Requirements Per Pole

Every captured pole needs **at least 1 photo**. More photos are better if they show different aspects.

### Photo 1: Context Shot (REQUIRED)

**What to show:**
- Full pole in frame
- Surrounding context: terrain, other structures, distance to building/road
- Scale reference if pole is far from camera (e.g., person standing next to it)
- Sky visible at top and ground visible at base (full height in frame)

**Why:**
- Validator checks that you can see the entire pole structure
- Helps auditor verify you're at the correct location
- Documents access and safety context

**Naming:**
```
<pole_id>_clear_01.jpg
```

**Example:**
- `P008-001_clear_01.jpg` — 20-meter wide shot showing pole, surrounding grass, distant treeline

---

### Photo 2: ID / Nameplate (CONDITIONAL)

**Required IF:** The pole has a visible ID tag, nameplate, or marking

**What to show:**
- Close-up of the ID/nameplate/marking
- Lighting clear enough to read the pole_id
- Surrounding pole surface visible (to confirm it's on the correct pole)

**Why:**
- Confirms pole_id by visual inspection
- Auditor can verify Trimble baseline matches physical pole

**Naming:**
```
<pole_id>_id_01.jpg
```

**Example:**
- `P008-001_id_01.jpg` — close-up of white nameplate showing "P008-001"

**If pole has NO visible marking:**
- Do NOT take this photo
- Mark `evidence_status=inferred` in the template
- Document in notes: "Pole label not visible; ID inferred from location"

---

### Photo 3: Top/Equipment (CONDITIONAL)

**Required IF:** You can safely see the top of the pole or equipment attached

**What to show:**
- Transformer (if present) — visible from safe distance
- Crossarm configuration
- Conductor position (if visible and safe)
- Pole top or insulator assembly
- Lightning rod or grounding hardware

**Why:**
- Documents equipment type and configuration
- Helps designer understand pole loading
- Useful for later asset/cable interaction work

**Naming:**
```
<pole_id>_equipment_01.jpg
```

**Example:**
- `P008-001_equipment_01.jpg` — photo of transformer mounted on pole

**Safety rule:**
- ❌ Do NOT climb the pole
- ❌ Do NOT use drone to get this photo (outside scope of field capture)
- ✅ Take photo from safe ground distance
- ✅ If you cannot see the top safely, skip this photo and mark `evidence_status=obscured`

---

### Photo 4: Base/Defects/Access (CONDITIONAL)

**Required IF:** Pole base is visible and accessible

**What to show:**
- Pole base condition (cracks, rot, concrete, metal, wood detail)
- Any visible defects or damage
- Soil/ground condition around pole
- Access difficulty (buried, accessible, blocked by vegetation)
- guy/stay attachments at base

**Why:**
- Documents structural condition for asset inventory
- Identifies access challenges for future work
- Informs design decisions around foundation/loading

**Naming:**
```
<pole_id>_base_01.jpg
```

**Example:**
- `P008-001_base_01.jpg` — photo of wooden pole base showing minor rot and concrete footing
- `P008-001_stays_01.jpg` — photo of stay wires attached to pole base

**If base is inaccessible (buried, fenced, private):**
- Take a wide shot showing the inaccessible base
- Mark `evidence_status=obscured` in template
- Document in notes: "Base obscured by fence"

---

## Handling Special Situations

### Vegetation-Blocked Poles

**If vegetation obscures the pole:**

1. Take a photo showing the pole behind vegetation
2. Name it: `<pole_id>_obscured_01.jpg`
3. In the template, set `evidence_status=obscured`
4. In notes, document: "Dense vegetation blocks view; pole_id inferred from location"
5. Mark `verification_required=yes` if pole_id cannot be confirmed

**Validator will:**
- Flag the row as non-ideal but acceptable
- Require manual review before merge-ready classification
- Not treat this as a blocker (vegetation is environmental, not a data quality issue)

### Poles Where pole_id Is Not Visible

**If the pole has no visible label/nameplate:**

1. Take a context photo showing the pole and surrounding location
2. Use the Trimble baseline pole_id from the location map
3. Name photos as: `<baseline_pole_id>_clear_01.jpg` (use baseline ID)
4. In the template, set `evidence_status=inferred`
5. Mark `verification_required=yes` (you inferred the ID, not confirmed it visually)
6. In notes, document: "Pole label not visible; ID confirmed against Trimble baseline location"

**Validator will:**
- Classify row as review-required (not merge-ready) until manual auditor confirms
- NOT flag as a blocker; inferred IDs are acceptable with verification flag

### Unknown pole_id (Complete Uncertainty)

**If you CANNOT match the pole to the baseline (no ID visible, wrong location, etc.):**

1. Take photos anyway (context, detail)
2. Do NOT invent a pole_id
3. Use placeholder: `UNKNOWN_<sequence>` (e.g., `UNKNOWN_01`)
4. Set `evidence_status=none` (you have no way to link this to the baseline)
5. Mark `verification_required=yes` (required manual resolution)
6. In notes, document exactly why pole_id cannot be determined

**Example:**
```
pole_id: UNKNOWN_07
evidence_status: none
verification_required: yes
notes: "Pole not found at expected Trimble location. Possible baseline error or capture location error. Coordinates: [lat/long from device]. Recommend re-check baseline before decision."
```

**Impact:**
- Row will be flagged as BLOCKED (cannot merge without pole_id)
- Does not fail the pilot; indicates a specific baseline/capture mismatch that needs investigation
- In decision template, you document this as a mismatch and explain root cause

---

## Photo Naming Protocol

**Standard format (REQUIRED):**
```
<pole_id>_<evidence_type>_<sequence>.jpg
```

**Parts:**

| Part | Rule | Examples |
|------|------|----------|
| `<pole_id>` | Exact match from baseline CSV or pole label | P008-001, P-SPEN-042, P010.005 |
| `<evidence_type>` | clear, obscured, proxy, inferred, id, equipment, base, stays, or none | clear, equipment, inferred |
| `<sequence>` | 01, 02, 03... (order captured) | 01 (first photo of P008-001), 02 (second photo) |
| `.jpg` | File extension (see next section) | .jpg |

**Valid examples:**
- `P008-001_clear_01.jpg` ✅
- `P008-001_id_01.jpg` ✅
- `P008-001_equipment_02.jpg` ✅
- `P008-001_obscured_01.jpg` ✅
- `P-SPEN-042_base_01.jpg` ✅
- `UNKNOWN_07_clear_01.jpg` ✅ (if pole_id unknown)

**Invalid examples:**
- `P008-001.jpg` ❌ (missing evidence_type and sequence)
- `pole_001_clear.jpg` ❌ (pole_id doesn't match baseline)
- `P008-001_clear_1.jpg` ❌ (sequence should be 01, not 1)
- `P008-001_clearphoto_01.jpg` ❌ (evidence_type is "clear" not "clearphoto")
- `P008-001_clear_01.png` ⚠️ (PNG instead of JPG; see next section)

---

## File Format Handling

### JPG (Recommended)

**Use JPG for all photos unless you have a specific reason not to.**

- Smaller file size (easier to backup)
- Universal compatibility
- Standard for field photography
- Validator expects .jpg

**On iPhone/iPad:**
- Default camera output is HEIC (proprietary Apple format)
- Before exporting, convert to JPG in Photos app
- Or use a third-party camera app that outputs JPG directly (Halide, Moment)

### HEIC (Apple Native)

**If camera captures as HEIC:**
1. **Do NOT upload as-is.** Validator does not recognize HEIC.
2. Convert to JPG before organizing into evidence folder:
   - On iPad: Photos app → Edit → Share → Save as JPG
   - On Mac: Preview → Tools → Convert to JPG
3. Rename converted file to follow naming protocol: `P008-001_clear_01.jpg`
4. Verify JPG is in evidence folder before next pole

### PNG (Acceptable if Needed)

**Use PNG only if:**
- You need lossless compression (rare in field photography)
- You captured a screenshot or technical diagram

**If you use PNG:**
- Follow naming protocol: `<pole_id>_clear_01.png`
- Validator will accept .png and .jpg equally
- But keep file size small (convert from full-res if possible)

### NO video

- ❌ Do not capture video
- ❌ Validator does not support video files
- ✅ Capture multiple still images instead

---

## Avoiding Orphan and Unreferenced Photos

**Orphan photo:** Photo exists but no corresponding row in template
- **Example:** `P008-001_clear_01.jpg` exists, but pole P008-001 not in captured CSV
- **Cause:** Forgot to fill the template row, or deleted the row later
- **Impact:** Validator flags as untracked; makes it unclear if this is intentional

**Unreferenced photo:** Template row exists but photos named incorrectly
- **Example:** Template has row for P008-001, but photos are named `pole8_clear_01.jpg` (pole_id mismatch)
- **Cause:** Naming protocol not followed
- **Impact:** Validator cannot link the photo to the pole; row marked as missing evidence

**Prevention checklist:**

1. **Always fill template BEFORE taking photos**
   - Write pole_id to template first
   - Then take photos with that pole_id in filename
   - This prevents mismatches

2. **Match filenames exactly to template**
   - If template has `P008-001`, photos must be `P008-001_*.jpg`
   - ❌ Do NOT use `p008-001`, `P008_001`, or `P008.001` variations
   - ✅ Copy-paste the pole_id from template to filename to ensure exact match

3. **Check file organization before moving on**
   - For each pole you capture, verify photos exist in evidence folder
   - Count: photos in folder should equal or exceed number of template rows
   - Look for obvious mismatches (photo names vs. pole_ids in template)

4. **Use validator as final check**
   - Validator output explicitly lists missing/orphaned/duplicate photos
   - Review validator report before proceeding to decision template
   - Fix any mismatches before finalizing results

---

## Evidence Acceptance Checklist

Before marking the pilot as ready for decision template:

- [ ] All poles have at least 1 photo
- [ ] All photo filenames start with a pole_id that exists in the template
- [ ] All pole_ids in template have corresponding photos (no blank evidence_status rows)
- [ ] All photos are named with sequence number (01, 02, etc., not just 1, 2)
- [ ] All photos use .jpg extension (or .png if intentional; no .HEIC or .webp)
- [ ] Photos are organized in evidence subdirectories (clear/, obscured/, proxy/, inferred/, none/)
- [ ] No duplicate filenames (no two files with exact same name)
- [ ] At least 1 context photo per pole (full pole in frame, surrounding visible)
- [ ] Photos with pole_id visible or inferred are appropriately flagged in template
- [ ] Notes in template explain any uncertain or inferred IDs
- [ ] Validator output shows ≥90% evidence reference coverage

---

## Privacy and Safety Notes

### Private Property

**If a pole is on private land:**
- Do NOT trespass
- If accessible from public road, take photos from road/property line
- Mark in notes: "Photographed from public road; private property boundary"
- Do NOT skip the pole; document what you could safely capture

### Electrical Safety

- Do NOT climb poles
- Do NOT touch wires or equipment
- Maintain safe distance from overhead lines (at least 3 meters / 10 feet)
- If you feel unsafe, move away and note: "Safety hazard; did not approach"

### Privacy of Surroundings

- Avoid capturing houses, buildings, or people unless absolutely necessary for pole context
- Blur any visible addresses or identifying information in photos (optional but courteous)
- Focus lens on the pole, not surrounding properties

### Drone Photography

- ❌ Do NOT use drones for pole capture (outside scope of field pilot)
- Drones introduce regulatory/safety complexity
- Ground-based photography is sufficient for this pilot

---

## Final Check Before Validation

After field capture, before running the validator:

1. **Photo count:** `find photos_final -name '*.jpg' | wc -l` — should be ≥ number of poles
2. **Filename patterns:** `find photos_final -type f ! -name '*_*_*.jpg'` — should return nothing (all files follow protocol)
3. **Duplicate names:** `find photos_final -type f | sort | uniq -d` — should return nothing
4. **Missing folders:** `ls photos_final/` — should show clear/, obscured/, proxy/, inferred/, none/
5. **CSV row count:** `wc -l < csv/P_CONTROLLED_001.csv` — should be ≥ 30 and ≤ 200 (plus 1 header row)

**If anything fails:**
- Fix it before running validator
- Validator cannot fix naming or organizational issues; it can only report them

---

## Reference

- **Doc 73:** Controlled Baseline Pilot Prep (overall pilot workflow)
- **Doc 80:** Controlled Pilot Field Pack (simple field-day procedure)
- **Doc 82:** Operator Decision Notes (for recording friction and notes)
