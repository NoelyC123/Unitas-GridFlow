# Worktree and Branch Cleanup Plan

**Date:** 2026-05-10
**Purpose:** Classified recommendations for removal/retention of all active worktrees and branches
**Authority:** Document 66 (Pre-Pilot Cleanroom Audit)

---

## Worktree Cleanup Recommendations

### Immediate removal (safe post-verification)

These worktrees hold merged branches at old commits. Safe to remove after confirming the branch is merged to master:

1. **Unitas-GridFlow-field-pilot**
   - Branch: codex/stage4-field-pilot-operating-pack-v1
   - Commit: d9267c1 (merged to master 7971672)
   - Action: **Remove immediately after pilot**
   - Reason: Branch is fully merged; worktree is stale
   - Command: `git worktree remove Unitas-GridFlow-field-pilot`

2. **Unitas-GridFlow-stage4-readiness**
   - Branch: codex/stage4-readiness-specification
   - Commit: f09cc41 (merged to master)
   - Action: **Remove immediately after pilot**
   - Reason: Branch is fully merged; worktree is stale
   - Command: `git worktree remove Unitas-GridFlow-stage4-readiness`

3. **Unitas-GridFlow-stage4a-audit**
   - Branch: claude-code/stage4a-safety-harness-audit
   - Commit: 1c9f639 (merged to master)
   - Action: **Remove immediately after pilot**
   - Reason: Branch is fully merged; worktree is stale
   - Command: `git worktree remove Unitas-GridFlow-stage4a-audit`

4. **Unitas-GridFlow-stage4a-library**
   - Branch: codex/stage4a-library-correctness-fixes
   - Commit: 8a496c9 (merged to master)
   - Action: **Remove immediately after pilot**
   - Reason: Branch is fully merged; worktree is stale
   - Command: `git worktree remove Unitas-GridFlow-stage4a-library`

5. **Unitas-GridFlow-stage4b-safety**
   - Branch: codex/stage4b-4c-safety-pilot-harness
   - Commit: d9267c1 (merged to master)
   - Action: **Remove immediately after pilot**
   - Reason: Branch is fully merged; worktree is at old master
   - Command: `git worktree remove Unitas-GridFlow-stage4b-safety`

### Keep for field pilot (at or near master)

These worktrees hold current or recent work. Keep available during pilot for quick reference:

1. **Unitas-GridFlow-field-pilot-command**
   - Branch: codex/field-pilot-command-center-v1
   - Commit: 7971672 (at master HEAD)
   - Action: **Keep through pilot; remove after**
   - Reason: Field command center is stable reference; cleanup post-pilot
   - Timeline: Remove after field trial day

2. **Unitas-GridFlow-field-pilot-execution**
   - Branch: codex/real-field-pilot-execution-system-v1
   - Commit: 7971672 (at master HEAD)
   - Action: **Keep through pilot; remove after**
   - Reason: Real pilot execution CLI is active reference; cleanup post-pilot
   - Timeline: Remove after field trial day

3. **Unitas-GridFlow-stage4c-architecture**
   - Branch: claude-code/stage4c-architecture-gate-runtime-safety
   - Commit: d9267c1 (merged to master)
   - Action: **Keep through pilot; remove after**
   - Reason: Contains decision docs for reference during pilot; cleanup post-pilot
   - Timeline: Remove after field trial day

### Stale (do not use during pilot; remove post-cleanup phase)

These worktrees hold old feature branches not currently active:

1. **Unitas-GridFlow-c2f**
   - Branch: codex/c2f-review-focus-issue-filtering
   - Commit: 139c80a
   - Action: **Remove after branch health assessment**
   - Reason: Stale feature branch; not in use
   - Timeline: Cleanup phase, post-pilot

2. **Unitas-GridFlow-c2g**
   - Branch: codex/c2g-lifecycle-replacement-visualization
   - Commit: 9b7bb82
   - Action: **Remove after branch health assessment**
   - Reason: Stale feature branch; not in use
   - Timeline: Cleanup phase, post-pilot

3. **Unitas-GridFlow-review-v2**
   - Branch: codex/review-workspace-v2-command-center
   - Commit: 766599d
   - Action: **Remove after branch health assessment**
   - Reason: Stale feature branch; superseded by v3
   - Timeline: Cleanup phase, post-pilot

4. **Unitas-GridFlow-review-v3**
   - Branch: codex/review-operating-system-v3
   - Commit: 1166469
   - Action: **Remove after branch health assessment**
   - Reason: Stale feature branch; not in use
   - Timeline: Cleanup phase, post-pilot

### Do not touch (in use)

1. **Main repo (master)**
   - Action: **KEEP FOREVER**
   - Reason: Primary working branch

2. **Unitas-GridFlow-pre-pilot-audit**
   - Branch: claude-code/pre-pilot-cleanroom-release-readiness-audit
   - Action: **DO NOT TOUCH** (in active use)
   - Reason: Worktree conflict; in use by prior session
   - Timeline: Leave as-is; cleanup phase must investigate state

---

## Branch Cleanup Recommendations

### Cleanup timeline

#### Phase 1: Pre-Pilot (NOW)
- No branch deletions
- Merge decision-gate docs (see doc 68 recommendation)
- Complete this cleanroom audit and merge to master

#### Phase 2: Post-Pilot (after field trial day)
Delete remote branches (merged, stale):
- codex/c2f-review-focus-issue-filtering
- codex/c2g-lifecycle-replacement-visualization
- codex/review-workspace-v2-command-center
- codex/review-operating-system-v3
- (and 8 others from worktree audit — all safely merged)

Commands:
```bash
git push origin --delete codex/c2f-review-focus-issue-filtering
git push origin --delete codex/c2g-lifecycle-replacement-visualization
# ... etc for each
```

#### Phase 3: Post-Cleanup Verification (final)
After deletions, run `git branch -a` and `git worktree list` to confirm state.

### Branches to keep (forever, merged, reference value)

- master (primary)
- codex/c2e2-popup-expansion-implementation (reference if needed)
- claude-code/stage4c-architecture-gate-runtime-safety (decision docs reference)

### Unmerged branches: decision required

| Branch | Status | Recommendation | Owner decision |
|--------|--------|-----------------|---|
| claude-code/pre-pilot-cleanroom-v2 | Active task | Merge after audit complete | Merge to master |
| claude-code/stage4c-architecture-v2 | **Unmerged, has docs 56–60** | **MERGE before pilot** | Merge to master |
| claude-code/real-field-pilot-readiness-stage4c-gate-audit | **Unmerged, has docs 61–65** | **MERGE before pilot** | Merge to master |
| claude-code/post-c2e2-repository-control-audit | Unmerged, reference | Keep or merge; low priority | Decision deferred |
| claude-code/worker-coordination-hardening | Unmerged, reference | Keep or merge; low priority | Decision deferred |

---

## Cleanup safety checklist

Before removing any worktree or branch:

- [ ] Branch is confirmed merged to master (`git log --oneline master | grep <branch-name>` or `git merge-base --is-ancestor <branch> master`)
- [ ] No uncommitted changes in worktree
- [ ] No active development on branch
- [ ] No other team members using worktree
- [ ] Worktree deletion confirmed (`git worktree list` shows removal)

---

## Post-Cleanup Validation

After all deletions in Phase 2:

```bash
git worktree list          # Should show: main + 3 keeper worktrees
git branch -a | wc -l     # Should show significant reduction
git status                 # Should be clean
```

---

## Ownership and timing

- **Pre-Pilot:** Claude Code (this task)
- **Post-Pilot cleanup:** Noel or codex (after field trial day)
- **Final verification:** Noel or codex (after cleanup)

---

## Notes

- Do not rush cleanup; stale branches are safe.
- Merging unmerged decision-gate docs (phase 1) is **critical** before field pilot.
- Remove only after confirming merge status.
