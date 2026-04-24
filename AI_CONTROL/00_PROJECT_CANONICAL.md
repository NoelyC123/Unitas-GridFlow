# 00_PROJECT_CANONICAL.md

# Unitas-GridFlow — Canonical Project Definition

## 1. Project name

**Unitas-GridFlow**

---

## 2. Core identity

Unitas-GridFlow is a **survey-to-design workflow intelligence tool** for UK electricity network projects.

It is a **pre-CAD QA gatekeeper** that sits between:

- field survey output
- digital survey/controller files (Trimble, GIS export, CSV)
- office-based design and planning work

Its job is not to design the network.

Its job is to interpret, validate, and explain the digital survey handoff — determining whether it is:

- trustworthy
- understandable
- complete enough
- usable enough

for safe, compliant, and efficient engineering design work to begin with confidence.

The system interprets all record types found in a survey file — structural records (existing and proposed poles), context records (gates, tracks, streams), and anchor records (stays and braces) — and explains what those records mean in design terms: what is present, what is risky, and what is missing from the handoff.

---

## 3. Short definition

**A survey-to-design workflow intelligence tool that interprets digital survey data, identifies design risks and gaps, and determines whether a survey handoff is ready for engineering design work to begin.**

---

## 4. What the project is trying to solve

This project exists because repeated real-world friction was observed in the handoff between field survey and office design.

The problem is not usually that design software is missing.

The problem is often that incoming survey information is:

- inconsistent
- incomplete
- awkward to interpret
- mixed in quality
- discovered to be defective too late in the process

In practice, designers are often forced to perform hidden QA before they can begin actual design work.

That wastes time, creates avoidable rework, and increases the risk of poor assumptions entering the design process.

Unitas-GridFlow exists to act as the **trusted gate between survey and design**.

---

## 5. Core principle

This project is **validation-led, not feature-led**.

Its purpose is to act as the trusted gate between survey and design — turning raw, inconsistent, incomplete survey data into something a designer can confidently assess and use.

Every step must answer:

> **Does this improve the reliability, clarity, and design-readiness of real survey data?**

This principle is the main filter for deciding what the project should and should not do.

---

## 6. Correct framing of the product

### This project is NOT:

- a full CAD platform
- a full GIS platform
- a full survey capture platform
- an OCR/image interpretation system
- a general infrastructure management platform
- a broad SaaS workflow suite

### This project IS:

- a survey-to-design workflow intelligence tool
- a pre-CAD QA gatekeeper
- a data trust engine for real survey handoffs
- a decision-support tool for design readiness
- an interpreter of record roles (structural, context, anchor, existing/proposed)
- a surface for design risks, gaps, and missing evidence before CAD work begins

It answers questions like:

- What does this digital survey file actually contain?
- What is missing from the digital handoff?
- Can a designer safely proceed from this file alone?
- What still needs notebook, plan, or follow-up context?
- Which structures are existing assets and which are proposed?
- Are there angle structures with insufficient stay evidence?

### This project does NOT claim to replace:

- Trimble or other field capture software
- PoleCAD, AutoCAD, or other design tools
- engineering designers or overhead line engineers
- a full DNO compliance engine or regulatory approval system

It is an intelligence layer sitting before design — not a replacement for any of these tools or roles. It is also not yet a full DNO compliance engine.

---

## 7. Position in the real workflow

The real workflow is broadly:

**Field survey → digital export / handoff → validation / QA → design → planning / construction**

Unitas-GridFlow sits in the validation / QA layer between field capture and downstream design.

It exists to ensure that the digital representation of the survey reflects enough of the real-world field evidence to support engineering decisions.

A useful mental model is:

**Survey reality → digital handoff → Unitas-GridFlow → design confidence**

---

## 8. Current system capabilities

The system currently:

- ingests survey CSV and controller-derived survey data
- normalises input into a working schema
- applies rule-based QA validation
- generates structured issues
- visualises outputs on a Leaflet map
- produces PDF QA reports

The system now also supports:

- raw controller dump intake
- Irish Grid detection and conversion where needed
- completeness / capture summary generation
- initial controller-file QA refinement
- record-role classification (structural, context, anchor)
- EX/PR replacement cluster detection and narrative linking
- angle/stay evidence logic for angle structures
- designer summary layer (circuit summary, top design risks, replacement narratives)

---

## 9. What “good” currently looks like

A good result from Unitas-GridFlow is not merely “the file parsed”.

A good result is:

- the file is ingested successfully
- the system correctly identifies the coordinate system
- the data is normalised into a usable schema
- the output clearly shows what is present and missing
- the resulting QA/issues are meaningful rather than noisy
- a designer can quickly judge whether the survey is ready enough for design work

That is the current product test.

---

## 10. Primary users

Primary users are likely to include:

- designers and design engineers
- overhead line engineers
- project engineers and planners
- survey-to-design coordinators
- QA leads and checking engineers
- contractors receiving survey handoffs
- teams responsible for checking data quality before design release

The project is informed by survey practice, but it is **not only a surveyor tool**.

Its value spans the entire survey-to-design handoff — from surveyors handing over better-evidenced data, to designers receiving a clearer picture of what the digital file contains and what is still missing.

Future potential users include DNO asset management teams and network planners who need reliable digital representations of field conditions before committing to design decisions.

---

## 11. Current strategic position

The project should continue.

However, the next phase must remain **validation-led**.

The main unresolved question is:

> **Does the current tool provide meaningful value on real survey files for real users?**

Therefore, the current focus is:

- testing the tool on real files
- identifying what works
- identifying what breaks
- identifying what users actually care about
- refining the next phase from evidence rather than assumption

---

## 12. Scope discipline

During the current phase, the project should prioritise:

- real-file usefulness
- intake compatibility
- design-readiness clarity
- meaningful issue output
- targeted refinement based on validation evidence

During the current phase, the project should avoid broad expansion into:

- OCR
- notebook parsing
- plan/image parsing
- broad platform features
- speculative workflow systems
- premature productisation

Longer-term, the project may naturally extend toward:

- field-capture guidance (helping surveyors capture better evidence)
- structured survey standards for UK electricity network handoffs
- multi-DNO rulepack expansion based on validated real-world evidence

These are post-validation directions, not current scope.

---

## 13. Current development philosophy

The project should be developed using the following philosophy:

- stay narrow
- prefer small, targeted changes
- avoid architecture redesign unless necessary
- use real validation evidence to guide change
- optimise for real-world usefulness, not abstract completeness
- favour trustworthy output over impressive feature breadth

---

## 14. Toolchain operating model

The project now operates across multiple tools.

### ChatGPT

Project orchestrator:

- defines next steps
- reviews completed work
- prevents scope drift
- keeps all tools aligned

### Claude Code

Primary builder:

- reads full repo
- implements code changes
- runs tests
- commits and pushes

### Claude Desktop

Repo-aware analysis and validation layer:

- checks alignment
- reviews current state
- supports strategic and validation thinking

### VS Code / Cursor

Editing environment:

- browsing
- editing
- local developer workflow

### Codex

Optional bounded secondary coding / review agent:

- alternative implementations
- second opinions
- targeted support tasks

This toolchain is described operationally in `WORKFLOW_SYSTEM.md`.

---

## 15. Source of truth hierarchy

When there is uncertainty, truth should be resolved in this order:

1. real survey files and validation evidence
2. control layer files in `AI_CONTROL/`
3. current repo implementation and tests
4. documentation
5. AI summaries / assumptions

If anything conflicts with real validation evidence, validation evidence wins.

---

## 16. Canonical repository surface

### Active project surface

- `AI_CONTROL/`
- `app/`
- `tests/`
- `sample_data/`
- `README.md`
- `CHANGELOG.md`
- `CLAUDE.md`
- `PROJECT_DEEP_CONTEXT.md`
- `WORKFLOW_SYSTEM.md`

### Archive

- `_archive/`

Archive material is not active project truth and should not be used unless explicitly requested.

---

## 17. Canonical success statement

Unitas-GridFlow is successful when it can take messy real-world survey data and reliably tell a designer:

- what this digital survey contains
- what is missing
- what is risky
- what is still needed
- whether it is ready enough to move into design with confidence

That is the canonical definition of value for the project at this stage.
