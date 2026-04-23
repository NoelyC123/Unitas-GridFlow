# Unitas-GridFlow — Claude Code Runtime Instructions

## Core rule

Minimise token usage.

- Read the minimum necessary files
- Do not reload full context for each task
- Do not re-read files already read in the current task unless needed
- Do not ask repeated confirmation questions inside an approved step

---

## Session start (STRICT)

At the start of a session, read only:

1. `AI_CONTROL/00_PROJECT_CANONICAL.md`
2. `AI_CONTROL/02_CURRENT_TASK.md`

Read additional files only if needed:

- `AI_CONTROL/01_CURRENT_STATE.md` → only if current reality is needed
- `AI_CONTROL/04_SESSION_HANDOFF.md` → only if continuing prior work
- `AI_CONTROL/06_STRATEGIC_REVIEW_2026-04-22.md` → only if strategic direction is relevant to the current step
- `WORKFLOW_SYSTEM.md` → only if tool roles or operating model are relevant
- specific code/test files → only if they are part of the approved task

Never read unless explicitly asked:

- `AI_CONTROL/05_PROJECT_REFERENCE.md`
- anything under `_archive/`

---

## Project identity

Unitas GridFlow is a narrow pre-CAD QA and compliance tool for survey-to-design handoffs.

Core principle: act as the trusted gate between survey and design — improving the reliability, clarity, and design-readiness of real survey data before office work begins.

Purpose:

- validate survey data before design/CAD
- catch real-world data issues early
- act as a structured QA gate between survey and design

It is not a general platform.

In the workflow system (see `WORKFLOW_SYSTEM.md`), Claude Code is the **execution engine**: implement tasks exactly as defined, keep tests passing, make minimal targeted changes. Decisions about what to build are made by the human and ChatGPT orchestrator.

---

## Current direction

Follow:

- `AI_CONTROL/02_CURRENT_TASK.md` for what to do
- `AI_CONTROL/01_CURRENT_STATE.md` only if needed for current truth

Important strategic update:

- The project should continue
- The next phase must be validation-led
- Do not assume more features are the right next step without real survey-file evidence

Do not invent tasks or broaden scope.

---

## Default execution mode

When given an approved task, proceed end-to-end within scope.

You may:

- read only necessary files
- edit only necessary in-scope files
- run tests
- update clearly necessary docs/control files

You must:

- keep scope narrow
- avoid unrelated refactors
- avoid architecture changes unless explicitly part of the task
- stop only if something outside scope becomes necessary

---

## Default post-change workflow

After code changes:

1. Run:
   `pytest -v`

2. Run:
   `pre-commit run --all-files`

3. If pre-commit modifies files:
   - stage those files
   - continue

4. Then:
   `git add .`
   `git commit -m "<clear message>"`
   `git push`

Do not stop before commit unless instructed or blocked.

---

## Default output

Return one final report only:

1. files changed
2. exact work completed
3. tests run and results
4. docs/control files updated
5. commit message used
6. commit hash
7. final git status

Keep the report concise.

---

## Hard rules

- Never read unnecessary files
- Never reload full project context without need
- Never use `_archive/` as active instruction
- Never assume file contents
- Always test before commit
- Always commit completed approved work
- Never replace real-world validation with abstract feature work

---

## Efficiency behaviour

Prefer:

- fewer reads
- fewer messages
- end-to-end execution
- one final report

Avoid:

- repeated confirmations
- unnecessary explanations
- re-reading control files in the same task
- reviewing files unrelated to the approved task
