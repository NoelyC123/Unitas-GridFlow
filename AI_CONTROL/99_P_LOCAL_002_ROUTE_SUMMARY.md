# P_LOCAL_002 Route Summary

**Survey:** P_LOCAL_002
**Evidence root:** `real_pilot_data/P_LOCAL_002/enwl_enrichment_clean/`
**Poles:** 12
**DNO:** ENWL / Electricity North West
**Location:** Jolly's Farm / Station Road / Sheernest Lane, Carnforth area

---

## Route Overview

P_LOCAL_002 contains three distinct sub-routes captured in the same survey package:

| Sub-route | Poles | Voltage | Character |
|---|---|---|---|
| A — 11kV overhead | 01–06 | 11kV | Farm/field route with ABS, transformer, UG transitions |
| B — LV residential (903xxx) | 07–10 | 415V | Residential-side route, Sheernest Lane area |
| C — LV branch (903202–903203) | 11–12 | 415V (probable) | Short LV branch, tee-off + terminal with street light |

Sub-routes A and B are confirmed from enriched ENWL notes. Sub-route C is identified from
folder names and evidence counts; notes are not yet reconciled.

---

## Sub-route A — 11kV Overhead Route (Jolly's Farm / Station Road)

Six poles on the overhead 11kV network. The route includes a tee-off junction, two
overhead-to-underground transitions, and a 100 kVA support-mounted transformer.

### Pole 01 — Support 902202

| Field | Value |
|---|---|
| ENWL FID | 16858852 |
| SPN | 61090H02202 |
| Pole type | Terminal |
| Pole class | Single Wood Pole, Stout |
| Voltage | 11kV |
| Location | Private field, hedge/fence boundary |
| ENWL coordinates | 54.198494, -2.732341 |
| Field GPS pin | 54.198466, -2.732348 (GPS accuracy: 8.7 m) |
| Equipment | None confirmed via `fid_polestructure`; switch/fuse/link uncertain |
| UG transition | Probable — red downlead and cable guard visible |
| Stay | Present |
| Field photos | 6 |
| ENWL screenshots | 14 |
| Map screenshots | 1 |
| Linking confidence | MEDIUM (support_no + pole FID) |
| Evidence quality | HIGH |

Route context: Terminal pole with nearby HV sleeve/joint records (FIDs 16466853,
16467527, 16466840) and underground HV conductor FID 10924867 (95mm2 XLPE) and overhead
conductor FID 10924865 (0.025in2 HDC). Trifurcating joint FID 16466853 suggests a
UG/overhead junction near this pole. Exact span direction to Pole 02 not confirmed.

---

### Pole 02 — Support 902201

| Field | Value |
|---|---|
| ENWL FID | 16793152 |
| SPN | 61090H02201 |
| Pole type | Section |
| Pole class | Single Wood Pole, Medium |
| Voltage | 11kV |
| Location | Open field / field-boundary access |
| Field photos | 10 |
| ENWL screenshots | 7 |
| Map screenshots | 1 |
| Linking confidence | MEDIUM (support_no + pole FID) |
| Evidence quality | HIGH |

Route context: Section pole in the 11kV route sequence between Poles 01 and 03.
No direct `fid_polestructure` equipment link identified. Route-level HV conductor
evidence present (11kV HDC, `3x .025 Cu 11`). Nearby HV sleeve/overhead termination
captured as route context only.

---

### Pole 03 — Support 900343

| Field | Value |
|---|---|
| ENWL FID | 16869661 |
| SPN | 61090H00343 |
| Pole type | Tee-off Intermediate |
| Pole class | Single Wood Pole, Stout |
| Voltage | 11kV |
| Location | Open private field, no major obstructions |
| ENWL coordinates | 54.197240, -2.734666 |
| Field GPS pin | 54.197274, -2.734629 (GPS accuracy: 6.7 m) |
| Direct equipment | FSL/fuse FID 11883940 — `fid_polestructure` = 16869661 confirmed |
| Conductor evidence | HV overhead FID 10863709 (50mm2 Al alloy); route labels `3x .025 Cu 11`, `3x 50 Al 11`, `3x .06 Cu 11` |
| Stay | Present |
| Field photos | 7 |
| ENWL screenshots | 6 |
| Map screenshots | 1 |
| Linking confidence | HIGH (fid_polestructure — FSL switch) |
| Evidence quality | HIGH |

Route context: Network junction where the 11kV route branches. The Fault Sectionalising
Link (Closed, 60A nominal, SPN 5621334SW001) is directly associated with this pole.
Multiple conductor types visible in the surrounding spans, suggesting the tee-off branches
to at least two routes. Exact conductor FID-to-span assignment at the junction is unresolved.

---

### Pole 04 — Support 900342A

| Field | Value |
|---|---|
| ENWL FID | 16896331 |
| SPN | 61090H00342A |
| Pole type | Terminal |
| Pole class | Single Wood Pole, Stout |
| Voltage | 11kV |
| Location | Private field, livestock present, hedge/boundary nearby |
| ENWL coordinates | 54.197868, -2.735843 |
| Direct equipment | None confirmed via `fid_polestructure` |
| UG transition | Probable — red downlead and metal cable guard visible |
| Stay | Present |
| Field photos | 7 |
| ENWL screenshots | 9 |
| Map screenshots | 1 |
| Linking confidence | MEDIUM (support_no + pole FID) |
| Evidence quality | HIGH |

Route context: Terminal pole with multiple nearby HV conductor and sleeve records from
an ENWL trace (27 items, 1081.6 m total length, including underground XLPE 95mm2 and
overhead Al alloy 50mm2 conductors). Sleeve FIDs 53393796 and 16393029 are nearby
context only; not proven directly attached to this pole. The overhead-to-underground
transition context strongly suggests this is a route terminal or feeder change point.

---

### Pole 05 — Support 900344

| Field | Value |
|---|---|
| ENWL FID | 16869657 |
| SPN | 61090H00344 |
| Pole type | Intermediate (ENWL record; see note) |
| Pole class | Single Wood Pole, Stout |
| Voltage | 11kV |
| Location | Jolly's Farm / Station Road, farm field boundary |
| ENWL coordinates | 54.196464, -2.733156 |
| Field GPS pin | 54.196464, -2.733156 (GPS accuracy: 6.4 m) |
| Direct equipment | Fault Making Switch / Isolator FID 73189925 — `fid_polestructure` = 16869657; field label JOLLYS FM ABS / 654678 visible in photos |
| Support-mounted plant | FID 73190411 (Support Mounted, 11kV in/out, plant ref 654678) |
| Conductor evidence | HV overhead FIDs 73190266 + 73190215 (both 50mm2 Al alloy, `3x 50 Al 11`) |
| Stay | Uncertain from photos |
| UG transition | Not confirmed |
| Field photos | 9 |
| ENWL screenshots | 17 |
| Map screenshots | 1 |
| Linking confidence | HIGH (fid_polestructure — ABS/Fault Making Switch) |
| Evidence quality | HIGH |

Route context: Although ENWL records this as Intermediate, it carries an ABS (Auto/Fault
Making Switch, normally Closed, SPN 6546784SW001). This pole should be treated as an
equipment-bearing 11kV intermediate, not a plain through-pole. Strong three-source evidence
case: field photo, visible JOLLYS FM ABS label, ENWL switch record, ENWL plant record, and
confirmed `fid_polestructure` match.

---

### Pole 06 — Support 900345

| Field | Value |
|---|---|
| ENWL FID | 53427080 |
| SPN | 61090H00345 |
| Pole type | Terminal |
| Pole class | Stub Pole, Stout |
| Voltage | 11kV infeed / 415V outfeed |
| Location | Station Road / Mill Pond area, stone wall and boundary |
| ENWL coordinates | 54.196460, -2.733165 |
| Field GPS pin | 54.196444, -2.733178 (GPS accuracy: 4.2–6.4 m) |
| Direct equipment | Transformer FID 20636886 (100 kVA, Support Mounted 3-phase, `fid_polestructure` = 53427080); HV link FID 11835967 (`fid_polestructure` = 53427080); LV way FID 20676285 (415V support-mounted fuse) |
| Conductor evidence | HV overhead FID 73190266 (50mm2 Al alloy, `3x 50 Al 11`) |
| Nearby context | HV sleeve/termination FID 11970601; partial equipment screenshot (plant ref 4253214HF01 / SPN 6511284SW001 — full FID not confirmed) |
| Field photos | 14 |
| ENWL screenshots | 19 |
| Map screenshots | 2 |
| Linking confidence | HIGH (fid_polestructure — transformer + HV link; two independent links) |
| Evidence quality | HIGH |

Route context: This is the strongest single-pole evidence case in P_LOCAL_002. The 100 kVA
transformer (plant ref 6511284TX01, SPN 6511284TX001) supplies a 415V LV outfeed. ENWL
records `pole_class = Stub Pole` but field photos show a double-pole / H-pole arrangement —
a potential field/ENWL structural classification conflict for Stage 6D to investigate. The
transformer is the likely source feed for the 415V residential LV route on Poles 07–10.

---

## Sub-route B — LV Residential Route (Sheernest Lane / Station Road)

Four poles on a 415V LV overhead network running along the rear of residential properties
near Sheernest Lane. Separate from the 11kV farm route and likely fed from the transformer
at Pole 06 (support 900345), though this connection is not yet proven by span-linking.

### Pole 07 — Support 903104

| Field | Value |
|---|---|
| ENWL FID | 53426793 |
| SPN | 61090L03104 |
| Pole type | Terminal |
| Pole class | Single Wood Pole |
| Voltage | 415V LV |
| Location | Residential / property boundary context |
| Direct equipment | None confirmed via `fid_polestructure` |
| Conductor evidence | LV route, 415V, `4x 50 Cu` style context; LV sleeve/overhead termination nearby |
| Field photos | 9 |
| ENWL screenshots | 4 |
| Map screenshots | 2 |
| Linking confidence | MEDIUM (support_no + pole FID) |
| Evidence quality | HIGH |

Route context: Terminal pole at one end of the 903101–903104 LV route. ENWL records
pole_type = Terminal. Likely to have a stay or terminal arrangement, though configuration
not fully confirmed from current notes.

---

### Pole 08 — Support 903103

| Field | Value |
|---|---|
| ENWL FID | 16778530 |
| SPN | 61090L03103 |
| Pole type | Intermediate |
| Pole class | Single Wood Pole, Medium |
| Voltage | 415V LV |
| Location | Sheernest Lane, residential field/property boundary |
| ENWL GPS approx | 54.197465, -2.730234 |
| Direct equipment | None confirmed via `fid_polestructure` |
| Conductor evidence | 415V, Hard Drawn Copper, 50mm2, 4-core, route labels `2x .06 Cu` + `4x 50 Cu` |
| Stay | Present (visible in field photos) |
| Field photos | 7 |
| ENWL screenshots | 4 |
| Map screenshots | 1 |
| Linking confidence | MEDIUM (support_no + pole FID) |
| Evidence quality | HIGH |

Route context: Intermediate pole in the residential LV route. Stay wire visible, runs into
vegetation at field edge. Base partly obscured by vegetation.

---

### Pole 09 — Support 903102

| Field | Value |
|---|---|
| ENWL FID | 16920793 |
| SPN | 61090L03102 |
| Pole type | Section |
| Pole class | Single Wood Pole, Medium |
| Voltage | 415V LV |
| Location | Property boundary / garden-field edge, Sheernest Lane |
| ENWL GPS | 54.197869, -2.730461 |
| Direct equipment | None confirmed via `fid_polestructure` |
| Conductor evidence | `2x .06 Cu` (between 903101–903102) and `4x 50 Cu` (between 903102–903103) |
| Nearby context | sleeve_lv FID 16268427 (240V, Overhead Termination, Single Phase) — nearby context only |
| Stay | Probable from field photos |
| Field photos | 8 |
| ENWL screenshots | 3 |
| Map screenshots | 1 |
| Linking confidence | MEDIUM (support_no + pole FID) |
| Evidence quality | HIGH |

Route context: Section pole between the two conductor sections. The different route labels
on each side (`2x .06 Cu` vs `4x 50 Cu`) suggest a change in conductor type or configuration
somewhere in this section of the route. Exact span assignment unresolved.

---

### Pole 10 — Support 903101

| Field | Value |
|---|---|
| ENWL FID | 16788439 |
| SPN | 61090L03101 |
| Pole type | Section |
| Pole class | Single Wood Pole, Medium |
| Voltage | 415V LV |
| Location | Residential / property-boundary context, northern end of LV route |
| Direct equipment | None confirmed via `fid_polestructure` |
| Conductor evidence | `2x .06 Cu` route label in LV branch context |
| Nearby context | sleeve_lv FID 61933103 (415V, Mains LV, Three Phase) — nearby context only |
| Cable guard | Vertical guard/channel visible in field photos |
| Field photos | 9 |
| ENWL screenshots | 5 |
| Map screenshots | 1 |
| Linking confidence | MEDIUM (support_no + pole FID) |
| Evidence quality | HIGH |

Route context: Section pole at the northern end of the 903101–903104 LV sub-route.
A sleeve_lv record is nearby but not proven directly attached. Cable guard purpose not
confirmed; may indicate a service connection or LV transition.

---

## Sub-route C — LV Branch (903202–903203)

Two additional poles on a short LV branch. Folder names indicate a tee-off and a terminal
with street light. Evidence files are present but notes have not been reconciled with
ENWL screenshots.

### Pole 11 — Support 903202 (LV Tee-Off)

| Field | Value |
|---|---|
| Support number | 903202 (from folder name) |
| ENWL FID | Not confirmed in notes — notes file is empty |
| SPN | Not confirmed |
| Pole type | LV Tee-Off (from folder name; not confirmed from ENWL screenshots) |
| Voltage | 415V probable (LV branch, consistent with sub-route B) |
| Location | Not confirmed |
| Direct equipment | Not confirmed |
| Field photos | 7 |
| ENWL screenshots | 4 |
| Map screenshots | 5 |
| Linking confidence | LOW — folder name only; notes not populated |
| Evidence quality | LOW — evidence present, not yet reconciled |

Action required: Notes file is empty. Evidence must be reconciled from the 7 field photos
and 4 ENWL screenshots before this pole can be used for any linking or readiness assessment.

---

### Pole 12 — Support 903203 (LV Terminal with Street Light)

| Field | Value |
|---|---|
| Support number | 903203 (from folder name; note header says "Support UNKNOWN") |
| ENWL FID | Not confirmed in notes |
| SPN | Not confirmed |
| Pole type | LV Terminal with Street Light (from folder name) |
| Voltage | 415V probable |
| Location | Not confirmed |
| Direct equipment | Not confirmed |
| Field photos | 6 |
| ENWL screenshots | 5 (including screenshots captured 2026-05-17 — recently added) |
| Map screenshots | 3 |
| Linking confidence | LOW — folder name only; note is a placeholder |
| Evidence quality | LOW — evidence present, notes are a placeholder with "Support UNKNOWN" |

Action required: Note header states "Support UNKNOWN" and note body is a placeholder.
The support number in the folder name (903203) should be confirmed against the ENWL
screenshots. The street light attachment is declared in the folder name but not confirmed
from any note or ENWL record. ENWL screenshots captured 2026-05-17 are recent additions
and not yet referenced in any note or audit.

---

## Route-Level Analysis

### Route Continuity

The three sub-routes are internally consistent but their inter-connections are inferred,
not proven from notes:

**Sub-route A (11kV):**

The sequence 01 → 02 → 03 → 04/05/06 is consistent with the ENWL pole types and the
tee-off at Pole 03. Pole 03 (tee-off intermediate) and the presence of multiple conductor
types around it indicate the 11kV route branches at this point. The two terminal poles
(01 and 04) are consistent with route ends or UG transitions. Pole 06 terminates the
route with a 100 kVA transformer.

**Sub-route B (LV 903xxx):**

The sequence 10 → 09 → 08 → 07 is consistent with a simple residential LV overhead run
between supports 903101 and 903104. The transformer at Pole 06 (900345) is the probable
source feed for this LV network — but a formal connecting span/service record has not been
identified in the current evidence.

**Sub-route C (LV 903202–903203):**

Two poles with a tee-off and terminal arrangement. Their relationship to sub-route B or to
the transformer at Pole 06 is not confirmed. Based on support numbering (903202 and 903203
are in the same 903xxx block as sub-route B), they are likely part of the same residential
LV distribution network, but this must be confirmed from the ENWL screenshots.

---

### Voltage Consistency

| Sub-route | All poles confirmed at expected voltage |
|---|---|
| A — 11kV | YES — all 6 poles confirmed 11kV from ENWL records |
| B — 415V LV | YES — all 4 poles confirmed 415V from ENWL records |
| C — 415V probable | NOT YET — inferred from folder context; notes not populated |

---

### Support Type Mix

| Sub-route | Types observed |
|---|---|
| A — 11kV | Terminal (×3), Intermediate/ABS (×1), Tee-off (×1), Stub/H-pole transformer (×1) |
| B — LV | Terminal (×1), Intermediate (×1), Section (×2) |
| C — LV | Tee-off (×1), Terminal with street light (×1) — from folder names only |

Pole 06 is recorded by ENWL as a Stub Pole but field photos show an H-pole / double-pole
arrangement. This is a confirmed structural classification discrepancy and a Stage 6D
conflict candidate.

---

### What Is Proven vs Needs DNO Verification

| Evidence item | Status |
|---|---|
| All 10 pole identities (01–10) | PROVEN — ENWL FID, SPN, support number all confirmed |
| Three direct equipment links (Poles 03, 05, 06) | PROVEN — `fid_polestructure` confirmed |
| Sub-route A voltage | PROVEN — 11kV confirmed all poles |
| Sub-route B voltage | PROVEN — 415V confirmed all poles |
| Sub-route C pole identities | NOT PROVEN — notes empty or placeholder |
| Sub-route C voltage | PROBABLE — not confirmed from notes |
| Transformer feed connection (Pole 06 → sub-route B) | PROBABLE — not span-linked |
| Conductor specification per span | NOT PROVEN — route-level only for all spans |
| Sub-route C to sub-route B connection | NOT PROVEN |
| Pole 06 structural type (stub vs H-pole) | DISCREPANCY — requires Stage 6D review |
| Stay presence on Poles 02, 04, 07 | UNCERTAIN — not confirmed from current notes |
| Pole class/strength ratings | NOT PROVEN — DNO engineering records required |

---

## Summary Assessment

P_LOCAL_002 is a well-evidenced 12-pole survey covering three LV/11kV network sub-routes.
The evidence base for Poles 01–10 is strong and formally linked. Poles 11 and 12 have real
evidence on disk but unreconciled notes, and must not be used for any linking or readiness
assessment until their notes are completed.

**Immediate actions:**

1. Reconcile Pole 11 notes from 7 field photos and 4 ENWL screenshots (notes file is empty).
2. Reconcile Pole 12 notes from 6 field photos and 5 ENWL screenshots, including fresh
   screenshots added 2026-05-17.
3. Confirm sub-route C relationship to sub-route B from ENWL map screenshots.
4. Investigate Pole 06 structural classification discrepancy (ENWL Stub Pole vs field
   H-pole observation) as a Stage 6D conflict.
