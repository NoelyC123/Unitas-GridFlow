# 39 — Control File Audit

Audit of `AI_CONTROL/*.md` freshness and source-of-truth status,
performed against master HEAD `f2587ed` on 2026-05-10.

Companion to [36_POST_C2E2_REPOSITORY_AUDIT.md](36_POST_C2E2_REPOSITORY_AUDIT.md).
The actionable recommendation is a single line per file in the table
below.

## Method

Each `AI_CONTROL/*.md` file on master was classified into one of:

| Class | Meaning |
|---|---|
| **ACTIVE** | Current source of truth. Future agents must read this. |
| **STALE_BUT_USEFUL** | Out-of-date but historically valuable; mark as "superseded" but keep. |
| **DUPLICATE** | Two files cover the same concern; one wins, the other is superseded. |
| **SUPERSEDED** | Content has been replaced by a newer doc; safe to mark as such. |
| **DO_NOT_USE** | Content is misleading or contradicted by current state; should be quarantined. |
| **NUMBERING_RISK** | Filename slot is at risk of being clobbered by future audit numbering. |

## Numbering ambiguity is itself a finding

The **numeric prefix system is breaking down.** The Project Control
Center foundation introduced `00_PROJECT_BOARD.md` through
`09_WORKER_PROMPT_TEMPLATES.md` as Project-Control-System slots, while
**existing** product docs already used `00_PROJECT_CANONICAL.md`,
`03_WORKING_RULES.md`, `04_SESSION_HANDOFF.md`, etc. — *the same
numbers*. This produced two parallel meanings of `00`, `03`, `04`, etc.

Worse: this audit's task spec instructed the use of `20`–`26` for new
audit docs, but those slots were already occupied by Stage 3
acceptance / brief / runbook docs. This audit had to renumber to
`36`–`42`.

**Recommendation:** treat numeric prefixes as historical and rely on
explicit names. Adopt a *namespace prefix* convention going forward:

```
AI_CONTROL/PCS_*  — Project Control System (board / log / handoff / rules / checklists)
AI_CONTROL/PRD_*  — Product (canonical / current task / current state / origin)
AI_CONTROL/DOM_*  — Domain references (OHL operational standard / field reality / strategic review)
AI_CONTROL/STG_*  — Stage-specific closure / acceptance / runbook docs
AI_CONTROL/AUD_*  — Audits (this kind of doc)
```

Migration is out of scope for this audit (`Forbidden: ... Do not edit
app code` constrains this audit; the worker rules and renaming exercise
is a separate task).

## Per-file classification (master HEAD `f2587ed`)

### Project Control System slots (recent additions)

| File | Class | Notes |
|---|---|---|
| `00_PROJECT_BOARD.md` | **ACTIVE** | Source of truth for active task / done list. Updated by `start_task.py`. |
| `03_WORKER_LOG.md` | **ACTIVE** | Append-only worker log. Updated by `log_worker_update.py` and `log_validation_run.py`. |
| `04_VALIDATION_LOG.md` | **ACTIVE** | Validation evidence ledger. |
| `05_HANDOFF.md` | **ACTIVE** | Latest operational handoff. Updated by `start_task.py` for the marked active-task block. |
| `06_WORKER_RULES.md` | **ACTIVE** | Coordination rules. |
| `07_WORKER_START_CHECKLIST.md` | **ACTIVE** | Pre-coding checklist. |
| `08_WORKER_FINISH_CHECKLIST.md` | **ACTIVE** | Pre-handoff checklist. |
| `09_WORKER_PROMPT_TEMPLATES.md` | **ACTIVE** | Reusable prompt templates. |

### Product / canonical slots (older)

| File | Class | Notes |
|---|---|---|
| `00_PROJECT_CANONICAL.md` | **ACTIVE** | Project identity + 6-stage vision. **Numbering collides with `00_PROJECT_BOARD.md`.** |
| `01_CURRENT_STATE.md` | **ACTIVE** | Pre-coding required reading per worker rules. |
| `02_CURRENT_TASK.md` | **ACTIVE** | Pre-coding required reading per worker rules. |
| `03_WORKING_RULES.md` | **DUPLICATE** with `06_WORKER_RULES.md` | Older working rules; consolidate or supersede. |
| `04_SESSION_HANDOFF.md` | **DUPLICATE** with `05_HANDOFF.md` | Older handoff; supersede. |
| `05_PROJECT_REFERENCE.md` | **STALE_BUT_USEFUL** | Project background reference. |
| `06_STRATEGIC_REVIEW_2026-04-22.md` | **DO_NOT_USE** (per CLAUDE.md) | Explicitly marked superseded by 08 + 09 in CLAUDE.md. |
| `07_REAL_WORLD_SURVEY_WORKFLOW.md` | **DO_NOT_USE** (per CLAUDE.md) | Explicitly marked superseded by 08 + 09. |
| `08_OHL_SURVEY_OPERATIONAL_STANDARD.md` | **ACTIVE** | Domain reference for OHL surveys. |
| `09_PROJECT_ORIGIN_AND_FIELD_NOTES.md` | **ACTIVE** | Domain reference for QA wording / output. |

### Stage 2 closure (frozen)

| File | Class |
|---|---|
| `08_PHASE_C2D_IMPLEMENTATION_SPEC.md` | **STALE_BUT_USEFUL** |
| `09_C2D_VALIDATION_READINESS_REPORT.md` | **STALE_BUT_USEFUL** |
| `10_REAL_JOB_VALIDATION_PLAN.md` | **STALE_BUT_USEFUL** |
| `10_STAGE_2B_DESIGN_BRIEF.md` | **STALE_BUT_USEFUL** |
| `11_STAGE_2_VALIDATION_SUMMARY.md` | **STALE_BUT_USEFUL** |
| `12_STAGE_2B_DECISION_CHECKLIST.md` | **STALE_BUT_USEFUL** |
| `13_STAGE_2B_VALIDATION_ACCEPTANCE.md` | **STALE_BUT_USEFUL** |
| `14_STAGE_2C_POLISH_PLAN.md` | **STALE_BUT_USEFUL** |
| `15_STAGE_2C_VALIDATION_ACCEPTANCE.md` | **STALE_BUT_USEFUL** |
| `16_STAGE_2_COMPLETION_REVIEW.md` | **STALE_BUT_USEFUL** |
| `17_STAGE_2_CLOSURE_DECISION.md` | **STALE_BUT_USEFUL** |

### C2E2 phase docs (recent and active)

| File | Class |
|---|---|
| `11_C2E2_POPUP_EXPANSION_SPEC.md` | **ACTIVE** (popup truthfulness spec) |
| `12_C2E2_FIELD_MAPPING_AUDIT.md` | **ACTIVE** |
| `13_C2E2_IMPLEMENTATION_PLAN.md` | **STALE_BUT_USEFUL** (work complete) |
| `14_C2E2_VALIDATION_MATRIX.md` | **STALE_BUT_USEFUL** |
| `32_C2E2_PRE_IMPLEMENTATION_GUIDE.md` | **STALE_BUT_USEFUL** |
| `33_C2E2_IMPLEMENTATION_REVIEW_CHECKLIST.md` | **STALE_BUT_USEFUL** |
| `35_POPUP_HTML_EXAMPLES.md` | **ACTIVE** |

### Stage 3 closure (frozen)

| File | Class |
|---|---|
| `18_STAGE_3_OPTIONS_ANALYSIS.md` | **STALE_BUT_USEFUL** |
| `19_STAGE_3_EXECUTION_PLAN.md` | **STALE_BUT_USEFUL** |
| `20_STAGE_3C_VALIDATION_ACCEPTANCE.md` | **STALE_BUT_USEFUL** |
| `21_STAGE_3B_DESIGN_BRIEF.md` | **STALE_BUT_USEFUL** |
| `22_STAGE_3B_VALIDATION_ACCEPTANCE.md` | **STALE_BUT_USEFUL** |
| `23_STAGE_3A_DESIGN_BRIEF.md` | **STALE_BUT_USEFUL** |
| `24_STAGE_3A_VALIDATION_ACCEPTANCE.md` | **STALE_BUT_USEFUL** |
| `25_STAGE_3A2_DEPLOYMENT_PLAN.md` | **STALE_BUT_USEFUL** |
| `26_STAGE_3A_OPERATIONAL_RUNBOOK.md` | **STALE_BUT_USEFUL** |
| `27_STAGE_3_CLOSURE_AND_OPERATIONAL_USE.md` | **STALE_BUT_USEFUL** |

### Domain / reality references

| File | Class |
|---|---|
| `28_DOMAIN_REFERENCE_SUMMARY.md` | **ACTIVE** |
| `29_PRACTITIONER_REVIEW_SUMMARY.md` | **ACTIVE** |
| `30_FOUNDER_DOMAIN_AND_AI_USAGE_CONTEXT.md` | **ACTIVE** |
| `31_REAL_JOB_FIELD_REALITY_REPORT.md` | **ACTIVE** (the C2E2 audit foundation) |

### Stale memo

| File | Class |
|---|---|
| `07_BATCH_20_DECISION_MEMO.md` | **STALE_BUT_USEFUL** |

## Recommended source-of-truth list (after audit)

A future agent should read **only these** before starting product
work, in this order:

1. `AI_CONTROL/00_PROJECT_CANONICAL.md` — what the project is
2. `AI_CONTROL/01_CURRENT_STATE.md` — what's true right now
3. `AI_CONTROL/02_CURRENT_TASK.md` — what to do next
4. `AI_CONTROL/00_PROJECT_BOARD.md` — board view
5. `AI_CONTROL/05_HANDOFF.md` — latest handoff
6. `AI_CONTROL/06_WORKER_RULES.md` + `07_WORKER_START_CHECKLIST.md`
7. `AI_CONTROL/31_REAL_JOB_FIELD_REALITY_REPORT.md` — field reality
8. Domain refs as needed: `08_OHL_SURVEY_OPERATIONAL_STANDARD.md`,
   `09_PROJECT_ORIGIN_AND_FIELD_NOTES.md`, `28`–`30`
9. The four `docs/*.md` developer references (architecture, API, field
   reference, validation workflow).

A future agent should **not** read:

- `06_STRATEGIC_REVIEW_2026-04-22.md`
- `07_REAL_WORLD_SURVEY_WORKFLOW.md`
- `03_WORKING_RULES.md` (use `06_WORKER_RULES.md`)
- `04_SESSION_HANDOFF.md` (use `05_HANDOFF.md`)

## Recommended near-term consolidation (a separate task)

1. Rename `03_WORKING_RULES.md` → mark superseded, redirect to `06_WORKER_RULES.md`.
2. Rename `04_SESSION_HANDOFF.md` → mark superseded, redirect to `05_HANDOFF.md`.
3. Add a one-line "SUPERSEDED — see X" header to every `STALE_BUT_USEFUL` file.
4. Adopt the `PCS_/PRD_/DOM_/STG_/AUD_` namespace prefix for any *new* AI_CONTROL doc.
5. Update [`README_PROJECT_CONTROL.md`](../README_PROJECT_CONTROL.md) to describe the new namespace.
