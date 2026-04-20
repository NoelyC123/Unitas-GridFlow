# AI Role Rules

## Overview

This project uses multiple AI tools. Each has a defined role.
All AIs must read the AI_CONTROL files before doing anything.
No AI should be asked to rediscover or redefine the whole project from scratch.

---

## Claude app role (claude.ai — in the Unitas-GridFlow Project)

**Primary role: live development sessions**

Claude app has Filesystem MCP access — it can read and write files directly
on the Mac in real time without any file uploads needed.

Use Claude app for:
- active development sessions with direct file access
- reading, editing, and writing project files live
- implementing code changes directly to disk
- reviewing and improving any part of the codebase
- updating AI_CONTROL files after meaningful changes
- architecture review and structured decision-making
- validating whether a change fits the narrow MVP

Claude app should:
- read AI_CONTROL files fresh from disk at the start of every session
- write changes directly to files using Filesystem tools
- never ask the user to copy/paste code or upload files
- always run tests mentally / remind user to run pytest after changes

---

## Claude Code role

**Primary role: terminal-based repo work**

Use Claude Code for:
- reading the repo directly in terminal context
- tracing routes and imports across files
- running commands and interpreting output
- debugging implementation issues in terminal
- targeted file edits when working in terminal

Claude Code reads `CLAUDE.md` automatically at session start.

---

## Cursor Pro role

**Primary role: in-editor AI coding**

Use Cursor for:
- writing new functions and classes inside the editor
- multi-file refactoring with AI assistance
- inline suggestions while actively editing code
- generating boilerplate quickly

Cursor reads `.cursorrules` automatically when the project folder is open.

---

## GitHub Copilot role

**Primary role: passive inline autocomplete**

Use Copilot for:
- inline code suggestions while typing in VS Code
- completing repetitive patterns
- quick function signatures

Copilot is always on passively — no session setup needed.

---

## ChatGPT role

**Primary role: strategic decisions only**

Use ChatGPT for:
- strategic judgment at genuine decision points
- architecture review when a major direction change is being considered
- prioritisation between competing approaches
- synthesising multiple AI opinions into a decision

ChatGPT should NOT be used for:
- day-to-day implementation work
- questions that Claude app can answer with filesystem access
- broad free-form ideation during active build work

When using ChatGPT for a review, use the bundles in `CLAUDE_REVIEW_BUNDLES/`.

---

## Gemini role

**Primary role: structured challenger**

Use Gemini for:
- second opinion after current truth is locked
- testing whether the chosen path misses something important
- sector and market context

Use sparingly — only at genuine decision points.

---

## Grok role

**Primary role: practical trade-off enforcer**

Use Grok for:
- identifying wasted effort
- simplifying decisions
- calling out overbuilding
- "do this, not that" sharpening

Use sparingly — only at genuine decision points.

---

## Ollama (local) role

**Primary role: offline / private drafting**

Use Ollama for:
- private notes and offline work
- rough drafts before using cloud tools
- sensitive content that should not leave the machine
- first-pass analysis and brainstorming

Models: `qwen2.5:14b-instruct` (main), `llama3.2` (fast)

---

## Shared rules for all AIs

1. Read AI_CONTROL files first — every session, fresh from disk
2. Treat `app/` and project root as canonical live code
3. Treat `_quarantine/` as reference-only — do not restore blindly
4. Treat `PROJECT_SYNTHESIS/` as strategic context, not implementation truth
5. Never broaden scope beyond the narrow MVP
6. Never add features not tied to the current task
7. Always run `pytest -v` after code changes — 23 tests must pass
8. Always commit and push after confirmed passing tests
9. Update AI_CONTROL files when project state materially changes

---

## Tool priority for development work

```
1. Claude app (Filesystem MCP) — for live file reading/writing sessions
2. Claude Code — for terminal-based repo work
3. Cursor Pro — for in-editor coding
4. Copilot — passive autocomplete always on
5. ChatGPT / Gemini / Grok — only at genuine decision points
6. Ollama — offline / private only
```
