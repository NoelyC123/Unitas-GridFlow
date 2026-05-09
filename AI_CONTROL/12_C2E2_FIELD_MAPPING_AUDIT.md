# C2E2/D Field Mapping Audit

## Purpose

This audit reconciles the C2E2 popup plan with the real survey field audit from `AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md`.

It replaces the earlier theoretical field list with fields that are actually parsed from real Trimble jobs or safely derived by GridFlow.

## Required Upstream Dependency

Implementation should depend on merging `claude-code/c2e2-support-suite` first.

After merge, reference `app/field_reference.py` as the canonical field catalogue:

- `FIELD_DEFINITIONS`
- `POPUP_FIELD_GROUPS`
- `POPUP_GROUP_ORDER`
- `get_missing_wording()`
- `resolve_alias()`

## Real Trimble Extraction Boundary

The current Trimble parser extracts only:

| Field | Source | Status |
|---|---|---|
| `pole_id` | CSV point id | Real/current |
| `easting` | CSV easting | Real/current |
| `northing` | CSV northing | Real/current |
| `height` | `CODE:HEIGHT` attribute | Real/current, intentionally partial |
| `structure_type` | CSV feature code | Real/current |
| `location` / `name` | `CODE:REMARK` attribute | Real/current, partial |

Derived pipeline fields include `asset_intent`, `record_role`, `qa_status`, `relationship`, `being_replaced_by`, `replacing`, issue/warning counts, and issue/warning texts.

## Reality-Based Field Mapping

| Field | User label | Source / aliases from `field_reference.py` | Support status | Popup missing wording | Notes |
|---|---|---|---|---|---|
| `pole_id` | Point ID | `point_id`, `pt`, `pnt`, `point_no`, `no`, `number` | existing | `No ID` | Always present in real Trimble jobs. |
| `structure_type` | Feature Code | `code`, `feature_code`, `feat_code`, `fc`, `type` | existing | `Unknown` | Drives role/classification and conditional wording. |
| `asset_intent` | Asset Intent | derived | existing | `Not classified` | Derived, not a survey field. |
| `record_role` | Record Role | `_record_role` | existing/derived | `Unclassified` | Derived role; useful to explain context vs structural records. |
| `height` | Measured Height | `h`, `ht`, `elev`, `elevation`, `z`, `pole_height`, `heights` | existing, partial | type-specific; see height rules | Comes from `CODE:HEIGHT`, not GPS elevation. |
| `qa_status` | QA Status | `status` | existing/derived | `Not assessed` | Existing validation state; do not change semantics. |
| `name` / `location` | Survey Note | `location`, `remark`, `remarks`, `note`, `notes`, `description`, `comment`, `desc` | existing, partial | `-` | Richest free-text field in real data. |
| `relationship` | Relationship | derived | existing/derived | `-` | Show only when non-empty. |
| `being_replaced_by` | Being Replaced By | derived | partial/derived | `-` | Derived from EX/PR pairing. |
| `replacing` | Replacing | derived | partial/derived | `-` | Derived from EX/PR pairing. |
| `material` | Material | `mat`, `pole_material` | absent in Trimble | `Not recorded in survey` | May be displayed as truthful absence only. |
| `land_use` | Land Use | Trimble `CODE:LAND USE` | present in raw, not extracted | `Not recorded` | Add only if deliberately adding parser support later. |
| `stay_evidence_status` | Stay Evidence | derived QA/stay logic | partial/derived | `check field notes / plans` | Include only if already available in map properties after support-suite merge. |

## Absent Fields Deferred To Stage 4

These fields are **not in current Trimble format** and should be deferred to Stage 4 structured capture:

| Field | Status | Rationale |
|---|---|---|
| `pole_class` | Not in Trimble format - Stage 4 structured capture | Would require survey/capture schema not present in current files. |
| `specification` | Not in Trimble format - Stage 4 structured capture | Design-owned future field, not current survey evidence. |
| `condition` | Not in Trimble format - Stage 4 structured capture | No real source columns in audited Trimble jobs. |
| `defect_type` | Not in Trimble format - Stage 4 structured capture | No real source columns in audited Trimble jobs. |
| `defect_severity` | Not in Trimble format - Stage 4 structured capture | No real source columns in audited Trimble jobs. |
| `voltage_carried` | Not in Trimble format - Stage 4 structured capture | Job/rulepack may imply voltage, but no per-pole survey field. |
| `conductor_type` | Not in Trimble format - Stage 4 structured capture | No per-span/pole conductor field in current Trimble files. |
| `conductor_size` | Not in Trimble format - Stage 4 structured capture | No real source columns in audited Trimble jobs. |
| `phase_configuration` | Not in Trimble format - Stage 4 structured capture | No real source columns in audited Trimble jobs. |
| `stay_type` | Not in Trimble format - Stage 4 structured capture | Stay evidence may be derived; type is not recorded as a Trimble attribute. |
| `lean_direction` | Not in Trimble format - Stage 4 structured capture | No real source columns in audited Trimble jobs. |
| `lean_severity` | Not in Trimble format - Stage 4 structured capture | No real source columns in audited Trimble jobs. |
| `equipment_present` | Not in Trimble format - Stage 4 structured capture | Current files do not record equipment. |
| `equipment_type` | Not in Trimble format - Stage 4 structured capture | Current files do not record equipment. |

## Height Wording Rules

Height is intentionally partial:

- `Pol`: `Not measured (intermediate pole)`
- `EXpole`: `Not measured - check survey notes`
- `Angle`: `Not measured - check survey notes`
- Other records: `Not measured`

Do not treat missing `Pol` height as a blocker. Do not use GPS elevation as pole height.

## Mapping Decision

The C2E2 implementation should be a display and wording refinement over real/current fields. It should not add theoretical rows for absent fields except `material`, and even then only with `Not recorded in survey` wording.
