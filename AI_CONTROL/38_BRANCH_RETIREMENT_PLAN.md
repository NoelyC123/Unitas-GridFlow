# 38 — Branch Retirement Plan

Companion to [37_BRANCH_INVENTORY.md](37_BRANCH_INVENTORY.md). The
inventory documents *what is*; this document documents *what to do*.
The plan classifies every branch into one of six action buckets and
specifies the safety procedure for each.

The audit itself **must not delete or merge** any branch (per the task
spec). This document is a recommendation that a future explicitly
authorised cleanup task can execute.

## Action buckets

| Bucket | Meaning | When to act |
|---|---|---|
| **DELETE_NOW** | Already merged, no remaining work; tag (if any) preserves the SHA. Safe. | Immediately, in the next cleanup task. |
| **DELETE_AFTER_CONFIRM** | Merged or subsumed, but worth a second human glance before deletion. | After Noel confirms. |
| **KEEP_AS_REFERENCE** | Not merged but preserves useful historical context that might be cherry-picked later. | Indefinite; revisit in 90 days. |
| **DO_NOT_TOUCH** | Active work or backups that must remain. | Until owner re-classifies. |
| **MANUAL_INSPECTION** | Unmerged with non-trivial unique work; someone needs to read it before deciding. | Schedule a review task. |
| **CHERRY_PICK_ONLY** | Unmerged, but the only useful artifacts are specific files that should be plucked into master, not the whole branch. | Schedule a cherry-pick task. |

## Recommended action per branch

### Already merged into master

| Branch | Tag preserves SHA? | Recommended | Notes |
|---|---|---|---|
| `claude-code/backend-robustness-validation` | No tag | **DELETE_NOW** | Backend cleaning helpers landed in master |
| `claude-code/stage4-structured-capture-foundation` | `stage4-structured-capture-foundation-complete` | **DELETE_NOW** | Tag preserves SHA |
| `claude-code/technical-docs-field-architecture` | `technical-docs-field-architecture-complete` | **DELETE_NOW** | Tag preserves SHA |
| `codex/c2d-2-popup-grouping-labels` | various C2D tags | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-3-popup-field-catalog` | various C2D tags | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-aa-review-workspace-package` | C2D review tags | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-ab-control-refresh` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-ab-popup-field-truthfulness` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-ac-map-workspace-usability` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-ad-validation-readiness-consolidation` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-ae-validation-plan-docs` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-geometry-trust` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-geometry-trust-validation-upgrade` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-planner-awareness-layer` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-review-workspace-integration` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-route-highlight-layer` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-span-clustering` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-span-validity` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-ux-truthfulness` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-x-popup-system` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-y-popup-renderer` | – | **DELETE_NOW** | Old C2D iteration |
| `codex/c2d-z-map-review-polish` | – | **DELETE_NOW** | Old C2D iteration |
| `c2d-1-field-inventory-alias-mapping` | – | **DELETE_NOW** | Old C2D iteration; also a no-prefix legacy name |
| `codex/c2e2-map-navigation-followups` | `c2e2-map-navigation-followups-complete` | **DELETE_NOW** | Branch tip = master HEAD |
| `codex/c2f-review-focus-issue-filtering` | `c2f-review-focus-issue-filtering-complete` | **DELETE_NOW** | Tag preserves SHA |
| `codex/c2g-lifecycle-replacement-visualization` | `c2g-lifecycle-replacement-visualization-complete` | **DELETE_NOW** | Tag preserves SHA |
| `codex/stage4-structured-capture-integration-plan` | – | **DELETE_AFTER_CONFIRM** | Branch never advanced past bootstrap merge; confirm no unpublished planning content lives only on this ref |
| `codex/gridflow-control-center-v1` | – | **DO_NOT_TOUCH** | Currently the active codex branch; same SHA as master only because no work has landed yet |

### Not merged into master

| Branch | Recommended | Why |
|---|---|---|
| `claude-code/c2e2-support-suite` | **CHERRY_PICK_ONLY → then DELETE_AFTER_CONFIRM** | Master has *subsumed and gone stricter*. The aborted merge proved a mechanical merge would regress master's truthfulness. Cherry-pick: (a) `AI_CONTROL/35_POPUP_HTML_EXAMPLES.md` (already on master via `debea0b`); (b) any regression tests that still apply under master's stricter `c2e2SupportPopupSections`. Then archive. |
| `claude-code/stage4-structured-capture-technical-audit` | **CHERRY_PICK_ONLY → then DELETE_AFTER_CONFIRM** | The three Stage 4 audit docs (`22_STAGE4_TECHNICAL_AUDIT.md` etc.) are useful but their numbering collides with master. Cherry-pick under non-colliding numbers (e.g. `43_STAGE4_TECHNICAL_AUDIT.md`). Then delete. |
| `codex/c2d-duplicate-detection` | **MANUAL_INSPECTION** | 44 commits ahead, never merged; touches the map preview enrichment pipeline. Worth one read before retiring. |
| `codex/c2d-geom-pipeline` | **MANUAL_INSPECTION** | 44 commits ahead, never merged; predates the merged C2D geometry-trust work. Likely subsumed but verify. |
| `codex/c2d-struct-inference` | **MANUAL_INSPECTION** | 37 commits ahead, touches `map-viewer.js`. Definite conflict risk if revisited; needs a read to decide cherry-pick vs delete. |

### Backup / control branches

| Branch | Recommended | Notes |
|---|---|---|
| `backup/pre-cleanup-20260422-0943` | **DELETE_AFTER_CONFIRM** | Pre-cleanup snapshot from April; superseded |
| `backup/pre-control-audit-20260422-0946` | **DELETE_AFTER_CONFIRM** | Pre-control-audit snapshot from April; superseded |
| `control/c2e2-finalise-from-master` | **DELETE_AFTER_CONFIRM** | Control finalisation branch; tip is at `debea0b` (already merged) |

## Highest-risk stale branches (in order)

1. **`claude-code/c2e2-support-suite`** — High risk because:
   - It is *not yet* deleted, so a future agent could attempt to merge it again.
   - The literal "keep branch side" rule from the merge spec would regress master's stricter C2E2 truthfulness.
   - It touches `app/static/js/map-viewer.js`, the highest-blast-radius file in the repo.
2. **`codex/c2d-struct-inference`** — Medium-high risk because:
   - It also touches `map-viewer.js`.
   - It is far behind master (37 commits) so any revival merge is conflict-heavy.
3. **`codex/stage4-structured-capture-integration-plan`** — Low-medium risk because:
   - The branch reports as merged but its tip is the bootstrap merge commit, not its planning content. A reader might assume the integration plan is canon.
   - Either delete (if the planning lived only as working-tree drafts that never committed) or surface its actual planning content somewhere.

## Safety procedure for the future cleanup task

When the cleanup task runs (separate, explicitly-authorised branch):

1. Confirm master HEAD matches `f2587ed` (or whatever later baseline is named).
2. Run `pytest -v` and `pre-commit run --all-files` — both must pass.
3. For every **DELETE_NOW** branch, confirm `git branch --merged master` still lists it.
4. For every branch with a tag, confirm `git rev-list --count <tag> ^master` is `0` before deleting the branch (i.e. the tag actually preserves the SHA).
5. Delete local first, then push the deletion: `git push origin --delete <branch>`.
6. Never delete `master`, `origin/master`, the active codex branch, or any tag.
7. Open a PR adding to [03_WORKER_LOG.md](03_WORKER_LOG.md) with the
   list of branches deleted and why.

## What this audit deliberately does NOT do

- Does **not** delete any branch.
- Does **not** push deletions to `origin`.
- Does **not** rename branches.
- Does **not** create or remove tags.
- Does **not** modify the `_archive/` directory.
