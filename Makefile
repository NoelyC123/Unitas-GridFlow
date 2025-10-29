APP?=http://127.0.0.1:5010

.PHONY: docker-up docker-down gen-pass smoke smoke-map

docker-up:
\t@docker compose up -d --build

docker-down:
\t@docker compose down -v

gen-pass:
\t@./docker/frontend/generate-htpasswd.sh

smoke:
\t@echo "Presign -> PUT -> Finalize -> Map data"
\t@curl -fsS $(APP)/health/full >/dev/null || echo "warn: /health/full not present"
\t@curl -fsS -X POST $(APP)/api/presign \
\t  -H 'Content-Type: application/json' \
\t  -d '{"key":"uploads/J999/test.csv","size":128,"content_type":"text/csv","multipart":false}' | jq '.upload_type' || true
\t@curl -fsS $(APP)/map/data/J1 | jq '.type,.metadata' || true

smoke-map:
\t@JOB?=J1; curl -fsS $(APP)/map/data/$$JOB | jq '.type,.metadata' || true
