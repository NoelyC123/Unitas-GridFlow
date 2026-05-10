# Stage 4 Field Data Dictionary

This dictionary explains every Stage 4B field Noel may see in the iPad pilot
template. Required means required for Stage 4 validation, not required for
every field observation.

## Row identity

| Field | Purpose | Req | Allowed / example | Common mistakes | Validation consequence | Surveyor note |
| --- | --- | --- | --- | --- | --- | --- |
| `pole_id` | Exact support identity used for later Trimble match | Yes | `P008-001` | blank, `unknown`, `n/a`, typo, shortened IDs | blocked | Copy from Trimble exactly |
| `project_id` | Optional provenance for project/job | No | `P008` | using a folder nickname | accepted as text | Use project code if known |
| `file_id` | Optional file or route segment reference | No | `F001` | mixing with job name | accepted as text | Use the survey file segment if known |
| `structure_type` | Support/capture type | No | `EXpole`, `Pol`, `Angle`, `Context`, `Stay`, `PRpole`, `PRangle` | inventing a non-schema value | invalid | Use the closest real structure type only |
| `asset_intent` | Lifecycle/design intent | No | `existing`, `proposed`, `context`, `replacement`, `unknown` | using free text like `new` | invalid | Use `context` for crossing/context-only captures |

## Pole specification

| Field | Purpose | Req | Allowed / example | Common mistakes | Validation consequence | Surveyor note |
| --- | --- | --- | --- | --- | --- | --- |
| `material` | Observed support material | No | `wood`, `concrete`, `steel`, `unknown` | leaving fake guesses | invalid if not in enum | Leave blank if not captured; use `unknown` only when that is the real observation |
| `measured_height_m` | Captured height in metres | No | `9.2` | feet/inches, text like `tall`, slash values | blocked if out of range or invalid | Only fill when actually measured or verified |
| `height_source` | Provenance of height | No | `measured_tape`, `measured_rtk`, `legacy_record`, `estimated` | saying measured without height | review-required or invalid context | Must match how the value was obtained |
| `pole_class` | Pole class or DNO class code | No | `Medium`, `D` | inventing unavailable class | accepted as text | Leave blank unless genuinely known |
| `pole_strength` | Strength rating | No | `7kN` | using class instead of strength | accepted as text | Leave blank if not known on site |
| `pole_material` | Shaft construction material | No | `wood`, `concrete`, `steel`, `composite`, `unknown` | conflicting with `material` | invalid if enum not recognised | Use only if a second material-specific field is genuinely needed |
| `specification` | Manufacturer or DNO spec reference | No | `Spec-12A` | notes instead of a spec code | accepted as text | Leave blank if not confirmed |

## Condition and defects

| Field | Purpose | Req | Allowed / example | Common mistakes | Validation consequence | Surveyor note |
| --- | --- | --- | --- | --- | --- | --- |
| `condition` | Overall condition | No | `good`, `fair`, `poor`, `unsafe`, `unknown` | `excellent`, sentence text | invalid | Pick the closest schema value |
| `defect_type` | Main defect observed | No | `rot`, `split`, `corrosion` | long narrative in this field | accepted as text | Use short label here; detail goes in notes |
| `defect_severity` | Severity of the defect | No | `low`, `medium`, `high`, `critical`, `unknown` | mixing condition words here | invalid | Use only when a defect is recorded |
| `defect_notes` | Detail on defect | No | `Crack below top pin` | repeating whole row context | accepted as text | Keep short and factual |
| `access_notes` | Access or follow-up constraint | No | `Rear garden access required` | using defect content here | accepted as text | Use when a planner needs access context |
| `survey_notes` | Extra survey context | No | `Road crossing context point` | writing unsupported fields here | accepted as text | Keep it observational, not speculative |

## Electrical and conductor

| Field | Purpose | Req | Allowed / example | Common mistakes | Validation consequence | Surveyor note |
| --- | --- | --- | --- | --- | --- | --- |
| `voltage_carried` | Voltage carried by the support | No | `LV`, `11kV`, `33kV`, `110kV`, `unknown` | `11 kV`, guessed voltage | invalid if not recognised | Only fill if clear from evidence |
| `conductor_type` | Conductor construction | No | `bare`, `covered`, `abc`, `underground`, `unknown` | free-text descriptions | invalid | Leave blank if unclear |
| `conductor_size` | Size/code | No | `50mm2`, `DNO-95` | voltage entered here | accepted as text | Use known code or measured size only |
| `phase_configuration` | Phase arrangement | No | `single`, `three`, `split`, `unknown` | `3ph`, `3 phase` | invalid | Use schema value exactly |

## Structural support

| Field | Purpose | Req | Allowed / example | Common mistakes | Validation consequence | Surveyor note |
| --- | --- | --- | --- | --- | --- | --- |
| `stay_present` | Whether a stay exists | No | `yes`, `no`, `unknown` | `none` | invalid | Use `no` when no stay is present |
| `stay_required` | Whether a stay is needed | No | `yes`, `no`, `unknown` | using design guess without evidence | invalid | Use when the need is clear |
| `stay_type` | Stay construction type | No | `down`, `flying`, `strut`, `none`, `unknown` | leaving blank when absence is certain | invalid if unknown token | Use `none` only when no stay is definitely present |
| `stay_condition` | Condition of stay | No | `good`, `fair`, `poor`, `unsafe`, `unknown` | using it without a stay context | invalid | Leave blank if no stay |
| `lean_direction` | Direction of observed lean | No | `north`, `south`, `east`, `west`, `none`, `unknown` | compass text not in schema | invalid | Use `none` only when no lean is known |
| `lean_severity` | Severity of lean | No | `none`, `slight`, `moderate`, `severe`, `unknown` | words like `minor` | invalid | Match this to the visible lean |

## Equipment / pole-top

| Field | Purpose | Req | Allowed / example | Common mistakes | Validation consequence | Surveyor note |
| --- | --- | --- | --- | --- | --- | --- |
| `equipment_present` | Whether pole-top equipment exists | No | `yes`, `no`, `unknown` | `none` | invalid | Use `no` when clearly absent |
| `equipment_type` | Equipment category | No | `transformer`, `switchgear`, `regulator`, `recloser`, `fuse`, `isolator`, `none`, `unknown` | using text like `TX` | invalid | Use `none` only when no equipment is definitely present |
| `equipment_condition` | Equipment condition | No | `good`, `fair`, `poor`, `unsafe`, `unknown` | leaving a value when no equipment | invalid | Leave blank if equipment not observed |
| `equipment_notes` | Equipment detail | No | `Single fuse cutout` | long narrative | accepted as text | Keep concise |

## Capture metadata

| Field | Purpose | Req | Allowed / example | Common mistakes | Validation consequence | Surveyor note |
| --- | --- | --- | --- | --- | --- | --- |
| `capture_source` | How the row was captured | Yes | `surveyor_tablet`, `office_audit`, `historical_record` | free text like `ipad` | required/invalid | Use `surveyor_tablet` for the real pilot |
| `captured_by` | Who captured the row | Yes | `Noel Collins` | initials only with no audit value | required/invalid | Use a stable name |
| `capture_date` | Capture date | Yes | `2026-05-10` | `10/05/2026`, `2026/05/10` | invalid | ISO only: `YYYY-MM-DD` |
| `source` | Library provenance source | No | `structured_capture` | `spreadsheet`, blank guess values | invalid if unsupported | Use `structured_capture` in pilot rows |
| `evidence_status` | Evidence quality state | No | `measured`, `observed`, `legacy_record`, `estimated`, `not_recorded`, `verification_required`, `unknown` | using condition words | invalid | Use this to be honest about evidence strength |
| `photo_reference` | Link to external photo naming | No | `P008-001_01_context.jpg` | full cloud URL, ambiguous name | accepted as text | Must match the evidence folder protocol |
| `confidence_level` | Confidence in the row | No | `high`, `medium`, `low`, `unknown` | inventing percentages | invalid | Use `low` if field verification is still needed |
| `verification_required` | Flags follow-up need | No | `yes`, `no`, `unknown` | `required`, `tbc` | invalid | Use `yes` when the row should not be treated as final |

## Blank versus `none`

- Leave a field blank when the field was not captured.
- Use `none` only for these explicit-none fields:
  - `stay_type`
  - `equipment_type`
  - `lean_direction`
  - `lean_severity`
- Do not use `none` for:
  - `pole_id`
  - `condition`
  - `stay_present`
  - `equipment_present`
  - `capture_date`
