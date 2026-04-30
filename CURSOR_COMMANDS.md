# Cursor Commands Cheat Sheet — Unitas GridFlow

## Copy/Paste These Exact Commands

### Environment Setup
```bash
source .venv312/bin/activate
```

### Run Application
```bash
python run.py
```
Then open: http://localhost:5001

### Testing
```bash
# All tests
pytest -v

# With coverage
pytest --cov=app --cov-report=html

# Specific file
pytest tests/test_qa_engine.py -v

# Specific test
pytest -k test_name
```

### Code Quality
```bash
# Check and fix
ruff check --fix .

# Check only
ruff check .

# All pre-commit checks
pre-commit run --all-files
```

### Git Workflow
```bash
git status
git add .
git commit -m "clear message here"
git push origin master
```

### Clean Caches
```bash
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type d -name ".pytest_cache" -exec rm -r {} +
find . -type d -name ".ruff_cache" -exec rm -r {} +
rm -f .coverage
```

### Health Check
```bash
curl http://localhost:5001/health/full
```

---

## Cursor AI Prompts (Copy/Paste)

### Start New Session
```
Read AI_CONTROL/02_CURRENT_TASK.md and tell me what I should work on right now.
```

### Understand Current State
```
Read AI_CONTROL/01_CURRENT_STATE.md and summarize the current project status.
```

### Check Control Layer
```
What are the current working rules for this project?
```

### Implement Task
```
I need to [describe task]. Read the relevant files and propose the implementation.
```

### Add Tests
```
Add pytest tests for [feature/function] in the appropriate test file.
```

### Fix Lint Issues
```
Fix all Ruff linting errors in [filename].
```

### Update Documentation
```
Update CHANGELOG.md with the changes from this session.
```

### Explain Code
```
Explain what [function/module] does and how it fits into the overall system.
```

---

## Keyboard Shortcuts

| Action | Mac |
|--------|-----|
| Cursor Chat | `Cmd+L` |
| Quick Edit | `Cmd+K` |
| Composer | `Cmd+Shift+I` |
| Command Palette | `Cmd+Shift+P` |
| Quick Open | `Cmd+P` |
| Search | `Cmd+Shift+F` |
| Terminal | `` Ctrl+` `` |
| Source Control | `Cmd+Shift+G` |
| Debug | `F5` |
| Run Task | `Cmd+Shift+P` → Tasks: Run Task |

---

## Quick Tasks (Cmd+Shift+P → Tasks: Run Task)

- **Run All Tests**
- **Run Tests with Coverage**
- **Run Pre-Commit Checks**
- **Lint and Fix Code**
- **Run Flask Application**
- **Full Quality Check** (tests + pre-commit)
- **Clean Python Cache**

---

## File Locations

| What | Where |
|------|-------|
| Control layer | `AI_CONTROL/` |
| Source code | `app/` |
| Tests | `tests/` |
| Changelog | `CHANGELOG.md` |
| Setup guide | `CURSOR_SETUP_GUIDE.md` |
| This cheat sheet | `CURSOR_COMMANDS.md` |

---

## First-Time Setup Checklist

- [ ] Activate environment: `source .venv312/bin/activate`
- [ ] Verify Python: `python --version` (should be 3.13.x)
- [ ] Install extensions (see `CURSOR_SETUP_GUIDE.md`)
- [ ] Run tests: `pytest -v` (all should pass)
- [ ] Run app: `python run.py` (should start on port 5001)

---

## Daily Workflow Checklist

- [ ] Activate environment
- [ ] Read current task: `AI_CONTROL/02_CURRENT_TASK.md`
- [ ] Make changes
- [ ] Run tests: `pytest -v`
- [ ] Run pre-commit: `pre-commit run --all-files`
- [ ] Commit: `git add . && git commit -m "message"`
- [ ] Push: `git push origin master`

---

## Emergency Commands

### If tests fail
```bash
pytest -v --tb=short  # Show short traceback
pytest -x             # Stop at first failure
pytest --lf           # Run last failed tests only
```

### If pre-commit fails
```bash
ruff check --fix .    # Auto-fix most issues
pre-commit run --all-files  # Re-run after fixes
```

### If app won't start
```bash
# Check port not in use
lsof -i :5001

# Kill process on port 5001
kill -9 $(lsof -t -i:5001)

# Start fresh
source .venv312/bin/activate
python run.py
```

### If environment broken
```bash
# Deactivate
deactivate

# Remove old venv
rm -rf .venv312

# Recreate
python3.13 -m venv .venv312
source .venv312/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install pre-commit ruff pytest
```

---

**Keep this file open in a second Cursor window for quick reference.**
