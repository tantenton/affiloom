# Affiloom
Autonomous Indonesian affiliate platform — deterministic vertical slice through M4.

## Services
- Next.js App Router frontend: homepage, `/produk` catalog, `/produk/[id]` detail (Indonesian, SEO metadata + Product JSON-LD, affiliate disclosure).
- FastAPI backend: `/health`, `/ready`, `/api/products`, `/api/products/{id}`, `/api/admin/sync/*` — read layer served by the deterministic demo adapter; admin surface writes into Postgres via the sync service.
- Sync worker (`python -m workers.sync_worker`) — one-shot or `--interval SECONDS` loop; reuses the same sync service the admin endpoint calls.
- PostgreSQL / Redis / RabbitMQ / Meilisearch / MinIO via Docker Compose.

## Compliance guardrails
- Marketplace access is read-only through the demo adapter today. Real partner adapters must call **official partner APIs only** (Shopee Affiliate API, Tokopedia Affiliate API, etc.). No scraping, no reverse-engineered private endpoints, no automated browsing.
- Every page that surfaces affiliate deep-links renders a visible disclosure and marks outbound links `rel="sponsored nofollow noopener noreferrer"`.
- The sync service does not fabricate live-marketplace data — it upserts what the adapter returns and marks missing rows inactive.

## Quick start
```bash
cp .env.example .env
docker compose up -d postgres redis rabbitmq meilisearch minio
pnpm install
pnpm --filter frontend build
pnpm --filter frontend dev   # http://localhost:3000
```

Backend (Python + uv):
```bash
cd apps/backend
uv sync --frozen
uv run alembic upgrade head             # apply migrations (Postgres or SQLite)
uv run uvicorn main:app --reload        # http://localhost:8000
```

Trigger a sync manually (admin token required, see `.env.example`):
```bash
curl -X POST -H "Authorization: Bearer $ADMIN_API_TOKEN" \
     http://localhost:8000/api/admin/sync/demo
```

Or run the worker CLI:
```bash
cd apps/backend
uv run python -m workers.sync_worker              # one pass
uv run python -m workers.sync_worker --interval 300   # loop every 5 min
```

Full docker stack (frontend + backend + sync-worker + infra):
```bash
docker compose up --build
```

## API surface (M4)
Public read layer:
- `GET /health`
- `GET /ready`
- `GET /api/products?q=<query>&limit=<1..100>&offset=<n>` — paginated envelope: `{items, total, limit, offset, query}`.
- `GET /api/products/{id}` — 404 with `{"detail": "Product not found"}` when the id is unknown.

Admin surface (requires `Authorization: Bearer <ADMIN_API_TOKEN>`; returns 503 if the token is unset):
- `POST /api/admin/sync/{merchant}` — triggers an idempotent sync run.
- `GET  /api/admin/sync/runs?limit=&offset=` — paginated run history.
- `GET  /api/admin/sync/runs/{run_id}` — single run detail.

Frontend routes:
- `/` — landing page + code of conduct.
- `/produk` — searchable catalog grid (server-rendered, `q` query param).
- `/produk/[id]` — product detail with Indonesian rupiah pricing, Product schema (JSON-LD), and disclosed affiliate CTA.

## Data model (M4)
- `merchants` — one row per affiliate provider (slug = adapter name).
- `products` — deduplicated catalog rows, unique on `(merchant_id, external_id)`.
- `offers` — per-source price / URL / commission snapshot, unique on `(product_id, source)`.
- `sync_runs` — audit trail per ingest, with counters and status (`pending|running|success|failed`).

## Search
- `services.search.MeilisearchIndexer` — thin async wrapper on the Meilisearch REST API.
- `services.search.InMemoryIndexer` — deterministic dict-backed fallback for dev, tests, and CI.
- `services.search.get_indexer()` — picks Meilisearch when `MEILI_ENABLED=true` and reachable, else the fallback.

## Event bus & locking
- Redis (`REDIS_ENABLED=true`) — best-effort distributed lock per merchant sync to prevent concurrent runs.
- RabbitMQ (`RABBITMQ_ENABLED=true`) — best-effort `sync.completed` event on `affiloom.events` (topic exchange).
- Neither is required for the sync to succeed; both degrade silently when disabled or unreachable.

## Verification
```bash
# Backend tests
cd apps/backend && uv run pytest tests/ -q

# Alembic migration up/down + schema drift
cd apps/backend && DATABASE_URL="sqlite+aiosqlite:////tmp/affiloom.db" uv run alembic upgrade head
                    DATABASE_URL="sqlite+aiosqlite:////tmp/affiloom.db" uv run alembic check
                    DATABASE_URL="sqlite+aiosqlite:////tmp/affiloom.db" uv run alembic downgrade base

# Frontend lint + build
cd apps/frontend && pnpm lint && pnpm build

# Docker compose config
docker compose config
```

## CI
GitHub Actions workflow at `.github/workflows/ci.yml`.
