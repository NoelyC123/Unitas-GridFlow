# 23 — Stage 4 Schema Readiness Review

Group-by-group review of the Stage 4 field catalogue
(`app/structured_capture_schema.py`) for runtime-integration readiness.
Companion to [22_STAGE4_TECHNICAL_AUDIT.md](22_STAGE4_TECHNICAL_AUDIT.md);
risks fed into [24_STAGE4_RUNTIME_INTEGRATION_RISKS.md](24_STAGE4_RUNTIME_INTEGRATION_RISKS.md).

For each group, this review covers:

- **Fields** — canonical names and types
- **Allowed values** — schema-declared vocabulary
- **Likely data quality risks** — what real surveyors / designers will
  miscapture
- **Matching dependency** — what external context is needed to join the
  row to a pole
- **UI display risk** — what could go wrong in the popup
- **QA use risk** — what could go wrong if the QA engine consumes the
  field

## Cross-cutting issues (apply to every group)

- **No row identity in the schema.** No `pole_id`, no `project_id`, no
  `file_id`. Every group's "Matching dependency" is the same: external.
- **`"none"` is in `_BLANK_TOKENS`.** Any group whose enum includes
  `"none"` as a valid value (structural support, equipment) is bug-prone
  — the validator silently erases `"none"`. See
  [22_STAGE4_TECHNICAL_AUDIT.md](22_STAGE4_TECHNICAL_AUDIT.md#what-validators-do-not-guarantee).
- **No `source: "structured_capture"` in `app/field_reference.py`.** No
  group's fields have a popup-rendering path today.

---

## 1. Pole specification

### Fields

| Field | Type |
|---|---|
| `pole_class` | string (free) |
| `pole_strength` | string (free) |
| `pole_material` | enum |
| `specification` | string (free) |

### Allowed values

- `pole_material`: `wood` / `concrete` / `steel` / `composite` / `unknown`.
- All others: free text.

### Likely data quality risks

- **`pole_class` is unbounded free text.** A surveyor will write
  `"medium"`, the next surveyor will write `"M"`, the DNO doc says `"M5"`.
  No normalisation today.
- **`pole_strength` overlaps with `pole_class` semantically.** Both
  fields will collect similar values from different surveyors.
  Recommend documenting the distinction or merging.
- **`specification` is the most ambiguous field in the schema.** It's
  free text labelled "DNO or manufacturer specification reference" — no
  format, no examples in the docs.

### Matching dependency

- External: must be joined to a pole by `pole_id` (not in schema).

### UI display risk

- All four fields would render as plain strings. `pole_class` could
  collide visually with a Trimble-derived value in the same row layout
  if the popup doesn't label source clearly.

### QA use risk

- **Low** for `pole_material` (enum, well-bounded).
- **Medium** for the three free-text fields — QA cannot meaningfully
  reason about `pole_class: "medium"` without a normalisation table.

### Recommendations

- Convert `pole_class` to an enum (e.g. DNO-specific `light` / `medium`
  / `heavy` / `extra_heavy` plus per-DNO codes) before QA reads from it.
- Add an example to `pole_strength` and `specification` in
  `STRUCTURED_CAPTURE_TEMPLATE_GUIDE.md` so surveyors don't invent
  conventions.

---

## 2. Condition / defects

### Fields

| Field | Type |
|---|---|
| `condition` | enum |
| `defect_type` | string (free) |
| `defect_severity` | enum |
| `defect_notes` | string (free) |

### Allowed values

- `condition`: `good` / `fair` / `poor` / `unsafe` / `unknown`.
- `defect_severity`: `low` / `medium` / `high` / `critical` / `unknown`.

### Likely data quality risks

- **`defect_type` is unbounded.** The schema description suggests
  `rot / split / lean / woodpecker / corrosion` but the validator
  accepts anything. Two rows recording the same defect as `"rotten"`
  and `"rot"` will not group.
- **`condition` and `defect_severity` will be confused.** A surveyor
  may put the severity into the condition slot ("`condition: critical`"
  is invalid; "`condition: unsafe`" is the right value).
- **No relationship between `condition` and `defect_*` is enforced.** A
  row with `condition: good` and `defect_severity: critical` is
  accepted.

### Matching dependency

- External: `pole_id`.
- Optional: a defect timeline (when was this defect first observed?) is
  not in the schema; surveyors may add date strings to `defect_notes`.

### UI display risk

- Free-text `defect_type` could contain HTML-special characters or be
  unbounded length; popup must escape and truncate.
- Listing both `defect_type` and `defect_notes` could clutter the
  popup unless one is hidden behind a disclosure.

### QA use risk

- **High utility** if `condition` and `defect_severity` are integrated
  — these are the fields the QA engine could use to surface "unsafe
  pole identified by surveyor" as a hard-blocking design issue.
- **Risk:** QA must NOT escalate `condition: poor` to FAIL automatically;
  designers triage. Treat as WARN at most until the rulepack is
  explicit.

### Recommendations

- Convert `defect_type` to an enum drawn from a published taxonomy (NIE
  / SPEN / ENA defect catalogue if one exists).
- Add cross-field warning rules: `condition=good` with any
  `defect_severity` other than `low`/`unknown` should warn.

---

## 3. Electrical / conductor

### Fields

| Field | Type |
|---|---|
| `voltage_carried` | enum |
| `conductor_type` | enum |
| `conductor_size` | string (free) |
| `phase_configuration` | enum |

### Allowed values

- `voltage_carried`: `LV` / `11kV` / `33kV` / `110kV` / `unknown`.
- `conductor_type`: `bare` / `covered` / `abc` / `underground` / `unknown`.
- `phase_configuration`: `single` / `three` / `split` / `unknown`.

### Likely data quality risks

- **Voltage list is incomplete for the GB market.** Missing: `6.6kV`
  (some legacy NIE), `22kV` (occasional farm-supply networks), `132kV`
  (transmission). A surveyor encountering one of these has no valid
  enum and will fall back to `unknown`, losing fidelity.
- **`conductor_size` is free text** but is naturally numeric (e.g.
  "70mm²", "150mm²"). Two surveyors will write `"70mm²"` vs `"70 mm2"`
  vs `"70"`.
- **`phase_configuration: split`** is unusual UK terminology — most
  surveyors say "two-phase". Risk of misclassification.

### Matching dependency

- External: `pole_id`.
- The same conductor often spans multiple poles. A per-span Stage 4
  layer (not yet in scope) would be a more natural home for
  `conductor_type` / `conductor_size` / `phase_configuration`.

### UI display risk

- Voltage strings carry mixed case (`LV` vs `11kV`). Popup labels
  should reflect the canonical case the validator preserves.

### QA use risk

- **Medium-high.** Voltage drives clearance rules. If Stage 4 voltage
  contradicts the rulepack inferred from job geography, QA must flag
  rather than silently accept.
- Phase configuration is currently not used by any QA rule.

### Recommendations

- Extend `VOLTAGE_VALUES` to include `6.6kV`, `22kV`, `132kV`. (Cheap;
  schema-only change.)
- Tighten `conductor_size` to a numeric+unit format (regex) or a
  bounded enum of standard sizes.
- Reconsider whether `conductor_type` / `conductor_size` /
  `phase_configuration` belong on a per-pole record or a per-span /
  per-circuit record. Stage 4 currently treats them as per-pole.

---

## 4. Structural support

### Fields

| Field | Type |
|---|---|
| `stay_present` | boolean_enum |
| `stay_type` | enum |
| `stay_condition` | enum |
| `lean_direction` | enum |
| `lean_severity` | enum |

### Allowed values

- `stay_present`: `yes` / `no` / `unknown`.
- `stay_type`: `down` / `flying` / `strut` / **`none`** / `unknown`.
- `stay_condition`: `good` / `fair` / `poor` / `unsafe` / `unknown`.
- `lean_direction`: **`none`** / `north` / `south` / `east` / `west` / `unknown`.
- `lean_severity`: **`none`** / `slight` / `moderate` / `severe` / `unknown`.

### Likely data quality risks

- **`"none"` is a valid value AND a `_BLANK_TOKENS` member.** This
  group has the highest blast radius from the validator bug — three of
  its five fields have `"none"` as a meaningful value.
- **`stay_present=no` paired with `stay_type=down`** is currently
  accepted. Cross-field consistency not enforced.
- **`lean_direction` cardinal-only.** Real lean can be NE / SW; the
  enum forces a lossy 4-direction quantisation.
- **`lean_severity: slight`** is subjective. No measurement (e.g.
  degrees) is captured.

### Matching dependency

- External: `pole_id`.
- `stay_evidence_status` already exists as a *derived* field in the
  GridFlow output (computed from nearby `Stay` records). Stage 4 must
  reconcile with that derived field rather than overwrite it.

### UI display risk

- A row with `stay_type: none` correctly captured today renders as
  blank in the popup post-`normalise_stage4_row`. A reviewer would
  read this as "stay_type not captured" — the opposite of the truth.

### QA use risk

- **High.** A clear `lean_severity: severe` from a surveyor is
  actionable evidence; the QA engine should surface it. But the
  `"none"` bug means a row stating `lean_severity: none` (the safe
  answer) is indistinguishable from a row that didn't capture lean at
  all. Until the bug is fixed, QA cannot distinguish "checked, fine"
  from "didn't check".

### Recommendations

- **Highest priority:** disambiguate `"none"` vs blank in the validator
  before any field in this group is consumed by QA or popup rendering.
- Replace `lean_direction` with a numeric `lean_bearing_degrees`
  (optional) or extend the enum to 8 cardinals.
- Add `lean_severity_degrees` (optional numeric) for designers who
  measure rather than estimate.

---

## 5. Equipment / pole-top

### Fields

| Field | Type |
|---|---|
| `equipment_present` | boolean_enum |
| `equipment_type` | enum |
| `equipment_condition` | enum |
| `equipment_notes` | string (free) |

### Allowed values

- `equipment_present`: `yes` / `no` / `unknown`.
- `equipment_type`: `transformer` / `switchgear` / `regulator` /
  `recloser` / `fuse` / `isolator` / **`none`** / `unknown`.
- `equipment_condition`: `good` / `fair` / `poor` / `unsafe` / `unknown`.

### Likely data quality risks

- **`"none"` collision** (same as structural support). A pole with
  `equipment_type: none` is treated as not-captured.
- **A pole can carry multiple equipment items** (transformer plus
  fuse). The schema models a single `equipment_type` per row. A
  surveyor encountering a transformer + isolator combination has no
  clean way to express it.
- **`equipment_present=no` paired with `equipment_type=transformer`**
  is currently accepted. Cross-field check absent.

### Matching dependency

- External: `pole_id`.
- A future equipment-line layer (transformers per circuit, switchgear
  per substation feeder) would tie individual equipment items to
  network elements rather than poles. Stage 4 currently flattens.

### UI display risk

- `equipment_notes` is unbounded free text. Same escape/truncate
  caution as `defect_notes`.

### QA use risk

- **Medium-high.** Pole-top equipment changes clearance, span limits,
  and replacement scope. QA could meaningfully use `equipment_type`
  + `equipment_condition` for design-readiness checks.
- **Risk** that a surveyor records `equipment_type: transformer` on a
  pole that just has a stay → corrupts the design record.

### Recommendations

- Allow multi-valued `equipment_type` (semicolon-separated list, or a
  separate per-equipment Stage 4 row keyed on pole + equipment_id).
- Same `"none"` disambiguation as structural support.
- Add example matrices to the template guide for common
  transformer/switchgear/fuse combinations.

---

## 6. Capture metadata

### Fields

| Field | Type | Required? |
|---|---|---|
| `capture_source` | enum | **yes** |
| `captured_by` | string (free) | **yes** |
| `capture_date` | date | **yes** |
| `confidence_level` | enum | no |
| `verification_required` | boolean_enum | no |

### Allowed values

- `capture_source`: `surveyor_tablet` / `surveyor_paper` / `office_audit`
  / `designer_input` / `historical_record` / `unknown`.
- `confidence_level`: `high` / `medium` / `low` / `unknown`.
- `verification_required`: `yes` / `no` / `unknown`.

### Likely data quality risks

- **`captured_by` is free text.** Two rows recorded as `"N. Collins"`
  and `"N Collins"` are different identities. No internal user table
  to bind against.
- **`capture_date` is not format-checked.** Schema declares
  `type="date"` but the validator only checks blank-or-not. A row with
  `capture_date: "yesterday"` passes.
- **`confidence_level` is self-reported.** A surveyor's "high
  confidence" is not the same as a designer's. No calibration mechanism.
- **`verification_required` and `confidence_level` are independent.** A
  `confidence: low, verification_required: no` row is valid but
  probably unwanted.

### Matching dependency

- None for the metadata itself, but the metadata is the *only* part of
  a Stage 4 row that proves provenance once it's joined to a pole.

### UI display risk

- All five fields are short and structured; popup rendering is
  straightforward.
- The popup must label every Stage 4 value with `capture_source` and
  `capture_date` — the metadata's whole reason for existing.

### QA use risk

- **Critical.** This is the group QA must check **first** before
  reading any asset field. A `confidence_level: low` row should not
  produce a hard-blocking QA item; an `office_audit` row from years ago
  may be stale; a `designer_input` row may be most current.
- The QA rulepack will need a Stage-4-aware confidence weighting.

### Recommendations

- Add ISO-8601 format validation for `capture_date` before runtime
  integration.
- Add a cross-field rule: `confidence_level: low` ⇒
  `verification_required: yes` (warn otherwise).
- Consider lookup of `captured_by` against a known-workers list when
  Stage 4 is wired into the office workflow.

---

## Required-metadata gaps

Beyond the per-group recommendations:

| Missing field | Why it matters |
|---|---|
| `pole_id` | The most fundamental gap. Without it, no row can be joined to a survey. |
| `project_id` / `file_id` | `pole_id` alone is not globally unique across jobs. |
| `survey_run_id` or `superseded_by` | A Stage 4 row recorded today should be marked when a later row supersedes it. The schema is currently append-only by date but has no explicit chain. |
| `stage4_row_id` | Internal identifier so two rows that disagree can be referenced unambiguously in QA logs. |

These are integration-time additions (per the audit's "do not integrate
until" checklist in [24_STAGE4_RUNTIME_INTEGRATION_RISKS.md](24_STAGE4_RUNTIME_INTEGRATION_RISKS.md)).

## Fields needing stronger enums or normalisation before runtime integration

In priority order:

1. `pole_class` — convert from free text to enum.
2. `defect_type` — convert from free text to enum (taxonomy ref needed).
3. `conductor_size` — enforce numeric + unit pattern.
4. `voltage_carried` — extend to cover real GB voltages (`6.6kV`,
   `22kV`, `132kV`).
5. `lean_direction` — extend cardinals or replace with bearing degrees.
6. `equipment_type` — allow multi-value (semicolon list or separate row).
7. `captured_by` — bind against a workers list once an internal
   identity layer exists.

## Cross-references

- [22_STAGE4_TECHNICAL_AUDIT.md](22_STAGE4_TECHNICAL_AUDIT.md) — top-level audit + reproduced bugs.
- [24_STAGE4_RUNTIME_INTEGRATION_RISKS.md](24_STAGE4_RUNTIME_INTEGRATION_RISKS.md) — risks of integrating before fixes land.
- [docs/STAGE4_STRUCTURED_CAPTURE.md](../docs/STAGE4_STRUCTURED_CAPTURE.md) — original Stage 4 rationale.
- [docs/STRUCTURED_CAPTURE_TEMPLATE_GUIDE.md](../docs/STRUCTURED_CAPTURE_TEMPLATE_GUIDE.md) — surveyor-facing template instructions.
