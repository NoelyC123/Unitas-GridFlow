# Current Task

## Immediate task

**Improve QA rules so the tool becomes genuinely useful**

Primary file:
- `app/dno_rules.py`

---

## Why this is the current task

The project has completed:

- working MVP
- repository cleanup
- control layer redesign
- testing and CI setup

The remaining limitation is now:

**lack of meaningful validation**

The tool runs correctly, but it does not yet provide real value.

That is because:
- QA rules are placeholder-level
- real-world problems are not being caught

---

## Task definition

This task is NOT:

- adding large numbers of rules
- redesigning the QA engine
- expanding scope

This task IS:

**Adding a small number of high-value, realistic validation rules**

---

## What “good QA rules” means

Rules should:

- reflect real survey/design issues
- catch common mistakes early
- be simple, clear, and testable
- produce meaningful error messages

---

## Examples of valid rule types

- physically impossible values (e.g. unrealistic heights)
- missing required fields
- invalid coordinate ranges
- coordinate inconsistencies (lat/lon vs easting/northing)
- invalid asset/type combinations
- structurally inconsistent data

---

## Expected outcome

After this task:

**The tool should clearly catch real problems in survey data**

A user should be able to say:

> “This actually flags issues I care about”

---

## Execution approach

1. Read the current implementation:
   - `app/dno_rules.py`
   - `app/qa_engine.py` (if needed)

2. Add 1–2 meaningful rules at a time

3. For each rule:
   - keep logic simple
   - ensure clear error messages
   - ensure deterministic behaviour

4. Test locally:
   ```bash
   python run.py
   ```

5. Validate via UI:
   - upload CSV
   - confirm issues are correctly flagged

6. Run full checks:
   ```bash
   pytest -v
   pre-commit run --all-files
   ```

7. Commit:
   ```bash
   git add .
   git commit -m "Add meaningful QA rule(s)"
   git push
   ```

---

## Constraints (important)

Do NOT:

- broaden scope beyond QA rules
- redesign architecture
- introduce new features
- attempt to cover every edge case
- modify schema handling (that is Phase 2)
- add UI or browser tests (that is Phase 3)

---

## Success condition

This task is complete when:

- 5–10 meaningful validation rules exist
- rules reflect real-world survey problems
- outputs are clearly useful

NOT when:
- rule count is high
- complexity increases unnecessarily

---

## What comes next (do not start yet)

### Phase 2
Broader input handling
(`app/routes/api_intake.py`)

### Phase 3
Browser automation testing
(Playwright)

---

## When to update this file

Update only when:

- Phase 1 is complete
- priority changes
- a blocker changes the plan

Otherwise, leave this file unchanged.
