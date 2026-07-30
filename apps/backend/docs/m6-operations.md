# M6: Audit, Observability & Admin Operations

## Overview

M6 adds the operational surface needed to run Affiloom in production:
structured logging, dependency health checks, application metrics, an admin
dashboard, a daily audit job, and retry/dead-letter-safe worker patterns.

## Endpoints

### Health & Readiness

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/health` | GET | none | Liveness probe. Always 200 while process is up. |
| `/ready` | GET | none | Readiness probe. 200 when all *required* deps healthy; 503 otherwise. |
| `/deps` | GET | none | Per-dependency detail: name, healthy, latency, error, required. |
| `/metrics` | GET | none | Application metrics: product/sync/content counts. |

**Required dependencies** (failure = not ready):
- `database` — PostgreSQL must answer `SELECT 1`.

**Optional dependencies** (failure = degraded but ready):
- `redis` — checked only when `REDIS_ENABLED=true`.
- `search` — Meilisearch checked only when `MEILI_ENABLED=true`.

### Admin Dashboard

All admin endpoints require `Authorization: Bearer <ADMIN_API_TOKEN>`.

| Endpoint | Method | Description |
|---|---|---|
| `/api/admin/dashboard/summary` | GET | Aggregate stats: products, sync health, content counts. |
| `/api/admin/audit` | GET | Run the daily audit on demand; returns actionable findings. |
| `/api/admin/sync/{merchant}` | POST | Trigger a sync run. |
| `/api/admin/sync/runs` | GET | Paginated sync run history. |
| `/api/admin/sync/runs/{run_id}` | GET | Sync run detail. |

## Daily Audit

### What it checks

1. **Sync health**
   - Failed syncs in the last 24h (CRITICAL)
   - Active merchants with no successful sync (WARNING)
   - Merchants last synced >7 days ago (WARNING)
   - Sync runs stuck in PENDING/RUNNING for >1h (CRITICAL, dead-letter)

2. **Data quality**
   - Active products missing category (WARNING)
   - Active products missing description (INFO)
   - Active offers missing price (WARNING)
   - Active products with no active offers / orphaned (WARNING)

3. **Content gaps**
   - Published articles missing excerpt (INFO)
   - Published articles missing meta_description (WARNING)
   - Published articles with no product links (INFO)

### Running the audit

```bash
# One-shot (exits 0 if no critical findings, 1 otherwise)
python -m workers.audit_worker

# Daily loop
python -m workers.audit_worker --interval 86400

# Via API (requires admin token)
curl -H "Authorization: Bearer $ADMIN_API_TOKEN" \
  http://localhost:8000/api/admin/audit
```

### Finding format

```json
{
  "severity": "critical",
  "category": "sync.dead_letter",
  "message": "Sync run abc-123 stuck in running for >1h",
  "remediation": "Inspect worker process; check Redis lock ownership; restart worker if needed.",
  "context": {
    "run_id": "abc-123",
    "merchant_id": "...",
    "status": "running",
    "started_at": "2026-07-30T..."
  }
}
```

Each finding includes a `remediation` hint so the operator knows the next step.

## Structured Logging

All logs are single-line JSON objects with `ts`, `svc`, `level`, `msg`, plus
any contextual fields passed via `extra=`.

```python
from services.logging import get_logger

log = get_logger(__name__)
log.info("sync: started", extra={"merchant": "demo", "run_id": "..."})
```

```json
{"ts":"2026-07-30T...","svc":"services.sync","level":"INFO","msg":"sync: started","merchant":"demo","run_id":"..."}
```

Workers automatically call `setup_logging()` at startup.

## Sync Worker Retry & Dead-Letter Safety

The sync worker supports retry with exponential backoff and per-attempt timeout:

```bash
python -m workers.sync_worker \
  --interval 300 \
  --max-retries 3 \
  --retry-delay 10 \
  --run-timeout 120
```

| Flag | Default | Description |
|---|---|---|
| `--interval` | 0 | Seconds between runs; 0 = one-shot. |
| `--max-retries` | 3 | Max attempts before giving up. |
| `--retry-delay` | 10 | Base backoff seconds; doubles each attempt. |
| `--run-timeout` | none | Max wall-clock seconds per attempt. |
| `--log-level` | INFO | Log verbosity. |

**Dead-letter safety:**
- No uncaught exceptions escape to the scheduler.
- Failed runs are recorded with `status=FAILED` in the DB, visible in the
  dashboard and surfaced by the audit job.
- The Redis lock (when enabled) prevents concurrent runs for the same merchant.
- Skipped runs (lock held by another worker) are not retried.

## Docker Compose

The `sync-worker` service in `docker-compose.yml` runs the sync worker. To
add the audit worker as a daily job, add a service:

```yaml
audit-worker:
  build:
    context: ./apps/backend
    dockerfile: Dockerfile
  restart: unless-stopped
  command: ["python", "-m", "workers.audit_worker", "--interval", "86400"]
  environment: *backend_env
  depends_on:
    - postgres
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ADMIN_API_TOKEN` | (empty) | Bearer token for admin endpoints. Required. |
| `REDIS_ENABLED` | false | Enable Redis lock + health probe. |
| `MEILI_ENABLED` | false | Enable Meilisearch indexing + health probe. |
| `RABBITMQ_ENABLED` | false | Enable event publishing. |

When `ADMIN_API_TOKEN` is unset, all admin endpoints return 503 (fail closed).