# Known Issues

## Meilisearch `_ensure_index` swallows 4xx silently

**File**: `services/search.py:88-96`
**Impact**: Low. The index-creation call fires every upsert and silently ignores "already exists" (4xx). After the first upsert the call is a no-op that returns 204, so no practical harm. Fix would be to check `resp.status_code == 409` explicitly.

## `admin_content.py:create_site` lacks idempotency

**File**: `routers/admin_content.py:38-63`
**Impact**: Low. `POST /api/admin/content/sites` returns 409 when a slug already exists. An idempotent variant (upsert) would be cleaner but only admin tooling hits this endpoint.

## Integration smoke tests not run in CI

**File**: `tests/test_smoke_integration.py`
**Impact**: Low. Tests are `@pytest.mark.integration` and require a running backend on `localhost:8000`. CI has no docker stack, so tagging prevents accidental failure. Manual or compose-based runs pick them up.

## RabbitMQ password in docker-compose.yml

**File**: `docker-compose.yml`
**Impact**: Low. The compose file uses `amqp://guest:guest@rabbitmq:5672/` — the RabbitMQ default credentials. This is a dev convenience and should be overridden for staging/production via `RABBITMQ_URL` env var.

## `REDIS_URL` / `MEILI_MASTER_KEY` / `MINIO_ROOT_PASSWORD` hardcoded in compose

**Impact**: Medium in production context. These are dev defaults (`minioadmin`, `masterKey`, `affiloom`). Override via environment variables or `.env` when deploying outside local compose. The CI pipeline does not start these services — tests use the in-memory fallback.