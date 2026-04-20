# Unitas GridFlow

**Pre-CAD QA, compliance, and workflow automation for UK electricity network survey-to-design handoffs.**

---

## Overview

Unitas GridFlow is a focused workflow tool for validating survey inputs before CAD/design handoff.

Its current role is:

- ingest survey CSV data
- normalize the input into a working internal schema
- run QA checks
- generate issue outputs
- render mapped results
- generate a PDF QA report
- retain job outputs locally for review

Short version:

**a DNO survey compliance gatekeeper**

---

## Current MVP Status

The project now has a **working local MVP**.

### Current working flow

**upload CSV -> save file -> run QA -> save outputs -> view map -> download PDF -> browse jobs**

### Confirmed working parts

- upload page
- upload/presign flow
- CSV save to job folder
- intake/finalize route
- QA processing
- `issues.csv` generation
- `map_data.json` generation
- PDF QA report route
- jobs listing page
- representative sample input schema
- initial pytest coverage
- GitHub Actions CI for `pre-commit` and `pytest`

### Current limitations

- QA rules are still basic / placeholder-level
- issue modelling is still lightweight
- browser E2E coverage is not yet in place
- current output model is still MVP-level, not production-grade
- current branding has only partly been updated from legacy naming

---

## Quick Start

### Create and activate the virtual environment

```bash
python3.13 -m venv .venv312
source .venv312/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
python -m pip install pre-commit ruff pytest
