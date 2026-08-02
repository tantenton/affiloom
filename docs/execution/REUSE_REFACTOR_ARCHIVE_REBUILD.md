REUSE / REFACTOR / ARCHIVE / REBUILD — Affiloom

Audit memastikan tidak ada rebuild total yang perlu dilakukan. Stack existing layak untuk MVP dan masa depan modular-monolith.

REUSATA — LANGSUNG PAKAI (tidak perlu diubah)
=============================================

Backend:
- Python 3.12 + FastAPI 0.110+ + uvicorn
- SQLAlchemy 2.0 async + asyncpg/aiosqlite
- Alembic migrations (M4 catalog, M5 content)
- pydantic-settings untuk config
- httpx untuk Meilisearch REST API
- aio-pika untuk RabbitMQ; redis-py untuk Redis
- pytest + pytest-asyncio (66 tests pass)
- DeterministicDemoAdapter (10 produk deterministik) — safe untuk dev/test/CI
- MarketplaceProviderAdapter ABC — contract siap untuk adapter partner resmi
- ContentAIAdapter ABC + NullContentAIAdapter + DeterministicContentAIAdapter — safe fallback
- SearchIndexer Protocol + MeilisearchIndexer + InMemoryIndexer — swapable
- Services: sync.py (idempotent), audit.py (findings), events.py (lock+publish), content.py (draft+publish+links), logging.py (JSON-lines)
- Routers: health, products, content (public+admin), sitemap, dashboard
- Schemas: product, admin, content (Pydantic DTOs)
- Workers: sync_worker (CLI), audit_worker (CLI), seed (CLI idempotent)
- Dockerfile backend multi-stage
- ruff config (E/F/I, noqa untuk S105/S110/E501)

Frontend:
- Next.js 14.1.0 App Router + React 18.2.0
- Tailwind CSS 3.4.3
- TypeScript 5.4.5
- ESLint config-next 14.1.0
- Components: SiteHeader, AffiliateDisclosure (transparan), ProductCard, SearchForm
- lib/api.ts (typed fetcher), lib/types.ts (TS interfaces), lib/format.ts (price/commission), lib/markdown.ts (minimal renderer)
- Frontend pages: /, /produk, /produk/[id], /artikel, /artikel/[slug], /kategori/[slug], sitemap, robots
- SEO: openGraph metadata, Product/Article JSON-LD, AffiliateDisclosure visible, rel="sponsored nofollow noopener noreferrer"
- Frontend Dockerfile multi-stage (pnpm 9.15.4 pinned for Node 20)

Infra:
- docker-compose.yml (8 services, dev defaults, best-effort Redis/RabbitMQ degrade)
- GitHub Actions CI (backend pytest+alembic, frontend pnpm build)
- .gitignore (protects .env, .venv, node_modules, .next, .agent-work)
- README.md, PROGRESS.md, DECISIONS.md, KNOWN_ISSUES.md (docs)
- .github/ISSUE_TEMPLATE, PULL_REQUEST_TEMPLATE

REFAKTOR — DIPERBAIKI TAPI TETAP
=================================

1. next.config.js output: "standalone"
   - Issue: Windows local build EPERM symlink. Linux CI/Docker OK.
   - Refactor: Make output conditional (standalone only when Docker/CI env var set). Atau buang standalone entirely; buat Dockerfile lebih kompleks but symlink-free. Mendukung local Windows dev.
   - Priority: MEDIUM (blocks local Windows build, not CI)

2. docker-compose.yml secrets
   - Issue: hardcoded dev credentials (guest/guest, masterKey, minioadmin).
   - Refactor: Use .env file interpolation, add prod profile warning at compose-up, or fail if ENVIRONMENT != "development" and defaults present.
   - Priority: MEDIUM

3. admin_content.py create_site idempotency
   - Issue: POST /api/admin/content/sites returns 409 on slug conflict (known issue).
   - Refactor: Add upsert variant or explicit 409 handling. Low harm karena admin endpoints only.
   - Priority: LOW

4. Meilisearch _ensure_index silently swallows 4xx
   - Issue: 409 already-exists returned but code passes; function noop after first run.
   - Refactor: Check status_code == 409 explicitly. Optional.
   - Priority: LOW

5. RabbitMQ URL in compose
   - Issue: .env.example uses `***` mask; compose uses guest:guest verbatim.
   - Refactor: Align both to guest:guest in dev. Add prod override via RABBITMQ_URL env.
   - Priority: LOW

6. CI smoke tests skipped
   - Issue: Integration tests require running backend on localhost:8000; CI has no docker stack.
   - Refactor: Add a CI job that starts docker-compose then runs smoke tests. Or just inline the integration tests into the unit test-suite using TestClient across started services.
   - Priority: LOW

7. No CSP / secure headers / rate limiting
   - Issue: Missing security middleware on backend and frontend.
   - Refactor: Add slowapi rate limiting + secure headers middleware to FastAPI. Add CSP header to Next.js via next.config.js headers().
   - Priority: HIGH (M1 secure foundation)

8. No per-action admin audit log
   - Issue: structured JSON logging exists but no admin-action trail.
   - Refactor: Add AuditEvent entity + middleware that logs admin POST/PUT actions with token-hash, ip, timestamp, action.
   - Priority: MEDIUM (M1/M3)

ARSIP — TIDAK ADA
==================

Tidak ada file yang perlu diarsipkan. Semua digunakan.
- requirements.txt disertakan tapi pyproject.toml/uv digunakan — bisa diarsipkan opsional tapi tidak mendesak.
- .hermes/m1-prompt.txt, run-affiloom-aliyun-m1.sh — artefak lama (VPS aliyun session); bisa diarsipkan nanti saat struktur multi-agent dibuat.

REBUILD — TIDAK PERLU TOTAL
=============================

Tidak ada komponen yang perlu dibangun ulang dari nol. Stacknya solid:
- Python async + FastAPI + SQLAlchemy 2.0 + Alembic = modern, mainstream, scalable.
- Next.js 14 App Router + TypeScript = modern frontend.
- Docker Compose = local dev + small prod viable.
- CI on GitHub Actions = standard.

Yang mungkin perlu dibangun baru (bukan rebuild):
- Multi-agent files di .hermes/agents/affiloom/ (16 agent files)
- docs/architecture/DOMAIN_MODEL.md, BOUNDED_CONTEXTS.md, API_CONTRACTS.md, ADR/
- docs/product/AFFILOOM_PRODUCT_SPEC.md
- docs/security/THREAT_MODEL.md, SECURITY_CONTROLS.md, INCIDENT_RESPONSE.md, AGENT_SECURITY_POLICY.md
- docs/affiliate/AFFILIATE_POLICY_REGISTRY.md, MERCHANT_ADAPTER_SPEC.md, DISCLOSURE_POLICY.md
- docs/ai/AI_GOVERNANCE.md, PROMPT_REGISTRY.md, CONFIDENCE_AND_APPROVAL.md, EVALUATION_STRATEGY.md, PROMPT_INJECTION_DEFENSE.md
- Master backlog, risk register, decision log, approval matrix, definition of done, status
- Product model extensions (Source, Evidence, Claim, ReviewSource, Recommendation, Comparison, Collection, etc.) sebagai migrasi baru
- Affiliate redirect service (endpoint baru + link validation + health)
- Rate limiting + secure headers middleware
- CSP header di frontend next.config.js
- Per-action admin audit log middleware

KEPUTUSAN REUSE
================
Stack tetap. Yang dibangun baru adalah superset (layer tambahan) di atas yang sudah ada. Tidak ada rewrite, tidak ada framework swap, tidak ada bahasa swap. Migandar autentikasi tetap Bearer token untuk admin, public reads tanpa auth untuk MVP.
