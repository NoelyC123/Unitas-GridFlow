# SpanCore – Quick Start
1) python3 -m venv .venv312 && source .venv312/bin/activate
2) pip install -r requirements.txt || pip install Flask gunicorn
3) cp -n .env.example .env
4) ./start.sh  → http://127.0.0.1:5010

## Docker
- `make docker-up` (MinIO, Postgres, app)
- `make gen-pass` then `docker compose --profile with-nginx up -d` for nginx on http://localhost

## Smoke
- `make smoke` calls presign and tries map data.
