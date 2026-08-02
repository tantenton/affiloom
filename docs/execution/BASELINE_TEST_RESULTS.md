BASELINE TEST RESULTS — Affiloom (real output captured)

BACKEND
=======

1. Unit tests (pytest)
Command: cd apps/backend && DATABASE_URL="sqlite+aiosqlite:////tmp/affiloom.db" uv run pytest tests/ -q -x -k "not integration"
Result: 66 passed, 10 deselected, 1 warning (StarletteDeprecationWarning httpx)
Status: PASS

2. Lint (ruff)
Command: uvx ruff check .
Result: All checks passed!
Status: PASS

3. Alembic (SQLite temp DB)
Command: DATABASE_URL="sqlite+aiosqlite:////tmp/affiloom.db" uv run alembic upgrade head
Result: Applied m4 catalog + m5 content
Status: PASS

4. Alembic check (compare to SQLite)
Command: uv run alembic check
Result: No new upgrade operations detected
Status: PASS

5. Alembic downgrade
Command: uv run alembic downgrade base
Result: Downgraded m5 → m4 → base
Status: PASS

6. Seed worker (idempotency)
First run: {"status":"success","seen":10,"created":10,"updated":0,"deactivated":0}
Second run: {"status":"success","seen":10,"created":0,"updated":0,"deactivated":0}
Status: PASS (verified idempotent)

7. Integration smoke tests
Command: uv run pytest tests/test_smoke_integration.py
Status: SKIPPED (requires running backend on localhost:8000; tagged @pytest.mark.integration)

FRONTEND
========

1. Lint (Next lint)
Command: pnpm --filter frontend lint
Result: No ESLint warnings or errors
Status: PASS

2. Build (next build at apps/frontend)
Command: pnpm --filter frontend build
Result: FAILED with EPERM symlink (Windows, next.config.js `output: "standalone"`)
Status: FAIL on Windows local; OK on Linux CI

Blocking issue: next.config.js `output: "standalone"` tries to create symlinks when writing traced files. Windows without dev mode cannot create symlinks — Next.js 14 requires either:
- Use `output: "standalone"` only in Docker/Linux
- Or switch to default (remove standalone) — smaller but enough for local dev

WORKAROUND: In CI (Linux) build succeeds. Local Windows dev using `next dev` works. Need explicit instruction to whoever runs `pnpm build` locally on Windows.

DOCKER
======

Command: docker compose config
Result: Not executed (no docker daemon running on this laptop; services are stopped)
Status: NOT TESTED (dev machine pre-condition missing)

Expected OK (validated by PROGRESS.md on M7 release).

COVERAGE SUMMARY
================

| Test | Status |
|------|--------|
| Backend 66 unit tests | ✅ PASS |
| Backend ruff lint | ✅ PASS (0 errors) |
| Alembic upgrade/check/downgrade (SQLite) | ✅ PASS |
| Seed idempotency | ✅ PASS |
| Frontend lint | ✅ PASS |
| Frontend build | ❌ FAIL (Windows symlink, standalone) |
| Integration smoke | ⊘ SKIP (running backend required) |
| Docker compose config | ⊘ SKIP (no docker daemon) |

ENV / SECRET CHECK
==================

Files reviewed:
- .env.example: ADMIN_API_TOKEN empty; CONTENT_AI_* empty; RABBITMQ URL masked `***`; S3/Meili/Redis dev defaults visible
- .env: not present (missing — typical local dev gap)
- .env.test / .env.ci: not present
- .env.example is safe to commit; no real secret leaked

Service defaults confirmed:
- RabbitMQ: guest/guest (dev compose) — low risk local
- Meilisearch: masterKey - low risk local
- MinIO: minioadmin/minioadmin — low risk local
- Redis: no password in local URL — low risk local

Next steps:
1. Remove or conditionally disable `output: "standalone"` for Windows local build
2. Create CI test that runs integration tests on first error-free run with docker stack
