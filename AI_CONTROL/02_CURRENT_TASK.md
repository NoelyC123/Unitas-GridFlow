# Current Task

## Immediate task

The immediate task is:

**Begin validation-led Phase 2 by testing the current tool against one or more real survey files from real jobs.**

---

## Why this is the current task

Phase 1 (meaningful QA rule improvements) is complete.

Phase 2A (column/header normalisation improvements) is also complete.

The strongest remaining uncertainty is no longer whether the tool can be built.

It is whether the current tool provides meaningful value on real-world survey data.

That means the next task is not broad feature expansion.

The next task is to validate the current MVP against real usage conditions.

---

## What this task means

This task means:

- obtain one or more real survey files (ideally anonymised if necessary)
- run them through the current intake and QA pipeline
- log what works
- log what breaks
- identify what the tool catches that users care about
- identify what the tool misses that users care about
- use that evidence to refine the next development phase

---

## What success looks like

This task is successful when we can answer questions like:

- Did the tool work on a real file without manual reconstruction?
- Which rules produced meaningful value?
- Which rules produced noise or false positives?
- What real issues were missed?
- What would an actual user most want fixed next?

---

## What not to do during this task

Do NOT:

- broaden the product into a larger platform
- add major new features without validation evidence
- add more superficial rulepacks just for coverage
- focus on commercial packaging before proof-of-value exists

---

## Approved focus areas

The likely files involved next are:

- `app/routes/api_intake.py`
- `app/qa_engine.py`
- `app/dno_rules.py`
- `tests/test_api_intake.py`
- `tests/test_qa_engine.py`

along with any safe, anonymised sample data used for validation.

---

## Strategic note

The external AI review completed on 2026-04-22 concluded:

- continue the project
- keep the scope narrow
- treat the project primarily as an internal tool / consultancy asset for now
- shift the next phase toward validation-led development

---

## What comes next (do not start yet)

Possible next work after validation findings are known may include:

- refining intake handling based on real file structures
- refining QA rules based on real false positives / false negatives
- improving output usefulness based on real user feedback
- adding more genuinely differentiated rule depth only where evidence supports it

This should be decided from validation findings, not assumed in advance.

---

## When to update this file

Update when:

- one or more real survey files have been tested
- the most important validation findings are known
- the next development phase becomes clearer from real evidence

Otherwise leave unchanged.
