# AGENTS.md

## Codex operating rules

Use the current task prompt and active `AI_CONTROL/` files for project direction.

Codex may:
- edit files
- create or use branches
- run checks
- commit locally

Codex must not:
- push to GitHub
- merge into `master`

When finished, return a short summary with:
- branch
- commit, if made
- changed files
- checks
- final status
