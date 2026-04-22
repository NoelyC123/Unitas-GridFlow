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
- `_archive/docs/PROJECT_SYNTHESIS/` — only if historical strategic context is needed
- `_archive/control_layer/old_ai_control/` — only if old control-layer history is needed

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
```

## Active project focus

Unitas GridFlow is a narrow pre-CAD QA and compliance tool for UK electricity network survey-to-design handoffs.

Core purpose:
- validate survey data before CAD/design
- enforce DNO-specific compliance rules
- surface issues early
- generate QA outputs (CSV, map, PDF)

## Current working direction

Always derive direction from:

- `AI_CONTROL/02_CURRENT_TASK.md`
- `AI_CONTROL/01_CURRENT_STATE.md`

These override assumptions.

## Key live files

- `app/dno_rules.py` — QA rulepacks (primary development area)
- `app/qa_engine.py` — QA engine (check execution logic)
- `app/routes/api_intake.py` — CSV processing pipeline
- `app/routes/api_upload.py` — file upload handling
- `app/routes/pdf_reports.py` — PDF generation
- `app/routes/api_rulepacks.py` — rulepack API (integration layer)
- `tests/` — pytest suite (must always stay green)

## Development workflow

After any code change:

1. Run tests:
   ```bash
   pytest -v
   ```

2. If passing:
   ```bash
   git add .
   git commit -m "clear message"
   git push
   ```

3. Keep control layer updated if needed:
   - `AI_CONTROL/01_CURRENT_STATE.md`
   - `AI_CONTROL/02_CURRENT_TASK.md`
   - `AI_CONTROL/04_SESSION_HANDOFF.md`
   - `CHANGELOG.md`

## Hard rules

- Read a file before editing it.
- Do not assume file contents.
- Run `pytest -v` after every code change.
- Keep scope tied strictly to the current task.
- Do not treat archived files as active instructions.
- Never restore from `_archive/quarantine/old_quarantine/` blindly.
- Never treat autocomplete or AI suggestions as authoritative for DNO-specific values.
- Keep the active control layer and live code aligned at all times.

## Important constraints

- This is a narrow MVP tool, not a general platform.
- Avoid adding features outside current task scope.
- DNO rules must be:
  - explicit
  - testable
  - traceable to real-world logic, not guessed

## Historical context (optional)

Use only if needed:

- `_archive/docs/PROJECT_SYNTHESIS/` → strategy and AI analysis
- `_archive/control_layer/old_ai_control/` → previous system versions

These are reference only, not active instructions.
