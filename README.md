# Affiloom
Autonomous Indonesian affiliate platform — deterministic vertical slice through M3.

## Services
- Next.js App Router frontend: homepage, `/produk` catalog, `/produk/[id]` detail (Indonesian, SEO metadata + Product JSON-LD, affiliate disclosure).
- FastAPI backend: `/health`, `/ready`, `/api/products`, `/api/products/{id}` — served by the deterministic demo adapter (no scraping).
- PostgreSQL / Redis / RabbitMQ / Meilisearch / MinIO via Docker Compose (reserved for later milestones).

## Compliance guardrails
- Marketplace access is read-only through the demo adapter today. Real partner adapters must call **official partner APIs only** (Shopee Affiliate API, Tokopedia Affiliate API, etc.). No scraping, no reverse-engineered private endpoints, no automated browsing.
- Every page that surfaces affiliate deep-links renders a visible disclosure and marks outbound links `rel="sponsored nofollow noopener noreferrer"`.

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
uv run uvicorn main:app --reload   # http://localhost:8000
```

Full docker stack (frontend + backend + infra):
```bash
docker compose up --build
```

## API surface (M3)
- `GET /health`
- `GET /ready`
- `GET /api/products?q=<query>&limit=<1..100>&offset=<n>` — paginated envelope: `{items, total, limit, offset, query}`.
- `GET /api/products/{id}` — 404 with `{"detail": "Product not found"}` when the id is unknown.

Frontend routes:
- `/` — landing page + code of conduct.
- `/produk` — searchable catalog grid (server-rendered, `q` query param).
- `/produk/[id]` — product detail with Indonesian rupiah pricing, Product schema (JSON-LD), and disclosed affiliate CTA.

## Verification
```bash
# Backend tests
cd apps/backend && uv run pytest tests/ -q

# Frontend lint + build
cd apps/frontend && pnpm lint && pnpm build

# Docker compose config
docker compose config
```

## CI
GitHub Actions workflow at `.github/workflows/ci.yml`.
