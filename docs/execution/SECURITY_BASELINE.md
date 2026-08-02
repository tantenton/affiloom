SECURITY BASELINE — Affiloom

INVENTORY (dari audit langsung file aktual)
===========================================

1. Secrets & Credentials
   - .env.example: all secrets empty/placeholder. SAFE per policy.
   - ADMIN_API_TOKEN empty → fail closed (503 when unset). SAFE.
   - CONTENT_AI_API_KEY empty/placeholder. SAFE.
   - S3_ACCESS_KEY/SECRET_KEY: minioadmin dev default in .env.example. MEDIUM.
   - MEILI_MASTER_KEY: masterKey dev default in .env.example. MEDIUM.
   - RABBITMQ URL shows guest:*** in .env.example (masked). SAFE.

2. docker-compose.yml security
   - RABBITMQ_DEFAULT_USER/PASS = guest/guest. Dev-only. LOW for local, HIGH if exposed.
   - MEILI_MASTER_KEY = masterKey. Dev-only. MEDIUM.
   - MINIO_ROOT_USER/PASSWORD = minioadmin/minioadmin. Dev-only. MEDIUM.
   - Postgres user/pass = affiloom/affiloom. Dev-only. MEDIUM.
   - Backend port 8000 mapped. Frontend 3000 mapped. Management 9001/15672 mapped.
   - NO mutual TLS, NO network isolation between services in compose (same network segment).

3. Code security
   - Admin token comparison: hmac.compare_digest (constant time). FIXED in M7. ✅
   - SQLAlchemy with parameterized queries (no raw SQL injection risk). ✅
   - FastAPI Pydantic input validation on all endpoints. ✅
   - CORS restricted to configured origins (default http://localhost:3000). ✅
   - Only GET methods allowed on public endpoints (allow_methods=["GET"]). ✅
   - Admin endpoints use Bearer token + header dependency. ✅
   - No eval/exec/pickle/os.system/etc in codebase. ✅
   - No secret in git: .env is in .gitignore. ✅
   - No TODO/FIXME/HACK in source Python. ✅

4. Dependencies
   - All Python deps via uv (pyproject.toml), versions pinned via uv.lock.
   - All Node deps via pnpm (pnpm-lock.yaml), versions pinned.
   - No known CVE-ridden packages on surface inspection (FastAPI 0.110+, SQLAlchemy 2.0+, httpx 0.27+).
   - aio-pika, redis-py, asyncpg are network dependencies with standard auth.

5. Endpoint security
   - /health: public, no auth — returns {"status":"ok"}. SAFE.
   - /ready, /deps: public — return dep probe results. LOW risk (info leakage minimal).
   - /metrics: public — returns product/merchant/sync/article counts. SAFE (aggregate data).
   - /api/products/*: public, read-only. SAFE.
   - /api/sites/current, /api/categories, /api/articles: public, read-only. SAFE.
   - /api/sitemap, /api/robots: public, read-only. SAFE.
   - /api/admin/*: requires Bearer token; tokens empty returns 503. SAFE.
   - /api/admin/sync/{merchant}: triggers sync. Protected by admin token. SAFE.
   - /api/admin/dashboard/*: protected by admin token. SAFE.
   - /api/admin/content/*: protected by admin token. SAFE.

6. Content/AI
   - CONTENT_AI_ENABLED=false by default. Content is deterministic only. SAFE.
   - AI adapter code has prompt injection section but prompt injection defense not yet implemented in code.
   - No hallucination guardrails in code yet (deterministic draft so no risk now).

KNOWN ISSUES & RISKS (dari audit langsung)
==========================================

Medium:
- docker-compose.yml hardcodes dev credentials for S3/Meili/Redis/MinIO/Postgres/RabbitMQ. Must warn if deployed to non-dev environment.
- No CSP/secure headers middleware set on FastAPI or Next.js.
- No rate limiting on any endpoint.
- No CSRF protection (public endpoints only GET, so low risk; admin endpoints POST but use Bearer token).
- No input length validation on POST admin endpoints for body_md, title etc. (Pydantic handles some; body_md has no max_length).
- No mutate limits: one admin token is global (not per-user or per-scope).
- No audit log of admin actions (current logging is structured JSON but no per-action audit trail).
- Webhook signature / replay protection: not implemented (no webhooks yet, but sync events use RabbitMQ without auth).

Low:
- RabbitMQ management port 15672 exposed in compose (viewable metrics/env)
- MinIO console 9001 exposed in compose
- Admin token length/format: no minimum length enforced in .env.example
- Meilisearch _ensure_index silently swallows 4xx (known issue)
- Outbound URL validation: none for S3 endpoint or Meilisearch host URLs
- SSRF defense: not explicit (httpx used for Meilisearch; S3 SDK will be used)

Already fixed (M7):
- hmac.compare_digest for admin token comparison
- Ruff violations (S105, S110) suppressed intentionally for dev defaults

RECOMMENDED ACTIONS (prioritas)
================================
1. [HIGH] Add CSP + secure headers middleware to FastAPI backend
2. [HIGH] Add rate limiting middleware (slowapi or custom) to public endpoints
3. [MEDIUM] Disable management ports (15672, 9001) in docker-compose.yml for non-dev profiles
4. [MEDIUM] Add env validation: warn/fail on dev credentials if ENVIRONMENT != "development"
5. [MEDIUM] Add admin action audit logging (who/ip/timestamp/action)
6. [LOW] Add body_md max_length validation in ArticleCreate schema
7. [LOW] Add outbound URL validation for S3/Meilisearch config URLs
8. [LOW] Add secret scan (trufflehog/gitleaks) to CI pipeline