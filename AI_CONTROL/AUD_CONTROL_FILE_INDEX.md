# AUD_CONTROL_FILE_INDEX.md — AI_CONTROL Source-of-Truth Index

Produced by branch-retirement-control-deconfliction task, 2026-05-10.
Companion to [39_CONTROL_FILE_AUDIT.md](39_CONTROL_FILE_AUDIT.md) and
[42_NEXT_PHASE_READINESS.md](42_NEXT_PHASE_READINESS.md).

## Why this file exists

The `AI_CONTROL/` directory has accumulated 70+ files across multiple
project phases. Numeric prefixes collide between the original product
docs (slots 00–09), the Project Control System docs (also 00–09), and
the stage closure archives (08–27). This index resolves the ambiguity
without renaming files — renaming would break git history and require
updating cross-references across the entire repo.

**Rule for new documents:** do NOT use bare numeric prefixes. Use a
namespace prefix instead:

| Prefix | Scope |
|--------|-------|
| `PCS_` | Project Control System (board / log / handoff / rules / checklists) |
| `PRD_` | Product canonical docs |
| `DOM_` | Domain references (OHL operational standard, field reality, etc.) |
| `STG_` | Stage-specific closure / acceptance / runbook docs |
| `AUD_` | Audits and governance reports (like this file) |

---

## Active source-of-truth files (read these first)

A worker starting a new task must read these in this order:

| File | Purpose |
|------|---------|
| [00_PROJECT_BOARD.md](00_PROJECT_BOARD.md) | Active task, branch ownership, validation state |
| [00_PROJECT_CANONICAL.md](00_PROJECT_CANONICAL.md) | Project identity and 6-stage vision |
| [01_CURRENT_STATE.md](01_CURRENT_STATE.md) | Current codebase truth |
| [02_CURRENT_TASK.md](02_CURRENT_TASK.md) | What to do next |
| [05_HANDOFF.md](05_HANDOFF.md) | Latest worker handoff |
| [06_WORKER_RULES.md](06_WORKER_RULES.md) | Coordination rules (including doc 41 protocol) |
| [07_WORKER_START_CHECKLIST.md](07_WORKER_START_CHECKLIST.md) | Mandatory pre-coding checks |
| [08_WORKER_FINISH_CHECKLIST.md](08_WORKER_FINISH_CHECKLIST.md) | Mandatory handoff checks |

**Do NOT read** (explicitly superseded):

- [03_WORKING_RULES.md](03_WORKING_RULES.md) — use `06_WORKER_RULES.md`
- [04_SESSION_HANDOFF.md](04_SESSION_HANDOFF.md) — use `05_HANDOFF.md`
- [06_STRATEGIC_REVIEW_2026-04-22.md](06_STRATEGIC_REVIEW_2026-04-22.md) — use `08_OHL_SURVEY_OPERATIONAL_STANDARD.md`
- [07_REAL_WORLD_SURVEY_WORKFLOW.md](07_REAL_WORLD_SURVEY_WORKFLOW.md) — use `09_PROJECT_ORIGIN_AND_FIELD_NOTES.md`

---

## Project Control System files (PCS slot)

Files introduced by the GridFlow Control Center v1.0:

| File | Status | Purpose |
|------|--------|---------|
| [00_PROJECT_BOARD.md](00_PROJECT_BOARD.md) | **ACTIVE** | Task board with PROJECT_CONTROL markers |
| [03_WORKER_LOG.md](03_WORKER_LOG.md) | **ACTIVE** | Append-only worker log |
| [04_VALIDATION_LOG.md](04_VALIDATION_LOG.md) | **ACTIVE** | Validation evidence ledger |
| [05_HANDOFF.md](05_HANDOFF.md) | **ACTIVE** | Latest operational handoff |
| [06_WORKER_RULES.md](06_WORKER_RULES.md) | **ACTIVE** | Coordination rules + protocol |
| [06_WORKER_LANES.md](06_WORKER_LANES.md) | **ACTIVE** | Role definitions per worker type |
| [07_WORKER_START_CHECKLIST.md](07_WORKER_START_CHECKLIST.md) | **ACTIVE** | Pre-coding checklist |
| [07_TASK_TEMPLATE.md](07_TASK_TEMPLATE.md) | **ACTIVE** | Task definition template |
| [08_WORKER_FINISH_CHECKLIST.md](08_WORKER_FINISH_CHECKLIST.md) | **ACTIVE** | Pre-handoff checklist |
| [08_COMPLETION_REPORT_TEMPLATE.md](08_COMPLETION_REPORT_TEMPLATE.md) | **ACTIVE** | Completion report template |
| [09_WORKER_PROMPT_TEMPLATES.md](09_WORKER_PROMPT_TEMPLATES.md) | **ACTIVE** | Reusable prompt templates |
| [09_MERGE_GATE_CHECKLIST.md](09_MERGE_GATE_CHECKLIST.md) | **ACTIVE** | Merge gate checklist |
| [10_VALIDATION_EVIDENCE_PROTOCOL.md](10_VALIDATION_EVIDENCE_PROTOCOL.md) | **ACTIVE** | Validation evidence rules |
| [11_BRANCH_RETIREMENT_PROTOCOL.md](11_BRANCH_RETIREMENT_PROTOCOL.md) | **ACTIVE** | Branch retirement procedure |
| [12_OPEN_FOLLOWUPS.md](12_OPEN_FOLLOWUPS.md) | **ACTIVE** | Open follow-ups tracker |
| [13_C2E2_CLOSEOUT.md](13_C2E2_CLOSEOUT.md) | **ACTIVE** | C2E2 closeout record |
| [14_CONTROL_CENTER_USER_GUIDE.md](14_CONTROL_CENTER_USER_GUIDE.md) | **ACTIVE** | Control center usage guide |
| [15_WORKER_PROMPT_LIBRARY.md](15_WORKER_PROMPT_LIBRARY.md) | **ACTIVE** | Worker prompt library |
| [16_CONFLICT_AND_ROLLBACK_PROTOCOL.md](16_CONFLICT_AND_ROLLBACK_PROTOCOL.md) | **ACTIVE** | Conflict and rollback procedures |

---

## Product canonical files (PRD slot)

| File | Status | Purpose |
|------|--------|---------|
| [00_PROJECT_CANONICAL.md](00_PROJECT_CANONICAL.md) | **ACTIVE** | 6-stage vision, project identity |
| [01_CURRENT_STATE.md](01_CURRENT_STATE.md) | **ACTIVE** | What is true right now |
| [02_CURRENT_TASK.md](02_CURRENT_TASK.md) | **ACTIVE** | What to do next |
| [05_PROJECT_REFERENCE.md](05_PROJECT_REFERENCE.md) | HISTORICAL | Background reference; not maintained |
| [03_WORKING_RULES.md](03_WORKING_RULES.md) | **SUPERSEDED** | Use `06_WORKER_RULES.md` |
| [04_SESSION_HANDOFF.md](04_SESSION_HANDOFF.md) | **SUPERSEDED** | Use `05_HANDOFF.md` |

---

## Domain reference files (DOM slot)

| File | Status | Purpose |
|------|--------|---------|
| [08_OHL_SURVEY_OPERATIONAL_STANDARD.md](08_OHL_SURVEY_OPERATIONAL_STANDARD.md) | **ACTIVE** | OHL survey domain standard |
| [09_PROJECT_ORIGIN_AND_FIELD_NOTES.md](09_PROJECT_ORIGIN_AND_FIELD_NOTES.md) | **ACTIVE** | QA wording / output language reference |
| [28_DOMAIN_REFERENCE_SUMMARY.md](28_DOMAIN_REFERENCE_SUMMARY.md) | **ACTIVE** | Domain reference summary |
| [29_PRACTITIONER_REVIEW_SUMMARY.md](29_PRACTITIONER_REVIEW_SUMMARY.md) | **ACTIVE** | Practitioner review findings |
| [30_FOUNDER_DOMAIN_AND_AI_USAGE_CONTEXT.md](30_FOUNDER_DOMAIN_AND_AI_USAGE_CONTEXT.md) | **ACTIVE** | Founder context and AI usage |
| [31_REAL_JOB_FIELD_REALITY_REPORT.md](31_REAL_JOB_FIELD_REALITY_REPORT.md) | **ACTIVE** | Field reality (C2E2 audit foundation) |

---

## C2E2 phase docs

| File | Status | Notes |
|------|--------|-------|
| [11_C2E2_POPUP_EXPANSION_SPEC.md](11_C2E2_POPUP_EXPANSION_SPEC.md) | **ACTIVE** | Popup truthfulness spec |
| [12_C2E2_FIELD_MAPPING_AUDIT.md](12_C2E2_FIELD_MAPPING_AUDIT.md) | **ACTIVE** | Field mapping reference |
| [35_POPUP_HTML_EXAMPLES.md](35_POPUP_HTML_EXAMPLES.md) | **ACTIVE** | Popup HTML examples |
| [13_C2E2_IMPLEMENTATION_PLAN.md](13_C2E2_IMPLEMENTATION_PLAN.md) | HISTORICAL | Work complete |
| [14_C2E2_VALIDATION_MATRIX.md](14_C2E2_VALIDATION_MATRIX.md) | HISTORICAL | Work complete |
| [32_C2E2_PRE_IMPLEMENTATION_GUIDE.md](32_C2E2_PRE_IMPLEMENTATION_GUIDE.md) | HISTORICAL | Work complete |
| [33_C2E2_IMPLEMENTATION_REVIEW_CHECKLIST.md](33_C2E2_IMPLEMENTATION_REVIEW_CHECKLIST.md) | HISTORICAL | Work complete |

---

## Stage 2 closure archive (STG slot)

All files below are frozen. Do not update them. For current state see [01_CURRENT_STATE.md](01_CURRENT_STATE.md).

| File | Status |
|------|--------|
| [08_PHASE_C2D_IMPLEMENTATION_SPEC.md](08_PHASE_C2D_IMPLEMENTATION_SPEC.md) | HISTORICAL |
| [09_C2D_VALIDATION_READINESS_REPORT.md](09_C2D_VALIDATION_READINESS_REPORT.md) | HISTORICAL |
| [10_REAL_JOB_VALIDATION_PLAN.md](10_REAL_JOB_VALIDATION_PLAN.md) | HISTORICAL |
| [10_STAGE_2B_DESIGN_BRIEF.md](10_STAGE_2B_DESIGN_BRIEF.md) | HISTORICAL |
| [11_STAGE_2_VALIDATION_SUMMARY.md](11_STAGE_2_VALIDATION_SUMMARY.md) | HISTORICAL |
| [12_STAGE_2B_DECISION_CHECKLIST.md](12_STAGE_2B_DECISION_CHECKLIST.md) | HISTORICAL |
| [13_STAGE_2B_VALIDATION_ACCEPTANCE.md](13_STAGE_2B_VALIDATION_ACCEPTANCE.md) | HISTORICAL |
| [14_STAGE_2C_POLISH_PLAN.md](14_STAGE_2C_POLISH_PLAN.md) | HISTORICAL |
| [15_STAGE_2C_VALIDATION_ACCEPTANCE.md](15_STAGE_2C_VALIDATION_ACCEPTANCE.md) | HISTORICAL |
| [16_STAGE_2_COMPLETION_REVIEW.md](16_STAGE_2_COMPLETION_REVIEW.md) | HISTORICAL |
| [17_STAGE_2_CLOSURE_DECISION.md](17_STAGE_2_CLOSURE_DECISION.md) | HISTORICAL |

---

## Stage 3 closure archive (STG slot)

| File | Status |
|------|--------|
| [18_STAGE_3_OPTIONS_ANALYSIS.md](18_STAGE_3_OPTIONS_ANALYSIS.md) | HISTORICAL |
| [19_STAGE_3_EXECUTION_PLAN.md](19_STAGE_3_EXECUTION_PLAN.md) | HISTORICAL |
| [20_STAGE_3C_VALIDATION_ACCEPTANCE.md](20_STAGE_3C_VALIDATION_ACCEPTANCE.md) | HISTORICAL |
| [21_STAGE_3B_DESIGN_BRIEF.md](21_STAGE_3B_DESIGN_BRIEF.md) | HISTORICAL |
| [22_STAGE_3B_VALIDATION_ACCEPTANCE.md](22_STAGE_3B_VALIDATION_ACCEPTANCE.md) | HISTORICAL |
| [23_STAGE_3A_DESIGN_BRIEF.md](23_STAGE_3A_DESIGN_BRIEF.md) | HISTORICAL |
| [24_STAGE_3A_VALIDATION_ACCEPTANCE.md](24_STAGE_3A_VALIDATION_ACCEPTANCE.md) | HISTORICAL |
| [25_STAGE_3A2_DEPLOYMENT_PLAN.md](25_STAGE_3A2_DEPLOYMENT_PLAN.md) | HISTORICAL |
| [26_STAGE_3A_OPERATIONAL_RUNBOOK.md](26_STAGE_3A_OPERATIONAL_RUNBOOK.md) | HISTORICAL |
| [27_STAGE_3_CLOSURE_AND_OPERATIONAL_USE.md](27_STAGE_3_CLOSURE_AND_OPERATIONAL_USE.md) | HISTORICAL |

---

## Audit and governance docs (AUD slot)

New docs created by the governance audit workstream. These use the `AUD_` prefix
to avoid numeric collisions.

| File | Purpose |
|------|---------|
| [36_POST_C2E2_REPOSITORY_AUDIT.md](36_POST_C2E2_REPOSITORY_AUDIT.md) | Top-level post-C2E2 repository audit |
| [37_BRANCH_INVENTORY.md](37_BRANCH_INVENTORY.md) | Branch inventory at audit date |
| [38_BRANCH_RETIREMENT_PLAN.md](38_BRANCH_RETIREMENT_PLAN.md) | Six-bucket retirement plan |
| [39_CONTROL_FILE_AUDIT.md](39_CONTROL_FILE_AUDIT.md) | Per-file AI_CONTROL classification |
| [40_VALIDATION_AUDIT.md](40_VALIDATION_AUDIT.md) | Validation state at audit date |
| [41_WORKER_COORDINATION_RISK_REVIEW.md](41_WORKER_COORDINATION_RISK_REVIEW.md) | Coordination incidents + protocol |
| [42_NEXT_PHASE_READINESS.md](42_NEXT_PHASE_READINESS.md) | Next-phase readiness assessment |
| **[AUD_CONTROL_FILE_INDEX.md](AUD_CONTROL_FILE_INDEX.md)** | **This file — source-of-truth index** |

---

## Stale / other

| File | Status | Notes |
|------|--------|-------|
| [07_BATCH_20_DECISION_MEMO.md](07_BATCH_20_DECISION_MEMO.md) | HISTORICAL | Batch 20 decision memo; frozen |
| [06_STRATEGIC_REVIEW_2026-04-22.md](06_STRATEGIC_REVIEW_2026-04-22.md) | SUPERSEDED | Use `08_OHL_SURVEY_OPERATIONAL_STANDARD.md` |
| [07_REAL_WORLD_SURVEY_WORKFLOW.md](07_REAL_WORLD_SURVEY_WORKFLOW.md) | SUPERSEDED | Use `09_PROJECT_ORIGIN_AND_FIELD_NOTES.md` |

---

## Numbering collision summary

The numeric prefix scheme has broken down due to two parallel numbering
systems (original product docs + Project Control System) competing for
the same slots. The collision map is:

| Slot | Colliding files |
|------|----------------|
| 00 | PROJECT_BOARD ↔ PROJECT_CANONICAL |
| 03 | WORKER_LOG ↔ WORKING_RULES (superseded) |
| 04 | SESSION_HANDOFF (superseded) ↔ VALIDATION_LOG |
| 05 | HANDOFF ↔ PROJECT_REFERENCE (historical) |
| 06 | STRATEGIC_REVIEW (superseded) ↔ WORKER_LANES ↔ WORKER_RULES |
| 07 | BATCH_20_MEMO (historical) ↔ REAL_WORLD_WORKFLOW (superseded) ↔ TASK_TEMPLATE ↔ WORKER_START_CHECKLIST |
| 08 | COMPLETION_REPORT_TEMPLATE ↔ OHL_SURVEY_OPERATIONAL_STANDARD ↔ PHASE_C2D_SPEC (historical) ↔ WORKER_FINISH_CHECKLIST |
| 09 | C2D_VALIDATION_READINESS (historical) ↔ MERGE_GATE_CHECKLIST ↔ PROJECT_ORIGIN_AND_FIELD_NOTES ↔ WORKER_PROMPT_TEMPLATES |
| 10 | REAL_JOB_VALIDATION_PLAN (historical) ↔ STAGE_2B_DESIGN_BRIEF (historical) ↔ VALIDATION_EVIDENCE_PROTOCOL |
| 11 | BRANCH_RETIREMENT_PROTOCOL ↔ C2E2_POPUP_EXPANSION_SPEC ↔ STAGE_2_VALIDATION_SUMMARY (historical) |
| 12 | C2E2_FIELD_MAPPING_AUDIT ↔ OPEN_FOLLOWUPS ↔ STAGE_2B_DECISION_CHECKLIST (historical) |
| 13 | C2E2_CLOSEOUT ↔ C2E2_IMPLEMENTATION_PLAN (historical) ↔ STAGE_2B_VALIDATION_ACCEPTANCE (historical) |
| 14 | C2E2_VALIDATION_MATRIX (historical) ↔ CONTROL_CENTER_USER_GUIDE ↔ STAGE_2C_POLISH_PLAN (historical) |
| 15 | STAGE_2C_VALIDATION_ACCEPTANCE (historical) ↔ WORKER_PROMPT_LIBRARY |
| 16 | CONFLICT_AND_ROLLBACK_PROTOCOL ↔ STAGE_2_COMPLETION_REVIEW (historical) |

**Resolution (no renaming required):** All HISTORICAL and SUPERSEDED files have
been marked with inline headers. The ACTIVE files in each colliding slot are
identifiable by their names. Any future AI worker should use **name** not **number**
to identify files, and use this index as the lookup table.

**Future docs:** use `AUD_`, `PCS_`, `PRD_`, `DOM_`, or `STG_` prefixes.
Do not use bare numeric prefixes for new files.
