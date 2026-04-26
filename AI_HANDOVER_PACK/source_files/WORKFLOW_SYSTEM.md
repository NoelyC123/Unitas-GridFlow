# Unitas-GridFlow — Workflow System

## Purpose

This document defines how the Unitas-GridFlow project is operated across all tools.

It ensures alignment between AI tools, controlled development, and real-world usefulness.

---

## 1. Core Principle

This project is **validation-led, not feature-led**.

Every step must answer:

> **"Does this improve the reliability, clarity, and design-readiness of real survey data?"**

---

## 2. The Product Vision (6 stages)

| Stage | Name | Status |
|-------|------|--------|
| 1 | Post-survey QA gate | ✅ Complete |
| 2 | D2D elimination | ← CURRENT |
| 3 | Live intake platform | Planned |
| 4 | Structured field capture | Planned |
| 5 | Designer workspace | Planned |
| 6 | DNO submission layer | Planned |

Work on the **current stage only**. The orchestrator defines when a stage is complete and when to advance.

---

## 3. Tool Roles (STRICT)

### You (Human) — Domain Authority

- provide real survey files
- define real-world problems
- make final decisions

---

### Claude Desktop — Project Orchestrator

- defines WHAT gets built, WHY, and in WHAT ORDER
- reviews validation results
- manages all tools
- prevents scope creep and stage drift
- holds full project context between sessions

This is the **control layer above all tools**.

---

### Claude Code (VS Code) — Primary Builder

- reads the full repository
- writes and edits code
- runs tests
- commits and pushes

Responsibilities:
- implement tasks exactly as defined by the orchestrator
- keep tests passing
- make minimal, targeted changes

This is the **execution engine**.

---

### ChatGPT — Second Opinion Only

- available for commercial thinking and review
- not the orchestrator
- not the primary decision-maker

---

### Codex — Optional

- second opinion on code
- use sparingly for bounded tasks

---

## 4. Source of Truth Hierarchy

1. **Real survey files** (highest truth)
2. **AI_CONTROL/** files
3. **Codebase (GitHub)**
4. **Documentation**
5. **AI outputs** (lowest)

If anything conflicts: real data wins, control layer overrides assumptions.

---

## 5. The Core Workflow Loop

**Step 1 — Real Input (Human)**
Provide real survey file or real-world issue.

**Step 2 — Task Definition (Claude Desktop)**
Claude Desktop defines the exact problem, narrow solution, and constraints. Updates `AI_CONTROL/02_CURRENT_TASK.md`.

**Step 3 — Implementation (Claude Code)**
Claude Code implements, runs tests, commits, pushes.

**Step 4 — Verification (Claude Desktop)**
Claude Desktop reviews the result, checks alignment with intent, identifies gaps.

**Step 5 — Decision (Claude Desktop)**
Claude Desktop decides: next step, refine, stop, or advance to next stage.

---

## 6. Development Rules

**Always:**
- stay within the current stage
- validate against real files before advancing
- keep tests passing
- make small, targeted changes

**Never:**
- build features without validation evidence
- jump ahead to later stages
- redesign architecture unnecessarily
- allow tools to drift out of sync

---

## 7. Repository Strategy

**GitHub (PRIMARY):** Single source of truth for code, tests, and control files.

**Claude Desktop:** Reads control layer files and implementation files. Does not hold a separate copy of the codebase.

**Local:** `/Users/noelcollins/Unitas-GridFlow/`

---

## 8. Engineering Workflow

After any code change:

1. `pytest -v` — all tests must pass
2. `pre-commit run --all-files`
3. `git add . && git commit -m "clear message" && git push`

---

## 9. Current Stage Context

**Stage 2 — D2D Elimination**

Goal: tool takes raw controller dump → produces structured, sequenced, PoleCAD-ready output. The manual D2D spreadsheet step is eliminated.

What this means:
- automatic pole sequencing (spatial route order, not file order)
- correct pole numbering
- section splitting at sensible points
- coordinate output in PoleCAD-compatible format
- EXpole records matched to their route position

See `AI_CONTROL/02_CURRENT_TASK.md` for the immediate next step.

---

## 10. Success Criteria

The system is working correctly when:
- all tools agree on current state
- changes are small and targeted
- real files produce meaningful outputs
- a designer reviewing output saves measurable time

---

## Final Statement

This is a controlled system for building a real, valuable product.

The goal is not feature completeness. The goal is that the tool produces genuinely useful output for real survey-to-design workflows, at each stage in sequence.
