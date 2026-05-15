# GridFlow — Long-Term Vision and Roadmap

**Date created:** 2026-05-14
**Status:** Strategic planning document
**Author:** Noel Collins (Unitas / GridFlow)
**Purpose:** Capture the full long-term vision for GridFlow so future work starts from clarity, not memory.

---

## 1. The Full Vision

GridFlow is to become a complete survey-to-design evidence and analysis tool for UK electricity network overhead line work.

The user has stated the full vision is:

1. **Field survey evidence** — captured by the user on iPad, GPS, photos, condition notes, field observations
2. **DNO baseline records** — pulled from ENWL Network Asset Viewer per pole (FID, pole_type, pole_class, support_diameter, support_no, spn, orientation)
3. **DNO network trace evidence** — pulled as GeoJSON from the ENWL Network Asset Viewer (conductor material, cable size, rated current, summer/winter ratings, cable length, voltage, FID references, network geometry, transformer/switch context)
4. **Survey analysis tool** — that makes survey data design-ready as much as possible by combining all three evidence sources against design requirements
5. **Eventually a design tool** — performing or significantly assisting with the work that PoleCAD and AutoCAD do today

All five points are valid and captured here. They are staged so each part gets the engineering rigour appropriate to its risk profile.

---

## 2. The Three Layers of the Vision

### Layer 1 — Evidence Engine (Stage 6, Foundation)

GridFlow as a three-source evidence comparison tool. All three sources reconciled against each other, with clear provenance, conflict detection, and gap identification. This is the immediate next stage.

### Layer 2 — Design-Readiness Analysis (Stages 7-8, Maturation)

GridFlow analyses the combined evidence and produces:

- design-readiness judgements per pole (ready / blocked / conditional)
- conflict reports between sources
- DNO data request outputs for what remains unknown
- verification checklists for designer review
- span and route analysis
- evidence-quality scoring
- audit-ready provenance records

### Layer 3 — Design Production (Stages 9-10+, Long-term Ambition)

GridFlow eventually produces design-ready outputs that feed PoleCAD/AutoCAD directly, or in selected cases performs simpler design calculations itself:

- pre-populated PoleCAD input files
- pre-calculated span geometries
- pre-flagged clearance issues
- standardised drawing inputs
- selected native calculations (where safe and certifiable)

This layer requires extensive engineering review, professional sign-off considerations, and validation against published standards (ENA G7/4, ESQCR, ENA TS 43-8, etc.).

---

## 3. Where GridFlow Is Today

**Stage 5 Complete (1368 tests passing, tagged stage5-complete):**

- Pipeline ingests baseline CSV + field survey folder
- 11 pilot reports generated (00, 05-10)
- Review workspace with filtering and pole detail views
- Dual-layer map overlay (baseline vs field)
- Pipeline output registration to web routes (Stage 5E)
- Truthfulness hardening (Stage 5F: 114 review confirmed 0/10 design-ready is correct behaviour for current data sources)
- Designer review kit with one-pager, script, live feedback form, preflight check (Stage 5G)

**Stage 5F Key Finding:**

P_LOCAL_001 returning 0/10 design-ready is correct because conductor specification and pole class/strength rating require authoritative DNO engineering records that field survey alone does not provide. This is not a bug. It is GridFlow correctly identifying the design-readiness gap.

**The Discovery That Changed Everything (End of Stage 5):**

The ENWL Network Asset Viewer is a publicly accessible DNO tool that provides exactly the missing authoritative engineering records:

- Per-pole DNO records (FID, pole_type, pole_class, support_diameter, support_no, spn)
- Network trace evidence with conductor specifications and ratings (115A, 190A, 284A observed)
- Full network geometry and topology in GeoJSON format

This means GridFlow's "missing DNO records" problem is not unsolvable. The records are publicly available, the user knows how to access them, and they can be captured per pole or per trace.

---

## 4. The Strategic Implications

The ENWL discovery is not a feature idea. It is a product strategy shift.

**Before:** GridFlow is a one-sided tool that processes field survey data and identifies what is missing. Useful but limited.

**After:** GridFlow is a three-source evidence comparison engine. It compares field survey, DNO baseline records, and DNO network trace evidence against design-readiness requirements. The evidence is complete, the conflicts are visible, and design judgements are provable.

The user advantage:

- **Domain expertise** — knowing the ENWL Network Asset Viewer exists, knowing how FIDs work, knowing what is authoritative vs indicative, years of OHL surveying and design experience
- **Field capability** — can perform real surveys at any pole on demand with iPad
- **DNO access** — can capture authoritative DNO records for any pole at any time
- **Design knowledge** — understands what design-ready actually means in practice

This combination is the real competitive moat. The code is delivery. The knowledge is the product.

---

## 5. The Realistic Long-Term Arc

Each stage assumes the previous one has been validated through real use on a real Unitas job, not just built.

### Stage 6 — ENWL Evidence Integration (Next: 2-4 months)

The three-source evidence engine. The thing the user described as points 1-3 of the vision.

**Stage 6A — Capture and Store (1-2 weeks)**
- Parse ENWL trace GeoJSON exports
- Store as first-class evidence artifacts on registered jobs
- Display trace evidence in workspace pole detail page
- Add trace evidence links to Report 00
- Do NOT change `design_ready` logic yet

**Stage 6B — Per-Pole DNO Record Capture (1-2 weeks)**
- Support capture of per-pole ENWL Network Asset Viewer records
- Store as second-class evidence (alongside trace)
- Surface in workspace alongside field survey data
- Three-source view per pole in workspace

**Stage 6C — FID-to-Pole Linking (2-3 weeks)**
- Geometry-based matching (trace point coords near surveyed pole coords)
- Support number matching where available
- Manual confirmation workflow ("yes, FID X is pole Y")
- Confirmed-link evidence storage with audit trail

**Stage 6D — Three-Source Conflict Detection (2-3 weeks)**
- Compare field survey vs DNO baseline per pole
- Compare field survey vs DNO trace per span/circuit
- Compare DNO baseline vs DNO trace for internal consistency
- Conflict reports with severity and recommended action

**Stage 6E — Updated Design-Readiness Logic (1-2 weeks)**
- Design-ready logic uses three sources, not one
- Blocker reasons become specific (not just "missing data")
- Report 06 (DNO request) becomes smaller as more data is captured
- Report 07 (design readiness) becomes more actionable

**Stage 6 Outcome:** GridFlow is a genuinely useful evidence comparison tool. Real OHL jobs can be processed end-to-end with all three sources. Design-readiness judgements are based on actual evidence, not absence of evidence.

### Stage 7 — Workspace and Reporting Maturation (3-6 months)

This is point 4 of the vision starting to take shape. Survey analysis becomes more sophisticated.

- Photo and evidence integration in workspace
- Pole detail page becomes comprehensive evidence dashboard
- Cross-source provenance visualisation
- Report wording improvements based on real use
- Export formats for downstream tools
- Multi-job comparative views
- Search and filter across the full evidence set

### Stage 8 — Design-Readiness Analytics (6-9 months)

The fuller expression of point 4. GridFlow analyses everything it has and produces design preparation outputs.

- Span analysis (length, sag implications candidates, clearance candidates)
- Route analysis (continuity, gaps, anomalies)
- Equipment context analysis (transformer placement, switch logic)
- Pre-design preparation outputs
- Designer verification checklists
- "Ready to start PoleCAD" outputs

This is everything UP TO the point where a designer opens PoleCAD. GridFlow does not design. It makes design preparation comprehensive, fast, and audit-ready.

### Stage 9 — Design Assistance (9-15 months)

The beginning of point 5 of the vision. GridFlow produces inputs that feed directly into PoleCAD/AutoCAD.

- PoleCAD-ready input file generation
- Pre-calculated span geometries (3D distances, elevation profiles)
- Pre-flagged clearance issues (statutory clearance candidates identified)
- Pre-flagged stay requirements (angle pole analysis)
- Pre-flagged conductor capacity issues (rating vs load checks)
- Standardised CAD input formats (DXF, DWG inputs)

GridFlow becomes the designer's setup tool. The designer still uses PoleCAD/AutoCAD for the actual engineering, but their setup time drops dramatically.

### Stage 10+ — Native Design Calculations (Year 2+)

This is the final expression of point 5 of the vision, the part that requires real care. Native engineering calculations carry liability and may require professional certification.

**Safer starting points (Stage 10A):**
- Span distance calculations (already partially done)
- Basic clearance checks (vegetation, road, structure)
- Angle pole identification and stay placement logic
- Conductor route optimisation suggestions
- Foundation type recommendations

**Higher-risk calculations (Stage 10B, only after extensive validation):**
- Conductor sag and tension under varying conditions
- Pole strength verification against wind and ice loading
- Statutory clearance enforcement to G7/4 specifics
- Stay angle and tension calculations

These should only be built with:

- Professional engineering review (PE/CEng involvement)
- Validation against published reference calculations
- Comparison testing against established tools (PoleCAD reference cases)
- Clear scope boundaries on what GridFlow will and will not calculate
- Liability and indemnity considerations
- Possible third-party engineering certification

This stage may end up being "GridFlow integrates with a certified calculation engine" rather than "GridFlow does the certified calculations natively." Both are viable. The decision should be evidence-based at the time, not pre-committed.

---

## 6. What Makes This Realistic

Several things are working in this vision's favour:

1. **The data is publicly available.** ENWL publishes the trace tool. The user has access. No DNO partnership negotiation required.

2. **The user is the domain expert.** No need to hire OHL designers to validate assumptions. The user has done OHL surveying, planning, and design work for years.

3. **The user is the field operator.** No need to schedule field surveyors. The user has the iPad and can survey on demand.

4. **The user is the customer.** No need to find product-market fit externally first. The user is delivering real OHL work at Unitas and can use GridFlow on real jobs immediately.

5. **The codebase is already strong.** 1368 tests, clean architecture, good separation of concerns, working web/CLI/registration chain. Foundation is sound.

6. **Stage 5 is genuinely complete.** Not "complete-ish." Seven sub-stages, properly tested, tagged.

What is working against the vision:

1. **Scope ambition.** Five layers of work, each substantial.

2. **Solo development.** The user is one person. Even with AI assistance, calendar time is real.

3. **Stage 10 liability profile.** Native design calculations bring engineering liability questions that pure software does not.

4. **Market size if commercial.** UK OHL design is specialist. Even at full scale this is not a mass-market SaaS company.

5. **Validation discipline.** Each stage needs real use before the next stage begins. Resisting the urge to build ahead is harder than it sounds.

---

## 7. The North Star

When in doubt about whether to build something, ask:

> "Does this make the next real Unitas job easier and more correct?"

If yes, build it.
If no, defer it.
If unsure, do the next real Unitas job first and see what was actually missing.

---

## 8. Decisions Deferred

These should not be decided now. Decide them when the relevant stage approaches:

- Whether GridFlow becomes commercial (Stage 7-8 decision)
- Whether to seek engineering certification for design calculations (Stage 10 decision)
- Whether to partner with established calculation engines vs build native (Stage 10 decision)
- Whether to expand beyond ENWL to other DNOs (after Stage 6 proven)
- Whether to add mobile/tablet capture as a GridFlow feature vs continue using existing iPad tools (after Stage 7)
- Whether to seek investment or remain bootstrapped (Stage 8-9 decision)

---

## 9. Risks to Watch

**Scope creep within stages.**
Each stage has sub-stages. Discipline is needed to ship one before starting the next. Each sub-stage should merge cleanly before the next begins.

**Premature design calculation work.**
The temptation to "add a sag calculation while we're here" will be real. Resist it. Design calculations belong in Stage 10 with proper engineering review.

**Building ahead of validation.**
Each stage needs real use on real jobs before the next begins. Not building ahead is harder than building.

**Wording discipline.**
GridFlow should not claim it does design until it actually does. "Design preparation tool" through Stage 8. "Design assistance tool" through Stage 9. "Design tool" only when Stage 10 is actually proven and reviewed.

**Liability awareness.**
Once GridFlow influences real design decisions on real jobs, the question of professional indemnity becomes real. Should be flagged before Stage 8, addressed before Stage 9, resolved before Stage 10.

**Solo developer pacing.**
The full arc is 12-24 months of focused work. Pacing matters. Real stops between stages matter.

---

## 10. Success Criteria

The vision is on track if at each stage:

- The work merges cleanly with tests passing
- The user uses it on a real Unitas job within two weeks of completion
- Findings from real use inform the next stage's scope
- No stage is started before the previous one is validated through real use

The vision is off track if:

- Stages are built ahead of validation
- Scope creeps within stages
- Real use never happens between stages
- Test count grows but real-job use stalls
- The user starts feeling pressure to commercialise before the product is ready

---

**This document is the long-term reference. It does not change with each sprint. It is updated only when the strategic picture changes — for example, if a major new data source becomes available, or if a stage is fundamentally redefined by validation findings.**

**For current-sprint detail, see `AI_CONTROL/02_CURRENT_TASK.md`.**
**For current-state detail, see `AI_CONTROL/01_CURRENT_STATE.md`.**
**For where to start tomorrow, see `119_TOMORROW_MORNING_START_HERE.md`.**
