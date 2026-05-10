# 24 — Stage 4 Runtime Integration Risks

Catalogue of the concrete failure modes if Stage 4 structured-capture
data is wired into the live upload, QA, and popup pipeline before the
foundation is hardened. Companion to
[22_STAGE4_TECHNICAL_AUDIT.md](22_STAGE4_TECHNICAL_AUDIT.md) and
[23_STAGE4_SCHEMA_READINESS_REVIEW.md](23_STAGE4_SCHEMA_READINESS_REVIEW.md).

This is risk analysis only. Mitigations are prescriptive but
implementation belongs to a separate scoped branch.

## Risk overview (at a glance)

| Risk | Severity | Detected today? | Fix is library-only? |
|---|---|---|---|
| Stage 4 data merged into popup with no source label | High | No | No (popup + field_reference) |
| `pole_id` join is ambiguous (no identity in schema) | High | No | Yes (schema + validators) |
| `"none"` enum erased by `_BLANK_TOKENS` | High | No | Yes (validators) |
| Two Stage 4 rows for the same pole conflict | High | No | No (needs merge policy) |
| Low-confidence Stage 4 row treated as hard truth by QA | High | No | No (needs rulepack-aware weighting) |
| Free-text Stage 4 value visually mistaken for measured Trimble value | Medium | No | No (popup labelling) |
| Popup clutter: every Stage 4 field rendered always | Medium | No | No (popup design) |
| Duplicate rows from same surveyor on same date | Medium | No | Yes (validators) |
| `capture_date` accepts non-ISO strings | Medium | No | Yes (validators) |
| Cross-field inconsistency (e.g. `stay_present=no, stay_type=down`) | Low-medium | No | Yes (validators) |

## Risks if Stage 4 is integrated too early

### 1. Designers will trust unverified data

The whole point of GridFlow's truthfulness rules
([FIELD_REFERENCE_GUIDE.md](../docs/FIELD_REFERENCE_GUIDE.md)) is to
keep "captured by survey" distinct from "captured by office". Wiring
Stage 4 into the popup before the renderer enforces a *source label*
on every Stage 4 row will erase that distinction. Designers will see
`condition: poor` next to `height: 9.5m` and treat both as observed
field measurements when one is a designer-keyed string.

### 2. QA escalations will fire on opinions, not evidence

Every Stage 4 enum (`condition`, `defect_severity`, `lean_severity`,
`equipment_condition`) is a human judgement. If `qa_engine.run_qa_checks`
treats `condition: unsafe` as a hard FAIL the moment Stage 4 lands, the
issue list becomes dominated by other people's subjective ratings
rather than measured evidence. Some of those ratings will be wrong.

### 3. The "none vs blank" bug becomes a data corruption bug

Today, `is_blank("none")` returns `True` and `validate_allowed_value`
short-circuits at line 111 before the enum match step (reproduced in
[22_STAGE4_TECHNICAL_AUDIT.md](22_STAGE4_TECHNICAL_AUDIT.md)). A
surveyor row stating `stay_type: none, equipment_type: none,
lean_severity: none` — i.e. "I checked, there's no stay, no equipment,
no lean" — is silently rewritten to all-`None` and classified as a
"minimum" row. If Stage 4 integration writes the post-`normalise`
result into job storage, the captured fact "no stay here" is destroyed
on first read.

### 4. Popups become unscannable

The Stage 4 schema has 26 fields. The current popup layout is tuned
for ~10 informative rows. Naïvely appending all Stage 4 fields will
push real measured evidence below the fold and force scrolling on
every popup, including those for poles with no Stage 4 data. The
popup-readability check in the manual review harness will start
failing.

## Risks around `pole_id` matching

### Gap

The Stage 4 schema does not include a `pole_id` field. The docs assert
"per-pole keyed by `pole_id`" but the template generator produces a
CSV that has no column to record one.

### Failure modes

- **Surveyor invents a column.** Free-form `pole_id` columns produce a
  warning ("Unknown Stage 4 columns ignored") and are dropped during
  validation — silent data loss.
- **Job-local `pole_id` collisions.** Trimble `pole_id` is the survey
  point number from column 0 of the controller dump. Multiple jobs
  each have a `pole_id: 1`. A Stage 4 CSV that travels between jobs
  has no built-in disambiguation.
- **Re-numbered surveys.** A re-survey changes point numbers; old
  Stage 4 rows now point at the wrong pole.

### Mitigations (in priority order)

1. Add `pole_id`, `project_id`, `file_id` to the schema (mark all three
   required for any non-metadata-only row).
2. Reject rows whose `pole_id` does not match an existing pole in the
   referenced project/file (validator helper, not just schema).
3. Document the join key clearly in
   [STRUCTURED_CAPTURE_TEMPLATE_GUIDE.md](../docs/STRUCTURED_CAPTURE_TEMPLATE_GUIDE.md).
4. Optionally add a stable `gridflow_uuid` per pole that survives
   re-numbering (schema-level, separate task).

## Risks around duplicate rows

### Failure modes

- Two surveyors record the same pole on the same day with different
  `confidence_level` values.
- A designer corrects a surveyor's row by re-recording without removing
  the original.
- A bulk-import reruns the same CSV twice.

### Validator behaviour today

`validate_stage4_rows` returns a per-row results list and an aggregate
`valid` flag. It does **not** check for duplicates within the batch.
There is no "primary key" since `pole_id` is not in the schema.

### Mitigations

1. Once `pole_id` lands in the schema, add a "duplicate `pole_id` in
   batch" warning in `validate_stage4_rows`.
2. Define a merge policy (latest `capture_date` wins? highest
   `confidence_level`? designer overrides surveyor?) and document it
   before integration.
3. Treat this as a non-blocking warning, not an error — designers may
   intentionally want a history of conflicting captures.

## Risks around conflicting values

Two Stage 4 rows for the same pole can disagree (e.g. surveyor says
`condition: good`, designer says `condition: poor`).

### Failure modes

- The merge silently picks one (whichever the implementation iterates
  to last) and discards the other.
- The popup shows one value; the QA log uses the other.
- Reviewers cannot trace which source produced the chosen value.

### Mitigations

1. Define a deterministic merge order (`capture_source` priority:
   `designer_input` > `office_audit` > `surveyor_tablet` >
   `surveyor_paper` > `historical_record` > `unknown`).
2. Log the discarded values somewhere accessible (a per-pole "conflict
   history" structure).
3. Surface conflicts in the popup with an explicit "designer
   over-rode surveyor" badge — never just show the winner.
4. QA engine reads from the merged record but the conflict history
   stays accessible for triage.

## Risks around low-confidence data

The schema collects `confidence_level` (`high`/`medium`/`low`/`unknown`)
and `verification_required` (`yes`/`no`/`unknown`).

### Failure modes

- QA treats a `confidence_level: low` row as authoritative and fires
  hard-blocking design issues from it.
- A `confidence: high, verification_required: yes` row (which is a
  surveyor saying "I'm sure but please double-check") is interpreted
  the same as a `confidence: high, verification_required: no` row
  (which is "I'm sure, no follow-up needed").
- Popup labelling does not communicate confidence.

### Mitigations

1. Build a Stage-4-aware confidence weighting into the QA engine:
   - `confidence: high` ⇒ same weight as Trimble-derived data.
   - `confidence: medium` ⇒ WARN, not FAIL.
   - `confidence: low` or `verification_required: yes` ⇒ never escalate.
   - `confidence: unknown` ⇒ treat as `low`.
2. Popup must surface confidence next to the value, not under a
   collapsible details section. A muted "low confidence" tag is the
   minimum.

## Risks around making Stage 4 values look like Trimble measured evidence

### Failure modes

- Popup renders Stage 4 `pole_class: medium` in the same row layout as
  Trimble `height: 9.5m` with no visual distinction.
- PDF reports list both as "Survey data".
- Downstream PoleCAD / D2D exports lose the source attribution
  entirely.

### Mitigations

1. Register every Stage 4 field in `app/field_reference.py` with
   `source: "structured_capture"` (parallel to today's `survey` /
   `trimble_attr` / `derived`).
2. Update `format_field_display` / `get_popup_display_value` in
   `app/field_validators.py` to emit a source label per field.
3. Update the popup CSS to render structured-capture rows with a
   different background or accent so the visual distinction is obvious.
4. PDF / export code paths (audit separately): include a "Stage 4
   structured capture" section header rather than mixing into Trimble
   columns.

## Risks around popup clutter

### Failure modes

- The popup-readability check
  ([VALIDATION_WORKFLOW.md](../docs/VALIDATION_WORKFLOW.md)) starts
  failing because the popup exceeds the viewport.
- Designers learn to ignore the popup because it is dominated by
  "unknown" Stage 4 fields.
- The "Not recorded in survey" wording (the C2E2 truthfulness rule)
  collides with Stage 4 fields that legitimately *are* "unknown".

### Mitigations

1. Render Stage 4 fields conditionally — only show fields that are
   non-blank AND not equal to `"unknown"`.
2. Group Stage 4 fields under a collapsible "Designer / structured
   capture" section.
3. Add a manual-review checklist for Stage 4 popup readability before
   the integration branch lands.
4. Test specifically with `P008/F001` and `P010` once Stage 4 rows
   exist for those jobs — these are the canonical reference jobs and
   they currently have no Stage 4 data.

## Risks around QA engine treating structured capture as hard truth

The QA engine today only acts on Trimble-captured + GridFlow-derived
fields. Stage 4 fields will tempt the engine to fire on opinions.

### Failure modes

- `condition: unsafe` triggers a FAIL on a pole the surveyor never
  actually inspected (a designer guessed).
- `defect_type: split` triggers a clearance check that fires on every
  pole because the rulepack can't tell which kind of split.
- `voltage_carried: 33kV` from Stage 4 contradicts the rulepack's job-
  level voltage; QA flips clearance rules silently.

### Mitigations

1. Treat *every* Stage 4 field as evidence-only (WARN at most) until a
   per-field rulepack escalation policy is defined.
2. When Stage 4 voltage contradicts rulepack-inferred voltage, surface
   the contradiction as its own QA item — do not silently override.
3. Run the manual review harness with a Stage 4 dataset present *and
   absent* to ensure popup, navigation, and QA navigation behave the
   same in both states.

## Recommended risk mitigations summary

In priority order:

1. **Fix the `"none"` enum / `_BLANK_TOKENS` collision** in
   `app/structured_capture_validators.py`. Library-only change. No
   risk to runtime. (Smallest blast radius, biggest correctness payoff.)
2. **Add `pole_id`, `project_id`, `file_id`** to the schema with
   appropriate validation. Library-only change. Updates the template
   generator + tests.
3. **Register Stage 4 fields in `app/field_reference.py`** with
   `source: "structured_capture"` so the popup renderer has a path to
   display them. Library-only.
4. **Define and document the merge policy** for duplicate / conflicting
   rows. Docs change; informs the integration branch.
5. **Add `capture_date` ISO-8601 format check** in
   `validate_stage4_row`. Library-only.
6. **Add cross-field consistency warnings** (`stay_present=no` ⇒
   `stay_type=none`; `equipment_present=no` ⇒ `equipment_type=none`;
   `confidence: low` ⇒ `verification_required: yes`). Library-only.
7. **Define the QA engine's confidence weighting policy** for Stage 4
   evidence — separate doc, separate branch, before any QA wiring.
8. **Plan the popup integration** — collapsible section, conditional
   rendering, source label. Frontend design task.
9. **Add a manual-review checklist** for Stage 4 popup behaviour
   (`validation_checklists/stage4_structured_capture.yml`). Drop-in
   after popup integration.

## Recommended "do not integrate until" checklist

Stage 4 must remain library-only until **all** of these are true.
Integration is unsafe before any single one of them is met.

- [ ] `"none"` is no longer in `_BLANK_TOKENS`, and at least one
      regression test exists per field where `"none"` is a valid enum
      (`stay_type`, `equipment_type`, `lean_direction`, `lean_severity`).
- [ ] The schema carries `pole_id`, `project_id`, and `file_id`, and
      `validate_stage4_row` rejects rows missing these.
- [ ] `app/field_reference.py::FIELD_DEFINITIONS` (or a parallel
      registry) includes every Stage 4 field with
      `source: "structured_capture"`.
- [ ] `app/field_validators.py::get_popup_display_value` returns a
      source label for Stage 4 values that the popup CSS distinguishes
      visually.
- [ ] A merge policy for duplicate / conflicting rows is documented in
      `docs/STAGE4_STRUCTURED_CAPTURE.md` (or a successor doc).
- [ ] `capture_date` is format-checked in the validator.
- [ ] At least one cross-field consistency warning is implemented and
      tested.
- [ ] The QA engine has a Stage-4-aware confidence weighting policy
      documented (does not need to be wired yet — but the policy must
      be written before any QA rule reads from a Stage 4 field).
- [ ] The manual review harness gains a Stage 4 popup checklist and is
      run successfully against `P008/F001` and `P010`, both with and
      without Stage 4 rows attached.
- [ ] Pre-commit clean; full pytest passing; all 23 existing Stage 4
      tests still passing; no regressions in the 866-test full suite.

The schema, validators, template generator, docs, and tests are
foundationally sound. They are not yet runtime-safe. Closing the
checklist above is the bridge between "ready as a library" and
"ready as an upload feature".

## Cross-references

- [22_STAGE4_TECHNICAL_AUDIT.md](22_STAGE4_TECHNICAL_AUDIT.md) — what exists today + reproduced bugs.
- [23_STAGE4_SCHEMA_READINESS_REVIEW.md](23_STAGE4_SCHEMA_READINESS_REVIEW.md) — group-by-group field review.
- [docs/STAGE4_STRUCTURED_CAPTURE.md](../docs/STAGE4_STRUCTURED_CAPTURE.md) — original Stage 4 rationale.
- [docs/FIELD_REFERENCE_GUIDE.md](../docs/FIELD_REFERENCE_GUIDE.md) — field truth-category rules this audit defends.
