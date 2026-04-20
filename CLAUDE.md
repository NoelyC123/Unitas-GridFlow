# Unitas-GridFlow — Claude Code Bootstrap

## First action — read this before anything else
Read: AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md
That file is the single source of truth for the entire project.

## Then also read
- AI_CONTROL/03_CURRENT_TASK.md — what to do this session
- AI_CONTROL/04_SESSION_HANDOFF.md — what changed last session

## Claude Code specific

**Canonical location:** /Users/noelcollins/Unitas-GridFlow/
**GitHub repo:** https://github.com/NoelyC123/Unitas-GridFlow

**Run commands:**
source .venv312/bin/activate
python run.py              # port 5001
pytest -v                  # 23 tests must pass
pre-commit run --all-files

**Key files:**
- app/dno_rules.py         — QA rulepacks (CURRENT PRIORITY — add more DNOs)
- app/qa_engine.py         — QA engine (7 check types)
- app/routes/api_intake.py — CSV processing pipeline
- app/routes/api_upload.py — file upload handling
- app/routes/pdf_reports.py — PDF generation
- app/routes/api_rulepacks.py — rulepack API (currently stub — needs wiring)
- tests/                   — pytest suite, must stay green

**Hard rules:**
- Read a file before editing it — never assume contents
- Run pytest -v after every code change — 23 tests must pass
- git add/commit/push after confirmed passing tests
- Never broaden scope beyond narrow MVP
- Never restore from _quarantine/ blindly
