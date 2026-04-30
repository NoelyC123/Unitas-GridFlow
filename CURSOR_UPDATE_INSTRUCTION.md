# CURSOR FILE UPDATE COMMAND

Copy this ENTIRE message into Cursor (use Cmd+Shift+I for Composer mode):

---

## Task: Update Configuration Files with Softer Stage Boundary Language

Please update these 5 files to replace rigid "DO NOT" / "NEVER" language with nuanced guidance that allows discussion while maintaining focus.

### Files to Update:
1. `.cursorrules`
2. `CURSOR_BOOTSTRAP_COMMAND.md`
3. `CURSOR_COST_OPTIMIZATION.md`
4. `CURSOR_SETUP_GUIDE.md`
5. `CURSOR_SETUP_COMPLETE.md`

---

## Principles for Updates

### Replace This Pattern:
```
❌ DO NOT implement Stage 4
❌ NEVER build tablet capture
🚫 Must NOT create photo upload
Hard Rule: Never work on Stage 4
```

### With This Pattern:
```
Future stages requiring validation evidence:
- Stage 4: Structured field capture (tablet, photos, GPS)
- Stage 5: Designer workspace
- Stage 6: Production deployment

If Stage 3 work naturally touches these areas, pause and discuss the boundary.
```

---

## Specific Changes Needed

### 1. Section Title Changes

**Find and replace these section titles:**

- "What Should NOT Be Built Yet" → "Future Work Requiring Validation Evidence"
- "What NOT to Do" → "Avoid Without Discussion"
- "Hard Rules" → "Working Boundaries"
- "NEVER" (in headings) → "Requires Discussion"

### 2. Tone Changes

**Change command language to guidance:**

| Before | After |
|--------|-------|
| "Never implement" | "Requires evidence before implementation" |
| "Do NOT build" | "Not current priority" |
| "Must NOT work on" | "Future work needing validation" |
| "You are forbidden" | "Please pause and discuss" |
| "Absolutely prohibited" | "Needs discussion first" |

### 3. Add Allowances Section

**Add this to each file where stage boundaries are discussed:**

```
You're encouraged to:
- Discuss implications across all 6 stages
- Ask "what if" questions about future stages
- Think holistically about the roadmap
- Prepare current work for future integration
- Suggest connections between stages

Just pause before:
- Building complete future-stage features
- Implementing workflows without current operational need
- Expanding scope significantly without discussion
```

### 4. Stage Boundary Context

**Replace rigid stage lists with this framework:**

```
## Stage Context

**Current Active Work:** Stage 3 (operational refinement and practitioner-review remediation)

**Completed Stages:**
- Stage 1: Basic intake and QA
- Stage 2: Raw controller format support (2A/2B/2C complete)
- Stage 3: Multi-file projects, designer review, remote access (3A/3B/3C complete)

**Future Stages Requiring Evidence:**

**Stage 4 — Structured Field Capture**
- Tablet capture interface
- Photo upload and attachment
- Real-time GPS validation
- ArcGIS/Trimble integration
- Field evidence annotation

**Stage 5 — Designer Workspace**
- Design task management
- PoleCAD integration
- Collaborative review
- Version control

**Stage 6 — Production Deployment**
- Multi-tenant hosting
- User accounts and roles
- Cloud storage
- Production monitoring

**Boundary Guidance:**
If current Stage 3 work naturally extends into Stage 4/5/6 concepts:
1. Pause and discuss the boundary
2. Ask: "Does this solve a current Stage 3 operational need?"
3. If yes → discuss approach and implement narrowly
4. If no → document as future work and return to current priorities
```

### 5. Examples of Good Boundary Judgment

**Add practical examples to `.cursorrules`:**

```
## Boundary Judgment Examples

**Good examples (allowed):**
✅ Adding a photo-reference placeholder column to Stage 3 exports (prepares handoff, no implementation)
✅ Discussing how Stage 4 capture might integrate with current design chain (planning)
✅ Structuring Stage 3 data model to accommodate future photo attachments (architecture)
✅ Asking "Would this Stage 3 fix make Stage 4 harder?" (thinking ahead)

**Requires discussion (pause first):**
⚠️ Building a tablet photo-upload UI (Stage 4 feature, no current operational need)
⚠️ Implementing GPS validation gating (Stage 4 feature, needs real survey evidence)
⚠️ Creating user account system (Stage 6 feature, not needed yet)
⚠️ Redesigning entire data model for future stages (speculative architecture)

**Clear overreach (avoid):**
❌ Building complete Stage 4 tablet interface because "we might need it"
❌ Implementing all of Stage 5 designer workspace in advance
❌ Deploying to production hosting without operational validation
```

### 6. Update Cost Optimization Section

**In `CURSOR_COST_OPTIMIZATION.md`, soften the "What NOT to Do" section:**

**Before:**
```
❌ Don't ask Cursor to build Stage 4
❌ Don't implement features without approval
```

**After:**
```
## Work to Discuss First (Not Prohibit)

Before implementing future-stage features, pause and discuss:
- Does this solve a current Stage 3 operational need?
- Do we have evidence this approach works?
- Is this the narrowest solution to the current problem?

Examples:
- "Should we add tablet capture?" → Discuss: Is there a Stage 3 handoff need this solves?
- "Can we integrate with ArcGIS?" → Discuss: Do we have evidence of the target integration model?
- "Should we build user accounts?" → Discuss: Is there a current multi-user operational need?
```

### 7. Soften Bootstrap Command

**In `CURSOR_BOOTSTRAP_COMMAND.md`, update the working rules section:**

**Replace:**
```
❌ Don't implement Stage 4 without approval
❌ Don't expand scope
```

**With:**
```
## Working Boundaries (Not Prohibitions)

**Current focus:** Stage 3 operational refinement

**Future stages need evidence first:**
- Stage 4 (field capture)
- Stage 5 (designer workspace)
- Stage 6 (production deployment)

**When work touches future stages:**
1. Pause and discuss the boundary
2. Ask if it solves a current Stage 3 need
3. Implement narrowly if yes, document for later if no

**You're allowed to:**
- Discuss implications across all stages
- Think about future integration points
- Ask planning questions about later stages
- Prepare current work for future needs

**Just avoid:**
- Building complete future features speculatively
- Expanding scope without operational evidence
```

---

## Implementation Instructions for Cursor

**For each of the 5 files:**

1. Read the current version
2. Identify all instances of rigid prohibition language
3. Replace with nuanced guidance following the patterns above
4. Add the "allowances" and "boundary judgment" sections where appropriate
5. Keep the same file structure and overall content
6. Preserve all technical details and commands
7. Just soften the tone and add discussion allowances

**After updating all 5 files, show me:**
- List of files updated
- Summary of key changes made
- Confirm the tone is now "guidance with light guardrails" not "rigid rules"

---

## Example Before/After

**Before (`.cursorrules` excerpt):**
```
### Rule 5: Respect Project Boundaries
- Stage 3 is complete and working
- Stage 4 is future work only
- Do NOT implement Stage 4 features without explicit approval
- Do NOT assume more features are the right next step
```

**After (`.cursorrules` excerpt):**
```
### Guideline 5: Understand Project Phases
- Current focus: Stage 3 operational refinement
- Future stages (4/5/6) require validation evidence before implementation
- If work naturally touches future stages, pause and discuss the boundary
- Consider implications across stages, but implement narrowly for current needs
```

---

Please update all 5 files now, following these principles consistently.
