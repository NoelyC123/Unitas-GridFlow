# Unitas-GridFlow — Claude Code Bootstrap

## First action — read this before anything else
Read these files in this order:

1. `AI_CONTROL/00_PROJECT_CANONICAL.md`
2. `AI_CONTROL/01_CURRENT_STATE.md`
3. `AI_CONTROL/02_CURRENT_TASK.md`
4. `AI_CONTROL/03_WORKING_RULES.md`
5. `AI_CONTROL/04_SESSION_HANDOFF.md`
6. `AI_CONTROL/05_PROJECT_REFERENCE.md`

These files are the active control layer for the project.

## Then also read
- `CHANGELOG.md` — rolling history of what shipped
- `README.md` — project overview and setup
- `_archive/docs/PROJECT_SYNTHESIS/` only if historical strategic context is needed
- `_archive/control_layer/old_ai_control/` only if old control-layer history is needed

## Claude Code specific

**Canonical location:** `/Users/noelcollins/Unitas-GridFlow/`
**GitHub repo:** `https://github.com/NoelyC123/Unitas-GridFlow`

## Run commands

```bash
source .venv312/bin/activate
python run.py
pytest -v
pytest --cov=app
pre-commit run --all-files
