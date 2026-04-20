# AI Role Rules

## ChatGPT role
Use ChatGPT for:
- strategic judgment
- architecture review
- prioritisation
- decision quality
- file-by-file implementation guidance
- final synthesis and direction

## Claude app role
Use Claude app for:
- second-opinion architecture review
- challenge and critique of plans
- repo-level reasoning
- validating whether a change still fits the narrow MVP

## Claude Code role
Use Claude Code for:
- reading the repo directly
- tracing routes/imports
- editing files
- debugging implementation
- producing full file replacements

## Shared rule for all AIs
All AIs must:
- read AI_CONTROL files first
- treat live root and app/ as canonical code
- treat _reference as important non-runtime context
- treat _archive as non-live archive
- treat _quarantine as reference-only
- avoid broadening scope
- focus on narrow MVP recovery first

## Session rule
No AI should be asked to rediscover or redefine the whole project from scratch.
