# AI Handover Pack

Use this folder to update Claude Desktop, ChatGPT and other AI tools with the current Unitas GridFlow project vision and development state.

## Latest State

- Stage 1: complete
- Stage 2A: implemented
- Stage 2B: implemented and validated as a strong D2D replacement baseline
- Current tests: 211 passing
- Stage 2A commit: `5f99bf0`
- Stage 2B commit: `54417ba`
- Stage 2B validation bugfix commit: `e51d0ee`
- Current focus: Stage 2C polish pass vs Stage 2 completion review

## Best files to give an AI

If the AI can accept multiple files, give it this whole folder.

If the AI can only accept one file, give it:

`05_FULL_PROJECT_CONTEXT_FOR_AI.md`

## Prompts

- For Claude Desktop: use `01_PROMPT_FOR_CLAUDE_DESKTOP.md`
- For ChatGPT: use `02_PROMPT_FOR_CHATGPT.md`
- To check whether an AI is aligned: use `03_AI_CONFIRMATION_CHECKLIST.md`

## Source Files Included

The source files are copied into `source_files/` for reference.

No `.env`, private keys, virtual environments, caches, uploads, or archive folders are included.
