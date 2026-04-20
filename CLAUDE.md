# Unitas-GridFlow — Claude Code Context

## What this project is
Unitas GridFlow is a narrow pre-CAD QA and compliance tool for UK electricity
network survey-to-design handoffs. Local Flask/Python web app.
Short identity: a DNO survey compliance gatekeeper.

## Canonical location
/Users/noelcollins/Unitas-GridFlow/

## GitHub repo
https://github.com/NoelyC123/Unitas-GridFlow

## Session start rule — read these first every session
1. MASTER_PROJECT_READ_FIRST.md
2. AI_CONTROL/00_READ_THIS_FIRST.md
3. AI_CONTROL/01_PROJECT_TRUTH.md
4. AI_CONTROL/02_CURRENT_STATE.md
5. AI_CONTROL/03_CURRENT_TASK.md
6. AI_CONTROL/04_SESSION_HANDOFF.md

## Current phase
Working local MVP with rulepack architecture in place.
23 tests passing. Next: coordinate consistency check + SSEN_11kV rulepack.

## Tech stack
- Python 3.13, venv: .venv312
- Flask, pandas, geopandas, reportlab, shapely, pyproj
- Leaflet, Bootstrap 5
- pre-commit, Ruff, pytest, GitHub Actions CI
- Tools: VS Code, Cursor Pro, Claude Code, macOS Terminal/zsh, Git/GitHub

## Run commands
source .venv312/bin/activate
python run.py              # runs on port 5001
pytest -v                  # 23 tests must pass
pre-commit run --all-files

## Key files
- app/dno_rules.py         — QA rulepacks (SPEN_11kV live, more DNOs next)
- app/qa_engine.py         — QA engine (7 check types)
- app/routes/api_intake.py — CSV processing pipeline
- app/routes/api_upload.py — file upload handling
- app/routes/pdf_reports.py — PDF generation
- app/templates/           — HTML templates (Unitas GridFlow branding)
- tests/                   — pytest suite, must stay green

## Hard rules
- Never broaden scope beyond narrow MVP
- Always read a file before editing it — never assume contents
- Always run pytest -v after any code change
- Always git add/commit/push after confirmed passing tests
- Commit messages must be clear and descriptive
