MASTER BACKLOG — Affiloom

Format tiap task:
ID | Title | Owner Agent | Priority | Dependency | Status | AC | Tests | Security impact | Evidence | Committer | Reviewer | Rollback

====================================================
M0 — AUDIT & SAFETY (✅ SELESAI)
====================================================

M0-001 | Safety snapshot (repo path, branch, commit, dirty, remote, tags, containers) | PM | P0 | - | ✅ DONE | Snapshot file ada di docs/execution/ | - | None required | git status, git log, ls | hermès | auditor | N/A (read-only)
M0-002 | Audit repo structure (.hermes, apps/frontend, apps/backend, migrations, workers, Docker, CI, tests, env, docs, git history) | PM | P0 | M0-001 | ✅ DONE | CURRENT_STATE.md + REPOSITORY_MAP.md berisi temuan nyata | - | None | File content review | hermès | auditor | N/A (read-only)
M0-003 | Baseline tests (backend pytest, ruff lint, alembic upgrade/check/downgrade, seed idempotency, frontend lint/build) | QA/SDET | P0 | M0-001, M0-002 | ✅ DONE | Tiap test dijalankan dan hasil tercatat di BASELINE_TEST_RESULTS.md | 66 unit tests | None | Test output | hermès | auditor | alembic downgrade base
M0-004 | Security baseline (secrets, endpoints, dependencies, known issues) | Security Engineer | P0 | M0-002 | ✅ DONE | SECURITY_BASELINE.md dengan 8 rekomendasi | - | Secret scan | File content review | hermès | auditor | N/A (read-only)
M0-005 | Reuse/Refactor/Archive/Rebuild decision | Solution Architect | P0 | M0-002 | ✅ DONE | REUSE_REFACTOR_ARCHIVE_REBUILD.md: REUSE majority, REFACTOR 8 item, ARCHIVE none, REBUILD none | - | - | File content review | hermès | auditor | N/A (read-only)
M0-006 | Create agent files structure (.hermes/agents/affiloom/) | PM | P1 | M0-005 | ⏳ BACKLOG | 16 agent files minimal berisi identity, mission, scope, authority, workflow | - | - | - | - | - | - |

====================================================
M1 — SECURE FOUNDATION (P0)
====================================================

M1-001 | Add CSP + secure headers middleware (FastAPI backend) | Backend Worker | P0 | - | ⏳ BACKLOG | Backend returns Content-Security-Policy, X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security | Integration test verify headers present | MEDIUM: XSS/clickjack | Header in response | - | Security Engineer | Rollback: revert middleware addition
M1-002 | Add rate limiting to public endpoints | Backend Worker | P0 | - | ⏳ BACKLOG | slowapi integrated: 100 req/min per IP for public, 20 req/min for admin | Rate limit test at threshold | MEDIUM: DoS protection | Test output | - | Security Engineer | Remove rate limiter dependency
M1-003 | Disable management ports in docker-compose profile | DevOps/SRE | P1 | - | 🔵 IN_PROGRESS | Profiles: dev exposes 15672+9001; prod does not | docker compose config check | MEDIUM: attack surface | Compose config | hermès | Security Engineer | Rollback: revert profile
M1-004 | Add env validation (warn on dev defaults in non-dev) | Backend Worker | P1 | - | ⏳ BACKLOG | Backend logs WARNING if ENVIRONMENT != development and S3/Meili/Redis defaults unchanged | Unit test | MEDIUM: prevent accidental prod | Log output | - | Security Engineer | Revert validation
M1-005 | Add per-action admin audit log | Backend Worker | P1 | - | ⏳ BACKLOG | Every admin POST/PUT logged with admin_token_hash, ip, timestamp, action, resource | Integration test | MEDIUM: audit trail | Audit log DB rows | - | Security Engineer | Rollback: remove middleware
M1-006 | Remove next.config.js standalone output (Windows build fix) | Frontend Worker | P1 | - | ⏳ BACKLOG | pnpm build succeeds on both Windows and Linux | Build test on Windows | None | Build output | - | PM | Revert next.config.js
M1-007 | Add CI integration test job (docker compose up + smoke test) | DevOps/SRE | P2 | - | ⏳ BACKLOG | CI starts docker compose, runs integration tests, tears down | CI pipeline passes | None | CI run log | - | QA/SDET | Revert workflow

====================================================
M2 — REVENUE MVP (P0)
====================================================

M2-001 | Product page improvements: evidence, freshness badge, alternatives | Frontend Worker | P0 | - | ⏳ BACKLOG | Product detail shows evidence sources, freshness timestamp, alternative products | E2E test | None | Screenshot | - | UX/Design | Revert page changes
M2-002 | Comparison MVP (2-4 products side-by-side) | Frontend + Backend | P0 | - | ⏳ BACKLOG | /compare endpoint + comparison page with normalized attributes, prices, recommendation | Integration + E2E | None | Live page | - | Product Manager | Revert router
M2-003 | Buying guide MVP (top pick, budget pick, upgrade pick) | Frontend + Backend | P0 | - | ⏳ BACKLOG | Buying guide page template + backend content type with structured methodology | E2E | None | Live page | - | Content/Editorial | Revert
M2-004 | Search & filters (frontend search bar + Meilisearch integration) | Frontend + Backend | P0 | M2-001 | ⏳ BACKLOG | Search by keyword, filter by category, pagination | Integration test | None | Test output | - | Product Manager | Revert
M2-005 | Collections (curated, shareable, visual) | Frontend + Backend | P1 | M2-001 | ⏳ BACKLOG | Collection page with product grid, share link, visual layout | E2E | None | Live page | - | Product Manager | Revert
M2-006 | Admin approval queue (publish/unpublish article) | Backend Worker | P1 | - | ⏳ BACKLOG | Admin dashboard shows pending articles for review/publish | API test | LOW: auth | Test output | - | PM | Revert
M2-007 | Link health checker (affiliate URL validation) | Affiliate Integration | P1 | - | ⏳ BACKLOG | Background job validates affiliate links, logs broken ones | Integration test | None | Audit finding | - | QA/SDET | Revert job

====================================================
M3 — AI OPERATIONS (P1)
====================================================

M3-001 | AI provider abstraction (OpenAI-compatible adapter) | AI Workflow Engineer | P1 | - | ⏳ BACKLOG | ContentAIAdapter implementation for OpenAI-compatible API, structured output validation | Unit test + hallucination eval | MEDIUM: cost, content quality | Test output | - | Security Engineer | N/A (feature-flagged)
M3-002 | Prompt registry (versioned, evaluatable) | AI Workflow Engineer | P1 | M3-001 | ⏳ BACKLOG | PromptVersion model + CRUD, retrieval with fallback to latest | Unit test | LOW | DB migration | - | AI Workflow | alembic downgrade
M3-003 | Confidence & approval gate | AI Workflow Engineer | P1 | M3-001 | ⏳ BACKLOG | Low-confidence drafts held for admin review; scores persisted | Integration test | MEDIUM: prevents bad content | Test output | - | Product Manager | Revert gate
M3-004 | Cost limits & model fallback | AI Workflow Engineer | P2 | M3-001 | ⏳ BACKLOG | Per-task cost ceiling, fallback chain, circuit breaker | Unit test | MEDIUM: cost | Test output | - | DevOps/SRE | Revert

====================================================
M4 — DIFFERENTIATION (P2)
====================================================

M4-001 | Recommendation assistant (chat-style product finder) | AI Workflow + Frontend | P2 | M3-001 | ⏳ BACKLOG | Chat UI + backend RAG pipeline with product catalog | E2E | MEDIUM: prompt injection | Live page | - | Product Manager | Feature flag off
M4-002 | Creator storefront (curated collection page per persona) | Frontend + Backend | P2 | M2-005 | ⏳ BACKLOG | /creator/:slug page with profile, curated picks, shareable | E2E | None | Live page | - | UX/Design | Feature flag off
M4-003 | Advanced comparisons (shareable, loadable by URL) | Frontend | P2 | M2-002 | ⏳ BACKLOG | Comparison URL param loads saved comparison state | E2E | None | Live page | - | Product Manager | Revert

====================================================
SECURITY BACKLOG (selalu di-re-evaluasi)
====================================================

S-001 | SSRF defense (outbound URL validation) | Security Engineer | P1 | - | ⏳ BACKLOG | Validate S3/Meilisearch/outbound URLs against allowlist | Security test | HIGH | Test output | - | Security | Override: URL validation
S-002 | Webhook signature + replay protection | Backend Worker | P2 | - | ⏳ BACKLOG | HMAC-signed payloads, timestamp window check | Unit test | HIGH | Test output | - | Security | Revert
S-003 | Secret scanning in CI (trufflehog/gitleaks) | DevOps/SRE | P1 | - | ⏳ BACKLOG | CI job fails on secret patterns | CI pipeline | HIGH | CI run | - | Security | Revert workflow
S-004 | Prompt injection defense (AI pipeline) | AI Workflow Engineer | P1 | M3-001 | ⏳ BACKLOG | Input sanitization, output boundary, red-teaming | Security test | HIGH | Test output | - | Security | Feature flag off

====================================================
TASK STATE LEGEND
====================================================
BACKLOG → READY → CLAIMED → IN_PROGRESS → SELF_TEST → PEER_REVIEW → SECURITY_REVIEW → QA → AUDIT → OWNER_APPROVAL → DONE
Additional: BLOCKED | NEEDS_REWORK | REJECTED | DEFERRED | ROLLED_BACK