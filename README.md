# Affiloom

Autonomous Indonesian affiliate platform — deterministic vertical slice through M7 (final MVP hardening).

## Services
- **Next.js App Router frontend**: homepage, `/produk` catalog, `/produk/[id]` detail, `/artikel`, `/artikel/[slug]`, `/kategori/[slug]` — Indonesian, SEO metadata + Product/Article JSON-LD, affiliate disclosure.
- **FastAPI backend**: health/readiness probes, product catalog (read-only via deterministic demo adapter), SEO content API, admin sync/content/dashboard/audit endpoints.
- **Sync worker** (`python -m workers.sync_worker`) — one-shot or `--interval SECONDS` loop; retry + timeout + dead-letter-safe.
- **Audit worker** (`python -m workers.audit_worker`) — daily operational audit; findings as JSON.
- **Seed script** (`python -m workers.seed`) — idempotent demo catalog population.
- PostgreSQL / Redis / RabbitMQ / Meilisearch / MinIO via Docker Compose.

## Compliance guardrails
- Marketplace access is read-only through the demo adapter today. Real partner adapters must call **official partner APIs only** (Shopee Affiliate API, Tokopedia Affiliate API, etc.). No scraping, no reverse-engineered private endpoints, no automated browsing.
- Every page that surfaces affiliate deep-links renders a visible disclosure and marks outbound links `rel="sponsored nofollow noopener noreferrer"`.
- The sync service upserts what the adapter returns and marks missing rows inactive — no fabricated data.

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
uv run alembic upgrade head        # apply migrations (Postgres or SQLite)
uv run python -m workers.seed      # populate deterministic demo catalog
uv run uvicorn main:app --reload   # http://localhost:8000
```

Trigger a sync manually (admin token required, see `.env.example`):

```bash
curl -X POST -H "Authorization: Bearer ***" \
     http://localhost:8000/api/admin/sync/demo
```

Or run the worker CLI:

```bash
cd apps/backend
uv run python -m workers.sync_worker                 # one pass
uv run python -m workers.sync_worker --interval 300  # loop every 5 min
```

Full docker stack (frontend + backend + sync-worker + infra):

```bash
docker compose up --build
```

## API surface (M7)

### Public read layer
- `GET /health` — liveness
- `GET /ready` — readiness (all *required* deps healthy)
- `GET /deps` — per-dependency detail
- `GET /metrics` — application metrics (product/sync/content counts)
- `GET /api/products?q=<query>&limit=<1..100>&offset=<n>` — paginated product catalog
- `GET /api/products/{id}` — product detail (404 if unknown)
- `GET /api/sites/current` — current active site
- `GET /api/categories` — article categories list
- `GET /api/categories/{slug}` — category detail
- `GET /api/articles?category=&limit=&offset=` — published articles
- `GET /api/articles/{slug}` — article detail with linked products
- `GET /api/sitemap` — canonical URL list
- `GET /api/robots` — robots directives

### Admin surface (requires `Authorization: Bearer <ADMIN_TOKEN>`; 503 if token unset)
- `POST /api/admin/sync/{merchant}` — trigger idempotent sync
- `GET  /api/admin/sync/runs?limit=&offset=` — paginated sync run history
- `GET  /api/admin/sync/runs/{run_id}` — single run detail
- `GET  /api/admin/dashboard/summary` — aggregate product/sync/content stats
- `GET  /api/admin/audit` — run daily audit on demand
- `POST /api/admin/content/sites` — create site
- `POST /api/admin/content/categories` — create category
- `GET  /api/admin/content/categories` — list categories
- `POST /api/admin/content/drafts` — create article draft (deterministic or AI)
- `POST /api/admin/content/articles` — create article directly
- `POST /api/admin/content/articles/{id}/publish` — publish draft
- `GET  /api/admin/content/articles/{id}/link-suggestions` — internal link suggestions

## Data model
- `merchants` — one per affiliate provider (slug = adapter name)
- `products` — deduplicated catalog rows, unique on `(merchant_id, external_id)`
- `offers` — per-source price/URL/commission snapshot
- `sync_runs` — audit trail per ingest with counters and status (`pending|running|success|failed`)
- `sites` — SEO site/domain surface
- `article_categories` — editorial category grouping
- `articles` — SEO article with slug + status lifecycle
- `article_products` — internal link between article and product (with ordering + score)

## Search
- `services.search.MeilisearchIndexer` — thin async wrapper on Meilisearch REST API
- `services.search.InMemoryIndexer` — deterministic dict-backed fallback for dev/tests/CI
- `services.search.get_indexer()` — picks Meilisearch when `MEILI_ENABLED=true` and reachable, else fallback

## Event bus & locking
- Redis (`REDIS_ENABLED=true`) — best-effort distributed lock per merchant sync
- RabbitMQ (`RABBITMQ_ENABLED=true`) — best-effort `sync.completed` event on topic exchange
- Neither required for sync to succeed; both degrade silently when disabled/unreachable

## Verification

```bash
# Backend tests + lint + migrations
cd apps/backend
uv run pytest tests/ -q
uv run ruff check .
DATABASE_URL="sqlite+aiosqlite:////tmp/affiloom.db" uv run alembic upgrade head
DATABASE_URL="sqlite+aiosqlite:////tmp/affiloom.db" uv run alembic check
DATABASE_URL="sqlite+aiosqlite:////tmp/affiloom.db" uv run alembic downgrade base
DATABASE_URL="sqlite+aiosqlite:////tmp/affiloom.db" uv run python -m workers.seed

# Frontend lint + build
cd apps/frontend && pnpm lint && pnpm build

# Docker compose config + build
docker compose config
docker compose build
```

## CI
GitHub Actions workflow at `.github/workflows/ci.yml`. Runs backend tests + migrations, frontend build. Integration tests (`@pytest.mark.integration`) are skipped in CI.