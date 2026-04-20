# Unitas-GridFlow — Claude Code Bootstrap

## First action — read this before anything else
Read: `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md`
That file is the single source of truth for the entire project. It contains current test count, check-type count, rulepack list, and current priority.

## Then also read
- `AI_CONTROL/03_CURRENT_TASK.md` — what to do this session
- `AI_CONTROL/04_SESSION_HANDOFF.md` — what changed last session
- `CHANGELOG.md` — rolling history of what shipped

## Claude Code specific

**Canonical location:** `/Users/noelcollins/Unitas-GridFlow/`
**GitHub repo:** `https://github.com/NoelyC123/Unitas-GridFlow`

**Run commands:**
```
source .venv312/bin/activate
python run.py              # port 5001
pytest -v                  # all tests must pass
pytest --cov=app           # coverage report
pre-commit run --all-files
```

**Key files:**
- `app/dno_rules.py`         — QA rulepacks (current priority: add more DNOs)
- `app/qa_engine.py`         — QA engine (check types listed in master truth §4)
- `app/routes/api_intake.py` — CSV processing pipeline
- `app/routes/api_upload.py` — file upload handling
- `app/routes/pdf_reports.py` — PDF generation
- `app/routes/api_rulepacks.py` — rulepack API (stub — needs wiring)
- `tests/`                   — pytest suite, must stay green

**Hard rules** (full list in master truth §7):
- Read a file before editing it — never assume contents.
- Run `pytest -v` after every code change.
- `git add / commit / push` after confirmed passing tests.
- Never broaden scope beyond narrow MVP.
- Never restore from `_quarantine/` blindly.
- Never treat Copilot suggestions as authoritative for DNO-specific values.
