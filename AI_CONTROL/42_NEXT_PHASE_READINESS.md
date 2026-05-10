# 42 — Next-Phase Readiness Assessment

Companion to [36_POST_C2E2_REPOSITORY_AUDIT.md](36_POST_C2E2_REPOSITORY_AUDIT.md).
Assesses whether the repo is ready to begin each of the candidate
next-phase workstreams.

## Headline answer

| Workstream | Ready? | Blockers |
|---|---|---|
| **Control Center v1** | ✅ **Ready now** | None — foundation + bootstrap + first-use polish all merged |
| **Stage 4 specification** (planning only) | ✅ **Ready now** | None — audit identifies the 3 library bugs to plan around |
| **Stage 4 implementation** (runtime integration) | ⚠ **Not ready** | Three library-only fixes must land first (see below) |
| **Customer validation work** | ⚠ **Conditional** | Only if `P005/F001` is added to the harness baseline first |
| **Next product implementation** (DNO rulepack / lifecycle viz / electrical layer) | ✅ **Ready now** | None for product code; coordination protocol changes recommended but not blocking |

## Workstream details

### Control Center v1 — READY NOW

The Project Control Center foundation, first-use polish, and worker
bootstrap are all merged and tagged. The audit set in this branch adds
documentation that strengthens the governance layer without requiring
code changes.

A Control Center v1 task could begin immediately. Recommended scope:

- Encode the [41_WORKER_COORDINATION_RISK_REVIEW.md](41_WORKER_COORDINATION_RISK_REVIEW.md)
  protocol changes into `06_WORKER_RULES.md` and the start/finish
  checklists.
- Implement the dirty-tree refusal in `start_task.py`.
- Add the AI_CONTROL namespace prefix migration (deferred from
  [39_CONTROL_FILE_AUDIT.md](39_CONTROL_FILE_AUDIT.md)).
- Mark the explicitly-superseded files as superseded.

### Stage 4 specification (planning only) — READY NOW

The library code in `app/structured_capture_schema.py` /
`app/structured_capture_validators.py` is sound *as a foundation*, and
this audit's content + the previous Stage 4 audit cataloguing
identifies every blocker that runtime integration would hit. A *spec*
can be written now.

The spec must consume:

- The "do not integrate until" checklist from the prior Stage 4
  audit.
- The pole_id / project_id / file_id schema gap.
- The `"none"` blank-token bug.
- The missing `source: "structured_capture"` registration in
  `app/field_reference.py`.
- The popup-display source-label requirement.

### Stage 4 implementation (runtime integration) — NOT READY

Three library-only fixes must land before runtime work begins. None
of these change runtime behaviour today; they are **prerequisites**:

1. **Disambiguate `"none"` from `_BLANK_TOKENS`.** Remove `"none"` from
   the blank-token set; add explicit handling for the schema fields
   where `"none"` is a valid enum (`stay_type`, `equipment_type`,
   `lean_direction`, `lean_severity`). Add a regression test per field.
2. **Add row-identity fields to the Stage 4 schema.** `pole_id`
   required for any non-metadata-only row; `project_id`, `file_id`
   recommended.
3. **Register Stage 4 fields in `app/field_reference.py`** with
   `source: "structured_capture"` so the popup renderer has a path.

Each fix is a separate scoped branch. No fix is large; together they
unblock integration.

After these land, the integration branch can proceed:

- Upload route accepts a Stage 4 CSV.
- Per-pole record merges Trimble + Stage 4 by `pole_id`.
- Popup renderer surfaces Stage 4 fields with a source label.
- QA engine consumes `condition`, `defect_severity`, etc. with a
  confidence-aware rulepack.

### Customer validation work — CONDITIONAL

The manual review harness has been validated against `P008/F001` and
`P010` repeatedly. **`P005/F001` has not been validated in any
2026-05 harness run** despite being on the recommended-jobs list in
`README_MANUAL_REVIEW.md`. Before any customer demo or external
validation:

1. Run the harness against `P005/F001`.
2. Capture the report into `validation_runs/`.
3. Log the run via `scripts/log_validation_run.py`.

If `P005/F001` runs cleanly, customer-facing validation work is
greenlit.

### Next product implementation — READY NOW

For the next product feature (lifecycle viz expansion, DNO rulepack
work, electrical asset layer, PoleCAD export):

- Master is at the cleanest state observed in 30 days.
- 866 tests pass.
- Pre-commit clean.
- The five unmerged branches do not block any of these workstreams —
  they are retirement candidates ([38_BRANCH_RETIREMENT_PLAN.md](38_BRANCH_RETIREMENT_PLAN.md)).

The coordination protocol changes recommended in
[41_WORKER_COORDINATION_RISK_REVIEW.md](41_WORKER_COORDINATION_RISK_REVIEW.md)
are *not* blocking — but starting a new feature without addressing
them is how the next set of merge conflicts gets created.

## Open risks before any next-phase work begins

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | The unmerged `claude-code/c2e2-support-suite` branch is "merge bait" — a future agent could attempt the literal merge again and regress master | High | Cherry-pick desired artefacts; archive branch; document in worker rules that mechanical merge is forbidden |
| 2 | The numbering collision in `AI_CONTROL/` will repeat on the next audit set | Medium | Adopt namespace prefixes; this audit had to renumber 20–26 → 36–42 |
| 3 | Two parallel active-task markers in `AI_CONTROL/05_HANDOFF.md` is not technically prevented | Medium | Single-writer rule + `start_task.py` refusing dirty AI_CONTROL working tree |
| 4 | `P005/F001` has no recent harness evidence | Low | Run before the next customer-visible release |
| 5 | The legacy `_archive/` is untouched but its structure is referenced occasionally | Low | Leave alone (per worker rules); revisit only if a dependency breaks |

## Recommended next action

In strict order:

1. **Tag and freeze master.** Apply a `post-c2e2-stable-2026-05-10`
   tag (or similar) to `f2587ed` so the audit's baseline is preserved.
2. **Land this audit branch** (`claude-code/post-c2e2-repository-control-audit`).
3. **Open a "Worker Coordination Hardening" branch** to encode the
   pre-task checks and `start_task.py` dirty-tree refusal.
4. **Open a "Branch Retirement" task** to execute
   [38_BRANCH_RETIREMENT_PLAN.md](38_BRANCH_RETIREMENT_PLAN.md)'s
   DELETE_NOW list.
5. **Open a "Stage 4 Library Fixes" task** to address the three
   blockers above before any Stage 4 runtime integration.
6. **Open a "P005/F001 Harness Baseline" task** before any
   customer-facing validation.

Every one of those is a scoped, easily-reviewable task. None of them
needs to happen in parallel; sequencing them in this order makes
each subsequent task safer than the last.
