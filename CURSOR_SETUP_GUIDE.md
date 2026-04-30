# Cursor Setup Complete — Quick Start Guide

## What Was Configured

✅ **`.cursorrules`** — Comprehensive AI rules for Cursor
✅ **`.vscode/settings.json`** — Optimized editor settings
✅ **`.vscode/tasks.json`** — Quick-run tasks
✅ **`.vscode/launch.json`** — Debug configurations
✅ **`.vscode/extensions.md`** — Recommended extensions
✅ **`.vscode/tasks.md`** — Task reference guide

---

## First-Time Setup

### 1. Install Recommended Extensions

```bash
# Essential extensions
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension charliermarsh.ruff
code --install-extension eamodio.gitlens
code --install-extension yzhang.markdown-all-in-one
```

Or: Press `Cmd+Shift+X` and search for each extension manually.

### 2. Activate Virtual Environment

```bash
source .venv312/bin/activate
```

### 3. Verify Setup

```bash
python --version          # Should show 3.13.x
which python              # Should show .venv312/bin/python
pytest --version          # Should show pytest installed
ruff --version            # Should show ruff installed
```

---

## Daily Workflow

### Start Working

```bash
# Activate environment
source .venv312/bin/activate

# Run app
python run.py
# App available at http://localhost:5001
```

### Run Tests

```bash
# All tests
pytest -v

# Specific file
pytest tests/test_qa_engine.py -v

# With coverage
pytest --cov=app --cov-report=html
```

### Check Code Quality

```bash
# Run all pre-commit checks
pre-commit run --all-files

# Or just Ruff
ruff check .
ruff check --fix .  # Auto-fix issues
```

### Commit Changes

```bash
git status
git add .
git commit -m "clear, specific message"
git push origin master
```

---

## Cursor Features to Use

### 1. Cmd+K (Quick Edit)
- Make inline code edits
- Ask questions about specific code
- Generate small functions

### 2. Cmd+L (Chat)
- Ask broader questions
- Get explanations
- Discuss architecture
- Reference control layer files

### 3. Cmd+Shift+I (Composer)
- Multi-file changes
- Complex refactors
- Feature implementation
- Always reads `.cursorrules` first

### 4. Cmd+Shift+P (Command Palette)
```
Tasks: Run Task          # Run pytest, pre-commit, etc.
Python: Select Interpreter  # Choose .venv312
Debug: Start Debugging   # Launch Flask debugger
Git: Commit              # Commit changes
```

### 5. Testing Panel
- Click Testing icon in sidebar
- See all tests
- Run/debug individual tests
- See coverage

---

## Key Cursor Behaviors

### Auto-Reads on Startup
When you start Cursor, it will automatically read:
1. `.cursorrules`
2. `AI_CONTROL/00_PROJECT_CANONICAL.md`
3. `AI_CONTROL/02_CURRENT_TASK.md`

### Smart Context
Cursor will prioritize these files for context:
- `AI_CONTROL/` files (control layer)
- `app/` files (source code)
- `tests/` files (test suite)
- `README.md`, `CHANGELOG.md`

### Auto-Ignores
Cursor will ignore:
- `.venv312/` (virtual environment)
- `_archive/` (historical files)
- `uploads/` (job data)
- `__pycache__/`, `.pytest_cache/`, etc.

---

## Task Shortcuts

Press `Cmd+Shift+P` → `Tasks: Run Task`:

- **Run All Tests** — `pytest -v`
- **Run Tests with Coverage** — `pytest --cov=app`
- **Run Pre-Commit Checks** — `pre-commit run --all-files`
- **Lint and Fix Code** — `ruff check --fix .`
- **Run Flask Application** — Starts dev server
- **Clean Python Cache** — Removes `__pycache__` etc.
- **Full Quality Check** — Tests + pre-commit

---

## Debug Shortcuts

Press `F5` or `Cmd+Shift+D` then select:

- **Python: Flask App** — Debug Flask application
- **Python: Current File** — Debug current Python file
- **Python: Pytest Current File** — Debug current test file
- **Python: Pytest All** — Debug all tests

Set breakpoints with `F9`.

---

## File Navigation

### Quick Open File
`Cmd+P` → Type filename → Enter

### Go to Symbol
`Cmd+Shift+O` → Type function/class name → Enter

### Search Across Files
`Cmd+Shift+F` → Type search term → Enter

### Navigate Back/Forward
`Ctrl+-` (back) / `Ctrl+Shift+-` (forward)

---

## Useful Cursor Commands

### Ask About Current Task
```
Cmd+L → "What should I work on right now?"
```
Cursor will read `AI_CONTROL/02_CURRENT_TASK.md`

### Understand a Function
```
Select function → Cmd+K → "Explain this function"
```

### Generate Tests
```
Select function → Cmd+K → "Write pytest tests for this"
```

### Fix Lint Errors
```
Cmd+K → "Fix all Ruff errors in this file"
```

### Check Control Layer
```
Cmd+L → "What is the current project status?"
```
Cursor will read `AI_CONTROL/01_CURRENT_STATE.md`

---

## Project Structure Awareness

Cursor knows:
- `AI_CONTROL/` = project truth and direction
- `app/` = live source code
- `tests/` = test suite (must stay green)
- `_archive/` = historical only (never use for active work)
- `uploads/` = job data (do not edit)

---

## Quality Gates

Before any commit, Cursor will remind you:
1. ✅ `pytest -v` must pass
2. ✅ `pre-commit run --all-files` must pass
3. ✅ Code changes are minimal and targeted
4. ✅ Control layer updated if state changed
5. ✅ `CHANGELOG.md` updated if something shipped

---

## Common Cursor Prompts

### Start a New Task
```
"Read AI_CONTROL/02_CURRENT_TASK.md and tell me what to work on"
```

### Implement a Feature
```
"Add a new QA check for [specific validation]"
```
Cursor will:
1. Read relevant files
2. Propose changes
3. Implement after confirmation
4. Run tests
5. Report results

### Fix a Bug
```
"Fix the issue where [describe bug]"
```

### Add Tests
```
"Add tests for the [feature] in tests/test_[module].py"
```

### Update Documentation
```
"Update CHANGELOG.md with today's changes"
```

---

## Troubleshooting

### Cursor Not Finding Python Interpreter
1. `Cmd+Shift+P`
2. `Python: Select Interpreter`
3. Choose `.venv312/bin/python`

### Tests Not Running
1. Check Testing panel (beaker icon)
2. Click "Configure Python Tests"
3. Select "pytest"
4. Select "tests" directory

### Ruff Not Formatting
1. Check `.vscode/settings.json` exists
2. Verify Ruff extension installed
3. Restart Cursor

### Git Integration Not Working
1. Ensure GitLens extension installed
2. Open Source Control panel (`Cmd+Shift+G`)
3. Initialize repository if needed

---

## Advanced Tips

### Multi-File Editing
1. `Cmd+Shift+I` (Composer)
2. Describe changes across multiple files
3. Review proposed changes
4. Apply all at once

### Code Navigation
- `F12` — Go to definition
- `Shift+F12` — Find all references
- `F2` — Rename symbol (refactor)

### Terminal Integration
- `` Ctrl+` `` — Toggle terminal
- Multiple terminals supported
- Auto-activates `.venv312`

### Git Integration
- `Cmd+Shift+G` — Source Control panel
- Stage changes with `+`
- Commit with message
- Push with sync icon

---

## Quick Reference Card

| Action | Shortcut |
|--------|----------|
| Quick edit | `Cmd+K` |
| Chat | `Cmd+L` |
| Composer | `Cmd+Shift+I` |
| Command palette | `Cmd+Shift+P` |
| Quick open file | `Cmd+P` |
| Search files | `Cmd+Shift+F` |
| Toggle terminal | `` Ctrl+` `` |
| Source control | `Cmd+Shift+G` |
| Testing panel | Click beaker icon |
| Debug | `F5` or `Cmd+Shift+D` |
| Go to definition | `F12` |
| Find references | `Shift+F12` |
| Rename symbol | `F2` |

---

## Remember

1. **Always read control layer first** — `AI_CONTROL/02_CURRENT_TASK.md`
2. **Test after every change** — `pytest -v`
3. **Stay within task scope** — Don't broaden without approval
4. **Control layer is truth** — Code follows control, not vice versa
5. **Archive is reference only** — Never use `_archive/` for active work

---

## Support

If Cursor behavior seems wrong:
1. Check `.cursorrules` is up to date
2. Read `AI_CONTROL/00_PROJECT_CANONICAL.md`
3. Verify task in `AI_CONTROL/02_CURRENT_TASK.md`
4. Ask Cursor: "What are the current working rules?"

---

**Setup complete. You're ready to use Cursor for Unitas GridFlow development.**
