# Batch 20 Decision Memo — Trust, Severity & Actionable Design Briefing

## Purpose

This memo records the conclusions from the April 2026 multi-AI review of the Batch 19 validation output.

Its purpose is to convert the review feedback into a narrow, practical Batch 20 development direction.

This file is not a broad roadmap. It exists to prevent scope drift and keep the next development step focused on real validation evidence.

---

## Review material considered

The review set included responses from:

- Claude
- Grok
- Gemini
- Cursor
- ChatGPT

Important note:

The ChatGPT response reviewed a different imagined product involving LiDAR, UAV imagery, point-cloud processing, deep learning segmentation, LAS/LAZ ingestion, and drone survey workflows.

That is not the current Unitas GridFlow product.

Therefore, the ChatGPT response should not be used to justify LiDAR, UAV, OCR, point-cloud, vegetation AI, or broad platform expansion.

The useful product-grounded feedback came primarily from Claude, Grok, Gemini, and Cursor.

---

## Main review conclusion

The reviews strongly agree that Unitas GridFlow is now a valuable working MVP.

The project should continue.

However, the tool should not yet be positioned as a mature DNO compliance engine or standalone commercial rulepack product.

The strongest current framing is:

**A pre-design survey handoff interpreter and QA briefing tool that tells a designer what the digital survey file contains, what is missing, what looks risky, and what should be checked before design starts.**

---

## What the reviews confirmed as genuinely valuable

The following capabilities were repeatedly identified as valuable:

- raw controller CSV intake
- CRS-aware coordinate handling
- mapping survey records onto a Leaflet map
- design readiness / survey coverage summary
- identifying missing design evidence
- replacement pair detection between existing and proposed supports
- span sanity checks
- PASS / WARN / FAIL filtering
- PDF QA reporting
- designer-facing summary of what the digital file does and does not contain

The strongest product insight is not generic data validation.

The strongest insight is:

**designers need a fast, trustworthy briefing on whether the survey handoff is complete enough to design from.**

---

## Main weaknesses identified

The reviews identified the following weaknesses:

### 1. Output is too noisy

The tool currently risks showing too many warnings without enough prioritisation.

A high issue count can cause alarm fatigue, especially when some items are not true defects but useful observations.

---

### 2. Issues and observations are conflated

The current output can treat different types of findings as equivalent.

For example:

- missing structural evidence
- ambiguous replacement pairings
- likely replacement pairs
- short spans caused by co-located replacement points
- missing heights
- suspicious height values

These should not all be counted in the same way.

---

### 3. Severity levels are needed

The output needs at least three practical levels:

- Critical / Blocker
- Warning
- Observation / Information

This allows a designer to understand what stops design, what needs review, and what is simply useful context.

---

### 4. Recommended actions are needed

The report currently says what is missing or risky, but it does not always say what to do next.

The next version should turn major findings into plain-English actions, such as:

- request missing pole height evidence
- confirm stay specifications from field notes or plans
- review ambiguous EX to proposed replacement groups
- confirm whether 5.0m values are true pole heights or controller-derived values

---

### 5. Design readiness wording can overclaim

A single broad readiness label such as "Partially Ready" can be misleading.

A file may be position-ready but not structurally ready.

The output should use scoped evidence gates instead of one over-broad readiness verdict.

Suggested gates:

- position / mapping evidence
- structure identity evidence
- structural specification evidence
- stay evidence
- clearance design evidence
- conductor scope evidence
- overall design handoff status

---

### 6. Rulepack truthfulness is a trust issue

The UI and API must not imply that unsupported rulepacks are available.

If a rulepack is shown to the user, it must exist in the backend and the applied rulepack must be clearly recorded.

Rulepack detail endpoints must not return misleading stub information.

---

### 7. Metric contradictions must be fixed

The UI must not show contradictory metrics.

Example:

- showing "0 Spans" while also showing span warnings damages trust.

Metrics should either be calculated correctly, renamed, or removed until reliable.

---

### 8. Raw controller labels can create noise

Raw labels such as `Pol:LAND USE` should not clutter designer-facing outputs if they add no useful design meaning.

They should be cleaned, suppressed, or moved to a technical/debug section.

---

## Accepted Batch 20 direction

Batch 20 should focus on:

**Trust, severity, and actionability.**

The goal is to make the Batch 19 output clearer, safer, and more useful to a real designer without broadening scope.

Batch 20 should improve the tool from:

**"Here are many warnings"**

to:

**"Here is what matters, why it matters, and what action should happen next."**

---

## Batch 20 scope

Approved scope:

1. Fix rulepack truthfulness between frontend, backend, and API.
2. Fix or remove misleading span-count metrics.
3. Clean noisy raw controller labels in designer-facing outputs.
4. Introduce severity levels.
5. Separate issues from observations.
6. Add recommended actions for top design risks.
7. Reframe readiness as scoped evidence gates.
8. Improve the first page of the PDF as a designer briefing.
9. Add basic run provenance where practical:
   - input filename
   - rulepack applied
   - CRS detected
   - parser used
   - run timestamp
   - version or commit if available

---

## Out of scope for Batch 20

Do not add:

- OCR
- handwritten note parsing
- plan parsing
- LiDAR processing
- UAV imagery processing
- point-cloud processing
- vegetation AI
- broad CAD automation
- PoleCAD replacement
- commercial packaging
- pricing pages
- broad SaaS/platform features
- extra superficial rulepacks just for coverage

These may be considered only after stronger real-world validation, and only if supported by evidence.

---

## Batch 20A immediate implementation focus

The first implementation step should be Batch 20A.

Batch 20A should fix narrow trust issues before larger output restructuring.

Batch 20A tasks:

1. Ensure the frontend only offers backend-supported rulepacks.
2. Make the rulepack API truthful and auditable.
3. Fix the map/sidebar span-count contradiction.
4. Clean or suppress noisy raw controller labels such as `Pol:LAND USE`.
5. Add or update tests.
6. Run `pytest -v`.
7. Run `pre-commit run --all-files`.
8. Commit and push.

---

## Batch 20B follow-up focus

After Batch 20A, implement a structured issue model.

Suggested fields:

- issue_code
- severity
- category
- scope
- confidence
- recommended_action
- is_observation

---

## Batch 20C follow-up focus

After the structured issue model exists, add a designer-facing recommended actions section.

This should appear near the top of the PDF and in any relevant UI summary.

---

## Batch 20D follow-up focus

Reframe design readiness into scoped evidence gates.

The output should clearly distinguish:

- suitable for route / position review
- suitable for structure identity review
- not sufficient for structural loading
- not sufficient for clearance design
- requires field notes / plan evidence

---

## Batch 20E follow-up focus

Improve the PDF first page so it reads as a professional designer briefing.

The first page should show:

- job summary
- parser used
- CRS detected
- rulepack applied
- record counts
- top blockers
- top warnings
- recommended actions
- clear statement on whether design can proceed from the digital file alone

Detailed row-level findings should be lower down or in an appendix.

---

## Final decision

The project should continue.

The next development phase should not broaden the product.

The next development phase should improve trust, clarity, severity, and actionability.

The goal for Batch 20 is:

**Make Unitas GridFlow feel trustworthy to a real designer within the first 60 seconds of reading the report.**
