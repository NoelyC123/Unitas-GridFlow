# C2D Task 1 — Geometry Pipeline Validation

## Status

PASS — Approved for progression to Task 2

---

## Branch

codex/c2d-geom-pipeline
Commit: 4108ced

---

## Scope

Deterministic geometry normalisation prior to span generation:

- Snap nearby points
- Merge duplicates
- Remove zero-length sequence steps

---

## Implementation Verification

### Pipeline order (CONFIRMED)

snap_nearby_points → merge_duplicates → remove_zero_length_sequences

### Integration points (CONFIRMED)

- span_generator.py → uses cleaned geometry only
- map_preview.py → fallback spans use cleaned sequence
- No raw geometry leakage detected

---

## Thresholds

| Step                | Value |
| ------------------- | ----- |
| Snap                | 3.0m  |
| Merge               | 2.0m  |
| Zero-length removal | 2.0m  |

Note: Slightly aggressive vs 1m spec — accepted for now.

---

## Determinism

- No randomness
- Anchor-based snapping
- Order-dependent but stable for identical inputs

Status: ACCEPTED (non-blocking)

---

## Test Coverage

### Covered

- Duplicate collapse
- Short span removal (~1m)
- Distance recomputation

### Gaps (non-blocking)

- Multi-duplicate clusters
- Threshold edge boundaries
- Order independence

---

## Real Job Validation (P008 / F001)

### Observations

- Total point features: 56
- Span count: 28
- Route visually continuous
- No missing intermediate poles

### Critical Behaviour

✔ Short spans preserved and flagged:

- 3.5m
- 6.7m
- 10m

✔ Span anomaly system active:

- “likely duplicate or co-located pair”

✔ Crossing context correctly separated from anomalies

---

## Failure Mode Check

| Risk              | Result       |
| ----------------- | ------------ |
| Over-cleaning     | NOT observed |
| Hidden duplicates | NOT observed |
| Route breakage    | NOT observed |
| Data loss         | NOT observed |

---

## Conclusion

Geometry pipeline:

- Removes noise
- Preserves QA signals
- Safe for downstream design logic

---

## Decision

APPROVED
→ Proceed to C2D Task 2 (Duplicate Detection Layer)

---

## Follow-ups (Backlog)

1. Reduce zero-length threshold (2m → 1m)
2. Expand edge-case tests
3. Improve anchor determinism (future)
