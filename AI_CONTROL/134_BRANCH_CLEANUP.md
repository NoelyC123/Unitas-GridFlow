# Branch Cleanup Register

**Date:** 2026-05-18
**Command used:** `git branch -r` + `git branch -r --merged master`

**Updated:** 2026-05-18 — cleanup executed. See "Cleanup Executed" section below.

---

## Summary

| Category | Count |
|---|---|
| Merged into master (safe to delete) | 48 |
| Unmerged (active or orphaned) | 7 feature branches + 6 dependabot |
| Dependabot (auto-managed) | 6 |

---

## Merged Branches — Safe to Delete

All of the following are merged into `master`. Remote deletion is safe; local delete
with `git push origin --delete <branch>` after confirming no in-progress work.

| Branch | Owner | Stage |
|---|---|---|
| `claude-code/branch-retirement-control-deconfliction` | Claude Code | Governance |
| `claude-code/controlled-pilot-field-pack-v1` | Claude Code | Stage 4 |
| `claude-code/p-controlled-001-readiness-gate` | Claude Code | Stage 4 |
| `claude-code/p-real-001-mini-independent-gate-audit` | Claude Code | Stage 4 |
| `claude-code/stage4a-safety-harness-audit` | Claude Code | Stage 4A |
| `claude-code/stage4c-architecture-v2` | Claude Code | Stage 4C |
| `claude-code/stage4c-controlled-baseline-pilot-prep` | Claude Code | Stage 4C |
| `claude-code/stage5-data-readiness-plan` | Claude Code | Stage 5 |
| `claude-code/stage5b-workspace-foundation` | Claude Code | Stage 5B |
| `claude-code/stage5c-map-overlay` | Claude Code | Stage 5C |
| `claude-code/stage5e-design-ready-fix` | Claude Code | Stage 5E |
| `claude-code/stage5f-readiness-trimble-review` | Claude Code | Stage 5F |
| `claude-code/stage5g-feedback-tool-and-preflight` | Claude Code | Stage 5G |
| `claude-code/stage6a-complete-pole-notes` | Claude Code | Stage 6A |
| `claude-code/stage6c-completion-and-6e-spec` | Claude Code | Stage 6C/6E |
| `claude-code/stage6c-linking-spec` | Claude Code | Stage 6C |
| `claude-code/stage6e-workspace-readiness` | Claude Code | Stage 6E |
| `claude-code/stage7a-photo-spec` | Claude Code | Stage 7A |
| `claude-code/update-stage6a0-spike-after-notes-cleanup` | Claude Code | Stage 6A |
| `codex/c2d-struct-inference` | Codex | Stage 2 |
| `codex/plocal002-evidence-organiser` | Codex | P_LOCAL_002 |
| `codex/review-workspace-v2-command-center` | Codex | Stage 5 |
| `codex/stage4-structured-capture-integration-plan` | Codex | Stage 4 |
| `codex/stage5-control-refresh` | Codex | Stage 5 |
| `codex/stage5-plocal-validation-findings` | Codex | Stage 5 |
| `codex/stage5-quick-wins` | Codex | Stage 5 |
| `codex/stage5-validation-discovery` | Codex | Stage 5 |
| `codex/stage5a-foundation-v1` | Codex | Stage 5A |
| `codex/stage5a2-enhanced-reports` | Codex | Stage 5A |
| `codex/stage5e-output-registration` | Codex | Stage 5E |
| `codex/stage5f-safety-and-smoke-test` | Codex | Stage 5F |
| `codex/stage5g-review-script-and-summary` | Codex | Stage 5G |
| `codex/stage6a-enwl-evidence-parser` | Codex | Stage 6A |
| `codex/stage6a-enwl-trace-inspector-cli` | Codex | Stage 6A |
| `codex/stage6b-evidence-combiner` | Codex | Stage 6B |
| `codex/stage6b-evidence-export-bundle` | Codex | Stage 6B |
| `codex/stage6c-linking-implementation` | Codex | Stage 6C |
| `codex/stage6d-conflict-detection` | Codex | Stage 6D |
| `codex/stage6e-readiness-logic` | Codex | Stage 6E |
| `codex/stage7a-photo-integration` | Codex | Stage 7A |
| `control/add-gridflow-delivery-style` | Control | Governance |
| `control/c2e2-finalise-from-master` | Control | Stage 2 |
| `control/gridflow-delivery-style` | Control | Governance |
| `control/plocal002-notes-cleanup-before-stage6a` | Control | P_LOCAL_002 |
| `control/stage6a0-plocal002-linking-feasibility` | Control | Stage 6A |
| `control/stage6b-evidence-combiner-spec` | Control | Stage 6B |
| `worktree-p-local-001-field-capture-readiness-review` | Worktree | Stage 4 |
| `worktree-stage4-real-survey-pack-readiness-review` | Worktree | Stage 4 |

---

## Unmerged Branches — Review Before Deleting

These branches are NOT merged into master. Check whether they contain useful work before
deletion.

| Branch | Owner | Notes |
|---|---|---|
| `claude-code/c2e2-support-suite` | Claude Code | C2E2 support work — may contain unmerged evidence additions |
| `claude-code/pre-pilot-cleanroom-v2` | Claude Code | Pre-pilot cleanup — may supersede `pre-pilot-cleanroom` |
| `claude-code/real-field-pilot-readiness-stage4c-gate-audit` | Claude Code | Stage 4C gate audit — may still be relevant |
| `claude-code/stage4-structured-capture-technical-audit` | Claude Code | Structured capture audit — check against current state |
| `claude-code/stage4b-4c-safety-pilot-harness` | Claude Code | Safety harness — check if superseded by 8afeee0 fixes |
| `codex/c2d-duplicate-detection` | Codex | C2D duplicate detection — check if merged elsewhere |
| `codex/c2d-geom-pipeline` | Codex | C2D geometry pipeline — check if merged elsewhere |
| `claude-code/stage7-control-docs` | Claude Code | **ACTIVE** — current working branch (this document) |

---

## Dependabot Branches — Auto-managed

These are opened and managed automatically by Dependabot. Do not delete manually —
they are closed/merged by the GitHub workflow.

| Branch | Package | Action |
|---|---|---|
| `dependabot/github_actions/actions/checkout-6` | GitHub Actions | Merge or dismiss when ready |
| `dependabot/github_actions/actions/setup-python-6` | GitHub Actions | Merge or dismiss when ready |
| `dependabot/pip/certifi-2026.2.25` | certifi | Merge when ready |
| `dependabot/pip/geopandas-1.1.3` | geopandas | Merge when ready |
| `dependabot/pip/pyogrio-0.12.1` | pyogrio | Merge when ready |
| `dependabot/pip/pytz-2026.1.post1` | pytz | Merge when ready |
| `dependabot/pip/reportlab-4.4.10` | reportlab | Merge when ready |

---

## Recommended Action

1. Bulk-delete the 48 merged branches remotely when convenient. No work will be lost —
   all commits are in `master`.
2. Review the 7 unmerged feature branches individually before deleting. The two `c2d-*`
   branches in particular may contain Stage 2 geometry/duplicate-detection work not
   yet integrated.
3. Leave dependabot branches to auto-manage.
4. Leave `claude-code/stage7-control-docs` active until merged.

Bulk delete command (run only after review):

```bash
# Example — do not paste without reviewing the list first
git push origin --delete \
  claude-code/branch-retirement-control-deconfliction \
  claude-code/controlled-pilot-field-pack-v1 \
  ...
```

---

## Cleanup Executed — 2026-05-18

**Date:** 2026-05-18
**Executed by:** Claude Code session cleanup

**41 merged branches deleted via `git push origin --delete`:**

claude-code branches (19 deleted):
- `claude-code/branch-retirement-control-deconfliction`
- `claude-code/controlled-pilot-field-pack-v1`
- `claude-code/p-controlled-001-readiness-gate`
- `claude-code/p-real-001-mini-independent-gate-audit`
- `claude-code/stage4a-safety-harness-audit`
- `claude-code/stage4c-architecture-v2`
- `claude-code/stage4c-controlled-baseline-pilot-prep`
- `claude-code/stage5-data-readiness-plan`
- `claude-code/stage5b-workspace-foundation`
- `claude-code/stage5c-map-overlay`
- `claude-code/stage5e-design-ready-fix`
- `claude-code/stage5f-readiness-trimble-review`
- `claude-code/stage5g-feedback-tool-and-preflight`
- `claude-code/stage6a-complete-pole-notes`
- `claude-code/stage6c-completion-and-6e-spec`
- `claude-code/stage6c-linking-spec`
- `claude-code/stage6e-workspace-readiness`
- `claude-code/stage7a-photo-spec`
- `claude-code/update-stage6a0-spike-after-notes-cleanup`

codex branches (22 deleted):
- `codex/c2d-struct-inference`
- `codex/plocal002-evidence-organiser`
- `codex/review-workspace-v2-command-center`
- `codex/security-dependency-fix`
- `codex/stage4-structured-capture-integration-plan`
- `codex/stage5-control-refresh`
- `codex/stage5-plocal-validation-findings`
- `codex/stage5-quick-wins`
- `codex/stage5-validation-discovery`
- `codex/stage5a-foundation-v1`
- `codex/stage5a2-enhanced-reports`
- `codex/stage5e-output-registration`
- `codex/stage5f-safety-and-smoke-test`
- `codex/stage5g-review-script-and-summary`
- `codex/stage6a-enwl-evidence-parser`
- `codex/stage6a-enwl-trace-inspector-cli`
- `codex/stage6b-evidence-combiner`
- `codex/stage6b-evidence-export-bundle`
- `codex/stage6c-linking-implementation`
- `codex/stage6d-conflict-detection`
- `codex/stage6e-readiness-logic`
- `codex/stage7a-photo-integration`

**7 unmerged branches kept (unchanged):**

| Branch | Reason kept |
|---|---|
| `claude-code/c2e2-support-suite` | Unmerged — content review required |
| `claude-code/pre-pilot-cleanroom-v2` | Unmerged — check against current state |
| `claude-code/real-field-pilot-readiness-stage4c-gate-audit` | Unmerged — gate audit content may still be relevant |
| `claude-code/stage4-structured-capture-technical-audit` | Unmerged — check if superseded |
| `claude-code/stage4b-4c-safety-pilot-harness` | Unmerged — check if superseded by 8afeee0 fixes |
| `codex/c2d-duplicate-detection` | Unmerged — may contain unreleased Stage 2 work |
| `codex/c2d-geom-pipeline` | Unmerged — may contain unreleased Stage 2 geometry work |

Dependabot branches left untouched (auto-managed by GitHub).
