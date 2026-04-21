# Unitas Grid-Flow — Project Rationale and Concept

## Working instruction for all AI tools and contributors

- **Unitas Grid-Flow is a true fresh-start project.**
- Do not assume any previous EW Design Tool / SpanCore codebase is the current Unitas product
  state. Older builds may be used as historical or technical reference only if explicitly stated.
- Real survey-origin files are now confirmed and available (Trimble CSV exports, .job binary,
  site images, handwritten field notebook sketches).
- This document is a source-of-truth project explanation file. It describes why the project
  exists, what it is, and what it is not. It does not describe current code state — for that,
  read `AI_CONTROL/00_MASTER_SOURCE_OF_TRUTH.md`.

**Source:** Fresh-Start Master Project Rationale and Concept Document (revised final version)
**Saved:** 21 April 2026

---

## Document purpose

To explain why the project exists, the real-life workflow problems it is intended to solve, how
the idea arose, what the tool is meant to do, and how it should be framed as a completely fresh
project.

**Project position:** New project / fresh start. This document intentionally excludes claims about
prior development being relied on as current delivery.

**Core concept:** A survey-to-design validation, QA, and pre-CAD compliance tool for overhead line
and electricity distribution workflows.

---

## 1. Executive summary

Unitas Grid-Flow is a fresh-start project built around a repeated real-world problem: the gap
between what is captured on site during overhead line or electricity distribution survey work and
what is actually needed in the office to design confidently and efficiently.

The idea did not begin with software first. It came from direct exposure to the way survey
information is captured, written down, transferred, interpreted, checked, and eventually turned
into design and CAD work. Over time it became clear that the biggest inefficiency was often not
the engineering itself, but the poor handoff between survey and design.

The purpose of this project is to create a structured gate between survey and design: a tool that
can inspect incoming survey data, validate structure and quality, apply workflow or DNO-specific
checks, flag issues early, and produce cleaner, more reliable, design-ready outputs before
expensive office time is wasted.

---

## 2. The full origin of the idea

This project exists because repeated exposure to real survey and design workflows showed the same
weakness again and again: the process technically worked, but it worked inefficiently. Too much of
the chain still depended on memory, handwritten notes, personal habits, delayed transfer methods,
and late-stage interpretation.

The important insight was that the biggest source of inefficiency was often not the engineering
calculation or the final CAD production. The weakness sat earlier, in the handoff from field
survey to office design. Raw information was being collected in the field, partly captured
digitally and partly noted manually, and then passed on in a form that still needed too much
interpretation, correction, and checking before anyone could design confidently from it.

That is the point at which the idea started to become specific. There should be a proper gate
between survey and design. Instead of designers, CAD staff, or engineers discovering missing
fields, inconsistent naming, unclear notes, suspect coordinates, or invalid values later in the
process, a dedicated tool should catch those issues as soon as the survey data comes in.

It is not just a file uploader, not simply a map viewer, and not merely a reporting dashboard. Its
purpose is to receive field survey information, make that information more structured and reliable,
apply practical rules and checks, identify issues before they become expensive, and output results
that reduce friction for designers, CAD technicians, QA staff, and delivery teams.

Specifically, the tool is intended to:

- Ingest structured or semi-structured survey information
- Validate completeness, consistency, and basic engineering/data quality logic
- Apply DNO-specific or client-specific rule packs where relevant
- Flag missing, risky, or non-compliant information early
- Visualise issues clearly rather than hiding them in spreadsheets
- Produce cleaner downstream outputs for design, checking, and CAD preparation

---

## 3. Why the tool felt necessary

- Because the existing workflow was too fragile. Important information could live partly in digital
  files and partly in handwritten notes or verbal explanation.
- Because what came back from site was not always yet a reliable design input, even when the right
  information existed in principle.
- Because designers and CAD staff could end up doing hidden QA and data repair instead of actual
  design work.
- Because basic input problems were being discovered too late, often when the work was already in
  PoleCAD, AutoCAD, or other downstream design steps.
- Because there was no strong early checkpoint where uploads could be previewed, validated, and
  either approved or flagged before office work properly began.
- Because the process relied too heavily on good people compensating for weak systems.

---

## 4. The real-life workflow problems that triggered the project

| Observed issue | What was happening | Why it matters |
|---|---|---|
| Handwritten notes still central | Important details were still being written manually rather than captured in a structured digital form. | Anything written manually must later be interpreted. That creates inconsistency, risk of omission, and dependence on whoever wrote or read the note. |
| Poor handoff from survey into design | Information coming back from site was not always in a form that a designer could use immediately with confidence. | Designers end up doing hidden QA and data repair work instead of design work. |
| PoleCAD / CAD used too late as validation | Basic problems could become obvious only once the information was already being handled in downstream design tools. | CAD should be for production, not for discovering input defects that should have been caught earlier. |
| Incomplete first-pass surveys | Some jobs could look finished after the first visit but still lack detail needed for confident office progression. | That creates delay, uncertainty, clarification work, and avoidable repeat visits. |
| Delayed or informal transfer methods | Transfer habits could be slower or less structured than they should be, including later batch handover or USB-style methods. | That weakens feedback loops, creates version uncertainty, and slows the whole chain. |
| No enforced intake schema | Survey outputs could vary in naming, structure, completeness, and numeric quality. | Every downstream user has to re-check what the file means instead of trusting a standard. |
| No visible QA checkpoint | There was no consistent stage where uploads could be previewed, checked, and approved or rejected early. | Errors survive longer and become more expensive to fix. |
| Weak auditability | Too much could live in people's heads rather than in a visible record of what was checked, what failed, and what was generated. | That makes the process harder to defend, review, improve, or scale. |

---

## 5. Specific real-life scenarios that explain the value

**Scenario 1 — The designer doing hidden QA instead of design**
A survey file comes back from site and technically contains the job data, but column names are
inconsistent, some values are blank, a few coordinates look wrong, and key context sits outside
the structured file. Instead of starting design, the designer first has to work out what the file
actually means, what can be trusted, and what needs clarification. That is not design work. It is
hidden repair work. The project exists to reduce or remove that stage.

**Scenario 2 — Handwritten notes carrying critical design context**
The main asset positions may be captured digitally, but important exceptions are written by hand:
a stay conflict, restricted access, an awkward crossing, a clearance concern, tree issues, or
something unusual about an existing asset. The office later has to interpret that note without
standing on the site. If the note is vague or incomplete, the design quality drops immediately.

**Scenario 3 — CAD being used as a late-stage error detector**
Someone only realises a problem once the data is already being handled in PoleCAD or AutoCAD
related work. At that point a more expensive person in the chain is discovering that the input
itself was flawed. The tool is intended to catch those failures before the design environment
becomes the first place the problem is noticed.

**Scenario 4 — Incomplete first-pass capture creates repeat work**
A first site visit captures enough to make the job look done, but not enough to let the office
proceed confidently. Later, someone realises that a crossing detail, pole relationship, clearance
issue, telecom interaction, or environmental constraint was not recorded properly. Now the team
either guesses, delays, or goes back out.

**Scenario 5 — Every incoming file has to be re-understood**
If one survey output names fields one way, another uses different headings, and another mixes
formats or leaves blanks, the office has no true standard intake. Every new file starts with
interpretation rather than trust. The project is intended to become that intake standard.

---

## 6. What the project is intended to do

Unitas Grid-Flow is intended to sit directly in the gap between field survey and design. Its role
is to take raw or semi-structured survey input, inspect it, validate it, apply rules, flag issues
early, and produce cleaner, more usable outputs for the next stage of work.

- Ingest survey inputs such as CSV, GeoJSON, and later more packaged GIS-style or survey-origin
  formats (including Trimble .job exports).
- Preview what has been uploaded before committing it to a full QA run.
- Detect missing columns, bad data types, suspect coordinates, inconsistent values, and structural
  issues.
- Apply workflow-specific and DNO-specific rule checks.
- Generate clear outputs: cleaned CSVs, issue reports, normalised geospatial outputs, and
  CAD-oriented exports.
- Reduce the amount of manual checking required from designers and CAD staff.
- Create a visible and defensible record of what was checked, what failed, and what was generated.

### Real-world workflow the tool is designed to support

1. **Job or route initiation** — A work package, route, section, or design requirement is
   identified and assigned for survey and design.
2. **Field survey preparation** — Surveyors receive route or asset context, sometimes with limited
   digital integration and sometimes relying on maps or separate references.
3. **On-site data capture** — Survey teams collect coordinates, asset information, observations,
   and contextual notes using field equipment (GNSS receivers, controllers, tablets, Trimble
   devices, or mixed digital/manual methods).
4. **Data export and handover** — Outputs may include CSV, GIS formats, CAD references, images,
   and informal notes. In weaker workflows this stage is where ambiguity enters.
5. **Pre-design QA and structured review** — **This is the stage the tool is meant to improve.**
   The incoming data is checked and normalised before larger design effort is spent.
6. **Design and CAD preparation** — Only once the data is sufficiently trusted should it move more
   cleanly into the design and CAD workflow.
7. **Reporting, issue tracking, and auditability** — The system leaves a clearer trail of what was
   checked, what failed, and what needs attention.

---

## 7. What the project is not

- Not an attempt to replace the whole design function.
- Not a generic construction software platform for everything.
- Not just a file uploader or dashboard.
- Not relying on the claim that a previous tool has already solved the problem.
- A fresh-start project built around a clear, narrow operational weakness: the point where survey
  information becomes design input.

---

## 8. Intended users and beneficiaries

**Primary users:** Design engineers, overhead line designers, CAD technicians, project engineers,
and QA leads working with electricity distribution or similar infrastructure workflows.

**Wider beneficiaries:** Survey teams who receive earlier feedback, office teams who spend less
time repairing inputs, and the business as a whole — fewer avoidable errors, delays, and repeat
visits flowing through the system.

---

## 9. The core value proposition

The simplest explanation: the tool should strengthen the weakest part of the chain. Instead of
allowing raw survey information to move into office design with too much ambiguity, it validates,
standardises, and explains that information early so that downstream work starts from a cleaner
base.

Specifically:

- Less manual interpretation
- Fewer avoidable follow-up queries
- Earlier issue detection
- Better consistency between jobs and between surveyors
- Cleaner preparation for CAD and design
- Better audit trail of what was checked and why

**In plain English:** the project is meant to stop designers wasting time figuring out whether the
input is trustworthy before they can even begin the real job.

---

## 10. Why this is a good tool to create

This is a good tool to create because it addresses a narrow, real, and expensive problem rather
than a vague one. It is easier to explain, easier to test, and easier to validate than a much
broader all-in-one engineering platform.

It also comes from direct exposure to the field and office workflow rather than detached
speculation. Many software ideas in technical industries are built from assumptions. This one comes
from repeatedly seeing where the process breaks down.

The strongest strategic framing is not that the tool does everything. It is that it becomes a
structured gatekeeper between survey and design — a pre-CAD validation and compliance layer that
saves time, improves trust, and reduces avoidable rework.

---

## 11. Proposed scope

**Survey intake and file handling:**
- Accept job-related survey data and associated context files
- Normalise naming and structure where possible
- Identify obvious missing items or malformed inputs

**Validation and quality checks:**
- Record-level completeness checks
- Consistency checks across linked data
- Warnings for suspect values, relationships, or omissions

**Rules and compliance logic:**
- Apply client, DNO, or internal rule packs where appropriate
- Surface breaches, risks, and missing evidence for key checks

**Visual review:**
- Map-based view of assets and issues
- Clear prioritisation of critical versus minor problems

**Outputs:**
- Summary reports
- Issue lists
- Clean downstream exports
- CAD-preparation outputs and structured handover information

---

## 12. Fresh-start project principles

- Treat this as a completely fresh project from a delivery perspective.
- Carry forward the insight, the rationale, and the observed workflow pain points — but do not rely
  on past builds as the current product state.
- Keep the scope tight around survey intake, validation, QA, and design-readiness.
- Stay grounded in practical field-to-office workflow realities.
- Use real-life examples and user conversations to guide scope, language, and priorities.
- Aim for a product story built on operational usefulness first, technical complexity second.

### Specific practical examples of where value could appear

- A survey dataset arrives with inconsistent asset identifiers, missing required fields, and
  partial contextual notes. Instead of passing that confusion directly into design, the system
  highlights the problems before the job advances.
- A route includes crossings, constraints, or site observations that are mentioned informally but
  not recorded in a structured way. The system prompts for more complete handling or flags the
  dataset as not yet design-ready.
- Different surveyors record equivalent information in slightly different ways. The platform helps
  standardise inputs and checking expectations across teams.
- A project lead wants to know whether a job is ready for design, where the main data quality
  risks are, and whether another field visit is likely. A structured readiness view would be more
  useful than several disconnected files and notes.

---

## 13. What still needs to be proved

- The problem itself is already understood from direct experience.
- What still needs proving is whether other users will trust, adopt, and potentially pay for this
  exact solution.
- Validation should focus on: fit, workflow acceptance, realistic survey files, and operational
  usefulness — not on re-proving that the underlying problem exists.

**Confirmed available for testing (as of 21 April 2026):**
- Real Trimble CSV exports from actual OHL jobs (via Electricity Worx) — jobs 4-474, 474c, 513
- Native Trimble `.job` binary file (job 474c) — proprietary binary, not the first parsing target
- Marked-up ArcGIS/SpatialNI design print (Strabane area, TM65 Irish Grid)
- PoleCAD-style design drawing with annotated work instructions
- Handwritten field notebook sketches showing stay geometry, clearance dimensions, and site
  constraints not captured in the structured CSV

The intake and normalisation logic must be tested against these real files before any user
validation conversation happens. The real Trimble CSV format differs materially from the
current sample schema in the codebase.

---

## 14. Final conclusion

The reason this project exists is simple: the current workflow functions, but it functions
inefficiently. Too much value is lost in the gap between what is captured on site and what is
required in the office. Unitas Grid-Flow is an attempt to fix that gap in a focused, practical,
and commercially sensible way.

This project began from a genuine operational observation: there is unnecessary friction in the
path from survey to design. That friction shows up in incomplete capture, messy handovers,
repeated manual checking, late issue discovery, and too much dependence on human interpretation.

A clean new project should preserve that original insight. The aim is not to carry over
assumptions about old builds. The aim is to carry over the real reason the idea mattered in the
first place.

Viewed in that light, the project has a strong conceptual foundation. It is grounded in an actual
industry workflow, aimed at a genuine pain point, and capable of becoming a useful internal tool,
consultancy asset, or niche software product if the next stages are handled with real-world
validation and focus.

---

## Principles for moving forward

- **Start with the workflow, not the interface** — The software should be shaped around how
  survey, QA, design, and CAD teams actually work.
- **Use real data examples as early as possible** — The biggest risk in niche software is building
  around imagined inputs rather than the files and edge cases people really use.
- **Keep the first version focused** — The initial value should come from solving one painful
  section of the workflow well rather than trying to replace the whole ecosystem immediately.
- **Treat rules and checks as first-class assets** — The real defensible value is in codifying
  useful logic, not just displaying uploaded files on a screen.
- **Aim for trust and usability** — If users cannot quickly understand why something was flagged,
  the tool will feel like noise rather than help.
