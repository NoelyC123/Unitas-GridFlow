# Unitas Grid-Flow — Project Deep Context

## Purpose of this document

This document exists to give Claude full background context about **why this project exists**, **how the idea arose**, **what real-world workflow problems it is intended to solve**, and **how it should be framed as a fresh-start project**.

It is **not** the day-to-day control layer.

It should be used alongside the live control files and project instructions so Claude understands both:

- the **current state of the repository**
- and the **deeper operational and commercial reasoning** behind the project

---

## 1. Executive summary

**Unitas Grid-Flow** is a fresh-start project built around a repeated real-world problem: the gap between what is captured on site during overhead line or electricity distribution survey work and what is actually needed in the office to design confidently and efficiently.

The idea did **not** begin software-first.

It came from direct exposure to the way survey information is captured, written down, transferred, interpreted, checked, and eventually turned into design and CAD work. Over time it became clear that the biggest inefficiency was often **not the engineering itself**, but the poor handoff between **survey and design**.

The purpose of the project is to create a **structured gate between survey and design**:

- inspect incoming survey data
- validate structure and quality
- apply workflow or DNO-specific checks
- flag issues early
- produce cleaner, more reliable, design-ready outputs before expensive office time is wasted

The strongest framing is:

**A narrow pre-CAD QA and compliance gatekeeper for survey-to-design handoffs.**

---

## 2. The origin of the idea

This project exists because repeated exposure to real survey and design workflows showed the same weakness again and again:

The process technically worked, but it worked **inefficiently**.

Too much of the chain still depended on:

- memory
- handwritten notes
- personal habits
- delayed transfer methods
- late-stage interpretation
- downstream staff silently repairing poor inputs

The important insight was that the biggest source of inefficiency was often **not the engineering calculation or final CAD production**.

The weakness sat **earlier**, in the handoff from field survey to office design.

Raw information was being collected in the field, partly captured digitally and partly noted manually, and then passed on in a form that still needed too much interpretation, correction, and checking before anyone could design confidently from it.

That is the point at which the idea became specific:

There should be a proper **gate between survey and design**.

Instead of designers, CAD staff, or engineers discovering missing fields, inconsistent naming, unclear notes, suspect coordinates, or invalid values later in the process, a dedicated tool should catch those issues **as soon as the survey data comes in**.

---

## 3. Why the tool felt necessary

The tool felt necessary because the existing workflow was too fragile.

### Key reasons

- Important information could live partly in digital files and partly in handwritten notes or verbal explanation.
- What came back from site was not always yet a reliable design input, even when the right information existed in principle.
- Designers and CAD staff could end up doing hidden QA and data repair instead of actual design work.
- Basic input problems were being discovered too late, often when the work was already in PoleCAD, AutoCAD, or other downstream design steps.
- There was no strong early checkpoint where uploads could be previewed, validated, and either approved or flagged before office work properly began.
- The process relied too heavily on good people compensating for weak systems.

---

## 4. Real-life workflow problems behind the project

### Handwritten notes still carrying critical information

Important details were still being written manually rather than captured in a structured digital form.

That matters because anything written manually must later be interpreted. That creates:

- inconsistency
- risk of omission
- dependency on whoever wrote or read the note

### Poor handoff from survey into design

Information coming back from site was not always in a form that a designer could use immediately with confidence.

That means:

- designers do hidden QA
- designers repair inputs
- design time is lost before design even starts

### CAD / PoleCAD being used as a late-stage error detector

Basic problems could become obvious only once the information was already being handled in downstream design tools.

That matters because CAD should be for production, not for discovering defects that should have been caught earlier.

### Incomplete first-pass surveys

Some jobs could look finished after the first visit but still lack detail needed for confident office progression.

That creates:

- delays
- uncertainty
- clarification work
- avoidable repeat visits

### Delayed or informal transfer methods

Transfer habits could be slower or less structured than they should be, including later batch handover or informal file transfer patterns.

That weakens:

- feedback loops
- version clarity
- process reliability

### No enforced intake schema

Survey outputs could vary in naming, structure, completeness, and numeric quality.

That means every downstream user has to re-check what the file means instead of trusting a standard.

### No visible QA checkpoint

There was no consistent stage where uploads could be previewed, checked, and approved or rejected early.

That means errors survive longer and become more expensive to fix.

### Weak auditability

Too much could live in people’s heads rather than in a visible record of:

- what was checked
- what failed
- what was generated

That makes the workflow harder to defend, review, improve, or scale.

---

## 5. Concrete real-world scenarios that explain the value

### Scenario 1 — the designer doing hidden QA instead of design

A survey file comes back from site and technically contains the job data, but:

- column names are inconsistent
- some values are blank
- some coordinates look wrong
- key context sits outside the structured file

Instead of starting design, the designer first has to work out:

- what the file actually means
- what can be trusted
- what needs clarification

That is **not design work**. It is hidden repair work.

The project exists to reduce or remove that stage.

### Scenario 2 — handwritten notes carrying critical design context

The main asset positions may be captured digitally, but important exceptions are written by hand:

- stay conflict
- restricted access
- awkward crossing
- clearance concern
- tree issues
- telecom interaction
- something unusual about an existing asset

The office later has to interpret that note without standing on the site.

If the note is vague or incomplete, the design quality drops immediately.

### Scenario 3 — CAD being used as a late-stage error detector

Someone only realises a problem once the data is already being handled in PoleCAD or AutoCAD-related work.

At that point, a more expensive person in the chain is discovering that the input itself was flawed.

The tool is intended to catch those failures **before the design environment becomes the first place the problem is noticed**.

### Scenario 4 — incomplete first-pass capture creates repeat work

A first site visit captures enough to make the job look done, but not enough to let the office proceed confidently.

Later, someone realises that a:

- crossing detail
- pole relationship
- clearance issue
- telecom interaction
- environmental constraint

was not recorded properly.

Now the team either:

- guesses
- delays
- or goes back out

### Scenario 5 — every incoming file has to be re-understood

If one survey output names fields one way, another uses different headings, and another mixes formats or leaves blanks, the office has no true standard intake.

Every new file starts with interpretation rather than trust.

The project is intended to become that intake standard.

---

## 6. What the project is intended to do

Unitas Grid-Flow is intended to sit directly in the gap between field survey and design.

Its role is to take raw or semi-structured survey input, inspect it, validate it, apply rules, flag issues early, and produce cleaner, more usable outputs for the next stage of work.

### Intended capabilities

- ingest survey inputs such as CSV, GeoJSON, and later more packaged GIS-style or survey-origin formats
- preview what has been uploaded before committing it to a full QA run
- detect missing columns, bad data types, suspect coordinates, inconsistent values, and structural issues
- apply workflow-specific and later DNO-specific rule checks
- generate clear outputs such as cleaned CSVs, issue reports, normalised geospatial outputs, and CAD-oriented exports
- reduce the amount of manual checking required from designers and CAD staff
- create a visible and defensible record of what was checked, what failed, and what was generated

---

## 7. Real-world workflow the tool is designed to support

The intended workflow is anchored in how electrical or overhead line survey and design work often happens in practice.

### Workflow

1. **Job or route initiation**
   A work package, route, section, or design requirement is identified and assigned for survey and design.

2. **Field survey preparation**
   Surveyors receive route or asset context, sometimes with limited digital integration and sometimes relying on maps or separate references.

3. **On-site data capture**
   Survey teams collect coordinates, asset information, observations, and contextual notes using field equipment such as GNSS receivers, controllers, tablets, or mixed digital/manual methods.

4. **Data export and handover**
   Outputs may include CSV, GIS formats, CAD references, images, and informal notes. In weaker workflows this is where ambiguity enters.

5. **Pre-design QA and structured review**
   This is the stage the proposed tool is meant to improve. Incoming data is checked and normalised before larger design effort is spent.

6. **Design and CAD preparation**
   Only once the data is sufficiently trusted should it move more cleanly into the design and CAD workflow.

7. **Reporting, issue tracking, and auditability**
   The system should leave a clearer trail of what was checked, what failed, and what needs attention.

---

## 8. What the project is not

This project is **not**:

- an attempt to replace the whole design function
- a generic construction software platform for everything
- just a file uploader or dashboard
- a claim that a previous tool has already solved the problem

It is a **fresh-start project** built around a clear, narrow operational weakness:

**the point where survey information becomes design input**

---

## 9. Intended users and beneficiaries

### Primary users

- design engineers
- overhead line designers
- CAD technicians
- project engineers
- QA leads
- delivery teams handling electricity distribution or similar infrastructure workflows

### Wider beneficiaries

- survey teams who receive earlier feedback
- office teams who spend less time repairing inputs
- project leads who need clearer design-readiness status
- the wider business, because fewer avoidable errors, delays, and repeat visits should flow through the system

---

## 10. Core value proposition

The simplest explanation of the value proposition is this:

**The tool should strengthen the weakest part of the chain.**

Instead of allowing raw survey information to move into office design with too much ambiguity, it should validate, standardise, and explain that information early so that downstream work starts from a cleaner base.

### Core value

The value is not that it is modern software.

The value is that it addresses a **narrow but expensive operational weakness**.

If successful, it would:

- reduce rework
- improve consistency
- standardise checking
- shorten the path from survey to usable design data
- make it easier for teams to trust what they are working with

### In plain English

The project is meant to stop designers wasting time figuring out whether the input is trustworthy before they can even begin the real job.

---

## 11. Why this is a good tool to create

This is a good tool to create because it addresses a **narrow, real, and expensive problem** rather than a vague one.

That makes it:

- easier to explain
- easier to test
- easier to validate
- easier to prove useful

It also comes from direct exposure to the field and office workflow rather than detached speculation.

That matters.

Many software ideas in technical industries are built from assumptions. This one comes from repeatedly seeing where the process breaks down.

The strongest strategic framing is not that the tool does everything.

It is that it becomes a **structured gatekeeper between survey and design**:
a pre-CAD validation and compliance layer that saves time, improves trust, and reduces avoidable rework.

---

## 12. Fresh-start project principles

- Treat this as a completely fresh project from a delivery perspective.
- Carry forward the insight, rationale, and observed workflow pain points — but do not rely on past builds as current product state.
- Keep the scope tight around survey intake, validation, QA, and design-readiness.
- Stay grounded in practical field-to-office workflow realities rather than trying to over-promise a huge platform too early.
- Use real-life examples and user conversations to guide scope, language, and priorities.
- Aim for a product story built on operational usefulness first, technical complexity second.

---

## 13. Specific practical examples of where value could appear

- A survey dataset arrives with inconsistent asset identifiers, missing required fields, and partial contextual notes. Instead of passing that confusion directly into design, the system highlights the problems before the job advances.
- A route includes crossings, constraints, or site observations that are mentioned informally but not recorded in a structured way. The system prompts for more complete handling or flags the dataset as not yet design-ready.
- Different surveyors record equivalent information in slightly different ways. The platform helps standardise inputs and checking expectations across teams.
- A project lead wants to know whether a job is ready for design, where the main data quality risks are, and whether another field visit is likely. A structured readiness view would be more useful than several disconnected files and notes.

---

## 14. What still needs to be proved

The underlying problem is already understood from direct experience.

What still needs to be proved is:

- whether other users will trust the solution
- whether they will adopt it
- whether they would pay for it
- whether it fits cleanly into real workflows

So later validation should focus on:

- fit
- workflow acceptance
- realistic survey files
- operational usefulness

not on re-proving that the underlying problem exists.

---

## 15. Commercial framing

The project has the potential to create value because it addresses a repeated operational cost, not a cosmetic annoyance.

Potential value comes from:

- less manual interpretation
- fewer avoidable follow-up queries
- earlier issue detection
- better consistency between jobs and between surveyors
- cleaner preparation for CAD and design
- better audit trail of what was checked and why

Commercially, the strongest logic is:

- save engineering time
- reduce avoidable delay
- reduce rework
- improve trust in survey intake
- create a standardised pre-CAD validation checkpoint

This could support the project as:

- a useful internal tool
- a consultancy leverage asset
- a niche software product

depending on later validation and execution.

---

## 16. Final conclusion

The reason this project exists is simple:

**the current workflow functions, but it functions inefficiently.**

Too much value is lost in the gap between what is captured on site and what is required in the office.

Unitas Grid-Flow is an attempt to fix that gap in a focused, practical, and commercially sensible way.

This project began from a genuine operational observation:

There is unnecessary friction in the path from survey to design.

That friction shows up in:

- incomplete capture
- messy handovers
- repeated manual checking
- late issue discovery
- too much dependence on human interpretation

A clean new project should preserve that original insight.

The aim is not to carry over assumptions about old builds.

The aim is to carry over the **real reason the idea mattered in the first place**.

Viewed in that light, the project has a strong conceptual foundation.

It is grounded in an actual industry workflow, aimed at a genuine pain point, and capable of becoming a useful internal tool, consultancy asset, or niche software product if the next stages are handled with real-world validation and focus.
