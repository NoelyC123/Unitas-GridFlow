# Current State

## Project status

The project has now completed two distinct phases:

1. baseline/professionalisation phase — complete
2. first QA-rule improvement step — complete

It is now in:

**working local MVP + rulepack architecture in place + QA engine extended + next iteration ready**

---

## Canonical active project identity

### Active project name
**Unitas GridFlow**

### Canonical active repo
`NoelyC123/Unitas-GridFlow`

### Canonical active local folder
`/Users/noelcollins/Unitas-GridFlow`

### Repo rule
This is the **only active canonical repo** for the project.
Older EW / SpanCore / design-tool repos are archived and are not active development repos.

---

## Current MVP status

The narrow MVP is working locally.

### Confirmed working flow
**upload CSV -> save file -> run QA -> save outputs -> view map -> download PDF -> browse jobs**

### Confirmed working parts
- `/upload` page works
- `/api/presign` works
- CSV upload/save works
- `/api/import/<job_id>` works — now selects rulepack by DNO
- QA processing runs with extended check types
- `issues.csv` is written
- `map_data.json` is written
- `/map/view/<job_id>` works
- `/pdf/qa/<job_id>` works
- `/jobs/` works
- `/health/full` works

---

## Current QA architecture state

### dno_rules.py
Upgraded from a single flat list to a proper rulepack architecture.

**Structure:**
- `BASE_RULES` — generic UK-wide rules, used as fallback
- `DNO_RULES` — backwards-compatible alias for `BASE_RULES`
- `SPEN_11KV_RULES` — extends BASE_RULES with SPEN-specific checks
- `RULEPACKS` dict — `{"DEFAULT": BASE_RULES, "SPEN_11kV": SPEN_11KV_RULES}`

**SPEN_11kV rulepack includes:**
- Corrected height range: 7m-20m (ENA TS 43-8 / SPEN OHL policy)
- Pole ID regex validation (stable identifier format)
- Paired coordinate checks (lat/lon must both be present, easting/northing must both be present)
- SPEN network area coordinate bounds (lat 54.5-60.9, lon -6.5 to -0.7)
- Material/structure_type cross-field consistency check

### qa_engine.py
Extended with three new check types:
- `regex` — validates field against a pattern
- `paired_required` — both fields in a pair must be present or both absent
- `dependent_allowed_values` — allowed values for one field depend on another field's value

### api_intake.py
Now selects rules by the requested DNO:
- `RULEPACKS[requested_dno]` → fallback to `RULEPACKS["DEFAULT"]` → fallback to `DNO_RULES`

---

## Current testing status

### Test count
**23 passing tests**

### Coverage includes
- schema normalization
- issue post-processing
- CSV payload sanitization
- feature collection generation
- JSON-safe output
- health endpoint
- jobs API
- job status endpoint
- PDF endpoint
- import/finalize success and error paths
- regex check
- paired_required check
- dependent_allowed_values check

### Quality tooling
- pre-commit: active
- Ruff: active
- pytest: active (23 passing)
- GitHub Actions CI: active

---

## Tool bootstrapping state

All development tools are now bootstrapped with project context:

- Claude app Project: Instructions + 8 AI_CONTROL knowledge files
- Claude Code: `CLAUDE.md` in project root
- Cursor Pro: `.cursorrules` in project root
- GitHub Copilot: installed in VS Code
- ChatGPT/Gemini/Grok: use `CLAUDE_REVIEW_BUNDLES/` zips

---

## Current remaining weaknesses

### 1. Only one rulepack exists (SPEN_11kV)
Other DNOs (SSEN, ENWL, NIE, UKPN) have no rulepack yet.
The architecture supports adding them — the rules don't exist yet.

### 2. No coordinate consistency cross-check yet
lat/lon and easting/northing are each validated independently.
A check confirming they point to the same location (within tolerance) does not yet exist.

### 3. Input handling is still narrow
One representative schema is supported.
Broader real-world survey export variation is not yet handled.

### 4. Browser test coverage does not yet exist
Playwright is not yet active.
Current automated testing is backend-focused.

### 5. Architecture still has MVP debt
Some route/code paths were built quickly.
Cleanup/hardening can come after the rule quality improves further.

---

## Current phase

**working MVP + rulepack architecture complete + SPEN_11kV rulepack live + 23 tests passing**

## Current next priority

Add coordinate consistency cross-check (lat/lon vs easting/northing).
Then expand rulepacks to cover a second DNO.
