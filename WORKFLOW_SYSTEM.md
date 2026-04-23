# Unitas-GridFlow — Workflow System (All Tools)

## Purpose

This document defines how the Unitas-GridFlow project is operated across all tools.

It ensures:

- alignment between AI tools
- controlled development
- validation-led progress
- real-world usefulness

This is the **operating system for the project**, not the product itself.

---

# 1. Core Principle

This project is **validation-led, not feature-led**.

Its purpose is to:

> **Act as the trusted gate between survey and design — turning raw, inconsistent, incomplete survey data into something a designer can confidently assess and use.**

Every step must answer:

> **“Does this improve the reliability, clarity, and design-readiness of real survey data?”**

---

# 2. What This Project Actually Does

This is NOT:

- a CAD tool
- a design engine
- a GIS platform

This IS:

- a **pre-CAD QA gatekeeper**
- a **data trust engine**
- a **survey-to-design validation layer**

It answers:

> “Can I trust this data enough to design from it?”

---

# 3. Tool Roles (STRICT)

## 🧠 You (Human)

Role:

- provide real survey files
- define real-world problems
- make final decisions

You are the **domain authority**.

---

## 🧠 ChatGPT (Project Orchestrator)

Role:

- defines WHAT should be built
- defines WHAT should NOT be built
- translates validation into tasks
- reviews outputs from all tools
- prevents scope creep

Responsibilities:

- maintain project direction
- ensure alignment across tools
- break work into narrow steps

This is the **control layer above all tools**.

---

## ⚙️ Claude Code (Primary Builder)

Role:

- reads full repository
- writes and edits code
- runs tests
- commits and pushes

Responsibilities:

- implement tasks exactly as defined
- keep tests passing
- make minimal, targeted changes

This is the **execution engine**.

---

## 📊 Claude Desktop

Role:

- deep project understanding
- alignment checking
- validation analysis

Responsibilities:

- verify code matches intent
- identify hidden issues
- confirm real-world usefulness

This is the **verification layer**.

---

## 💻 VS Code / Cursor

Role:

- editing interface only
- file navigation

No decision-making responsibility.

---

## 🤖 Codex (Optional)

Role:

- second opinion on code
- alternative implementations
- support for complex logic

Use sparingly and only when needed.

---

# 4. Source of Truth Hierarchy

1. **Real survey files** (highest truth)
2. **AI_CONTROL/** (project truth)
3. **Codebase (GitHub)**
4. **Documentation**
5. **AI outputs**

If anything conflicts:

- real data wins
- control layer overrides assumptions

---

# 5. The Core Workflow Loop

## Step 1 — Real Input (You)

You provide:

- real survey file
- real-world issue

---

## Step 2 — Task Definition (ChatGPT)

ChatGPT defines:

- exact problem
- narrow solution
- constraints

---

## Step 3 — Implementation (Claude Code)

Claude Code:

- implements change
- runs tests
- commits and pushes

---

## Step 4 — Verification (Claude Desktop)

Claude Desktop:

- checks alignment
- validates correctness
- identifies gaps

---

## Step 5 — Decision (ChatGPT)

ChatGPT decides:

- next step
- refine / stop / continue
- validation direction

---

# 6. Development Rules

## Always:

- stay narrow in scope
- validate against real files
- keep tests passing
- prioritise usefulness over completeness

## Never:

- build features without validation evidence
- redesign architecture unnecessarily
- allow tools to drift out of sync
- assume correctness without real-file testing

---

# 7. File & Repo Strategy

## GitHub Repository (PRIMARY)

This is the **single source of truth** for:

- code
- tests
- control files

---

## Claude Desktop Project (SECONDARY)

Include only:

- control layer files
- core implementation files
- test files
- validation files

Do NOT:

- upload entire repo repeatedly
- keep outdated versions
- duplicate files unnecessarily

---

## ChatGPT (THIS SYSTEM)

Maintains:

- workflow
- priorities
- alignment
- orchestration

---

# 8. What Breaks This System

Avoid:

- multiple AIs making independent decisions
- working without real validation data
- trusting code without testing on real files
- duplicating files across environments
- expanding scope without evidence

---

# 9. Current Phase Context

You are currently in:

➡️ **Validation Phase (Phase 2C complete — ongoing refinement)**

Focus:

- run real files through system
- verify usefulness
- refine outputs based on real evidence

NOT focus:

- adding new features
- expanding platform
- scaling prematurely

---

# 10. Success Criteria

The system is working correctly when:

- all tools agree on current state
- changes are small and targeted
- real files produce meaningful outputs
- designers can trust the results

---

# Final Statement

This workflow ensures:

- clarity
- control
- speed
- correctness
- real-world value

This is not just development.

This is a **controlled system for building a real, valuable product**.
