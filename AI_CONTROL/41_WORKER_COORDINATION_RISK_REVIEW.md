# 41 — Worker Coordination Risk Review

Audit of where Codex and Claude Code agents collided over the last
month, and what protocol changes prevent it next time. Master HEAD
`f2587ed` on 2026-05-10.

## Concrete incidents observed in the worker log + git history

### Incident 1 — Stale-state carry-over via shared working tree

**What happened.** When this audit's branch (`claude-code/post-c2e2-repository-control-audit`)
was created, the previous shell state was on `codex/gridflow-control-center-v1`,
which had already been left clean. Earlier turns showed the same
working tree carrying forward foreign edits from another agent's run
— most notably uncommitted modifications to
`AI_CONTROL/00_PROJECT_BOARD.md`, `03_WORKER_LOG.md`, and `05_HANDOFF.md`
that pointed at a *different* active task than the one the new agent
was starting.

**Risk.** Without `git restore`, those foreign edits would have been
committed by the new agent's `start_task.py` plus subsequent work,
attributing them to the wrong task and silently rewriting board /
handoff state.

**Prevention.** Always check `git status --short --branch` and
`scripts/control_status.py` before any `start_task.py` invocation. If
the working tree is dirty with control-file edits the current agent
did not author, `git restore` them or move them to a different branch
first.

### Incident 2 — Stage 4 numbering collision (`AI_CONTROL/22`–`24`)

**What happened.** The branch
`claude-code/stage4-structured-capture-technical-audit` produced docs
named `22_STAGE4_TECHNICAL_AUDIT.md`, `23_STAGE4_SCHEMA_READINESS_REVIEW.md`,
`24_STAGE4_RUNTIME_INTEGRATION_RISKS.md` — but on master, slots `22`,
`23`, `24` are already taken by Stage 3 acceptance / brief docs. The
branch never merged, partly because the file numbers collide with
master.

**Risk.** A naive merge would have either overwritten the Stage 3
closure docs or produced a confused master where two different files
share the same numeric prefix.

**Prevention.** New AI_CONTROL docs must check the next free slot at
creation time and adopt the namespace prefix proposed in
[39_CONTROL_FILE_AUDIT.md](39_CONTROL_FILE_AUDIT.md) (`PCS_`, `PRD_`,
`DOM_`, `STG_`, `AUD_`).

### Incident 3 — Parallel "Active task" markers across branches

**What happened.** During the Stage 4 work, the `AI_CONTROL/05_HANDOFF.md`
marked-section block was updated by two agents in close succession on
two different branches:

- Codex: `codex/stage4-structured-capture-integration-plan` set
  Active = "Stage 4 Structured Capture Integration Plan".
- Claude Code: `claude-code/stage4-structured-capture-technical-audit`
  set Active = "Stage 4 Structured Capture Technical Audit".

Each agent's working tree showed the *other's* edits when context
switched, leading to repeated `git restore` calls and one merge that
was aborted because the markers were inconsistent.

**Risk.** A future merge that takes the wrong side of the `<!--
PROJECT_CONTROL:HANDOFF_ACTIVE_START -->` marker block would lose
either Codex's or Claude Code's task framing, and downstream agents
read the handoff as the source of truth.

**Prevention.** **One marked active-task block per branch** is the
rule. Two agents must not both run `start_task.py` against the same
master baseline without one of them rebasing first. The marker is
inherently single-writer.

### Incident 4 — Aborted merge of `claude-code/c2e2-support-suite`

**What happened.** A merge spec was written assuming master had the
**old** popup-rendering code and the branch had the **new**
scope-reduced version. Reality was reversed: master had continued the
C2E2 work and was the stricter side. Mechanical "keep branch" rules
would have regressed master's truthfulness behaviour.

**Risk.** The merge spec reflected a stale assumption about which side
of master had the more recent work. A junior agent following the
literal rules would have pushed a regression to `master`.

**Prevention.** Before writing a merge spec, run:

```
git rev-list --left-right --count master...<branch>
git log master..<branch> --oneline | head
git log <branch>..master --oneline | head
```

…to confirm which side is "ahead" on the relevant files. If both sides
have advanced, the spec must direct semantic merge, not "keep branch".

## Where Codex and Claude Code overlapped (general patterns)

| Domain | Codex's lane | Claude Code's lane | Overlap risk |
|---|---|---|---|
| Map viewer (popup, navigation, focus) | C2D / C2E2 / C2F / C2G implementations | Audit, scope-reduction enforcement, doc | High — both edit `app/static/js/map-viewer.js` |
| Project Control Center | Foundation, polish, worker bootstrap | (review work, e.g. 8th-test addition) | Medium — both edit `AI_CONTROL/*` |
| Stage 4 | Integration plan (separate branch) | Schema/validators foundation, audit | Medium — schema + plan must agree |
| Validation harness | Replicated runs | Original Selenium implementation | Low — Codex consumes, Claude Code maintains |
| Documentation (docs/) | Per-feature READMEs | Cross-cutting technical docs | Low — different scopes |

## Required pre-task checks (mandatory)

These should be added to `AI_CONTROL/07_WORKER_START_CHECKLIST.md` (a
separate task, not this audit):

1. `git status --short --branch` — must be clean or only contain edits
   the current agent will commit.
2. `git rev-parse HEAD` — record the master baseline for the start of
   work.
3. `python scripts/control_status.py` — read the current control state.
4. Confirm the chosen branch name does not collide with an existing
   branch (`git branch -a | grep <name>`).
5. Confirm the chosen new-doc filename slot is free (`ls AI_CONTROL/<N>_*`).
6. If touching `app/static/js/map-viewer.js`, confirm no other
   unmerged branch has competing changes (`git log --all --source --
   app/static/js/map-viewer.js | head`).
7. Read `AI_CONTROL/05_HANDOFF.md` to confirm no parallel active-task
   marker exists for the same scope.

## Required source-of-truth checks (mandatory)

Before writing a feature plan or audit:

1. Read `AI_CONTROL/00_PROJECT_CANONICAL.md`.
2. Read `AI_CONTROL/01_CURRENT_STATE.md` and `02_CURRENT_TASK.md`.
3. Read `AI_CONTROL/00_PROJECT_BOARD.md` for the active-task marker.
4. Read `AI_CONTROL/05_HANDOFF.md` for the latest handoff.
5. Read `AI_CONTROL/06_WORKER_RULES.md`.
6. Read `AI_CONTROL/07_WORKER_START_CHECKLIST.md`.
7. **Avoid** the explicitly-superseded files
   `06_STRATEGIC_REVIEW_2026-04-22.md` and
   `07_REAL_WORLD_SURVEY_WORKFLOW.md`.

## Coordination protocol — proposed additions

Recommended additions to the worker rules (a separate task):

1. **Single-writer marked sections.** The HANDOFF / BOARD active-task
   `<!-- PROJECT_CONTROL:* -->` blocks are single-writer per master
   baseline. Two agents must not both hold those blocks at the same
   time — the second agent rebases.
2. **Dirty-tree before start.** `start_task.py` should refuse to run
   if `git status` has uncommitted edits to AI_CONTROL files; the
   refusal message should suggest `git restore` or branch creation.
3. **File-numbering check.** A pre-flight check before creating a new
   AI_CONTROL doc must confirm the slot is free.
4. **Pre-merge baseline check.** Any merge into master must include a
   `git rev-list --left-right --count master...<branch>` summary in
   the merge commit message so the reviewer can see which side
   advanced where.
5. **Map-viewer guard.** Any task whose spec says "do not change
   `app/static/js/map-viewer.js`" must have its branch's diff verified
   pre-commit:
   `git diff master -- app/static/js/map-viewer.js | wc -l` should be
   `0`.

## What this audit recommends

The protocol changes above are recommendations, not implementations.
This audit is doc-only. A separate task should:

1. Update `06_WORKER_RULES.md` to encode the rules above.
2. Update `07_WORKER_START_CHECKLIST.md` to cover the seven pre-task
   checks.
3. Update `08_WORKER_FINISH_CHECKLIST.md` to include the
   left-right-count summary as a finish-time deliverable.
4. Update `start_task.py` to refuse a dirty AI_CONTROL working tree
   (with a clear error message) — this is a code change that needs
   its own scoped branch.
