#!/usr/bin/env bash
set -e
if [ -f ".venv312/bin/activate" ]; then source .venv312/bin/activate; fi
export FLASK_ENV=${FLASK_ENV:-development}
python run.py
