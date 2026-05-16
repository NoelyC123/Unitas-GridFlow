# Stage 6E — Design-Readiness Logic Update Specification

## Purpose

Stage 6E is the only stage where `design_ready` logic changes.

The objective is to update design-readiness assessment to use three-source evidence —
field survey, ENWL pole/equipment records, and ENWL trace — instead of field evidence alone.
It does this by consuming the outputs of Stage 6C (linking) and Stage 6D (conflict detection)
to produce an updated readiness status per pole.

Stage 6E must not run until Stage 6D conflict detection is complete for the survey.

---

## Dependency Chain

Stage 6A → Stage 6B → Stage 6C → Stage 6D → **Stage 6E**

Each stage is a precondition for the next in the readiness logic path:

- Stage 6A: evidence classified by relationship type
- Stage 6B: three-source evidence combined per pole
- Stage 6C: formal pole-to-ENWL linking with confidence levels
- Stage 6D: conflict detection between field/ENWL/trace evidence
- Stage 6E: readiness logic updated using all three sources

Stage 6E must not skip or bypass any upstream stage.

---

## Current Readiness Logic (Pre-Stage 6E)

The existing `design_ready` flag is set by the merge pipeline based on field-side evidence
and the absence of critical QA blockers. It does not consume ENWL evidence.

Under the current logic, P_LOCAL_002 poles remain `design_blocked` primarily because:

- `conductor_spec_missing`: no conductor specification proven per-pole from field survey alone
- `pole_class_verification_required`: pole strength class not confirmed from field photos
- `voltage_verification_required`: in some cases, voltage not definitively confirmed

This is correct behaviour. The field survey alone cannot resolve conductor specification or
pole strength rating without DNO engineering records.

---

## Updated Readiness Logic (Stage 6E)

Stage 6E introduces a `readiness_level` field alongside the existing `design_ready` boolean.
The `readiness_level` reflects the three-source combined evidence state more precisely than
a single boolean.

### Three Readiness Levels

**DESIGN_READY**

All of the following must be true:

- Field survey complete (photos, notes present)
- ENWL linking confidence HIGH or MEDIUM (Stage 6C)
- No CRITICAL conflicts from Stage 6D
- Conductor specification confirmed at span level (Stage 6D or Stage 6C proven chain)
- Pole class / strength rating confirmed from DNO engineering records

`design_ready = True` only at this level.

Note: `conductor_spec_missing` is cleared only when conductor FID-to-span-to-pole chain is
proven. Route-level conductor evidence (Level 3) is not sufficient to clear this flag.

**DESIGN_READY_WITH_CAUTIONS**

All of the following must be true:

- Field survey complete
- ENWL linking confidence HIGH or MEDIUM (Stage 6C)
- No CRITICAL conflicts from Stage 6D (WARNING-level conflicts are acceptable)
- Conductor evidence present at route level (Level 3) but not yet span-linked

`design_ready` remains `False`. The pole is usable for design planning but requires
designer awareness of outstanding items before CAD work begins.

This is the expected outcome for most P_LOCAL_002 poles after Stage 6E, because conductor
evidence is currently Level 3 (route-level) only.

**DESIGN_BLOCKED**

Any of the following is true:

- ENWL linking confidence NONE or LOW
- CRITICAL conflicts from Stage 6D that are unresolved
- Evidence gaps that prevent safe design (no field photos, no notes, no ENWL record)
- Manual confirmation required and not completed

`design_ready` remains `False`. The pole cannot be used for design work.

---

## P_LOCAL_002 Expected Outcomes After Stage 6E

These are expectations based on Stage 6C linking results and known evidence gaps. Actual
outcomes depend on Stage 6D conflict findings, which may modify any pole's level.

| Pole | Support | Stage 6C Confidence | Expected Level | Key Constraint |
|---|---|---|---|---|
| 03 | 900343 | HIGH | DESIGN_READY_WITH_CAUTIONS | Conductor route-level only; tee-off span assignment unresolved |
| 05 | 900344 | HIGH | DESIGN_READY_WITH_CAUTIONS | Conductor route-level only; stay wire uncertain |
| 06 | 900345 | HIGH | DESIGN_READY_WITH_CAUTIONS | Conductor route-level only; H-pole vs stub pole conflict pending 6D |
| 01 | 902202 | MEDIUM | DESIGN_BLOCKED | No conductor spec; UG transition relationship unresolved |
| 02 | 902201 | MEDIUM | DESIGN_BLOCKED | No conductor spec; span direction unresolved |
| 04 | 900342A | MEDIUM | DESIGN_BLOCKED | No conductor spec; UG transition relationship unresolved |
| 07 | 903104 | MEDIUM | DESIGN_BLOCKED | LV conductor route-level only; LV span assignment unresolved |
| 08 | 903103 | MEDIUM | DESIGN_BLOCKED | LV conductor route-level only |
| 09 | 903102 | MEDIUM | DESIGN_BLOCKED | LV conductor route-level only |
| 10 | 903101 | MEDIUM | DESIGN_BLOCKED | LV conductor route-level only; sleeve context unresolved |

At minimum, Poles 03, 05, and 06 are expected to reach DESIGN_READY_WITH_CAUTIONS after
Stage 6E, because they have HIGH linking confidence and direct equipment evidence. Whether
any pole reaches DESIGN_READY depends on whether Stage 6D can resolve conductor-to-span
assignment for those three poles — which is not expected in Stage 6D alone.

---

## Implementation Requirements

### 1. New module: `gridflow/design_readiness/`

Create a `readiness_updater.py` module that:

- Takes a `MergedPole` record, a `LinkingResult` (Stage 6C), and a `ConflictReport`
  (Stage 6D) as inputs
- Returns an updated `MergedPole` with:
  - `readiness_level`: `DESIGN_READY` / `DESIGN_READY_WITH_CAUTIONS` / `DESIGN_BLOCKED`
  - `design_ready`: True only when `readiness_level == DESIGN_READY`
  - `design_blocked`: True when `readiness_level == DESIGN_BLOCKED`
  - `readiness_blockers`: list of specific blocking reasons (actionable strings)
  - `readiness_cautions`: list of non-blocking warnings

### 2. Readiness decision rules (all must be implemented as explicit checks)

```
if linking_confidence in (NONE, LOW) or manual_confirmation_required:
    → DESIGN_BLOCKED, blocker: "Linking confidence insufficient"

if any CRITICAL conflict from Stage 6D:
    → DESIGN_BLOCKED, blocker: specific conflict description

if conductor_spec_missing AND no span-linked conductor proof:
    → not DESIGN_READY (but may be DESIGN_READY_WITH_CAUTIONS if other conditions met)

if all of:
  - linking HIGH or MEDIUM
  - no CRITICAL conflicts
  - route-level conductor evidence present
  - pole class uncertain but documented:
    → DESIGN_READY_WITH_CAUTIONS

if all of:
  - linking HIGH or MEDIUM
  - no CRITICAL conflicts
  - conductor spec confirmed at span level
  - pole class confirmed from DNO records:
    → DESIGN_READY
    → design_ready = True
```

### 3. `readiness_blockers` wording

Blockers must be specific and actionable. Examples:

- `"Conductor specification not confirmed at span level — route-level evidence only"`
- `"Pole class/strength rating not confirmed from DNO engineering records"`
- `"ENWL linking confidence MEDIUM — no fid_polestructure equipment link proven"`
- `"Stage 6D CRITICAL conflict: pole type mismatch — ENWL records Terminal, field shows intermediate arrangement"`

### 4. `readiness_cautions` wording

Cautions are non-blocking warnings for DESIGN_READY_WITH_CAUTIONS. Examples:

- `"Conductor evidence is route-level only — span assignment not proven"`
- `"Stay wire presence uncertain from field photos"`
- `"GPS coordinate within 20 m of ENWL record — corroborating but not surveyed independently"`
- `"Partial ENWL equipment screenshot — full FID not confirmed"`

### 5. Integration with existing pipeline

Stage 6E updates the merge pipeline to call `readiness_updater.py` as a final pass after
the existing merge/QA steps. The `design_ready` flag computed by the existing merge engine
is the input; Stage 6E may elevate it (never lower it without explicit conflict evidence).

Stage 6E must not change any merge/matching logic, QA engine behaviour, or report generation
that is not directly connected to the readiness level decision.

---

## Stage 6E Must NOT

- Clear `conductor_spec_missing` from route-level (Level 3) evidence alone.
- Mark any pole `design_ready = True` if CRITICAL conflicts from Stage 6D are unresolved.
- Ignore linking confidence — LOW confidence is a DESIGN_BLOCKED blocker.
- Skip the Stage 6D conflict check — Stage 6E cannot run without Stage 6D output.
- Mix 11kV and LV route contexts in readiness logic — they must be evaluated separately.
- Make operational safety claims from ENWL switch status fields (consistent with Stage 6B
  rule, carried forward).

---

## Acceptance Criteria

Stage 6E is complete when:

1. `gridflow/design_readiness/readiness_updater.py` exists and imports cleanly.
2. At least one P_LOCAL_002 pole reaches `DESIGN_READY_WITH_CAUTIONS` after running
   Stage 6E on the Stage 6C + Stage 6D outputs.
3. No pole with an unresolved CRITICAL Stage 6D conflict is marked `DESIGN_READY`.
4. `readiness_blockers` are non-empty and actionable for every DESIGN_BLOCKED pole.
5. `readiness_cautions` are non-empty for every DESIGN_READY_WITH_CAUTIONS pole.
6. `design_ready = True` only for poles at `DESIGN_READY` level.
7. Tests in `tests/test_readiness_updater.py` cover all three readiness level paths.
8. Full `pytest -q` passes with no regressions.
9. `git diff --check` passes.

---

## Boundary with Stage 6D

Stage 6E consumes Stage 6D conflict reports. Stage 6E does not implement conflict detection.

If Stage 6D has not run for a pole, Stage 6E must not assume the pole is conflict-free —
it must treat the missing conflict report as an evidence gap and return DESIGN_BLOCKED with
blocker `"Stage 6D conflict check not completed for this pole"`.

---

## Boundary with Stage 6F (if required)

If span-level conductor assignment is proven in a future stage (resolving
`conductor_spec_missing` for specific spans), Stage 6E logic should be re-run to evaluate
whether DESIGN_READY is achievable. This re-run is not part of Stage 6E itself; it is
triggered when new span-linking evidence is available.

---

## Notes on P_LOCAL_002 Readiness Expectations

The expected outcome for P_LOCAL_002 after Stage 6E is:

- **3 poles at DESIGN_READY_WITH_CAUTIONS** (03, 05, 06) — HIGH linking, route conductor
  only, pending Stage 6D conflict review.
- **7 poles at DESIGN_BLOCKED** — MEDIUM linking, route conductor only, no span-level proof.
- **0 poles at DESIGN_READY** — not expected until conductor specification is proven per span.

This is an honest and correct outcome for the current evidence state. P_LOCAL_002 is a
surveying prototype; the absence of DESIGN_READY outcomes after Stage 6E does not indicate
a failure — it indicates that the system is correctly identifying what DNO records are still
needed before design can proceed.
