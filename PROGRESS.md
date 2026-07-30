# Progress — Milestone 7 (final MVP hardening & debugging)

## Verified state (2026-07-30)

### All gates pass

| Gate | Result |
|------|--------|
| Backend tests (66) | PASS |
| Backend lint (ruff 0.16.0) | CLEAN (0 errors) |
| Frontend lint (`pnpm lint`) | CLEAN |
| Frontend build (`pnpm build`) | OK |
| Alembic upgrade → check → downgrade | PASS |
| `docker compose config` | VALID |
| `docker compose build` (backend, sync-worker, frontend) | OK (3 images) |
| Seed script idempotency | Verified: first run creates 10, second run creates 0 |

### Milestone scope

- [x] Dockerfile frontend: pin corepack pnpm@9.15.4 for Node 20 compatibility
- [x] `docker-compose.yml`: fix RabbitMQ URL from masked `guest:***` to `guest:guest`
- [x] `routers/admin.py`: replace timing-leaky compare with `hmac.compare_digest`
- [x] `services/content.py`: fix F821 `ContentDraft` lazy-import → top-level import
- [x] 68 → 0 ruff violations (E501, D104, D205, S105, S110, I001, F401, W292)
- [x] `workers/seed.py`: idempotent seed script added
- [x] `tests/test_smoke_integration.py`: integration smoke tests added
- [x] `ruff.toml`: tightened per-file-ignores; all non-cosmetic rules active
- [x] Docs: README, PROGRESS.md, DECISIONS.md, KNOWN_ISSUES.md

### What was preserved intact
- All M1-M6 features: health, products, sync, admin, content, audit, workers
- Existing 66 backend tests — all pass unchanged
- Frontend pages, components, types, markdown renderer, SEO metadata
- Alembic migrations (both revisions)
- CI workflow
- `.env.example` (secrets already properly masked)

### Known issues (unchanged)
- Meilisearch `_ensure_index` silently swallows 4xx (returns 204 after first run)
- `admin_content.py:create_site` lacks idempotency — slug conflict returns 409
- Integration smoke tests target `localhost:8000` — skipped in CI without docker stack