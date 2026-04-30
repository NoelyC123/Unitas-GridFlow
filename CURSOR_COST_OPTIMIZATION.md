# Cursor Cost Optimization Guide — Unitas GridFlow

## The Optimal Balance (Now Configured)

The setup balances three needs:

1. **Performance** — Don't waste tokens on heavy/noisy folders
2. **Validation** — Keep real job data accessible when needed
3. **Development** — Full access to live code/tests/control layer
4. **Flexibility** — Allow discussion across all stages, implement narrowly

---

## What Cursor WILL Index (Low Cost, High Value)

### ✅ Always Indexed — Live Development Surface

These are always available to Cursor with minimal token cost:

```
AI_CONTROL/          # Control layer (project truth)
app/                 # Source code
tests/               # Test suite
sample_data/         # Example inputs
scripts/             # Utility scripts
README.md
CHANGELOG.md
CLAUDE.md
WORKFLOW_SYSTEM.md
PROJECT_DEEP_CONTEXT.md
```

**Why:** These are the files you actively work on. Small size, high value.

**Token Impact:** ~100-200K tokens total (very manageable)

---

## What Cursor CAN Search But Won't Auto-Index

### ⚠️ Searchable When Needed — Real Job Evidence

These are **excluded from file watching** but **included in search**:

```
uploads/             # Real job data
validation_data/     # Validation evidence
```

**Why:** You need to search these during validation work, but they shouldn't spam Cursor's context.

**How to Use:**
- When you need a job file: `Cmd+P` → type filename
- When you need to search: `Cmd+Shift+F` → search term
- Cursor won't auto-load them, but accesses them when you ask

**Token Impact:** Only when explicitly needed (you control the cost)

---

## What Cursor WILL NEVER Index (Zero Cost)

### ❌ Always Ignored — Heavy/Noisy Stuff

```
.venv312/            # Virtual environment
.pytest_cache/       # Test cache
.ruff_cache/         # Linter cache
__pycache__/         # Python bytecode
_archive/            # Historical material
htmlcov/             # Coverage reports
build/               # Build artifacts
*.db, *.sqlite       # Database files
*.log                # Log files
```

**Token Impact:** Zero (completely ignored)

---

## Cost-Saving Best Practices

### 1. Use Minimal Context Windows

**Good (Low Cost):**
```
Cmd+K → "Fix this function"
```
Only indexes the current file.

**Better (Lower Cost):**
```
Cmd+K → Select specific lines → "Fix this logic"
```
Only indexes selected code.

**Higher Cost (But Sometimes Necessary):**
```
Cmd+L → "How does the intake pipeline work across these 3 files?"
```
Indexes multiple files — use when actually needed.

### 2. Ask Specific Questions

**Good (Low Cost):**
```
"What does _normalize_dataframe() do?"
```
Cursor reads one function.

**Higher Cost (But Valid):**
```
"Explain the entire intake pipeline and how it connects to QA"
```
Cursor reads multiple files — acceptable when you need comprehensive understanding.

### 3. Use Composer Only When Needed

**When to Use Composer (Cmd+Shift+I):**
- Multi-file changes
- Complex refactors
- Feature implementation across files

**When NOT to Use Composer:**
- Single-line fixes (use `Cmd+K`)
- Simple edits (type manually)
- Typo corrections (just fix it)

### 4. Let Cursor Auto-Read Control Layer

Cursor automatically reads:
- `AI_CONTROL/00_PROJECT_CANONICAL.md`
- `AI_CONTROL/02_CURRENT_TASK.md`

**Don't ask Cursor to read these manually.**

**Efficient (Uses Cached Context):**
```
"What should I work on right now?"
```

**Less Efficient (Re-reads):**
```
"Read AI_CONTROL/02_CURRENT_TASK.md and tell me what to do"
```

### 5. Avoid Repeated File Reads

**Less Efficient:**
```
Cmd+L → "What does app/qa_engine.py do?"
Cmd+L → "Explain app/qa_engine.py again"
Cmd+L → "How does app/qa_engine.py work?"
```

**Efficient:**
```
Cmd+L → "Explain app/qa_engine.py in detail, including its role in the pipeline"
```
Ask once comprehensively.

---

## Token Budget Estimates

### Small Task (50-500 tokens)
- Fix a typo
- Rename a variable
- Add a comment
- Simple `Cmd+K` edit

### Medium Task (500-5K tokens)
- Fix a bug
- Add a test
- Refactor a function
- `Cmd+L` question with 1-2 files

### Large Task (5K-20K tokens)
- Implement a feature
- Multi-file refactor
- Complex debugging
- `Cmd+Shift+I` Composer mode

### Very Large Task (20K+ tokens)
- Cross-stage architecture discussion
- Major feature planning
- Full context Composer sessions

---

## Work to Discuss First (Not Prohibit)

Before implementing certain features, pause and discuss:
- Does this solve a current Stage 3 operational need?
- Do we have evidence this approach works?
- Is this the narrowest solution to the current problem?

### Examples:

**Stage Boundary Questions (Welcome):**
```
Cmd+L → "If we implement X in Stage 3, will it complicate Stage 4 tablet capture?"
```
**Token cost:** Low — discussion, no implementation

**Stage Boundary Implementation (Discuss First):**
```
Cmd+Shift+I → "Build tablet photo-upload UI"
```
**Pause and discuss:** Is there a current Stage 3 need for this?

**Preparation Work (Encouraged):**
```
Cmd+K → "Add photo_reference column to design chain export as placeholder"
```
**Token cost:** Low — prepares for future without building it

---

## Cost-Optimized Workflow

### Daily Development (Minimal Cost)

1. **Start:**
   ```bash
   source .venv312/bin/activate
   ```

2. **Ask what to do (uses cached context):**
   ```
   Cmd+L → "What's the current priority?"
   ```

3. **Make targeted changes:**
   ```
   Cmd+K → "Fix this validation logic"
   ```

4. **Run tests manually:**
   ```bash
   pytest -v
   ```

5. **Commit manually:**
   ```bash
   git add . && git commit -m "message" && git push
   ```

**Token Cost:** ~1-5K per day (very low)

---

### Real Job Validation (Controlled Cost)

1. Upload job file to `uploads/`

2. Run through tool manually

3. Ask Cursor specific questions:
   ```
   Cmd+L → "Why did QA check X fail for this Gordon file?"
   ```

4. Search job data manually when possible:
   ```
   Cmd+Shift+F → Search for error pattern
   ```

**Token Cost:** ~5-15K per validation session (you control when)

---

### Feature Implementation (Higher Cost, Intentional)

1. Read control layer yourself first

2. Ask Cursor to implement:
   ```
   Cmd+Shift+I → "Add QA check for [specific validation]"
   ```

3. Review and refine:
   ```
   Cmd+L → "Explain why you structured it this way"
   ```

4. Run tests manually

**Token Cost:** ~10-30K per feature (adds real value)

---

### Cross-Stage Planning (Welcome, Moderate Cost)

1. Discuss future implications:
   ```
   Cmd+L → "If we structure the Stage 3 export this way, will it work for Stage 4 tablet capture?"
   ```

2. Think holistically:
   ```
   Cmd+L → "How should current design chain structure prepare for eventual PoleCAD integration?"
   ```

3. Ask boundary questions:
   ```
   Cmd+L → "Would adding user accounts now complicate Stage 3, or should we wait for Stage 6?"
   ```

**Token Cost:** ~2-10K per discussion (valuable for avoiding rework)

---

## What to Avoid (Token Waste)

### ❌ Don't Ask Cursor What You Can Read Yourself

**Less Efficient:**
```
"Read CHANGELOG.md and tell me what changed"
```

**Efficient:**
```
Open CHANGELOG.md yourself
```

### ❌ Don't Use Composer for Trivial Edits

**Wasteful:**
```
Cmd+Shift+I → "Fix this typo"
```

**Efficient:**
```
Just type the fix
```

### ❌ Don't Ask Repeated Questions

**Wasteful:**
```
"What does this do?"
"Explain this again"
"I still don't understand"
```

**Efficient:**
```
"Explain this in detail with examples and show how it fits the larger pipeline"
```

### ❌ Don't Use Cursor as Google

**Wasteful:**
```
"What is Flask?"
"How does pytest work?"
```

**Efficient:**
```
Check official docs
```

---

## Stage Boundary Efficiency

### Efficient Cross-Stage Thinking

**Good (Low Cost):**
```
"Should this Stage 3 export include a photo_reference placeholder for future Stage 4 work?"
```
Discussion, planning, minimal token cost.

**Good (Moderate Cost):**
```
"Explain how current sequencing logic would integrate with future tablet capture"
```
Architecture discussion, helps avoid rework.

**Less Efficient (High Cost Without Need):**
```
"Build complete Stage 4 tablet UI with photo upload"
```
If there's no current Stage 3 operational need, this wastes tokens on speculative work.

### Smart Preparation vs. Speculation

**Smart Preparation (Encouraged):**
- Adding placeholder columns for future fields
- Structuring data models for extensibility
- Discussing integration points
- Asking "will this complicate Stage 4?"

**Speculation (Discuss First):**
- Building complete future UIs
- Implementing features "just in case"
- Creating systems without operational need

---

## Summary: Optimal Setup Now in Place

### The Balance

| Folder | Watched? | Searchable? | Indexed? | Why? |
|--------|----------|-------------|----------|------|
| `app/` | ✅ Yes | ✅ Yes | ✅ Yes | Live development |
| `tests/` | ✅ Yes | ✅ Yes | ✅ Yes | Live development |
| `AI_CONTROL/` | ✅ Yes | ✅ Yes | ✅ Yes | Project truth |
| `uploads/` | ❌ No | ✅ Yes | ❌ No | Real job data (on demand) |
| `validation_data/` | ❌ No | ✅ Yes | ❌ No | Validation evidence (on demand) |
| `.venv312/` | ❌ No | ❌ No | ❌ No | Virtual env (huge, useless) |
| `_archive/` | ❌ No | ❌ No | ❌ No | Historical (reference only) |

### Token Budget Expectations

**Low-cost daily work:** 1-5K tokens/day
**Medium validation work:** 5-15K tokens/session
**High-value feature work:** 10-30K tokens/feature
**Cross-stage planning:** 2-10K tokens/discussion

**Annual estimate:** ~1-2M tokens for active development (very reasonable)

---

## Final Recommendations

### Do This:

✅ Use `Cmd+K` for small edits
✅ Use `Cmd+L` for targeted questions
✅ Use `Cmd+Shift+I` for multi-file changes
✅ Discuss cross-stage implications
✅ Ask boundary questions
✅ Think holistically, implement narrowly
✅ Search `uploads/` manually when validating
✅ Run tests manually
✅ Commit manually

### Avoid This:

❌ Don't ask Cursor to read files you can read
❌ Don't use Composer for typos
❌ Don't ask repeated questions
❌ Don't use Cursor as Google
❌ Don't build speculative features without discussion

---

**You're configured for maximum value at minimum cost with full cross-stage thinking encouraged.**
