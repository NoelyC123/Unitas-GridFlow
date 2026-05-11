# Stage 4C Baseline Pole_ID Match Protocol

**Date:** 2026-05-11
**Purpose:** Define exact pole_id matching rules for the controlled baseline pilot and Stage 4C runtime merge
**Authority:** Document 50 (Go/No-Go Gate, criterion G4)
**Scope:** Validation-phase matching only (runtime merge algorithm is in document 56)

---

## Principle: No Fuzzy Matching

**Rule:** pole_id matching is **EXACT MATCH ONLY** across the controlled pilot and all Stage 4C runtime operations.

**Rationale:**
- Fuzzy matching introduces silent merge errors (wrong pole matched, attributes corrupted)
- Real survey uncertainty should be handled by human review (`verification_required=yes`), not algorithm guessing
- Exact match enforces upstream data quality (Trimble IDs must be captured correctly)

**Exception:** Pre-merge normalisation ONLY (whitespace, case, dash formatting) IF and ONLY IF those rules are already approved by document 57 (boundary rules).

---

## Normalisation Rules

Before comparing pole_ids, apply these transformations to BOTH captured and Trimble pole_ids:

### Whitespace normalization

- **Rule:** Strip leading/trailing whitespace
- **Example:** `"  P008-001  "` → `"P008-001"`
- **Not allowed:** Collapsing internal whitespace (e.g., `"P008 001"` is NOT normalized to `"P008001"`)

### Case normalization

- **Rule:** Convert to uppercase
- **Example:** `"p008-001"` → `"P008-001"`
- **Rationale:** Trimble case sensitivity varies by region/equipment; uppercase is standard UK convention
- **Not allowed:** Accepting mixed case as a "close enough" match

### Dash/hyphen normalization (if approved in document 57)

- **Rule:** If document 57 approves it, standardize dash style (e.g., hyphens only, no underscores)
- **Example (if approved):** `"P008_001"` → `"P008-001"`
- **Important:** This rule MUST be in document 57 before applied in production
- **Current status:** PENDING APPROVAL (do not apply yet in controlled pilot)

---

## Matching Algorithm

### Step 1: Prepare the comparison set

```
Captured pole_ids = [from <PILOT_ID>.csv, after normalisation]
Trimble pole_ids = [from baseline CSV, after normalisation]
```

### Step 2: For each captured pole_id, attempt exact match

```
captured_id = "P008-001" (after normalisation)
trimble_ids = ["P008-001", "P008-002", "P008-003", ...]

IF captured_id in trimble_ids:
  result = "MATCH"
  trimble_match = captured_id
ELSE:
  result = "NO MATCH"
  trimble_match = null
```

### Step 3: Record match result

| Captured pole_id | Trimble match | Status | Reason |
|---|---|---|---|
| P008-001 | P008-001 | ✅ MATCH | Exact after normalisation |
| P008-005 | (none) | ❌ NO MATCH | Not in Trimble baseline |
| P008-010 | (none) | ❌ NO MATCH | Typo: captured as "P008-1" (missing leading zero?) |
| P008-NEW | (none) | ❌ NO MATCH | New pole not in original Trimble |

### Step 4: Calculate match rate

```
match_rate = (count of MATCH) / (total captured poles)
example: 28 matches / 30 captured = 93.3% match rate
```

---

## Decision Thresholds for Controlled Pilot

### Match rate GO threshold

| Rate | Verdict |
|---|---|
| ≥80% | ✅ GO condition met (document 50, G4) |
| 75–80% | ⚠️ CONDITIONAL GO (lower but acceptable if mismatches are explained) |
| <75% | ❌ NO-GO (requires root-cause analysis before re-pilot) |

### Mismatch categorization (for root-cause analysis)

For every NO MATCH, record the reason:

1. **New pole** — "Not in original Trimble; confirmed on-site as new construction"
   - **Assessment:** Acceptable. Stage 4C merge will add new pole to database.
2. **Trimble missing** — "Confirmed on-site; not in Trimble CSV (data entry omission?)"
   - **Assessment:** Acceptable. Indicates Trimble data incomplete; Stage 4 provides correction.
3. **Format mismatch** — "Captured as 'P008-001'; Trimble has 'P008.001' or 'P008/001'"
   - **Assessment:** Requires investigation. Is normalisation rule missing? Should it be applied?
4. **Typo by surveyor** — "Captured as 'P008-1'; Trimble has 'P008-01' (leading zero)"
   - **Assessment:** Capture technique issue. Better pole_id labeling or double-checking needed on next pilot.
5. **Ambiguous/uncertain** — "Pole label obscured; captured best guess; uncertain if correct"
   - **Assessment:** Mark with `verification_required=yes`. Document the uncertainty. Do not force match.

**Important:** If >20% of your mismatches are "Typo by surveyor" or "Ambiguous/uncertain," the capture technique needs improvement before proceeding to Stage 4C.

---

## Duplicate Pole_ID Handling

### Rule: No duplicates allowed in captured CSV

**Validation check:**
```
IF count(pole_id = "P008-001") > 1:
  RESULT = ERROR: Duplicate pole_id
  VERDICT = BLOCKED (cannot merge)
```

### Why duplicates are forbidden

- Merge algorithm (doc 56) requires unique pole_id as primary key
- Duplicate pole_ids create ambiguity: which row gets merged to Trimble record?
- No runtime recovery: once duplicates are in the database, manual cleanup is required

### If duplicates are detected during validation

1. **Immediate action:** Do NOT attempt merge; validator will reject
2. **Root cause:** Pole captured twice? Data entry error? Duplicate in Trimble baseline?
3. **Remediation:**
   - If duplicate in Trimble: contact baseline owner; clarify pole identity
   - If duplicate in capture: delete the erroneous row; recapture if needed
4. **Retry:** Re-run validator after removing duplicates

### Duplicate count in controlled pilot

- **Target:** 0 duplicates
- **Actual duplicate threshold:** Any duplicate = NO-GO (must be resolved before merge)

---

## Missing Pole_ID Handling

### Rule: All rows must have a pole_id

**Validation check:**
```
IF pole_id is null or empty string:
  RESULT = ERROR: Missing pole_id
  SEVERITY = BLOCKING (cannot merge)
```

### Why missing pole_ids are forbidden

- pole_id is the merge key; without it, merge location is undefined
- Impossible to determine which Trimble pole to update

### If missing pole_ids are detected

1. **During capture:** Always fill pole_id before moving to next pole
2. **If discovered during validation:** Go back to on-site notes; determine pole_id; recapture row if needed
3. **If pole_id is genuinely unknown:** Record as `verification_required=yes` and `pole_id = "UNKNOWN_<sequence>"` (temporary placeholder)
   - This will fail pole_id match validation
   - Next phase (Stage 4D) must provide a mechanism to resolve unknowns
   - For now, this is NOT acceptable for production merge

---

## Unmatched Stage 4 Row Handling

### Definition: Captured row with pole_id that has no Trimble baseline

**Example:**
```
Captured: pole_id = "P008-NEW", voltage = "11kV", ...
Trimble baseline: pole_ids = [P008-001, P008-002, ..., P008-030]
Result: P008-NEW is NOT in Trimble
```

### Merge behavior (Stage 4C runtime, doc 56)

- **No-overwrite invariant:** Unmatched rows are NOT added to live database
- **Handling:** Unmatched rows are flagged and reported to operator
- **Decision:** Operator decides: is this a new pole? Or a capture error?

### In controlled pilot

- **Acceptable count:** Up to 5 unmatched rows (new poles or baseline gaps)
- **Investigate:** Each unmatched row must have a documented reason
- **Decision:** Noel must confirm: Is this a real new pole? Or a mismatch issue?

---

## Unmatched Trimble Pole Handling

### Definition: Trimble baseline pole with no corresponding captured Stage 4 row

**Example:**
```
Trimble baseline: pole_id = "P008-025"
Captured rows: 30 rows, pole_ids = [P008-001 to P008-024, P008-026 to P008-031]
Result: P008-025 was NOT captured
```

### No merge issue (intentional)

- Unmatched Trimble poles are left as-is in the database
- Stage 4 data is additive only; non-captured poles are unaffected
- This is **expected and correct behavior**

### In controlled pilot

- **Expected:** Some Trimble poles will not be captured (sampling, access constraints, etc.)
- **No penalty:** This does NOT affect merge readiness or match rate calculation
- **Note:** Match rate is calculated as: (captured poles matched) / (total captured poles)
  - NOT as: (matched poles) / (all Trimble poles)

---

## Merge Simulation Requirements (For Noel)

Before signing GO on the decision board, simulate what happens if we merge:

### Simulation steps

1. **Take 3 matched captured rows** — e.g., P008-001, P008-005, P008-010
2. **Find their Trimble records** — Extract the corresponding Trimble rows
3. **Imagine merge:** What new Stage 4 fields would be added to each Trimble record?
4. **Verify no corruption:** Would any existing Trimble fields be overwritten? (Answer: NO, by design)
5. **Check evidence:** Are the Stage 4 photos correctly linked?

### Expected outcome

"If we merged these 3 rows, the Trimble records would gain Stage 4 attributes (voltage, condition, stays, etc.) without losing any Trimble data. No corruption. Evidence photos would be correctly referenced."

### If simulation reveals issues

- Do not sign GO
- Document the issue
- Sign NO-GO or CONDITIONAL GO instead

---

## Append-Only Merge Principle

**Rule:** Stage 4C merge is APPEND-ONLY. No existing Trimble fields are modified.

### What this means

- ✅ Allowed: Add new Stage 4 fields (e.g., `voltage`, `condition`)
- ✅ Allowed: Add evidence photo references
- ✅ Allowed: Set `source: "structured_capture"` on new fields
- ❌ NOT allowed: Overwrite existing Trimble data (e.g., `pole_type`, `coordinates`)
- ❌ NOT allowed: Delete existing fields
- ❌ NOT allowed: Modify Trimble records that have no Stage 4 match

### Implementation check (Stage 4C task, not this task)

When Stage 4C runtime is written, merge_safety_check.py will verify:
```
FOR each merged row:
  IF any Trimble field is modified (not just added):
    RESULT = LEAKAGE
    BLOCK = Yes
```

---

## No-Overwrite Invariant (Restatement)

**Core principle:** If Trimble baseline says pole is X, and Stage 4 capture says pole is Y, Stage 4 data does NOT overwrite Trimble.

### Example

```
Trimble record: { pole_id: "P008-001", pole_type: "wooden", height: 11 }
Stage 4 capture: { pole_id: "P008-001", condition: "fair", measured_height: 10.8 }

Merged result: { pole_id: "P008-001", pole_type: "wooden", height: 11, condition: "fair", measured_height: 10.8, source_condition: "structured_capture", source_measured_height: "structured_capture" }

NOT: { pole_id: "P008-001", pole_type: "wooden", height: 10.8 (WRONG — height overwritten) }
```

---

## Evidence Chain Integrity

### pole_id → evidence photos link

**Rule:** Each captured pole_id must have at least one evidence photo, and each photo filename must reference a valid pole_id.

### Validation check

```
FOR each captured pole_id:
  IF no photo filename contains this pole_id:
    RESULT = "Missing evidence for pole_id"
    SEVERITY = WARNING (not blocking, but flagged)

FOR each photo filename:
  IF pole_id prefix is not in captured CSV:
    RESULT = "Unreferenced photo"
    SEVERITY = WARNING (not blocking, but flagged)
```

### In controlled pilot

- **Target:** 0 missing evidence, 0 unreferenced photos
- **Threshold for GO:** ≥90% reference coverage (at most 3 missing out of 30)
- **Below ≥90%:** NO-GO (evidence workflow is too fragile)

---

## Sign-Off Protocol

**When Noel signs the decision board (doc 75), by signature Noel confirms:**

1. ✅ "I have verified pole_id matching against Trimble baseline"
2. ✅ "I understand what each NO MATCH reason means"
3. ✅ "I have simulated the merge and confirmed no data corruption will occur"
4. ✅ "I accept the match rate and mismatch profile"
5. ✅ "My verdict (GO / CONDITIONAL GO / NO-GO / STOP) is final and documented"

**This signature authorises (or denies) the start of Stage 4C runtime implementation.**

---

## Reference

- **Document 50:** Stage 4C Go/No-Go Gate (criterion G4)
- **Document 56:** Stage 4C Runtime Integration Architecture (merge algorithm details)
- **Document 73:** Controlled Baseline Pilot Prep (workflow, job selection, validation)
- **Document 75:** Controlled Pilot Decision Template (verdict recording)
