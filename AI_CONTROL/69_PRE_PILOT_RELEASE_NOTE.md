# Pre-Pilot Release Note

**For:** Noel
**Date:** 2026-05-10
**Subject:** What's Ready for Field Pilot Execution; What's Blocked

---

## What Is Ready ✅

### Structured Capture System (Stage 4A–4B)

- **Template:** `templates/structured_capture_template.csv` (36 optional fields for pole attributes)
- **Field Reference:** `app/structured_capture_field_reference.py` — complete catalogue of all pole_id fields and optional fields with validation metadata
- **Validators:** `app/structured_capture_validators.py` — 40+ pure validation functions; no side effects
- **CLI:** `python scripts/validate_stage4_pilot.py <CSV> <evidence_folder>` — validates your captured CSV + evidence photos
- **Output:** Terminal summary + JSON report + Markdown report (all saved to real_pilot_results/)
- **Documentation:** Documents 53–55 (result template, system outputs, evidence protocol)
- **Evidence Fixtures:** tests/fixtures/stage4/evidence/ (clean, problematic, invalid samples for reference)
- **Golden Samples:** tests/fixtures/stage4/ (valid, invalid, duplicates, minimal, legacy-header examples)

### Dictionaries & Reference Materials

- **DNO Rulepack:** Inferred from GPS coordinates; correct UK region automatically detected
- **Structured Capture Spec:** Document 51 (full field definitions, required/optional, data types, validation rules)
- **Field Evidence Protocol:** Document 54 (filename conventions, checksums, folder structure for photos)
- **Evidence Checklist:** Ready for use; 5 evidence types supported (clear, obscured, proxy, inferred, none)

### Git Protection

- **Local Data Ignored:** `real_pilot_data/` and `real_pilot_results/` are git-ignored by default
- **No Accidental Commits:** Raw captured CSV and validation outputs will not be committed to the repo
- **Safe for real data:** You can work with your real pilot CSV and evidence without risk of pushing data upstream

---

## What Is NOT Ready ❌

### Stage 4C Runtime Integration

- **Data upload:** No HTTP intake route for Stage 4 data yet. You cannot POST captured data to the app; you can only validate locally using the CLI.
- **Popup surfacing:** Stage 4 fields are not displayed in the C2E2 popup interface yet. That's Stage 4D (blocked).
- **Map integration:** Stage 4 data is not visible on the map yet. That's Stage 4E (blocked).
- **Design Chain export:** Stage 4 data is not exported in the Design Chain format yet. That's Stage 4F (blocked).

**Stage 4C remains blocked until after you record your field pilot decision and approve Stage 4C implementation.**

---

## How to Run Pilot Validation

```bash
# 1. Prepare your files:
# - Your captured CSV in real_pilot_data/your_survey.csv
# - Your evidence photos in real_pilot_data/evidence/ with subdirectories:
#   - evidence/clear/, evidence/obscured/, evidence/proxy/, evidence/inferred/, evidence/none/

# 2. Run the validation CLI:
python scripts/validate_stage4_pilot.py real_pilot_data/your_survey.csv real_pilot_data/evidence/

# 3. Review output:
# - Terminal: Summary of validation results
# - JSON: real_pilot_results/your_survey_validation.json (machine-readable)
# - Markdown: real_pilot_results/your_survey_validation.md (human-readable report)
```

---

## How to Record Field Pilot Result

After running validation, use **Document 65** (Stage 4C Decision Board Template) to record:

1. **Pilot Summary:** Date, survey, capture count, time on-site
2. **Validation Stats:** Rows, validation%, pole_id match%, merge-ready%
3. **Evidence Stats:** Photo count, evidence type distribution, missing/invalid filenames
4. **Defects:** Any issues found (template confusion, duplicate pole_ids, missing photos, etc.)
5. **Risks:** How pre-pilot controls worked; any surprises
6. **Recommendation:** GO, GO WITH CAUTIONS, or NO-GO
7. **Sign-off:** Your decision + date

This decision form is **required before Stage 4C development starts.**

---

## Critical Note: Decision-Gate Framework

Documents that define the formal decision gates for Stage 4C (checklist, metrics, risk controls, decision template) exist on unmerged branches:

- **Documents 61–65** are on branches `claude-code/stage4c-architecture-v2` and `claude-code/real-field-pilot-readiness-stage4c-gate-audit` (not yet merged to master).
- You can access them now using: `git checkout claude-code/real-field-pilot-readiness-stage4c-gate-audit` and review in `AI_CONTROL/`.
- **Before your final go/no-go decision, ensure you've reviewed all 5 decision documents** (61–65) to understand the success metrics and decision criteria.

**These are important governance docs; please review them in detail.**

---

## Pre-Field Checklist

Before you leave for the field:

- [ ] Template reviewed and printed/loaded on device
- [ ] Evidence folder structure ready (clear/, obscured/, proxy/, inferred/, none/ subdirectories)
- [ ] Validation CLI tested locally (ran `python scripts/validate_stage4_pilot.py --help`)
- [ ] Golden samples reviewed to understand valid/invalid CSV formats
- [ ] Field day checklist (doc 62) printed or available on device
- [ ] Success metrics (doc 63) understood; thresholds noted
- [ ] Decision template (doc 65) available for post-pilot recording
- [ ] Internet/connectivity plan ready for running CLI and sharing results

---

## FAQ

**Q: Can I upload data to the app during or after the field trial?**
A: No. Stage 4C intake route is not yet implemented. Use the CLI only.

**Q: Can I see Stage 4 fields on the map?**
A: No. Stage 4D (map integration) is blocked. After you approve Stage 4C, that work begins.

**Q: What if the pilot fails (metrics not met)?**
A: Review the defects, determine if they're fixable, and plan a remediation iteration. Do not merge decision-gate docs or start Stage 4C implementation until metrics pass.

**Q: Where do I store evidence photos?**
A: In `real_pilot_data/evidence/` with subfolders: `clear/`, `obscured/`, `proxy/`, `inferred/`, `none/`. Filenames must follow protocol (document 54).

**Q: What happens to my CSV and evidence after validation?**
A: They stay in `real_pilot_data/` and `real_pilot_results/` on your machine. They are git-ignored; they will not be committed to the repo.

---

## Support

- **Template questions:** See document 51 (Structured Capture Specification)
- **Validation errors:** See validate_stage4_pilot.py output; error messages reference field names and validation rules
- **Evidence protocol:** See document 54 (Structured Capture Evidence Protocol)
- **Success criteria:** See document 63 (Field Pilot Success Metrics)
- **Decision process:** See document 65 (Stage 4C Decision Board Template)

---

## Next Steps

1. **Now:** Review this release note and the decision-gate framework (docs 61–65)
2. **Before field day:** Run through the pre-field checklist above
3. **During field day:** Capture poles using the template and evidence protocol
4. **After field day:** Run validation CLI and review results
5. **Final decision:** Complete decision board template (doc 65) with your go/no-go verdict

---

**Noel, you are ready to conduct the field pilot. Good luck. 🎯**

For detailed governance and technical docs, see:
- Document 66 — Pre-Pilot Cleanroom Audit (repository state)
- Document 68 — Field Trial Release Readiness Verdict (formal GO verdict)
- Documents 61–65 — Decision-Gate Framework (field day guide, metrics, risk controls, decision template)
