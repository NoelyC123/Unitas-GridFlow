# 36 — Post-C2E2 Repository Audit

> **Filename note.** The task spec named the seven audit docs `20`–`26`, but
> those slots are already occupied on master by the Stage 2/3 closure docs
> (`20_STAGE_3C_VALIDATION_ACCEPTANCE.md` through
> `26_STAGE_3A_OPERATIONAL_RUNBOOK.md`). To avoid clobbering that prior
> product knowledge, this audit uses the next free slots `36`–`42`. The
> filename collision itself is a finding — see
> [39_CONTROL_FILE_AUDIT.md](39_CONTROL_FILE_AUDIT.md).

## Purpose

Repository-level governance audit performed on **2026-05-10** after
C2E2 closeout. This is **not** a feature task — it covers branch
safety, control-file freshness, validation evidence, and AI-worker
coordination risks **before** the next product phase begins.

Companion docs (this audit set):

- [37_BRANCH_INVENTORY.md](37_BRANCH_INVENTORY.md)
- [38_BRANCH_RETIREMENT_PLAN.md](38_BRANCH_RETIREMENT_PLAN.md)
- [39_CONTROL_FILE_AUDIT.md](39_CONTROL_FILE_AUDIT.md)
- [40_VALIDATION_AUDIT.md](40_VALIDATION_AUDIT.md)
- [41_WORKER_COORDINATION_RISK_REVIEW.md](41_WORKER_COORDINATION_RISK_REVIEW.md)
- [42_NEXT_PHASE_READINESS.md](42_NEXT_PHASE_READINESS.md)

## Master state (snapshot 2026-05-10)

| Aspect | Value |
|---|---|
| Master HEAD | `f2587ed Fix C2E2 map navigation followups` |
| Recent merges | `f2587ed` ← `debea0b` (popup HTML examples) ← `212bd23` (worker bootstrap) ← `9b7bb82` (C2G lifecycle) |
| Latest milestone tag | `c2e2-map-navigation-followups-complete` |
| Pre-C2E2 milestones merged | `c2e2-popup-scope-reduction-complete`, `project-control-worker-bootstrap-complete`, `c2g-lifecycle-replacement-visualization-complete`, `technical-docs-field-architecture-complete`, `c2f-review-focus-issue-filtering-complete`, `stage4-structured-capture-foundation-complete`, `project-control-center-first-use-polish-complete`, `project-control-center-foundation-complete`, `c2e2-popup-expansion-implementation-complete`, `c2e2-support-suite-complete`, `c2e2-popup-expansion-spec-complete` |
| `pytest -v` | **866 passed**, 13 pre-existing third-party warnings |
| `pre-commit run --all-files` | **all hooks pass** (trim-trailing-whitespace, fix-end-of-files, check-yaml, check-json, check-large-files, ruff, ruff-format) |
| Working tree | Clean |
| Origin | up to date |

### C2E2 closeout status

C2E2 is **complete and tagged**. The C2E2 work landed in three named
phases that all reached master and were tagged:

1. `c2e2-popup-expansion-spec-complete` — planning artifacts.
2. `c2e2-popup-expansion-implementation-complete` — initial 10-field popup.
3. `c2e2-popup-scope-reduction-complete` — truthfulness rule cleanup
   (forbidden-fields removal, slim Location, Source & Confidence).
4. `c2e2-map-navigation-followups-complete` — final navigation polish.

Two C2E2-flavoured branches **never merged** (both deliberately left as
references — see [37_BRANCH_INVENTORY.md](37_BRANCH_INVENTORY.md)):

- `claude-code/c2e2-support-suite` (5375069) — older, pre-scope-reduction
  popup work that was *subsumed* by master's stricter version. The
  recent merge attempt was aborted because the literal "keep branch"
  rule would have *regressed* master's truthfulness scope.
- `claude-code/stage4-structured-capture-technical-audit` (13019f4) —
  audit-only branch from a parallel agent run. Library code unchanged.

## Highest-level findings

| Finding | Severity | Reference |
|---|---|---|
| Filename-numbering collision in `AI_CONTROL/` made the spec's `20`–`26` slots unusable | Medium | [39_CONTROL_FILE_AUDIT.md](39_CONTROL_FILE_AUDIT.md) |
| `claude-code/c2e2-support-suite` cannot be merged with the literal "keep branch side" rule without regressing master | High | [38_BRANCH_RETIREMENT_PLAN.md](38_BRANCH_RETIREMENT_PLAN.md) |
| Five branches remain unmerged; three are old C2D feature stubs from May 5–7 with no path forward | Medium | [37_BRANCH_INVENTORY.md](37_BRANCH_INVENTORY.md) |
| `codex/stage4-structured-capture-integration-plan` reports as merged but its tip is the worker-bootstrap merge commit — branch never actually advanced | Low | [37_BRANCH_INVENTORY.md](37_BRANCH_INVENTORY.md) |
| Several superseded AI_CONTROL docs are still live alongside their successors (e.g. `06_STRATEGIC_REVIEW_2026-04-22.md`) | Medium | [39_CONTROL_FILE_AUDIT.md](39_CONTROL_FILE_AUDIT.md) |
| Two parallel "active task" markers existed simultaneously across branches (Codex's stage4 integration plan vs Claude Code's audit) | Medium | [41_WORKER_COORDINATION_RISK_REVIEW.md](41_WORKER_COORDINATION_RISK_REVIEW.md) |

## Forbidden-action confirmation

Per the task spec, this audit:

- ✅ **Did not** edit app code.
- ✅ **Did not** edit tests.
- ✅ **Did not** merge any branch.
- ✅ **Did not** delete any branch.
- ✅ **Did not** touch `_archive/`.
- ✅ **Did not** start Stage 4 implementation.
- ✅ **Did not** rewrite git history.

The audit produced documentation only.

## What this audit recommends, in one paragraph

Tag and freeze the current master as the C2E2 stability baseline.
Retire the old C2D feature branches that have been superseded by
master. **Do not** attempt another mechanical merge of
`claude-code/c2e2-support-suite` — instead cherry-pick its
`AI_CONTROL/35_POPUP_HTML_EXAMPLES.md` (already on master via
`debea0b`) and archive the branch as historical reference. Consolidate
duplicate AI_CONTROL files, mark superseded docs as superseded, and
adopt a strict pre-task workflow (always-from-master, always-check
`scripts/control_status.py`). Master is **ready for Control Center v1**
work but **not yet ready for Stage 4 implementation** until the audit
findings in [42_NEXT_PHASE_READINESS.md](42_NEXT_PHASE_READINESS.md)
are addressed.
