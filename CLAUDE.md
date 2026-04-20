# Unitas-GridFlow — Claude Code Bootstrap

## What this project is
Narrow pre-CAD QA and compliance tool for UK electricity network survey-to-design handoffs.
A DNO survey compliance gatekeeper.

## Canonical location
/Users/noelcollins/Unitas-GridFlow/

## Session start rule
Before doing anything, read:
1. MASTER_PROJECT_READ_FIRST.md
2. AI_CONTROL/00_READ_THIS_FIRST.md through AI_CONTROL/06_DEVELOPMENT_PROCESS.md

## Current phase
Working local MVP. Next priority: improve app/dno_rules.py with real DNO QA rules.

## Run commands
- source .venv312/bin/activate
- python run.py (port 5001)
- pytest -v (20 tests must pass)

## Hard rules
- Never broaden scope
- Always run pytest after changes
- Always commit and push after confirmed changes
