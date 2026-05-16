# Stage 6C — Formal Pole-to-ENWL Evidence Linking

## Purpose

Stage 6B proved that GridFlow can combine field evidence, ENWL pole/equipment records, and
ENWL trace GeoJSON into a single inspectable per-pole evidence record. The combiner runs,
the workspace displays evidence by relationship level, and the caution wording is in place.

Stage 6C formalises **linking**: the step from "we have evidence files for a pole" to "each
pole has a documented linking status, a confidence level, and an explicit basis."

The core question Stage 6C must answer for every pole:

> **By what mechanism is this field-surveyed pole linked to its ENWL network record, and how
> confident are we in that link?**

Stage 6C must not change `design_ready`, must not clear `conductor_spec_missing`, and must
not claim design authorisation from ENWL evidence alone.

---

## What Stage 6B Left Open

The Stage 6B combiner (`gridflow/evidence_combiner/combiner.py`) already implements:

- `fid_polestructure` matching: equipment records linked to a pole FID — used for Poles
  03, 05, and 06.
- Known conductor FID cross-referencing: matches conductor FIDs from notes against trace
  features.
- GPS proximity (50 m threshold): used for route conductors and nearby context features.

What it does **not** produce is a formal **pole-level linking status**. The combiner returns
evidence records organised by relationship type, but it does not declare which linking
mechanism was used for the pole itself, what confidence level that carries, or whether
manual confirmation is needed.

Stage 6C fills that gap.

---

## Linking Mechanisms (Priority Order)

The following mechanisms are defined in decreasing strength. The linker applies them in this
order and stops at the first mechanism that produces a confirmed match.

### 1. `fid_polestructure` match (HIGHEST — proven)

An ENWL equipment record (switch, transformer, link, LV way) that carries a `fid_polestructure`
field matching the pole's own ENWL FID extracted from `pole_notes.md`.

This is the strongest possible link because ENWL itself has asserted the equipment-to-pole
relationship. No human inference is required.

Confidence: **HIGH**

Proven P_LOCAL_002 examples:
- Pole 03 / 900343: FSL/switch FID 11883940 → `fid_polestructure` 16869661
- Pole 05 / 900344: Fault Making Switch FID 73189925 → `fid_polestructure` 16869657
- Pole 06 / 900345: transformer FID 20636886 + HV link FID 11835967 → `fid_polestructure` 53427080

### 2. Support number match

The support number extracted from `pole_notes.md` (e.g., `900344`) matches the `support_no`
field in an ENWL pole popup or pole record in the trace evidence.

ENWL support numbers are assigned by the DNO and are the primary operational identifier for
a pole. A confirmed support-number match between the field note and the ENWL record is the
next strongest link.

Confidence: **MEDIUM** (may be elevated to HIGH when corroborated by SPN and GPS)

### 3. SPN match

The SPN extracted from `pole_notes.md` (e.g., `61090H00344`) matches the SPN in the ENWL
pole record.

A SPN is a unique network point reference. An exact SPN match without a corroborating
support number is MEDIUM confidence because transcription errors are possible.

Confidence: **MEDIUM**

### 4. Pole FID match from notes

The ENWL pole FID extracted from `pole_notes.md` (e.g., `Pole FID: 16869657`) matches an
ENWL feature with the same FID in the trace dataset.

When a field note contains an explicit FID that was read from the ENWL Network Asset Viewer
and the trace dataset contains a pole record with that FID, the link is direct. Confidence
depends on whether the field note was manually read and could contain a transcription error.

Confidence: **MEDIUM** (elevated toward HIGH when combined with support number or SPN)

### 5. GPS proximity (supporting evidence only)

The pole's GPS coordinates from `pole_notes.md` are within a defined tolerance (currently
50 m, matching the Stage 6B combiner proximity threshold) of an ENWL pole feature geometry.

GPS proximity is **never** the sole basis for a confirmed link. It is supporting context
that may corroborate a match established by mechanisms 1–4, or may flag a candidate for
human review.

Confidence: **LOW as sole basis** / supporting MEDIUM when combined with support number

### 6. Manual confirmation (fallback)

A human reviewer has inspected the evidence and confirmed or assigned the link. This is the
fallback when automated mechanisms do not produce a confirmed result.

Confidence: **MEDIUM** (assessor-assigned) with `manual_confirmation_required: true` in
the output record.

---

## What a Confirmed Link Looks Like

Each pole in the Stage 6C output carries a `linking_status` record with the following
fields:

| Field | Type | Description |
|---|---|---|
| `linking_method` | str | The mechanism that established the link (see above) |
| `confidence` | str | `HIGH` / `MEDIUM` / `LOW` |
| `matched_enwl_fid` | str or null | ENWL pole FID confirmed for this link |
| `matched_support_no` | str or null | ENWL support number confirmed |
| `matched_spn` | str or null | ENWL SPN confirmed |
| `evidence_source` | str | e.g. `pole_notes+trace_geojson` |
| `direct_equipment_fids` | list[str] | FIDs of equipment linked via `fid_polestructure` |
| `manual_confirmation_required` | bool | True when no automated mechanism confirmed |
| `link_basis_notes` | str | Human-readable description of the linking evidence |

A pole is **not linked** if no mechanism above produces a match. It is flagged
`confidence: UNLINKED` and `manual_confirmation_required: true`.

---

## P_LOCAL_002 Expected Linking Outcomes

Based on the Stage 6A-0 spike findings (`AI_CONTROL/121_PLOCAL002_LINKING_FEASIBILITY_SPIKE.md`)
and the current enriched pole notes.

| Pole | Support | Pole FID | Expected Linking Method | Expected Confidence | Direct Equipment FIDs |
|---|---|---|---|---|---|
| 01 | 902202 | 16858852 | support_no + pole FID from notes + GPS | MEDIUM | None confirmed |
| 02 | 902201 | 16793152 | support_no + pole FID from notes + GPS | MEDIUM | None confirmed |
| 03 | 900343 | 16869661 | fid_polestructure (FSL FID 11883940) | HIGH | 11883940 |
| 04 | 900342A | 16896331 | support_no + pole FID from notes + GPS | MEDIUM | None confirmed |
| 05 | 900344 | 16869657 | fid_polestructure (ABS FID 73189925) | HIGH | 73189925 |
| 06 | 900345 | 53427080 | fid_polestructure (transformer 20636886 + HV link 11835967) | HIGH | 20636886, 11835967 |
| 07 | 903104 | 53426793 | support_no + pole FID from notes + GPS | MEDIUM | None confirmed |
| 08 | 903103 | 16778530 | support_no + pole FID from notes + GPS | MEDIUM | None confirmed |
| 09 | 903102 | 16920793 | support_no + pole FID from notes + GPS | MEDIUM | None confirmed |
| 10 | 903101 | 16788439 | support_no + pole FID from notes + GPS | MEDIUM | None confirmed |

All 10 poles are expected to link at MEDIUM or HIGH. No pole is expected to remain UNLINKED
because all 10 have confirmed support numbers and ENWL FIDs in their current notes.

---

## What Stage 6C Must Not Do

- Must not use GPS proximity as the sole basis for a confirmed link.
- Must not treat a conductor FID as a pole link. Conductors describe spans; they are not
  attached to poles by FID in the ENWL model without an explicit span-linking step.
- Must not change `design_ready` or any verification flag.
- Must not clear `conductor_spec_missing`. Conductor evidence remains route-level only
  until Stage 6D proves the exact conductor-to-span-to-pole chain.
- Must not mark a pole HIGH confidence from GPS proximity + conductor FIDs alone.
- Must not alter evidence image files, report generation, or the merge/matching pipeline.

---

## Stage 6C Deliverables

### 1. `gridflow/evidence_combiner/linker.py`

Formal linking algorithm. Returns a `LinkingResult` dataclass per pole.

**Key design rules:**

- Receives: `notes_path` (Path), `trace_datasets` (list of parsed `ENWLTraceDataset`)
- Applies linking mechanisms in priority order (1 → 6)
- Returns `LinkingResult` with all fields defined in the schema above
- Never modifies `design_ready`, `conductor_spec_missing`, or any flag
- Separates linking (pole identity) from evidence classification (equipment/conductor/nearby)

**`LinkingResult` must include:**

```python
@dataclass
class LinkingResult:
    pole_folder: str
    support_no: str | None
    pole_fid: str | None
    spn: str | None
    linking_method: str          # "fid_polestructure" / "support_no" / "spn" / "pole_fid" / "gps_proximity" / "manual" / "unlinked"
    confidence: str              # "HIGH" / "MEDIUM" / "LOW" / "UNLINKED"
    matched_enwl_fid: str | None
    matched_support_no: str | None
    matched_spn: str | None
    evidence_source: str
    direct_equipment_fids: list[str]
    manual_confirmation_required: bool
    link_basis_notes: str
```

**Implementation notes:**

- Use the existing `_find_first()` pattern from `combiner.py` to extract identity fields
  from notes text.
- Reuse the `ENWLTraceParser` and `DIRECT_EQUIPMENT_LINKED_TO_POLE` category from
  `gridflow/enwl_trace/parser.py`.
- The `fid_polestructure` check: scan all `DIRECT_EQUIPMENT_LINKED_TO_POLE` features
  across trace datasets; if any `feature.fid_polestructure == notes.pole_fid`, this is
  a confirmed HIGH-confidence link.
- The support_no check: scan all `DIRECT_POLE_IDENTITY` features; if any
  `feature.support_no == notes.support_no`, this is a MEDIUM-confidence link.
- If neither mechanism succeeds, check GPS proximity (50 m threshold) as LOW/supporting
  confidence and flag `manual_confirmation_required = True`.
- Never raise; capture errors in `LinkingResult.link_basis_notes`.

### 2. `scripts/link_survey_poles.py`

CLI that runs the linker on every pole folder in a survey root and prints a linking status
table.

```
Usage: python scripts/link_survey_poles.py --survey <path> --trace <path> [--output <json>]

Output (terminal):
  Pole     Support   Pole FID    Confidence  Method               Equipment FIDs
  01       902202    16858852    MEDIUM      support_no + pole_fid
  03       900343    16869661    HIGH        fid_polestructure    11883940
  05       900344    16869657    HIGH        fid_polestructure    73189925
  ...
```

The script should:
- Accept `--survey` (survey root, e.g., `real_pilot_data/P_LOCAL_002`)
- Accept `--trace` (path to one or more trace GeoJSON files, repeatable)
- Accept optional `--output` (write `LinkingResult` records as JSON)
- Exit non-zero if any pole returns `UNLINKED` confidence

### 3. `AI_CONTROL/126_PLOCAL002_LINKING_REPORT.md`

Actual Stage 6C results for all 10 P_LOCAL_002 poles. Format:

- Run command used
- Linking table (all 10 poles)
- Poles with HIGH confidence: list and basis
- Poles with MEDIUM confidence: list and next step
- Any poles unexpectedly unlinked: list and root cause
- Unresolved uncertainties carried forward from Stage 6A spike

---

## Tests Required

Tests belong in `tests/test_evidence_linker.py`.

Minimum coverage:

| Test | What it verifies |
|---|---|
| `test_linker_high_confidence_via_fid_polestructure` | Pole FID in notes + matching `fid_polestructure` in trace → HIGH |
| `test_linker_medium_confidence_via_support_no` | Support no in notes + matching support record in trace → MEDIUM |
| `test_linker_medium_confidence_via_spn` | SPN in notes + matching SPN in pole identity feature → MEDIUM |
| `test_linker_does_not_link_via_conductor_fid` | Conductor FID present in notes and trace → must not return HIGH or MEDIUM |
| `test_linker_gps_only_returns_low_confidence` | GPS proximity match with no identity match → LOW + manual_confirmation_required |
| `test_linker_unlinked_when_no_evidence` | Notes with no extractable identity → UNLINKED |
| `test_linker_design_ready_not_set` | `LinkingResult` has no `design_ready` attribute |
| `test_linker_plocal002_pole03_high` | Real Pole 03 notes + trace → HIGH via fid_polestructure |
| `test_linker_plocal002_pole05_high` | Real Pole 05 notes + trace → HIGH via fid_polestructure |
| `test_linker_plocal002_pole06_high` | Real Pole 06 notes + trace → HIGH via fid_polestructure |
| `test_linker_plocal002_all_10_linked` | All 10 poles in P_LOCAL_002 return MEDIUM or HIGH |

---

## Acceptance Criteria

Stage 6C is complete when:

1. `gridflow/evidence_combiner/linker.py` is written and imports cleanly.
2. `scripts/link_survey_poles.py` runs against `real_pilot_data/P_LOCAL_002` and prints
   a complete linking table.
3. All 10 P_LOCAL_002 poles return MEDIUM or HIGH confidence.
4. Poles 03, 05, and 06 return HIGH via `fid_polestructure`.
5. `AI_CONTROL/126_PLOCAL002_LINKING_REPORT.md` is written with actual run output.
6. All tests in `tests/test_evidence_linker.py` pass.
7. Full `pytest -q` passes with no regressions.
8. `design_ready` is unchanged in every pole record.
9. `conductor_spec_missing` is not cleared by any linking step.

---

## Boundary with Stage 6D

Stage 6C proves that each pole is linked to its ENWL network record with a declared
confidence level. It does not resolve:

- Which conductor FID applies to which span between which two poles.
- Whether a conductor's specification (`cable_size`, `material`, `voltage`) can be used
  to clear `conductor_spec_missing`.
- How LV route conductors (poles 07–10) are assigned to specific spans.

These are Stage 6D concerns. Stage 6C must not anticipate them.

---

## Notes on `123_GRIDFLOW_DELIVERY_STYLE.md`

That document was referenced in the Stage 6C mission brief but does not currently exist
in `AI_CONTROL/`. This spec has been written from first principles using the Stage 6A spike
(121), the Stage 6B spec (124), and the actual combiner code. When 123 is created, this
spec should be reviewed for alignment.
