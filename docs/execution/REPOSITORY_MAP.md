REPOSITORY MAP — Affiloom

Root: C:\Users\LENOVO\Documents\Project\affiloom

FILES & DIRECTORIES
===================

.
├── .env.example                  # env template: frontend/backend. All secrets empty. Safe.
├── .github/
│   ├── ISSUE_TEMPLATE/bug_report.md
│   ├── ISSUE_TEMPLATE/feature_request.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/ci.yml           # CI: backend pytest + alembic check, frontend pnpm build
├── .gitignore                     # proteksi .env, .venv, node_modules, .next, uv.lock, .agent-work
├── .hermes/
│   ├── m1-prompt.txt              # Prompt template untuk hermes chat di VPS aliyun
│   └── run-affiloom-aliyun-m1.sh  # Script untuk trigger M1 via hermes CLI di VPS
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── DECISIONS.md                   # M7 decisions: Docker pin, hmac, lazy-import, ruff config, smoke tests
├── docker-compose.yml             # 8 services: postgres, redis, rabbitmq, meilisearch, minio, backend, sync-worker, frontend
├── KNOWN_ISSUES.md                # Meilisearch 4xx silently, create_site idempotency, CI smoke skip, RabbitMQ default, hardcoded secrets
├── package.json                   # pnpm monorepo root + turbo 1.13.3
├── pnpm-lock.yaml
├── pnpm-workspace.yaml            # packages: apps/*
├── PROGRESS.md                    # M7 verified: 66 tests pass, lint clean, alembic ok, frontend build ok (non-Windows)
├── README.md                      # M7 hardening docs: api surface, data model, search, events, CI, verify commands
├── turbo.json
├── apps/
│   ├── backend/
│   │   ├── Dockerfile             # Python 3.12-slim, multi-stage
│   │   ├── __init__.py
│   │   ├── adapters/
│   │   │   ├── __init__.py
│   │   │   ├── ai.py              # ContentAIAdapter: Null, Deterministic adapters
│   │   │   └── provider.py        # MarketplaceProviderAdapter (ABC), DeterministicDemoAdapter (10 items)
│   │   ├── alembic.ini
│   │   ├── config.py              # Pydantic Settings: DB, Redis, RabbitMQ, Meili, S3, CORS, AI, sync knobs
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── models.py          # ORM: Merchant, Product, Offer, SyncRun, Site, ArticleCategory, Article, ArticleProduct
│   │   │   └── session.py         # AsyncEngine, async_sessionmaker, get_session, reset_engine, dispose_engine
│   │   ├── dependencies.py        # get_catalog_adapter() → DeterministicDemoAdapter (singleton)
│   │   ├── main.py                # FastAPI app: CORS, lifespan, all routers included
│   │   ├── migrations/
│   │   │   ├── env.py
│   │   │   ├── script.py.mako
│   │   │   └── versions/
│   │   │       ├── 20260729_0001_m4_catalog_init.py  # merchants, products, offers, sync_runs
│   │   │       └── 20260730_0001_m5_content.py      # sites, article_categories, articles, article_products
│   │   ├── pyproject.toml         # FastAPI 0.110+, uvicorn, pydantic-settings, httpx, sqlalchemy async, asyncpg, aiosqlite, alembic, redis, aio-pika, pytest, pytest-asyncio
│   │   ├── requirements.txt       # (unused — pyproject.toml used by uv)
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py           # POST /sync/{merchant}, GET /sync/runs, GET /audit. Bearer token + hmac.compare_digest
│   │   │   ├── admin_content.py   # Admin content: create_site, categories, drafts, articles, publish, link-suggestions
│   │   │   ├── admin_dashboard.py # GET /dashboard/summary: product/sync/content stats
│   │   │   ├── content.py         # Public content: GET /sites/current, /categories, /categories/{slug}, /articles, /articles/{slug}
│   │   │   ├── health.py          # GET /health, /ready, /deps, /metrics
│   │   │   ├── products.py        # GET /api/products, /api/products/{id}
│   │   │   └── sitemap.py         # GET /api/sitemap, /api/robots
│   │   ├── ruff.toml              # E/F/I active; D104, S110, E501 ignored
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── admin.py           # SyncRunOut, SyncRunListResponse, SyncTriggerResponse, AdminDashboardResponse
│   │   │   ├── content.py         # Site/Category/Article DTOs: Out, ListResponse, Create, DraftRequest, LinkSuggestion
│   │   │   └── product.py         # ProductOut, ProductListResponse
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── audit.py           # run_audit(): sync health, data quality, content gaps → Finding objects
│   │   │   ├── content.py         # generate_draft (deterministic/AI), publish_article, upsert_category, resolve_site, generate_internal_links
│   │   │   ├── events.py          # sync_lock (Redis-based), publish_sync_event (RabbitMQ)
│   │   │   ├── logging.py         # Structured JSON-line logger
│   │   │   ├── search.py          # SearchIndexer protocol, MeilisearchIndexer, InMemoryIndexer, get_indexer()
│   │   │   └── sync.py            # run_sync(): idempotent upsert merchants/products/offers, deactivate missing, search index, publish event
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py        # fixtures: client, session, seed_db
│   │   │   ├── test_admin_dashboard_api.py
│   │   │   ├── test_admin_sync_api.py
│   │   │   ├── test_audit.py
│   │   │   ├── test_content_admin_api.py
│   │   │   ├── test_content_public_api.py
│   │   │   ├── test_health.py
│   │   │   ├── test_logging.py
│   │   │   ├── test_products.py
│   │   │   ├── test_search_indexer.py
│   │   │   ├── test_smoke_adapter.py
│   │   │   ├── test_smoke_integration.py   # @pytest.mark.integration (skip in CI)
│   │   │   ├── test_sync_service.py
│   │   │   └── test_sync_worker.py
│   │   ├── uv.lock                # 1444 lines lockfile
│   │   └── workers/
│   │       ├── __init__.py
│   │       ├── audit_worker.py    # CLI daily audit
│   │       ├── seed.py            # CLI idempotent seed (10 products)
│   │       └── sync_worker.py     # CLI one-pass or --interval loop
│   │
│   └── frontend/
│       ├── Dockerfile             # Node 20-alpine, pnpm 9.15.4, multi-stage build, output standalone
│       ├── next.config.js         # output: "standalone" (Windows build EPERM issue)
│       ├── package.json           # Next.js 14.1.0, React 18.2.0, Tailwind 3.4.3, ESLint 8.57.0
│       ├── postcss.config.js
│       ├── tailwind.config.ts
│       ├── tsconfig.json
│       └── src/
│           ├── app/
│           │   ├── layout.tsx     # Root layout: font, metadata
│           │   ├── page.tsx       # Homepage: CTA katalog + kode etik + affiliate disclosure
│           │   ├── robots.ts      # Returns robots.txt from /api/robots
│           │   ├── sitemap.ts     # Returns sitemap.xml from /api/sitemap
│           │   ├── globals.css    # Tailwind base
│           │   ├── produk/
│           │   │   ├── page.tsx        # /produk: catalog listing
│           │   │   ├── loading.tsx
│           │   │   ├── not-found.tsx
│           │   │   └── [id]/             # /produk/[id]: product detail
│           │   │       ├── page.tsx
│           │   │       ├── loading.tsx
│           │   ├── artikel/
│           │   │   ├── page.tsx        # /artikel: article listing
│           │   │   └── [slug]/page.tsx # /artikel/[slug]: article read
│           │   ├── kategori/
│           │   │   └── [slug]/page.tsx # /kategori/[slug]: category page
│           │   ├── error.tsx
│           │   ├── loading.tsx
│           │   ├── not-found.tsx
│           ├── components/
│           │   ├── AffiliateDisclosure.tsx  # Disclosure banner for affiliate links
│           │   ├── ProductCard.tsx          # Product card component
│           │   ├── SearchForm.tsx           # Search form component
│           │   └── SiteHeader.tsx           # Navigation header
│           └── lib/
│               ├── api.ts            # Backend API fetchers
│               ├── format.ts         # formatPrice, formatCommission
│               ├── markdown.ts       # Minimal markdown→HTML renderer
│               └── types.ts          # TypeScript interfaces (Product, Article, etc.)
└── docs/
    └── execution/                    # Created by M0 audit
        ├── SAFETY_SNAPSHOT.md        # Created now
        ├── CURRENT_STATE.md          # Created now
        ├── REPOSITORY_MAP.md         # THIS FILE
        ├── BASELINE_TEST_RESULTS.md  # Created next
        ├── SECURITY_BASELINE.md      # Created next
        └── REUSE_REFACTOR_ARCHIVE_REBUILD.md  # Created next

KEY DECISIONS (dari DECISIONS.md)
===================================
- M7 hardening: pin corepack pnpm@9.15.4, hmac.compare_digest, drop lazy ContentDraft import, ruff config
- Seed script: -m workers.seed, idempotent
- Smoke tests: @pytest.mark.integration, skip in CI
- Dockerfile: pin corepack, multi-stage for frontend/backend

KEY KNOWN ISSUES
==================
- Meilisearch _ensure_index swallows 4xx silently (LOW)
- admin_content.py create_site 409 conflict (LOW)
- Integration smoke tests skip in CI (LOW)
- RabbitMQ default credentials in compose (LOW)
- Redis/Meili/MinIO hardcoded defaults in compose (MEDIUM in prod)
