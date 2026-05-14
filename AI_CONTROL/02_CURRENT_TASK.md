# Current Active Phase

Stage 5 Validation - Real Job Review

## Active Priority

Validate the completed Stage 5 pilot pack against available real jobs before starting broad new feature implementation.

Stage 4C is complete, and Stage 5A/5B/5C pilot-pack surfaces are active:

- enhanced reports,
- review workspace,
- pole detail pages,
- helpful workspace error pages,
- preview map overlay,
- overlay JSON endpoint.

The current priority is to prove the package on real job data, document findings, and identify the smallest set of fixes needed before any Stage 6 work.

## Validation Targets

Use available local data only. Discover paths rather than assuming exact locations.

Candidate targets:

- P_LOCAL_001,
- P010,
- P011,
- Gordon,
- Bellsprings.

Useful path-discovery commands:

```bash
find real_pilot_data uploads validation_data -maxdepth 4 -type f \( -name "*.csv" -o -name "*.json" -o -name "*.md" \) 2>/dev/null | sort
find real_pilot_data uploads validation_data -maxdepth 5 -type d \( -name "enwl_enrichment_clean" -o -name "pipeline_run_*" -o -name "photos_final" \) 2>/dev/null | sort
find uploads/jobs uploads/projects -maxdepth 4 -type f \( -name "*.csv" -o -name "04_merged_dataset.json" -o -name "pipeline_summary.json" \) 2>/dev/null | sort
```

Do not commit real job data, photos, local uploads, or validation outputs unless explicitly approved and anonymised.

## Per-Job Checklist

For each usable job or survey pack, record:

- baseline source found,
- field evidence source found,
- whether `scripts/run_pipeline.py` can run,
- whether reports `00`, `05`, `06`, `07`, `08`, `09`, and `10` are generated,
- whether `/workspace/view/<job_id>` loads,
- whether `/workspace/pole/<job_id>/<support_number>` loads for at least one pole,
- whether `/map/overlay/<job_id>` loads as a preview/review overlay,
- whether overlay JSON returns usable baseline-field comparison data,
- match rate,
- evidence quality distribution,
- design-ready/design-blocked counts,
- verification flag counts,
- missing file/path issues,
- data quality issues,
- wording or usability issues,
- recommended fix category: data issue, pipeline issue, report issue, workspace issue, overlay issue, or documentation issue.

## Required Output

Create:

- `AI_CONTROL/111_STAGE5_VALIDATION_FINDINGS.md`

The findings document should include:

- jobs checked,
- paths discovered,
- commands run,
- generated outputs,
- pass/fail/partial result per job,
- report quality observations,
- workspace observations,
- map overlay observations,
- data blockers,
- recommended fixes,
- whether validation is sufficient to proceed to targeted hardening,
- whether any Stage 6 planning is justified.

## Active Boundaries

Do not implement new features until `AI_CONTROL/111_STAGE5_VALIDATION_FINDINGS.md` exists.

Do not claim:

- final engineering design capability,
- DNO data replacement,
- autonomous design authorization,
- production multi-user deployment,
- PoleCAD export,
- DNO-grade compliance verification,
- full GIS product capability.

Do preserve:

- evidence-based claims,
- source authority hierarchy,
- verification flags,
- design blocker visibility,
- real-job validation notes,
- local-data privacy boundaries.

## Acceptance Direction

Stage 5 validation should answer:

- Which real jobs can run through the current pipeline?
- Which reports are useful without manual interpretation?
- Which workspace and overlay routes are reliable enough for pilot review?
- Which blockers are due to missing DNO data rather than pipeline failure?
- What must be fixed before an ICP/Tier-1 pilot review?
