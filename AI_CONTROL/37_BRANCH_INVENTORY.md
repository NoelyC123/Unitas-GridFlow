# 37 — Branch Inventory (post-C2E2)

Snapshot date: **2026-05-10**, against master HEAD `f2587ed`.

Companion to [36_POST_C2E2_REPOSITORY_AUDIT.md](36_POST_C2E2_REPOSITORY_AUDIT.md);
recommended actions are in [38_BRANCH_RETIREMENT_PLAN.md](38_BRANCH_RETIREMENT_PLAN.md).

## Method

For each branch the audit recorded:

- **Last commit** — `git log -1 <branch>`
- **Ahead / behind master** — `git rev-list --left-right --count master...<branch>`
- **Merged status** — `git branch --merged master` / `--no-merged master`
- **High-risk file touches** — whether the branch modified
  `app/static/js/map-viewer.js`, the C2E2 schema/validators, the QA
  engine, or the upload route in commits not yet on master.
- **Purpose** — inferred from the branch name, last-commit subject,
  and any Project Control Center logs.

## Already merged into master (subsumed)

These branches reached master via PR or direct merge. They no longer
contain any work that isn't already on master.

| Branch | Last commit | Purpose | Action |
|---|---|---|---|
| `claude-code/backend-robustness-validation` | `89414a7` 2026-05-08 | Backend cleaning for messy real-world surveys | Safe to delete |
| `claude-code/stage4-structured-capture-foundation` | `56c0d31` 2026-05-09 | Stage 4 schema, validators, template generator (library only) | Safe to delete; tag `stage4-structured-capture-foundation-complete` preserves the SHA |
| `claude-code/technical-docs-field-architecture` | `e2fbe3d` 2026-05-09 | docs/FIELD_REFERENCE_GUIDE / ARCHITECTURE / API_REFERENCE / VALIDATION_WORKFLOW | Safe to delete |
| `codex/c2d-2-popup-grouping-labels` | (May) | C2D popup label package | Safe to delete |
| `codex/c2d-3-popup-field-catalog` | (May) | C2D field catalog package | Safe to delete |
| `codex/c2d-aa-review-workspace-package` | (May) | C2D review workspace | Safe to delete |
| `codex/c2d-ab-control-refresh` | (May) | C2D control file refresh | Safe to delete |
| `codex/c2d-ab-popup-field-truthfulness` | (May) | C2D popup truthfulness | Safe to delete |
| `codex/c2d-ac-map-workspace-usability` | (May) | C2D map workspace | Safe to delete |
| `codex/c2d-ad-validation-readiness-consolidation` | (May) | C2D validation readiness | Safe to delete |
| `codex/c2d-ae-validation-plan-docs` | (May) | C2D validation plan | Safe to delete |
| `codex/c2d-geometry-trust` | `b3e2170` 2026-05-05 | Route-level geometry trust scoring | Safe to delete |
| `codex/c2d-geometry-trust-validation-upgrade` | `9e5b2e7` 2026-05-07 | Geometry trust validation 10-part | Safe to delete |
| `codex/c2d-planner-awareness-layer` | `0c4fdbd` 2026-05-07 | Planner awareness layer | Safe to delete |
| `codex/c2d-review-workspace-integration` | `ff12233` 2026-05-07 | C2D review intelligence layer | Safe to delete |
| `codex/c2d-route-highlight-layer` | `fcd8a48` 2026-05-07 | Route highlight visibility | Safe to delete |
| `codex/c2d-span-clustering` | `4b50326` 2026-05-05 | Geometry issue span clustering | Safe to delete |
| `codex/c2d-span-validity` | `9df023d` 2026-05-05 | Span validity classification | Safe to delete |
| `codex/c2d-ux-truthfulness` | `83be828` 2026-05-05 | Trust-aware distances + cluster messaging | Safe to delete |
| `codex/c2d-x-popup-system` | (May) | C2D popup system | Safe to delete |
| `codex/c2d-y-popup-renderer` | (May) | C2D popup renderer | Safe to delete |
| `codex/c2d-z-map-review-polish` | (May) | C2D polish | Safe to delete |
| `codex/c2e2-map-navigation-followups` | `f2587ed` 2026-05-10 | C2E2 map nav followups | **Already at master HEAD**; safe to delete |
| `codex/c2f-review-focus-issue-filtering` | `139c80a` 2026-05-09 | C2F focus / issue filtering | Safe to delete |
| `codex/c2g-lifecycle-replacement-visualization` | `9b7bb82` 2026-05-09 | C2G lifecycle visualisation | Safe to delete |
| `codex/gridflow-control-center-v1` | `f2587ed` 2026-05-10 | (current Codex active branch) | **Same SHA as master** — keep until next codex task starts |
| `codex/stage4-structured-capture-integration-plan` | `212bd23` 2026-05-09 | Stage 4 integration planning | **Branch is at the bootstrap merge commit, not at any planning content.** Effectively abandoned in place. Safe to delete. |
| `c2d-1-field-inventory-alias-mapping` | (May) | Field inventory + alias mapping | Safe to delete |

## Not merged into master (5 branches)

| Branch | Last commit | Ahead / behind | Touches map-viewer.js | Purpose | Notes |
|---|---|---|---|---|---|
| `claude-code/c2e2-support-suite` | `5375069` 2026-05-10 | 15 / 3 | **Yes** | Older C2E2 popup scope reduction | Master has subsumed and gone *stricter*. Recent merge attempt was aborted because the literal merge rules would regress master. |
| `claude-code/stage4-structured-capture-technical-audit` | `13019f4` 2026-05-10 | 2 / 1 | No | Stage 4 audit docs (`22_STAGE4_TECHNICAL_AUDIT.md` etc.) | Audit-only; library code unchanged. |
| `codex/c2d-duplicate-detection` | `5c6d3c4` 2026-05-05 | 44 / 3 | No | Duplicate detection + map preview enrichment | Old; predates many merged C2D milestones. |
| `codex/c2d-geom-pipeline` | `665a1e4` 2026-05-05 | 44 / 2 | No | C2D Task 1 geometry pipeline validation | Old; Task 1 work likely covered by later geometry-trust merges. |
| `codex/c2d-struct-inference` | `9841341` 2026-05-05 | 37 / 1 | **Yes** | Task 3 UI fix: span validation fields in popup | Old; touches `map-viewer.js` — definite merge-conflict risk if revisited. |

## Backup / control branches

| Branch | Purpose | Notes |
|---|---|---|
| `backup/pre-cleanup-20260422-0943` | Pre-cleanup snapshot 2026-04-22 | Already merged; safe to delete after the audit lands |
| `backup/pre-control-audit-20260422-0946` | Pre-control-audit snapshot 2026-04-22 | Safe to delete |
| `control/c2e2-finalise-from-master` | C2E2 finalisation control branch (`debea0b`) | Reference only |

## Observations on naming and ownership

- `claude-code/*` and `codex/*` prefixes consistently distinguish the
  two AI workers. Continue this convention.
- `c2d-*` (no owner prefix) is a legacy convention from before the
  prefix rule was adopted. Either rename if revived or retire.
- `c2e2-support-suite` and similar suite-style names invite scope
  drift; the branch ended up touching popup rendering, helpers, tests,
  and docs. Future suites should be split into per-concern branches
  (one popup change, one helper, one doc).

## High-risk-file touches summary

Branches not on master that touch `app/static/js/map-viewer.js`:

- `claude-code/c2e2-support-suite` (high risk — already-aborted merge).
- `codex/c2d-struct-inference` (low risk in practice; the change is a
  span-validation row addition that's likely already handled in
  master's later C2D merges, but a re-merge would conflict).

No unmerged branch touches `app/qa_engine.py`, `app/routes/api_intake.py`,
the Stage 4 schema, or the Stage 4 validators in commits not yet on
master.
