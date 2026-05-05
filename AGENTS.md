# AGENTS.md

## Codex operating rules

Use the current task prompt and active `AI_CONTROL/` files for project direction.

Codex may:

- edit files
- create or use branches
- run checks
- commit locally
- push the current feature/task branch when explicitly instructed
- create a pull request for the current feature/task branch when explicitly instructed

Codex must not:

- push directly to `master`
- merge into `master`
- merge pull requests

When finished, return a short summary with:

- branch
- commit, if made
- PR link, if created
- changed files
- checks
- final status

Purpose:
Codex may package task work into commits and, when explicitly instructed, publish the feature branch and open a PR. Noel remains the control point for merge into `master`.
