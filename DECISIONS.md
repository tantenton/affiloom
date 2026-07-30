# Decisions

## M7 — Final MVP hardening & debugging

| Decision | Rationale |
|----------|-----------|
| Pin `corepack prepare pnpm@9.15.4` in Dockerfile | `node:20-alpine` ships Node 20.20; corepack defaults to pnpm 11 which requires Node ≥22. `ERR_UNKNOWN_BUILTIN_MODULE`. Pin matches lockfile version. |
| Use `hmac.compare_digest` for admin token | Previous "constant-time-ish" compare still leaked token length via early return. `compare_digest` is the stdlib-provided constant-time comparison. |
| Drop lazy import of `ContentDraft` | `_deterministic_draft` imported `ContentDraft` inside the function body to avoid a circular import. No actual cycle existed — flattening the import silences a type-checker false positive (F821) and improves readability. |
| Ruff D104/S110 disabled project-wide | `__init__.py` docstrings add noise for zero value; `try-except-pass` on best-effort dependencies (Redis, RabbitMQ, Meilisearch) is intentional silence. |
| Seed script as `-m workers.seed` | Consistent with existing worker pattern (`sync_worker`, `audit_worker`). Reuses `run_sync` so seed behaviour is a subset of production behaviour. |
| Integration smoke tests for localhost:8000 | Marked `@pytest.mark.integration` so CI does not run them (no docker stack there). They validate the full HTTP path on a real running backend. |
| Ruff formatting applied to backend | `ruff format` auto-wrapped long lines; 21 files reformatted. Remaining docstring/comment E501 violations suppressed with `# noqa: E501`. |