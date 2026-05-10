---
status: PLANNING
created: 2026-05-10
branch: codex/stage4c-runtime-integration-architecture
note: Stage 4D (UI surfacing) is OUT OF SCOPE for Stage 4C. This doc plans ahead for Stage 4D.
---

# 58 — Stage 4C UI Surfacing Plan

This document defines **when, where, and how** Stage 4 structured capture data is surfaced in the Review OS C2E2 popup and related UI. This is **Stage 4D scope** (not Stage 4C), but planning happens now to ensure Stage 4C architecture supports it.

---

## Stage 4C vs Stage 4D scope

**Stage 4C (this stage)**: CSV intake, validation, merge, persistence, audit logging. **No UI changes.**

**Stage 4D (future)**: Query Stage 4 records, surface in popup, label completeness, prevent fake completeness, export to Design Chain.

This document plans the Stage 4D UI architecture so that Stage 4C code is designed to support it.

---

## Principle: completeness is truthful

**Risk R02** — fake completeness. Stage 4 row passes validation but all optional fields are `unknown` or `low` confidence. Popup shows "complete data available" but it's actually placeholder.

**Mitigation**:
- `completeness` classification (minimum / partial / complete) is persisted and displayed
- Popup labels indicate completeness level explicitly
- Designer cannot confuse minimum/partial/complete
- QA engine can flag minimum completeness as needing attention

---

## UI locations where Stage 4 appears (Stage 4D)

### Location 1: C2E2 Popup (Review OS)

When designer clicks a pole:

```
┌─────────────────────────────────────────┐
│ POLE P008-001                           │
├─────────────────────────────────────────┤
│ Trimble Baseline (from survey):         │
│  Type: Concrete                         │
│  Material: Wood                         │
│  Class: ▶ Distribution                  │
│  [...]                                  │
├─────────────────────────────────────────┤
│ Stage 4 Structured Capture:             │
│  Captured: 2026-05-10 (Surveyor Tablet) │
│  Completeness: COMPLETE ███░            │
│  Confidence: HIGH                       │
│                                         │
│  Condition: Good                        │
│  Voltage Carried: 11kV                  │
│  Stay Present: Yes (type: stay_down)   │
│  [Show more...]                         │
│                                         │
│  ⚠️ Conflict: Stage 4 says pole type    │
│     is steel, but Trimble says wood.    │
│     Designer review needed.             │
├─────────────────────────────────────────┤
│ [View Audit Trail] [Add Note] [...]     │
└─────────────────────────────────────────┘
```

**Labels shown**:
- Capture date
- Capture source (office_audit / surveyor_tablet)
- Completeness badge (minimum / partial / complete)
- Confidence level
- Captured by (surveyor name)
- Any conflicts flagged

**What is NOT shown in popup**:
- Raw validation errors
- Merge operation details
- Audit log entries (except one-line summary)

### Location 2: Pole inspection form (Stage 4D future)

When designer clicks "Edit" or "Capture more data":

```
┌─────────────────────────────────────────┐
│ P008-001 — Capture Form                 │
├─────────────────────────────────────────┤
│ Previous captures (read-only):          │
│  • 2026-05-10 Surveyor Tablet           │
│    Condition: Good (high confidence)    │
│    Voltage: 11kV (medium confidence)    │
│    [Show details] [View history]        │
│                                         │
│ Add new capture (future button):        │
│  [ + New capture session ]              │
│                                         │
│ Trimble baseline:                       │
│  Type: Concrete (immutable)             │
│  Material: Wood (immutable)             │
│  [...]                                  │
└─────────────────────────────────────────┘
```

### Location 3: Job completeness dashboard (Stage 4D future)

Designer sees job-level summary:

```
┌─────────────────────────────────────────┐
│ Job P008/F001 — Completeness Summary    │
├─────────────────────────────────────────┤
│ Trimble baseline: 87/87 poles           │
│ Stage 4 capture:  31/87 poles captured  │
│                                         │
│ Completeness breakdown:                 │
│  • Complete:   12 poles                 │
│  • Partial:    15 poles                 │
│  • Minimum:     4 poles                 │
│  • No capture: 56 poles                 │
│                                         │
│ Conflicts:      3 poles need review     │
│ Unmatched IDs:  2 poles (no Trimble)   │
└─────────────────────────────────────────┘
```

---

## Data model: what popup queries

### Query structure (Stage 4D)

```python
# map-viewer.js calls (Stage 4D):
GET /api/pole/{pole_id}/stage4-data

Response:
{
  "pole_id": "P008-001",
  "has_stage4_capture": true,
  "capture_records": [
    {
      "upload_id": "upload_2026-05-10_001",
      "capture_date": "2026-05-10",
      "captured_by": "Alice Smith",
      "capture_source": "surveyor_tablet",
      "completeness": "complete",
      "confidence_level": "high",
      "merge_timestamp": "2026-05-10T14:32:00Z",
      "conflict_with_trimble": true,
      "conflicts": [
        {
          "field": "pole_type",
          "trimble_value": "Concrete",
          "stage4_value": "Steel",
          "description": "Type classification differs"
        }
      ],
      "captured_fields": {
        "condition": "Good",
        "voltage_carried": "11kV",
        "stay_present": true,
        "stay_type": "stay_down",
        "lean_direction": "none",
        "equipment_present": false,
        "equipment_type": null,
        "clearance_issues": "None noted",
        "defect_notes": null,
        "conductor_size": null,
        "stay_required": false,
        "lean_severity": null,
        "verification_required": false
      }
    }
  ]
}
```

### New endpoint: `/api/pole/{pole_id}/stage4-data`

**Purpose**: Fetch Stage 4 records for a single pole.

**When available**: Stage 4D (not Stage 4C).

**Access control**: Designer (Review OS) only, not public API.

**Caching**: Cache for 5 minutes; invalidate on new Stage 4 merge.

---

## Completeness labels

### How completeness is computed (Stage 4B, persisted in Stage 4C)

From `classify_stage4_completeness()`:

```python
def classify_completeness(row: dict) -> str:
    """
    Returns: 'minimum' | 'partial' | 'complete'

    minimum: only required fields present
    partial: 50% of optional fields present
    complete: >50% of optional fields present
    """
```

**Schema has ~18 optional fields** (as of 2026-05-10):
- condition, voltage_carried, stay_present, stay_type, lean_direction
- equipment_present, equipment_type, clearance_issues, defect_notes
- conductor_size, stay_required, lean_severity, verification_required
- confidence_level, capture_date, captured_by, capture_source

**Thresholds**:
- `minimum`: 0–8 optional fields
- `partial`: 9–17 optional fields
- `complete`: 18+ optional fields

### Displaying completeness in popup

```javascript
// Popup badge for each completeness level
function completeness_badge(level: string) {
  if (level === 'complete') {
    return '✓ COMPLETE (full capture)';  // All green
  } else if (level === 'partial') {
    return '◐ PARTIAL (some detail)';    // Partial green
  } else {
    return '◑ MINIMUM (required only)';  // Minimal fill
  }
}
```

**Why this matters**: Designer knows whether "captured data" means comprehensive or just baseline required fields. Prevents fake completeness.

---

## Conflict surfacing

When Stage 4 data conflicts with Trimble baseline:

### Conflict detection (Stage 4C merge)

```python
def detect_conflict(stage4_record: dict, trimble_record: dict) -> list[str]:
    conflicts = []

    # Check fields that exist in both
    if stage4_record.get('pole_type') and \
       stage4_record['pole_type'].lower() != trimble_record['pole_type'].lower():
        conflicts.append('pole_type mismatch')

    if stage4_record.get('pole_material') and \
       stage4_record['pole_material'].lower() != trimble_record['material'].lower():
        conflicts.append('material mismatch')

    # ... more field comparisons

    return conflicts
```

### Conflict display (Stage 4D popup)

```
Conflicts detected:
 ⚠️  pole_type: Stage 4 says Steel, Trimble says Concrete
     → Designer must review; Trimble value is authoritative.

 ⚠️  voltage_carried: Stage 4 says 33kV, Trimble says 11kV
     → Designer must verify; may indicate new circuit added.
```

### Conflict resolution (designer action in Review OS)

Options:
1. **Accept Trimble**: Keep Trimble value, mark Stage 4 conflict as noted
2. **Accept Stage 4**: Acknowledge Stage 4 override, document reason in notes
3. **Request verification**: Flag for surveyor follow-up

---

## "none" truthfulness rule

**Risk R02 mitigation**: `"none"` must always mean "I verified nothing is present", never "I didn't check".

### Example: stay_present

```
CSV row: stay_present = "no", stay_type = "none"

Interpretation:
✓ Surveyor checked pole; no stay is present
✓ Confident that no stay exists
✓ Popup shows: "Stay: No (verified)"

WRONG interpretation:
✗ Surveyor didn't check for stay
✗ "none" is a placeholder
✗ Popup shows: "Stay: Unknown" (fake)
```

### How to enforce

**Stage 4B validation**:
- "none" is allowed for stay_type, lean_direction, equipment_type (see schema)
- "none" is rejected for other fields (e.g., condition cannot be "none")
- Template is clear: "none" means "verified to be absent", not "didn't check"

**Popup label**:
```javascript
// When displaying Stage 4 field value
if (value === "none" || value === "no") {
  return `${field}: No (verified) — surveyor confirmed absence`;
} else if (value === null || value === "") {
  return `${field}: Not captured (data missing)`;
} else {
  return `${field}: ${value}`;
}
```

**Completeness counting**:
- "none" counts as a valid optional field (surveyor did the work)
- null/"" does not count as optional field (data missing)

---

## "unknown" vs null vs "none"

| Value | Meaning | Counts as optional field? |
|---|---|---|
| `"none"` | Verified to be absent | YES (surveyor checked) |
| `null` | Not captured | NO (missing data) |
| `""` (empty) | Not captured | NO (missing data) |
| `"unknown"` | FORBIDDEN (see R02) | N/A |
| "Good" / "11kV" / etc. | Real value captured | YES |

### Why "unknown" is forbidden

From VLD-1 fix (Stage 4A):
- "unknown" is too vague; designer cannot trust it
- If surveyor cannot determine value, better to leave blank
- Blank triggers completeness warning (missing data)
- "unknown" pretends surveyor tried and got uncertain result

---

## Export to Design Chain (Stage 4D future)

When designer exports job to Design Chain:

```python
# Design Chain export includes Stage 4 summary but not raw values

per_pole:
{
  "pole_id": "P008-001",
  "trimble_baseline": { ... },  # Unchanged
  "stage4_completeness": "complete",
  "stage4_confidence": "high",
  "stage4_capture_date": "2026-05-10",
  "stage4_conflicts": [{"field": "pole_type", ...}],
  "stage4_notes": "[custom notes from designer]"
}
```

**Never included**:
- Raw Stage 4 field values (condition, voltage, etc.)
- Validation errors or warnings
- Merge operation details

**Rationale**: Design Chain is Trimble-based; Stage 4 is supplementary metadata. Raw Stage 4 values stay in Review OS.

---

## Testing for Stage 4D UI (planned, not yet implemented)

### Popup rendering tests

```python
def test_stage4_popup_shows_completeness():
    # Merge Stage 4 CSV with completeness=complete
    # Query /api/pole/P008-001/stage4-data
    # Assert: response includes completeness=complete
    # Assert: frontend renders "✓ COMPLETE (full capture)"

def test_stage4_popup_hides_conflicts_from_none():
    # Merge Stage 4 with none values (stay_type="none")
    # Assert: popup shows "Stay: No (verified)" not "Stay: None"
    # Assert: "none" is counted as valid capture, not null
```

### Completeness accuracy tests

```python
def test_completeness_minimum():
    # Row with only required fields (5 fields)
    # Assert: completeness=minimum

def test_completeness_partial():
    # Row with required + 10 optional fields
    # Assert: completeness=partial

def test_completeness_complete():
    # Row with required + 18+ optional fields
    # Assert: completeness=complete
```

---

## Not yet designed (Stage 4D future work)

- Real-time sync: designer adds notes in popup; notes persist to audit log
- Conflict resolution UI: designer chooses Trimble vs Stage 4
- Photo attachments: link geotagged photos to Stage 4 record
- Custom capture forms: extend Stage 4 schema with project-specific fields

---

## Sign-off gate

Before Stage 4D implementation:
- [ ] Noel reviews this plan
- [ ] UI/UX team confirms labels and completeness badges
- [ ] Frontend team plans /api/pole/{pole_id}/stage4-data endpoint
- [ ] QA lead reviews conflict detection logic
- [ ] Stage 4C code review approves architecture

See `AI_CONTROL/50_STAGE4C_GO_NO_GO_GATE.md` and future Stage 4D gate.
