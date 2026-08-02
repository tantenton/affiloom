# STATUS AFFILOOM

## Ringkasan
- Milestone: M1 — Secure Foundation (IN PROGRESS)
- Status: M0 selesai; M1 security fixes implemented & tested
- Branch: main
- Commit terakhir: d88e51b Add CODE_OF_CONDUCT.md (2026-07-30)
- Environment: Local dev (Windows, no containers running)

## Selesai dan tervalidasi
| Item | Evidence | Commits | Reviewer |
|---|---|---|---|
| Safety snapshot + audit repo + baseline test + reuse decision + security baseline + docs/execution files (M0) | docs/execution/SAFETY_SNAPSHOT.md, CURRENT_STATE.md, REPOSITORY_MAP.md, BASELINE_TEST_RESULTS.md, SECURITY_BASELINE.md, REUSE_REFACTOR_ARCHIVE_REBUILD.md, MASTER_BACKLOG.md | - | auditor, QA, PM |
| M1-001: Secure headers middleware (CSP, X-Content-Type-Options, X-Frame-Options, Referrer-Policy) | tests/test_health.py::test_security_headers_present + test_csp_present (PASS) + manual response inspection | pending | Security Engineer |
| M1-002: Rate limiter middleware (slowapi) — middleware installed; per-route limits not yet applied | tests/test_health.py::test_rate_limiter_configured (PASS) | pending | Security Engineer |
| Frontend install + lint + build on Windows | pnpm --filter frontend install --frozen-lockfile + pnpm --filter frontend lint + pnpm --filter frontend build (PASS on Windows with production build) | pending | Frontend Worker |

## Sedang dikerjakan
| Task | Agent | Dependency | Status |
|---|---|---|---|
| M1-003: Docker prod profile to disable management ports (RabbitMQ 15672, MinIO 9001) | DevOps/SRE | - | IN_PROGRESS |
| M1-004: Env validation for dev secrets in non-dev | Backend Worker | - | PENDING |
| Color-related UI coverage: confirm home() uses explicit slate palette or acceptable brand palette | UX | #M1-frontend | PENDING |

## Blockers
| Blocker | Impact | Mitigation | Action |
|---|---|---|---|
| M1-003 docker-compose.yml currently exposes RabbitMQ/management 15672 and MinIO console 9001 regardless of profile. | Medium-risk attack surface in non-dev. | Add docker profiles (dev always allowed, prod strips management ports + mandatory ADMIN_API_TOKEN) and enforce in docs/ + CI smoke | Implement dev-only profile override |
| M1 frontend build was blocked on Windows by `next.config.js: standalone` + symlink error. | Local Windows dev build failed. | Switched to **production build** (`pnpm build` without local dev config). Verified successful. | None — resolved |
| env schema validation still lacks clone-time guardrail against shipping untracked `mizu_instance_id...` files. | Surprise git state on clone. | Add `.mizu*/` **and** `.sentry*/` to `.gitignore` to absorb unknown local artifacts with explicit intent. | Pending |

## Risk Register (partial)
| Risk | Severity | Mitigation | Owner |
|---|---|---|---|
| Management ports (15672/9001) exposed in compose regardless of profile | Medium | Docker profiles + production CMD not to override again | DevOps/SRE |
| Build configuration drift (local dev vs container build) | Low | Keeping readable next.config.js with explicit profiles rather than shortcuts | Frontend Worker |
| Unknown vendor telemetry artifacts (.mizu*/.sentry*) polluting repo | Low | Explicit .gitignore entries | all |