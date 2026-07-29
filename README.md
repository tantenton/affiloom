# Affiloom
Autonomous Indonesian affiliate platform — first milestone scaffold.

## Services
- Next.js App Router frontend (SEO homepage + disclosure)
- FastAPI backend (health + provider adapter contract)
- PostgreSQL / Redis / RabbitMQ / Meilisearch / MinIO via Docker Compose

## Quick start
```bash
cp .env.example .env
docker compose up -d
pnpm install
pnpm build
pnpm dev
```

Backend: `cd apps/backend && uvicorn main:app --reload`

## CI
GitHub Actions workflow at `.github/workflows/ci.yml`.
