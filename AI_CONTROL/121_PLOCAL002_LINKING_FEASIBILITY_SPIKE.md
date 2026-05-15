# Stage 6A-0 — P_LOCAL_002 Linking Feasibility Spike

## Purpose

This document checks how safely GridFlow can link ENWL/DNO evidence to field-surveyed poles in the P_LOCAL_002 evidence set. The aim is to separate direct pole identity evidence, directly pole-linked equipment evidence, route/span evidence, and nearby context so Stage 6A can display evidence provenance without overstating design readiness.

The core question is: when an ENWL popup, equipment record, conductor record, trace item, or route label appears in the evidence pack, how confidently can GridFlow associate it with the surveyed pole?

## Scope

Evidence analysis only. This spike reviews:

- `real_pilot_data/P_LOCAL_002/enwl_enrichment_clean/`
- `real_pilot_data/P_LOCAL_002/route_notes/P_LOCAL_002_EVIDENCE_AUDIT.md`
- each pole folder's `notes/pole_notes.md`
- current control-layer caution in `AI_CONTROL/01_CURRENT_STATE.md` and `AI_CONTROL/02_CURRENT_TASK.md`

## Out of Scope

- No `design_ready` changes.
- No automatic `conductor_spec_missing` clearance.
- No automatic span linking.
- No runtime implementation.
- No matching, merge, or report logic changes.
- No image movement, renaming, deletion, or evidence-folder editing.

## Evidence Confidence Levels

**Level 1 — Direct pole identity evidence**

Evidence that identifies the physical pole itself:

- support number
- pole FID
- SPN
- ENWL pole popup
- field plate/marking
- GPS/map pin

**Level 2 — Direct pole-linked equipment evidence**

Equipment evidence that explicitly references the pole FID, or plant records that clearly match visible field equipment:

- transformer/switch/link/LV way where `fid_polestructure` equals the pole FID
- plant record clearly matching visible field equipment

**Level 3 — Route/span evidence**

Network evidence that appears to describe the route, trace, or span context, but is not yet proven to attach to a specific pole or exact span:

- conductor FIDs
- cable/conductor labels
- trace GeoJSON or CSV line features
- route labels such as `3x 50 Al 11`, `4x 50 Cu`, `2x .06 Cu`

**Level 4 — Nearby context only**

Nearby network features that may be relevant but are not proven to be attached to the surveyed pole:

- nearby sleeve/termination/service records
- adjacent route labels
- underground/transition records not directly linked to the pole

## Final P_LOCAL_002 Evidence Set

Final audit summary from `P_LOCAL_002_EVIDENCE_AUDIT.md`:

- Pole folders: 10
- Known support numbers: 10/10
- Notes present: 10/10
- Folders with missing evidence flags: 0/10

Support folders:

1. `01_SUPPORT_902202`
2. `02_SUPPORT_902201`
3. `03_SUPPORT_900343`
4. `04_SUPPORT_900342A`
5. `05_SUPPORT_900344`
6. `06_SUPPORT_900345`
7. `07_SUPPORT_903104`
8. `08_SUPPORT_903103`
9. `09_SUPPORT_903102`
10. `10_SUPPORT_903101`

Important note: the final audit confirms the folder-level evidence set is complete. However, the `pole_notes.md` files for poles 02, 07, and 10 still contain draft placeholder text showing `Support UNKNOWN` and old missing-evidence bullets. This spike treats those notes as incomplete and does not infer pole FID, SPN, equipment, or conductor links from the folder name alone.

## Per-Pole Linking Review Table

| Pole | Support | Pole FID | SPN | Route Context | Level 1 Pole Identity | Level 2 Direct Equipment | Level 3 Conductor/Route Evidence | Level 4 Nearby Context | Link Confidence | Remaining Uncertainties |
|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 902202 | 16858852 | 61090H02202 | 11kV route / terminal with overhead and underground context | Strong: support marking visible, ENWL FID/SPN, ENWL coordinates, field GPS pin, ENWL pole record | None proven by `fid_polestructure`; switch/fuse/link uncertain from photos | HV conductor FIDs 10924865, 10924867, 10906700 and route label context are present but not span-linked | HV sleeves/joints/terminations FIDs 16466853, 16467527, 16466840 nearby/associated but not proven direct | HIGH identity; MEDIUM route/equipment linkage | Exact relationship between pole FID and conductor FIDs; whether trifurcating joint and terminations are directly associated; exact direction to Pole 02; whether downlead/guard is HV underground transition |
| 02 | 902201 | Not stated in pole note | Not stated in pole note | Probable 11kV route by folder order between 902202 and 900343, but not confirmed in note | Folder/audit identify support 902201; pole note itself is a draft placeholder and does not confirm support, field marking, ENWL popup, FID, SPN, or GPS | None stated | None stated | None stated | LOW from note content; folder-level support known only | Pole notes need reconciliation with final audit; no FID/SPN/equipment/conductor evidence available in `pole_notes.md`; route assignment should remain tentative |
| 03 | 900343 | 16869661 | 61090H00343 | 11kV tee-off / junction branch | Strong: visible support plate 90 03 43, ENWL pole FID/SPN, GPS match, ENWL pole record | Strong: Fault Sectionalising Link / fuse FID 11883940 references pole structure FID 16869661 | HV conductor FID 10863709 plus route labels `3x .025 Cu 11`, `3x 50 Al 11`, `3x .06 Cu 11`; route/span assignment unresolved | Wider branch context at tee-off | HIGH identity and direct equipment; MEDIUM conductor route linkage | Exact conductor FID per connected span/branch; whether all visible top hardware corresponds to link/fuse record; exact sequence from Pole 02 to Pole 03 and onward branches |
| 04 | 900342A | 16896331 | 61090H00342A | 11kV terminal / overhead-to-underground transition context | Strong: support 900342A, ENWL pole popup, SPN, field photos, map pin | No direct `fid_polestructure` equipment link stated | Route-level trace and conductor evidence: FIDs 10827785, 10863709, 10827786, 10506239, 6212310, 6212299, 10822188, 75418548, 73190215; not pole/span-linked | Sleeve/termination FIDs 53393796 and 16393029; underground/transition records nearby | HIGH identity; MEDIUM route/transition linkage | Exact relationship between pole FID 16896331 and conductor/sleeve FIDs; whether underground transition is directly from this pole or adjacent asset; previous/next pole sequence |
| 05 | 900344 | 16869657 | 61090H00344 | 11kV overhead route / Jolly's Farm ABS equipment context | Strong: support plate 90 03 44, ENWL pole record, pole FID/SPN, GPS/map pin | Strong: Fault Making Switch / isolator FID 73189925 references `fid_polestructure` 16869657; visible JOLLYS FM ABS / 654678 label aligns with plant record; support-mounted plant/substation FID 73190411 | HV conductor FIDs 73190266 and 73190215; route labels `3x 50 Al 11`, `3x .025 Cu 11`, underground/transition context; not exact span-linked | Nearby underground/transition route context `3c 185 SAC XC TP` | HIGH identity and direct equipment; MEDIUM conductor route linkage | Exact span direction to poles 04 and 06; whether stay wire present; conductor FID-to-span relationship; operational switch status is time-specific |
| 06 | 900345 | 53427080 | 61090H00345 | 11kV route with 11kV/415V support-mounted transformer context | Strong: support 900345 from ENWL popup, field plate 90 03 45, pole FID/SPN, map/GPS screenshots | Strong: transformer FID 20636886 references `fid_polestructure` 53427080; HV link FID 11835967 references `fid_polestructure` 53427080; LV way FID 20676285 supports 415V outfeed/fuse context | HV conductor FID 73190266 and route label `3x 50 Al 11`; not exact span-linked | HV sleeve/termination FID 11970601 and additional partial equipment screenshot; underground/transition context nearby | HIGH identity and direct equipment; MEDIUM conductor route linkage | Exact physical pole members represented by support 900345; stay/anchor presence; upstream/downstream spans to 900344 and 900346; full title/FID for partial equipment screenshot |
| 07 | 903104 | Not stated in pole note | Not stated in pole note | Likely separate LV branch by route context in poles 08/09, but not confirmed in pole note | Folder/audit identify support 903104; pole note itself is a draft placeholder and does not confirm support, field marking, ENWL popup, FID, SPN, or GPS | None stated | None stated | None stated | LOW from note content; folder-level support known only | Pole notes need reconciliation with final audit; no FID/SPN/equipment/conductor evidence available in `pole_notes.md`; LV branch assignment is inferred from adjacent notes only |
| 08 | 903103 | 16778530 | 61090L03103 | Separate 415V LV overhead residential-side route | Strong: ENWL popup confirms 903103, field plate appears consistent with 90 31 03, pole FID/SPN, map capture | None with explicit `fid_polestructure` stated | LV route evidence: 415V, Hard Drawn Copper, 50mm2, 4-core, route labels `2x .06 Cu`, `4x 50 Cu`; no exact span/FID link yet | Nearby LV sleeve/termination/service context; no automatic attachment to pole | HIGH identity; MEDIUM LV route linkage | Exact relationship between LV conductor FIDs, sleeve records, and support 903103; whether all photos belong only to support 903103; access/permission status |
| 09 | 903102 | 16920793 | 61090L03102 | Separate LV overhead route / Sheernest Lane residential boundary | Strong: ENWL pole popup and field plate/photo evidence confirm 903102, pole FID/SPN, GPS reference | None with explicit `fid_polestructure` stated | LV route labels `2x .06 Cu` between 903101-903102 and `4x 50 Cu` between 903102-903103; not span-linked by FID in note | Nearby sleeve_lv FID 16268427, 240V overhead termination/service evidence; exact attachment not proven | HIGH identity; MEDIUM LV route linkage | Exact sleeve_lv relationship to Pole 09; conductor/span assignment between 903101, 903102, 903103; stay/support wire confirmation |
| 10 | 903101 | Not stated in pole note | Not stated in pole note | Likely separate LV branch by route context in poles 08/09, but not confirmed in pole note | Folder/audit identify support 903101; pole note itself is a draft placeholder and does not confirm support, field marking, ENWL popup, FID, SPN, or GPS | None stated | None stated | None stated | LOW from note content; folder-level support known only | Pole notes need reconciliation with final audit; no FID/SPN/equipment/conductor evidence available in `pole_notes.md`; LV branch assignment is inferred from adjacent notes only |

## Key Findings

### 1. Which poles have strong direct pole identity evidence?

Strong Level 1 pole identity evidence is present in the notes for poles 01, 03, 04, 05, 06, 08, and 09. These notes include combinations of visible support marking or field plate, ENWL pole popup/record, pole FID, SPN, GPS/map pin, and field-photo confirmation.

Poles 02, 07, and 10 have known support numbers at the folder/audit level, but their `pole_notes.md` files are still draft placeholders. Stage 6A should not treat those notes as confirmed pole identity evidence until they are reconciled with the final audit and ENWL screenshots.

### 2. Which poles have direct equipment links via `fid_polestructure`?

Clear Level 2 direct equipment links are present for:

- Pole 03 / support 900343: Fault Sectionalising Link / fuse FID 11883940 references pole structure FID 16869661.
- Pole 05 / support 900344: Fault Making Switch / isolator FID 73189925 references `fid_polestructure` 16869657; field label JOLLYS FM ABS / 654678 aligns with plant record.
- Pole 06 / support 900345: transformer FID 20636886 and HV link FID 11835967 both reference `fid_polestructure` 53427080; LV way FID 20676285 supports the transformer LV outfeed context.

No directly pole-linked equipment record is stated in the notes for poles 01, 02, 04, 07, 08, 09, or 10.

### 3. Which conductor records remain route/span evidence only?

All conductor evidence in the reviewed notes remains Level 3 route/span evidence, not design-ready per-pole conductor specification.

Examples include:

- Pole 01: conductor FIDs 10924865, 10924867, 10906700.
- Pole 03: HV conductor FID 10863709 and surrounding route labels.
- Pole 04: HV conductor/trace FIDs including 10827785, 10863709, 10827786, 10506239, 6212310, 6212299, 10822188, 75418548, 73190215.
- Pole 05: HV conductor FIDs 73190266 and 73190215.
- Pole 06: HV conductor FID 73190266.
- Pole 08: LV conductor context, including 415V 4-core 50mm2 copper route evidence and route labels `2x .06 Cu`, `4x 50 Cu`.
- Pole 09: LV route labels `2x .06 Cu` and `4x 50 Cu`.

None of these should be treated as confirmed per-pole conductor specification until the exact conductor FID to span/pole relationship is proven.

### 4. Which route separation issues exist between 11kV and LV sections?

P_LOCAL_002 contains at least two distinct route contexts:

- 11kV Jolly's Farm / Station Road route: poles 01, 03, 04, 05, and 06 are explicitly documented as 11kV route evidence. Pole 02 is probably in this sequence by folder order and adjacent notes, but its own note does not confirm this.
- Separate LV / residential-side route: poles 08 and 09 are explicitly documented as a separate LV route around Sheernest Lane / Station Road, with supports 903101, 903102, 903103, and 903104. Poles 07 and 10 are likely part of that LV branch by folder support and adjacent route context, but their own notes do not confirm this.

Stage 6A should display route context as a relationship type and should not merge 11kV and LV route evidence into a single undifferentiated conductor context.

### 5. Is GPS proximity enough for linking?

No. GPS/map proximity supports Level 1 pole identity evidence, but it is not sufficient to attach conductor, sleeve, termination, transformer, switch, or LV way records to a pole.

The strongest linking evidence is explicit identifier matching:

- support number and SPN for pole identity,
- pole FID from ENWL pole popup,
- `fid_polestructure` matching the pole FID for direct equipment.

GPS proximity can help a reviewer detect likely matches or errors, but Stage 6A should not use it as the sole basis for equipment or conductor linking.

### 6. What can Stage 6A safely parse/display?

Stage 6A can safely parse and display:

- direct pole identity fields: support number, pole FID, SPN, ENWL pole record, field marking status, map/GPS evidence;
- direct equipment records where `fid_polestructure` equals the pole FID;
- route/span conductor records as route-level evidence;
- nearby sleeve, termination, service, underground, or transition records as nearby context only;
- route separation between the 11kV farm route and the separate LV residential route;
- explicit unresolved uncertainties from the pole notes.

Stage 6A should present these as evidence relationships, not as design authorization.

### 7. What must wait until Stage 6C/6E?

The following should wait for later stages:

- automatic conductor-to-span assignment;
- trace FID to span geometry matching;
- conductor FID to pole/support linkage;
- automated voltage/conductor/pole-class clearance;
- any change to `design_ready` or verification-flag logic;
- any use of ENWL conductor evidence to clear `conductor_spec_missing`;
- any assertion that nearby sleeve/termination records are mounted on or directly associated with a pole without explicit linkage.

## Recommended Stage 6A Requirements

Stage 6A parser/display should classify ENWL evidence by relationship strength:

1. **Direct pole identity**
   - support number
   - pole FID
   - SPN
   - ENWL pole popup
   - field plate/marking
   - GPS/map pin

2. **Direct equipment linked to pole FID**
   - transformer/switch/link/LV way records where `fid_polestructure` equals the pole FID
   - plant records that clearly match visible field equipment and asset references

3. **Route/span conductor evidence**
   - conductor FIDs
   - trace line records
   - overhead/underground conductor labels
   - route labels
   - span context where exact pole/span linkage is not yet proven

4. **Nearby context only**
   - sleeve/joint/termination records not directly linked to the pole
   - service records
   - underground transition records
   - adjacent route labels

The display should make the relationship type visible to the reviewer. For example, a conductor popup should be shown as "route-level evidence / not yet span-linked" unless the source note explicitly proves the exact span/FID relationship.

Stage 6A should also flag note-level inconsistencies. In this dataset, poles 02, 07, and 10 have final audit support numbers but draft `pole_notes.md` content. That mismatch should be visible to reviewers before any automated parsing is trusted.

## Explicit Design-Readiness Caution

This spike does not change `design_ready`.

This spike does not clear `conductor_spec_missing`.

This spike does not authorize final design.

Conductor evidence in P_LOCAL_002 is valuable DNO provenance, but it remains route-level evidence or nearby conductor context until the exact conductor/span/pole relationship is proven. Poles without confirmed conductor specification and pole class/strength rating remain design-blocked under the current readiness model until the relevant DNO engineering records and linking chain are obtained and verified.
