# SpanCore Master Claims Ledger

## Purpose
This file is the deep synthesis layer for the SpanCore / EW Design Tool project.

Unlike the AI comparison matrix, which compares each AI at a high level, this ledger compares the AIs **issue by issue**.

For each major question, it records:
- what Claude says
- what ChatGPT says
- what Gemini says
- what Grok says
- the final synthesis judgment
- and the confidence level

The goal is to move from “what each AI said” to “what we now believe is most likely true.”

---

## 1. What the project is

### Claude
SpanCore is a narrow pre-CAD QA, compliance, and submission-readiness tool for UK electricity / OHL survey-to-design handoffs. It is best understood as a pre-CAD data validation engine that sits between raw survey data and formal design-tool input.

### ChatGPT
SpanCore appears to be a rules-heavy workflow tool or deterministic workflow engine intended to codify a narrow design/process task. ChatGPT is more cautious because it could not directly verify the underlying artefacts, but its strongest reading is still that the project is best understood as a narrow workflow accelerator, not a broad platform.

### Gemini
SpanCore is framed as an infrastructure compliance platform or submission engine for the survey-to-design handoff. Gemini presents it more expansively, with platform language and broader commercial ambition.

### Grok
SpanCore is a lightweight, web-first pre-CAD QA and compliance gatekeeper for UK electricity DNO survey-to-design handoffs. It is not a GIS/CAD replacement or full design suite.

### Final synthesis judgment
SpanCore is best understood as a **narrow pre-CAD QA / compliance / submission-readiness tool** for electricity-network survey-to-design handoffs. It should not currently be framed as a broad engineering platform, general utility SaaS, or design-suite replacement.

### Confidence
High

---

## 2. What has genuinely been built

### Claude
Claude gives the strongest repo-grounded view. It says the following are materially real:
- Flask app factory / modular structure
- QA engine
- placeholder DNO rules
- frontend templates and JavaScript
- Docker/deployment scaffolding

But Claude is equally clear that the end-to-end upload → processing → status → map flow is still blocked by missing backend endpoints and incomplete wiring.

### ChatGPT
ChatGPT refuses to claim certainty on detailed build state because it could not directly inspect the full underlying handover/code artefacts in that environment. Its position is that the project may be substantial, but the exact built state was not safely verifiable there.

### Gemini
Gemini tends to treat more of the system as already materially built, including broader compliance-engine and DXF-oriented capability, but it clearly blurs prototype capability and roadmap ambition.

### Grok
Grok broadly agrees with Claude that the project has a real technical base:
- modular Flask structure
- working QA core
- modern frontend
- near-usable route structure

But it stresses that the app is still effectively non-runnable end-to-end.

### Final synthesis judgment
A **meaningful scaffold has genuinely been built**, including:
- modular Flask app structure
- working QA engine
- placeholder rule logic
- modern frontend
- recovery-worthy product shell

But the project is **not yet a working product**, because the core operational pipeline is incomplete.

### Confidence
High

---

## 3. What is partial vs planned

### Claude
Claude sharply distinguishes between:
- live code
- partial/stubbed code
- and planned/context-only features

It identifies key missing endpoints, partial blueprint stubs, and the absence of several high-value planned capabilities.

### ChatGPT
ChatGPT’s main contribution is governance discipline: it warns strongly against conflating canonical current truth with historical narrative and aspirational roadmap material.

### Gemini
Gemini is weakest on this distinction. It frequently treats partial capability, conceptual roadmap, and commercial future-state as if they were closer to present reality.

### Grok
Grok broadly agrees with Claude that the project is substantial but blocked, with the critical missing piece being the end-to-end upload → process → status → map flow.

### Final synthesis judgment
The project is **neither a blank slate nor a working product**. It sits in the middle. The architecture and shell are real; the full trusted workflow is not. Roadmap ambition, historical documentation, and canonical current state must be kept clearly separate.

### Confidence
High

---

## 4. Is it a good idea?

### Claude
Claude judges it a niche-but-good idea with a real gap and clear value, provided it remains narrow and focused on pre-CAD validation.

### ChatGPT
ChatGPT says it is a good idea **only in narrow form**. It sees the category as viable, but warns that this class of product often sounds better than it proves out unless one specific workflow is validated with measurable ROI.

### Gemini
Gemini is the most bullish. It treats SpanCore as a high-potential specialist compliance platform with strong strategic timing and significant upside if stabilised.

### Grok
Grok sees it as a plausible, genuinely useful niche idea, but clearly not a broad product opportunity yet.

### Final synthesis judgment
Yes — **it is a good idea in narrow form**. More precisely, it is a **good niche workflow idea**, not a good broad platform idea.

### Confidence
High

---

## 5. Is it needed now?

### Claude
Claude says yes. The pain is real in the current UK electricity / OHL workflow, especially around manual validation, rework, and compliance-heavy data handoff.

### ChatGPT
ChatGPT also says yes at the category level, but only where the workflow is narrow, repeated, and tied to measurable ROI. Need does not automatically mean adoption.

### Gemini
Gemini is strongly positive and frames the current market moment as especially favourable because of grid-modernisation pressure, DNO submission friction, and digitalisation demands.

### Grok
Grok says yes, but the pain is moderate rather than acute. Useful enough to justify a tool, but not self-evidently strong enough to guarantee paid adoption.

### Final synthesis judgment
Yes — **the project is needed now**, but only in a narrow workflow sense. The need is real, but it becomes commercially meaningful only if tied to one repeated workflow with measurable value.

### Confidence
High

---

## 6. What similar tools already exist?

### Claude
Claude says the exact gap is narrow and partly open. It acknowledges adjacent competitors such as PLS-CADD, IQGeo, and broader utility/GIS/design systems, but argues they do not clearly own the same pre-CAD validation lane.

### ChatGPT
ChatGPT gives the most cautious competitive framing. It argues that a lot already exists in broader design automation, engineering workflow, and infrastructure software. The gap is not empty; it is only partly open.

### Gemini
Gemini treats the landscape as crowded but still sees SpanCore as having a distinctive wedge as a compliance and submission-readiness layer.

### Grok
Grok broadly agrees that similar tools exist, but mostly in adjacent rather than exact form. It sees the opportunity in a lightweight survey-first compliance gap.

### Final synthesis judgment
There is **substantial adjacent competition**, plus spreadsheet/manual workarounds, but the exact gap SpanCore wants to occupy still appears **partly open**. The right language is: **partly open, not empty**.

### Confidence
Medium-High

---

## 7. Technical success likelihood

### Claude
Claude is the most technically confident, because it sees the architecture as correct and the missing pieces as specific, small, and recoverable through targeted recovery.

### ChatGPT
ChatGPT is more cautious because it could not directly verify the whole implementation state, but at the category level it sees technical success as plausible for one deterministic workflow.

### Gemini
Gemini is broadly positive and tends to speak as if more of the system is already in place.

### Grok
Grok is positive on technical success and sees the main issue as not technical impossibility but blocked operational wiring.

### Final synthesis judgment
Technical success is **moderately to strongly likely for a narrow MVP**. It is **much less likely** for any broad platform version.

### Confidence
High

---

## 8. Commercial success likelihood

### Claude
Claude sees a real niche opportunity, but only with narrow positioning, real rule data, and real workflow validation. It is positive but conditional.

### ChatGPT
ChatGPT is the most commercially cautious. It treats broad productisation as premature until there is canonical truth, one proven workflow, and benchmarked ROI.

### Gemini
Gemini is the most commercially bullish and most willing to imagine SpanCore becoming a category player or specialist standard.

### Grok
Grok sees moderate commercial usefulness in a niche, but strongly prefers internal tool / consultancy leverage over broad SaaS.

### Final synthesis judgment
Commercial success is **possible but conditional and narrow**. Internal / consultancy-leverage use is the most realistic early commercial form. Licensed niche product potential exists only if repeatability and ROI are proven.

### Confidence
Medium-High

---

## 9. Strongest arguments in favour

### Claude
The problem is real, the workflow slot is right, the repo is worth recovering, and the rule-driven pre-CAD wedge is commercially sensible.

### ChatGPT
Rules-heavy workflow tools can create disproportionate value when the workflow is repeated, costly, and poorly handled by spreadsheets/manual coordination.

### Gemini
The strongest market-side argument is the fragmented survey-to-design pipeline and the cost of discovering bad data too late.

### Grok
There is already enough technical substance and product clarity for the project to become genuinely useful with a narrow MVP.

### Final synthesis judgment
The strongest arguments in favour are:
- the problem is real
- the workflow friction is real
- the codebase is not a blank slate
- the narrow product identity is strong
- and the project could become genuinely useful in practice

### Confidence
High

---

## 10. Strongest arguments against

### Claude
The market is niche, rule maintenance is a permanent burden, the project has drifted before, and some strategically interesting differentiators do not yet exist in live code.

### ChatGPT
This category often looks better in concept than in deployment; broad productisation is premature without canonical truth and proof-of-value.

### Gemini
Gemini underweights the danger of over-claiming maturity and overestimating both differentiation and market readiness.

### Grok
The product is still incomplete where it matters most; without fast proof, it could remain an interesting but commercially soft project.

### Final synthesis judgment
The strongest arguments against are:
- the project is still **not yet a working end-to-end product**
- the market gap is **narrow**
- incumbents and workarounds are already entrenched
- adoption is not automatic
- and scope expansion would likely weaken the project

### Confidence
High

---

## 11. Serious unanswered questions

### Claude
Claude is strongest on first-buyer, real workflow, rule ownership, and whether the founder can stay focused enough to reach proof-of-value.

### ChatGPT
ChatGPT focuses on governance and proof:
- who owns the rules
- what exact workflow is first
- what counts as canonical truth
- what benchmark proves value
- what liability/trust boundary exists

### Gemini
Gemini adds broader strategic questions around DNO integration, infrastructure/security requirements, and whether safety/environmental logic could become a differentiator.

### Grok
Grok focuses on near-term commercial reality:
- who pays
- what pain metric matters
- how much time it actually saves
- whether the deployment is better as software or consultancy capability

### Final synthesis judgment
The most important unanswered questions are:
1. Who is the first real buyer?
2. What exact workflow is the first proof-of-value workflow?
3. What exact ROI metric will prove value?
4. Who owns and maintains the rules?
5. What is the real moat: software, workflow embedding, or consultancy knowledge?
6. Can the product stand on its own without bespoke founder involvement?
7. Is this best as consultancy leverage first, or can it become a repeatable licensed product?
8. Can the project receive enough focused attention to get through proof-of-value?

### Confidence
High

---

## 12. Best realistic product identity

### Claude
A narrow pre-CAD validation / compliance engine for UK electricity / OHL survey-to-design handoffs.

### ChatGPT
A deterministic, domain-specific workflow engine that captures one narrow repeated rules-heavy task better than spreadsheets/manual workarounds.

### Gemini
A broader compliance engine or submission platform, which is directionally useful but too expansive for current truth.

### Grok
A web-based pre-CAD QA / compliance gatekeeper or DNO Survey Compliance Gatekeeper.

### Final synthesis judgment
The best realistic product identity is:

**A narrow pre-CAD QA / compliance / submission-readiness tool for UK electricity survey-to-design handoffs, starting with one DNO, one input format, and one proof-of-value workflow.**

Short version:
**a DNO survey compliance gatekeeper**
or
**a pre-CAD submission-readiness validator**

### Confidence
High

---

## 13. Best commercial form

### Claude
Consultancy leverage first, licensed niche product second.

### ChatGPT
Internal operational tool or consultancy-led workflow accelerator first; licensed product only if repeatability and trusted rule ownership are proven.

### Gemini
More open to broader platform/commercial ambition, but still implicitly supports a staged path.

### Grok
Internal tool / consultancy leverage / narrow licensed product is strongly favoured over broad SaaS.

### Final synthesis judgment
The best commercial form is:

**Phase 1:** internal tool / consultancy-leverage tool
**Phase 2:** licensed niche product
**Phase 3:** broader software ambition only if repeatability, rule ownership, and demand are all proven

### Confidence
High

---

## 14. Best next move

### Claude
Have a real conversation with a design team / buyer and use that to test whether the narrow product is genuinely wanted.

### ChatGPT
Define and prove one benchmark workflow with a canonical evidence pack and measurable ROI.

### Gemini
Stabilise the baseline, keep the compliance workflow narrow, and align it to a commercially relevant market story.

### Grok
Recover the missing operational MVP flow immediately and prove upload → QA → map / report.

### Final synthesis judgment
The best next move is a **two-track action**:

1. **Complete the narrow MVP recovery** so the product can actually be shown and used end-to-end
2. **Immediately validate it with one real user / design team / buyer champion**

### Confidence
High

---

## 15. What to avoid entirely

### Claude
Avoid full engineering-platform ambition, multi-DNO expansion too early, AI-heavy additions, and broader workflow-suite scope before core recovery.

### ChatGPT
Avoid pretending broad readiness before canonical truth, benchmark proof-of-value, and repeatability exist.

### Gemini
Gemini is weaker here because it remains more open to broader compliance-platform expansion.

### Grok
Avoid CAD/GIS replacement, multi-tenant SaaS, AI design generation, and broad utility platform ambition.

### Final synthesis judgment
Avoid entirely, for now:
- broad platform ambition
- multi-DNO expansion too early
- CAD/GIS replacement aspirations
- enterprise workflow-suite thinking
- AI-first positioning
- heavy infrastructure overbuild before MVP proof
- feature creep driven by possibilities rather than real workflow demand

The key thing to avoid is:
**turning a strong narrow opportunity into a vague broad project.**

### Confidence
High

---

## 16. Final synthesis notes

### High-confidence conclusions
- SpanCore is strongest as a **narrow pre-CAD QA / compliance / submission-readiness tool**
- The codebase is **worth continuing from**
- The project is **not yet a working product**, but it is more than just an idea
- The best early commercial form is **internal / consultancy leverage first**
- Broad platform ambition would weaken the project at this stage
- Real proof-of-value depends on:
  - one workflow
  - one rule source
  - one buyer/user
  - one measurable result

### Medium-confidence conclusions
- The market gap is real but **only partly open**
- Technical success for a narrow MVP is likely, but broader product success is much less certain
- Licensed niche product potential exists, but only if repeatability and low-customisation deployment are proven
- The long-term moat is likely to depend more on:
  - workflow embedding
  - rule quality
  - data/process trust
  than on code alone

### Low-confidence / speculative areas
- Exact ARR / TAM / exit-size estimates
- Any claim that SpanCore could become a broad market standard
- Any claim that ESG / safety / environmental differentiation is already a major moat
- Any assumption that large DNO or contractor adoption would come quickly
- Any claim that the product is already close to enterprise readiness

### Claims rejected from the final synthesis
- That SpanCore should currently be treated as a broad SaaS or engineering platform
- That the market gap is completely open and uncontested
- That broad productisation is ready now
- That current roadmap ambition should be treated as current capability
- That the best next step is more broad feature work rather than narrow proof-of-value
