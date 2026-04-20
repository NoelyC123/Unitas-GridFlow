# Unitas GridFlow — Quick Start

1. `python3.13 -m venv .venv312 && source .venv312/bin/activate`
2. `pip install -r requirements.txt`
3. `cp -n .env.example .env`
4. `python run.py` → http://127.0.0.1:5001

## Run tests
```bash
pytest -v
```

## Docker (optional)
- `make docker-up` — starts MinIO, Postgres, app
- `make gen-pass` then `docker compose --profile with-nginx up -d` for nginx on http://localhost

## Smoke test
```bash
make smoke
```

## Current MVP flow
upload CSV → run QA → view map → download PDF → browse jobs
