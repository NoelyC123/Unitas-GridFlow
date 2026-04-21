# Project Reference

**Purpose:** Preserve historical context and wider project documentation without bloating day-to-day control files.

**This file is reference only.** It is not part of the active operational control layer.

---

## Project evolution

The project has evolved through multiple iterations and naming conventions:

### SpanCore (original phase)
- Initial DNO compliance/QA tool concept
- Early design and problem definition
- Decision memos and initial architecture work
- Archived but referenced in historical synthesis

### EW Design Tool (middle phase)
- Secondary naming convention during development
- Broader design-tool exploration
- Later deprecated in favor of narrow MVP approach
- Archived, not for active development

### Unitas GridFlow (current phase)
- Final, canonical name for the project
- Narrow pre-CAD QA and compliance tool
- Current active repository and development branch
- All future work happens here

---

## Repository locations

### Active development
- **GitHub:** `https://github.com/NoelyC123/Unitas-GridFlow`
- **Local:** `/Users/noelcollins/Unitas-GridFlow`
- **Branch:** `master`

### Archive locations
Older repos (SpanCore, EW Design Tool) are archived and not used for active development.

They exist for:
- Historical reference
- Understanding decision evolution
- Finding old analysis or synthesis documents

Do not try to restore or develop from archived repos.

---

## Three-layer project structure

The project is managed across three aligned layers:

### Layer 1: AI Control (`AI_CONTROL/`)
**Current day-to-day operational control files:**
- `00_PROJECT_CANONICAL.md` — project identity and MVP status
- `01_CURRENT_STATE.md` — current project state
- `02_CURRENT_TASK.md` — immediate next work
- `03_WORKING_RULES.md` — how to work on this project
- `04_SESSION_HANDOFF.md` — what changed in the last session
- `05_PROJECT_REFERENCE.md` — this file (historical/reference context)

**Updated:** When project state materially changes

**Read:** Only the files you need for your current task

### Layer 2: Strategy/Synthesis (`PROJECT_SYNTHESIS/`)
Contains deeper analysis and decision documentation:

- `00_RAW_AI_RESPONSES/` — raw AI analyses and initial thinking
- `01_COMPARISON/` — comparison and evaluation work
- `02_FINAL_SYNTHESIS/` — consolidated analysis (e.g., `SPANCORE_MASTER_SYNTHESIS.md`)
- `03_DECISION_MEMO/` — strategic decisions and rationale (e.g., `FINAL_DECISION_MEMO.md`)
- `04_EXECUTION_ALIGNMENT/` — execution plans and alignment (e.g., `EXECUTION_ALIGNMENT_PLAN.md`)
- `05_SUPPORT_NOTES/` — prompts, reviews, and follow-up notes

**Purpose:** Preserves why decisions were made, not just what is true now

**Read:** When you need to understand the reasoning behind a current decision

### Layer 3: Live code (`app/` and root files)
The running implementation and tests:

- `app/` — Flask application code
- `run.py` — entry point
- `requirements.txt` and `pyproject.toml` — dependencies
- `tests/` — pytest suite
- `sample_data/` — example CSVs
- `uploads/` — working directory for jobs

**Purpose:** The actual working implementation

**Updated:** Every development session

---

## Multi-AI workflow background

This project has been coordinated across multiple AI systems to avoid drift and duplication:

### ChatGPT
**Role:** Strategic judgment, prioritisation, architecture review, decision-making

**When used:** For high-level direction and strategic questions

**Outputs:** Saved in `PROJECT_SYNTHESIS/05_SUPPORT_NOTES/` with CHATGPT prefix

### Claude (Claude.ai / Claude Code)
**Role:** Structured review, repo-level reasoning, implementation assistance

**When used:** For validation, code review, and targeted implementation help

**Outputs:** Saved in `PROJECT_SYNTHESIS/05_SUPPORT_NOTES/` with CLAUDE prefix

### Gemini and Grok
**Role:** Structured challenging (Gemini) and practical trade-off enforcement (Grok)

**When used:** For second opinions and simplification pressure

**Outputs:** If used, saved in `PROJECT_SYNTHESIS/05_SUPPORT_NOTES/`

**Rule:** All prompts and responses used for decision-making are saved so that later AIs can see the reasoning.

---

## Key decision documents

### Strategic decisions
**Location:** `PROJECT_SYNTHESIS/03_DECISION_MEMO/FINAL_DECISION_MEMO.md`

**Contains:** Why the tool is narrow pre-CAD QA, not a broad platform. Why MVP comes first.

### Execution alignment
**Location:** `PROJECT_SYNTHESIS/04_EXECUTION_ALIGNMENT/EXECUTION_ALIGNMENT_PLAN.md`

**Contains:** How to execute the MVP without scope creep, phased approach, next priorities.

### Master synthesis
**Location:** `PROJECT_SYNTHESIS/02_FINAL_SYNTHESIS/SPANCORE_MASTER_SYNTHESIS.md`

**Contains:** Comprehensive analysis from earlier phases, consolidated reasoning.

---

## Archive locations

### _archive/
Old versions, exports, and moved artifacts.

Used for: historical reference, finding old work.

**Do not restore from archive without understanding why something was moved.**

### _quarantine/
Legacy or reference-only code that is not part of live development.

Used for: understanding old approaches, historical context.

**Do not restore or execute quarantined code.**

---

## Why this structure exists

The three-layer system (control, strategy, live code) exists to solve a specific problem:

**Problem:** Multiple AIs, multiple tools, multiple sessions → constant re-discovery and drift

**Solution:** One canonical control layer that all AIs and sessions read first, combined with preserved reasoning (strategy layer) and actual code (live code).

**Result:**
- No AI re-discovers the project from scratch
- Decisions are preserved with reasoning, not just outcomes
- Control layer stays lean because history doesn't bloat it
- Strategy layer doesn't bloat code because it's separate
- Code stays focused because decisions are already made

---

## When to read each layer

### Read the control layer (AI_CONTROL/) when:
- Starting work on the project
- Trying to understand current status
- Wondering what to work on next
- Unsure how to commit or test your changes

### Read the strategy layer (PROJECT_SYNTHESIS/) when:
- You want to understand *why* a decision was made
- A design choice seems wrong but you don't understand the reasoning
- You're about to propose a scope change and want to see why earlier thinking went a different direction
- You're bringing in a new AI and want them to understand the decision history

### Read the live code layer (app/) when:
- You're implementing something
- You're debugging
- You're understanding how the system actually works

---

## Current project truths (as of latest session)

### What's working
- Local MVP (upload → QA → map → PDF)
- Tests passing (14 tests)
- CI/CD active (GitHub Actions)
- Canonical repo established
- Control layer lean and practical

### What's weak
- QA rules are placeholder/basic (highest priority)
- Input handling is narrow (one schema)
- No browser automation tests

### What's next
**Phase 1:** Better QA rules (immediate)
**Phase 2:** Broader input handling
**Phase 3:** Browser automation

---

## How to find things

**"Where do I find the decision to make the tool narrow pre-CAD instead of broad?"**
→ `PROJECT_SYNTHESIS/03_DECISION_MEMO/FINAL_DECISION_MEMO.md`

**"Why are we improving QA rules first?"**
→ `PROJECT_SYNTHESIS/04_EXECUTION_ALIGNMENT/EXECUTION_ALIGNMENT_PLAN.md`

**"What was the reasoning behind X choice?"**
→ Check `PROJECT_SYNTHESIS/05_SUPPORT_NOTES/` for archived prompts and AI reviews

**"What's the status right now?"**
→ `AI_CONTROL/02_CURRENT_STATE.md` or `01_CURRENT_STATE.md`

**"What should I work on?"**
→ `AI_CONTROL/02_CURRENT_TASK.md`

---

## Important reminders

- **Do not broaden scope.** The narrow MVP approach is deliberate.
- **Do not try to restore old repos.** They are archived for a reason.
- **Do read the control files before working.** They are lean for a reason.
- **Do update control files when state changes.** They are the single source of truth.
- **Do preserve strategy documents.** They explain the reasoning.

---

## Not in the control layer on purpose

These topics are not in the daily control files, but they exist elsewhere:

- **Detailed AI workflow rules** → See this file
- **Historical evolution** → See this file
- **Archive locations** → See this file
- **Decision reasoning** → `PROJECT_SYNTHESIS/`
- **Old code or approaches** → `_archive/` and `_quarantine/`
- **Experimental notes** → `PROJECT_SYNTHESIS/00_RAW_AI_RESPONSES/` or `05_SUPPORT_NOTES/`

This separation keeps control files lean while preserving important context.
