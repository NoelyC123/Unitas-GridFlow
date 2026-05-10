---
status: ACTIVE
created: 2026-05-10
branch: codex/stage4c-runtime-integration-architecture
---

# 56 — Stage 4C Runtime Integration Architecture

This document defines the **data flow, merge algorithm, and safety invariants** for Stage 4 structured capture intake into the live job database. This is the core design that enables Stage 4C to safely integrate with Trimble baseline without corruption.

---

## Design principle

**Append-only, never overwrite.**

Trimble record values are **immutable**. Stage 4 values are **additive only**. A merge operation adds Stage 4 fields to an existing Trimble record; it never replaces or updates Trimble values.

---

## Data flow

### Entry point: CSV upload → `api_intake.py`

1. Surveyor uploads completed Stage 4 CSV file to Review OS
2. `api_intake.py` receives file, triggers structured capture intake handler
3. Handler parses CSV header, instantiates `StructuredCaptureIntake` pipeline
4. Pipeline runs full validation (`validate_stage4_rows()`) from library

### Validation phase (Stage 4B output)

For each row in CSV:

```
1. Parse row → extract identity (pole_id), required fields, optional fields
2. Validate identity: pole_id not blank, not unsafe token
3. Validate structure: all required fields present (capture_source, captured_by, capture_date)
4. Normalize: whitespace trim, enum case-normalization, alias resolution
5. Classify: is_valid, merge_ready, completeness (minimum/partial/complete)
6. Output: per-row result + import-level summary (valid_count, invalid_count, warning_count)
```

If validation fails at any step, row is marked `merge_ready=False`.

### Merge phase (Stage 4C new — THIS DOCUMENT)

Only rows with `merge_ready=True` proceed to merge.

For each merge-ready row:

```
1. Pole_id lookup: exact-match pole_id against Trimble baseline
   - Pole_id is primary merge key; must be exact match
   - Whitespace is normalized on both sides before match
   - No fuzzy/partial matching allowed

2. Duplicate check: has this pole_id been merged in a prior upload?
   - Query job's Stage 4 merge history: any existing record for this pole_id?
   - If yes → CONFLICT (R08 — cross-session duplicate)
     - Log conflict with before/after snapshots
     - Reject merge; ask surveyor if this is an update
   - If no → proceed

3. Conflict detection: does this row conflict with Trimble baseline?
   - Example: Trimble says P008-001 is concrete; Stage 4 says steel
   - Conflicts are logged but NOT blocking (user review required later)
   - Record is still merged, but marked with conflict flag

4. Append merge: add Stage 4 record to job
   - Create new job_structured_capture record with pole_id, all valid Stage 4 fields
   - Link to Trimble pole via pole_id
   - Record merge timestamp, merge_source (iPad / office_audit / etc)
   - Preserve completeness classification
   - Set merge_ready=True on persisted record

5. Audit logging: log complete before/after state
   - Before: Trimble record (select key fields: pole_id, type, material, class, etc)
   - After: Trimble record (unchanged) + new Stage 4 record (added)
   - Merge operation timestamp, user, CSV source
   - Any conflicts detected
```

### Output: merge result summary

```json
{
  "job_id": "P008/F001",
  "upload_id": "upload_2026-05-10_001",
  "csv_rows_total": 15,
  "rows_merged_count": 13,
  "rows_rejected_count": 2,
  "rows_with_conflicts": 1,
  "merge_operations": [
    {
      "pole_id": "P008-001",
      "merge_ready": true,
      "conflict": false,
      "timestamp": "2026-05-10T14:32:00Z",
      "completeness": "complete"
    },
    ...
  ],
  "unmatched_pole_ids": [
    {
      "pole_id": "P008-999",
      "reason": "no_trimble_match"
    }
  ],
  "errors": [
    {
      "row_index": 4,
      "pole_id": "P008-005",
      "error": "required_field_missing",
      "field": "capture_date"
    }
  ]
}
```

---

## Pole_id matching algorithm

### Input:
- Stage 4 CSV row with pole_id (potentially whitespace-padded, dashes or spaces as separators)
- Trimble baseline for the job (list of known pole_id values)

### Algorithm:

```python
def match_stage4_pole_to_trimble(stage4_pole_id: str, trimble_pole_ids: set[str]) -> Optional[str]:
    """
    Returns the matching Trimble pole_id if found; None if no match.
    Exact match only after normalization.
    """
    # Normalize Stage 4 pole_id: strip whitespace
    normalized_stage4 = stage4_pole_id.strip()

    # Exact match against normalized Trimble pole_ids
    if normalized_stage4 in trimble_pole_ids:
        return normalized_stage4

    # No fuzzy matching; return None
    return None
```

### Failure modes:

| Scenario | Outcome | Logged |
|---|---|---|
| pole_id in Stage 4 CSV but not in Trimble | **Unmatched** — row merged but flagged as unmatched | Yes, with pole_id and reason |
| pole_id in Trimble, not in CSV | **Not captured** — Trimble record unchanged, no Stage 4 data | No (expected; not all poles may be captured) |
| pole_id format mismatch (e.g. `P008001` vs `P008-001`) | **No match** — row unmatched (R04 mitigation: normalise on import) | Yes |
| pole_id case mismatch (e.g. `p008-001` vs `P008-001`) | **No match** — caught by validation; rejected as unsafe identity token | Yes |

---

## No-overwrite invariant

**CRITICAL INVARIANT: Trimble record values are never modified by Stage 4 merge.**

Applied to fields that exist in both Trimble baseline and Stage 4:

| Trimble field | Stage 4 field | Merge rule |
|---|---|---|
| `pole_id` | `pole_id` | Use as merge key; never change Trimble value |
| `pole_class` | `pole_class` | Never overwrite Trimble value; Stage 4 is optional |
| `pole_type` | `pole_type` | Never overwrite Trimble value; Stage 4 is optional |
| `material` | `pole_material` | Never overwrite Trimble value; Stage 4 is separate field |

**How to enforce**:
- When loading a Trimble + Stage 4 record, display Trimble values as **read-only**
- When exporting to PoleCAD or Design Chain, Trimble values take precedence
- If conflict is detected (e.g. Stage 4 says steel, Trimble says concrete), log conflict but **keep Trimble**
- QA engine may issue a WARNING that Stage 4 conflicts with Trimble, but does **not** replace

---

## Conflict handling

### Types of conflicts

**Type A — Semantic conflict**
Stage 4 and Trimble have different values for the same real-world property:
- Trimble: `pole_type = concrete`
- Stage 4: `pole_type = steel`

**Type B — Duplicate pole_id in different uploads**
Same job, two uploads, both contain pole_id `P008-001`:
- Upload 1 (2026-05-10 08:00): captures P008-001 with condition=good
- Upload 2 (2026-05-10 14:00): captures P008-001 with condition=poor
- Q: Is this an update (surveyor re-visited pole) or duplicate error?

**Type C — Missing pole_id match**
Stage 4 row has valid pole_id but no Trimble record:
- May be: new pole added after Trimble survey
- May be: surveyor typed wrong ID
- May be: Trimble export is incomplete

### Resolution strategy

**Type A (Semantic conflict)**
- Merge proceeds; row is marked `conflict=true`
- Audit log records both values
- QA engine flags to designer: "Stage 4 conflicts with Trimble for P008-001 pole_type"
- Designer resolves in Review OS or Design Chain export

**Type B (Duplicate across sessions)**
- Merge **blocked** if same pole_id already has Stage 4 record in job
- Log error: "Duplicate pole_id P008-001 in separate uploads"
- Return to surveyor: "This pole was already captured on [date]. Upload this as an update?"
- **Future enhancement** (not Stage 4C): allow explicit "update" flag in CSV header

**Type C (Unmatched pole_id)**
- Merge proceeds; row is marked `unmatched_trimble=true`
- Audit log: "pole_id P008-999 not found in Trimble baseline"
- Designer can still review captured data in Review OS
- May be valid if pole was added after survey

---

## Data model: Stage 4 merge record

Persisted in job database as new `job_structured_capture` record:

```python
class JobStructuredCaptureRecord:
    job_id: str                    # e.g. "P008/F001"
    pole_id: str                   # Primary key (merge key)
    upload_id: str                 # Which CSV upload added this record
    merge_timestamp: datetime      # When merged
    merge_source: str              # "surveyor_tablet" / "office_audit" / etc
    merge_ready: bool              # Stage 4B validation passed
    completeness: str              # "minimum" / "partial" / "complete"
    conflict_with_trimble: bool    # Semantic conflict detected
    unmatched_trimble: bool        # pole_id not in Trimble baseline

    # Captured fields (subset of structured_capture schema)
    condition: Optional[str]       # "good" / "poor" / "fair"
    voltage_carried: Optional[str] # "11kV" / "33kV" / etc
    stay_present: Optional[bool]
    stay_type: Optional[str]       # "stay_down" / "stay_up" / "flying_down" / "none"
    lean_direction: Optional[str]  # "north" / "south" / "none"
    equipment_present: Optional[bool]
    equipment_type: Optional[str]  # "transformer" / "switchgear" / "none"
    clearance_issues: Optional[str]
    defect_notes: Optional[str]
    conductor_size: Optional[str]
    stay_required: Optional[bool]
    lean_severity: Optional[str]   # "minor" / "moderate" / "severe"
    verification_required: Optional[str]
    confidence_level: str          # "low" / "medium" / "high"
    capture_date: datetime         # When captured
    captured_by: str               # Surveyor name
    capture_source: str            # "office_audit" / "surveyor_tablet"
```

---

## Safety: prevent runtime leakage

See `AI_CONTROL/57_STAGE4C_RUNTIME_BOUNDARY_RULES.md` for enforcement.

**Code path rule**: Only `api_intake.py` receives and merges Stage 4 CSVs.
**Isolation rule**: `qa_engine.py` reads Stage 4 records but does NOT create them.
**Output rule**: Stage 4 data only surfaces in Review OS post-Stage 4D approval.

---

## Audit logging

Every merge operation produces an immutable audit record:

```python
class MergeAuditLog:
    merge_id: str                  # Unique identifier
    job_id: str
    pole_id: str
    upload_id: str
    timestamp: datetime
    operation: str                 # "merge_new" / "merge_duplicate_rejected" / "merge_unmatched"
    before_state: dict             # Trimble record snapshot (unchanged)
    after_state: dict              # Trimble record (unchanged) + Stage 4 record (added)
    conflicts_detected: list[str]  # ["pole_type mismatch", ...]
    operator_user_id: str          # Who uploaded CSV
    csv_row_index: int             # Row number in upload
```

Audit logs are immutable and queryable by job_id, pole_id, or date range. Used for:
- Compliance verification (Stage 4C correctness audit)
- Conflict resolution (designer debugging)
- Pilot analysis (real field pilot validation)

---

## Testing strategy

See `AI_CONTROL/60_STAGE4C_RISK_DRIVEN_TEST_PLAN.md` for full test plan.

Key tests:
- **test_merge_exact_pole_id_match** — only exact match succeeds
- **test_merge_rejects_format_mismatch** — fuzzy matching forbidden
- **test_merge_no_overwrite_trimble** — Trimble values unchanged after merge
- **test_merge_duplicate_across_sessions** — second upload rejected
- **test_merge_conflict_logged** — semantic conflicts recorded but don't block
- **test_merge_audit_log** — before/after snapshots captured
- **Integration test**: golden sample CSV → validation → merge → database state matches expected

---

## Ready for Stage 4D?

Once Stage 4C merge is complete and tested:
- Stage 4 records exist in job database
- Trimble baseline is unchanged
- All merges are logged with audit trail
- Conflicts are documented

Stage 4D will:
- Query Stage 4 records by job_id
- Surface in Review OS with completeness labels
- Support export to Design Chain / PoleCAD

See `AI_CONTROL/58_STAGE4C_UI_SURFACING_PLAN.md`.
