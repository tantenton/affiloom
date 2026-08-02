CURRENT STATE — Affiloom (post-audit)

Repo: C:\Users\LENOVO\Documents\Project\affiloom (main, d88e51b)
Branch kerja: tetap main (user belum minta branch baru)
Untracked: AFFILOOM_HERMES_MASTER_EXECUTION_COMMAND.txt (user brief file)

Audit langsung file aktual sudah dilakukan pada:
- .hermes/ (m1-prompt.txt, run-affiloom-aliyun-m1.sh)
- apps/backend/ (main.py, config, db/models, routers/*, adapters/provider+ai, services/*, workers/*, schemas/*, tests/*, Dockerfile, pyproject.toml)
- apps/frontend/ (src/app/*, src/components/*, src/lib/*, package.json, next.config.js)
- migrations (2 versi: 20260729 M4 catalog, 20260730 M5 content)
- docker-compose.yml
- .env.example (secrets kosong, RABBITMQ URL masked ***)
- docs/README.md, PROGRESS.md (M7 verified), KNOWN_ISSUES.md, DECISIONS.md
- .github/workflows/ci.yml

Struktur agent: belum ada folder .hermes/agents/affiloom/ — akan dibuat di milestone selanjutnya.

Baseline test hasil (nyata):
- Backend: 66 passed (pytest -q -x, tanpa integration)
- Ruff lint: CLEAN (0 errors)
- Alembic: upgrade head PASS, check PASS, downgrade base PASS
- Seed worker: idempotent (10 created pertama, 0 kedua) — PASS
- Frontend lint: CLEAN (next lint)
- Frontend build: GAGAL karena next.config.js `output: "standalone"` + Windows EPERM symlink. Ini blocker Windows, bukan kode salah.
- Docker compose config: belum diuji (tidak ada container aktif); file valid.

Security baseline:
- RabbitMQ default credentials (guest/guest) masih di compose — dev only, aman karena lokal.
- Secret S3/Meilisearch/Redis dev defaults masih hardcoded di compose — MEDIUM hanya jika deploy ke luar.
- ADMIN_API_TOKEN kosong (fail closed) — aman.
- AI disabled (CONTENT_AI_ENABLED=false) — aman.
- No scraping adapter; hanya DeterministicDemoAdapter — aman.
- HMAC compare_digest dipakai di admin router — sudah fix M7.
- No TODO/FIXME/HACK dalam source Python.

Reuse / Refactor / Archive / Rebuild:
- REUSE (langsung pakai): backend stack (FastAPI + SQLAlchemy async + alembic), adapter contract (MarketplaceProviderAdapter), demo adapter deterministik, semua routers, schemas, tests (66), workers sync/audit/seed, frontend components (SiteHeader, AffiliateDisclosure, ProductCard, SearchForm), markdown renderer, format helpers, frontend types, CI workflow.
- REFACTOR (diperbaiki tapi tetap): next.config.js standalone (Windows build EPERM — perlu disable standalone atau ganti OS saat build); docker-compose RabbitMQ URL (*** → guest/guest di .env.example tapi belum di compose; compose sudah guest:guest — ok); admin_content.py create_site (idempotency belum ada — 409 saat slug conflict).
- ARCHIVE: tidak ada yang perlu diarsipkan; semua file digunakan.
- REBUILD: tidak perlu rebuild total; stack existing layak untuk MVP.

Gap utama:
1. Frontend build Windows: EPERM symlink karena standalone. Solusi: ganti output ke default (buang standalone) atau build di Linux.
2. Agent files belum dibuat di .hermes/agents/affiloom/.
3. CI belum menjalankan integration smoke tests (tagged skip).
4. Multi-agent structure belum ada (hanya .hermes/ dengan 2 file lama).
5. M5 content: AI disabled, hanya deterministik — sesuai prinsip.

Evidence file (nyata):
- test output 66 passed (pytest log tersimpan di sesi ini)
- ruff check output (clean)
- alembic upgrade/check/downgrade output
- seed output JSON (run_id, status success)
- next.config.js terlihat
- docker-compose.yml terlihat
- .env.example terlihat (secret kosong)

Status milestone:
M0 (Audit + Safety) — SELESAI dengan catatan di atas.
M1 (Secure Foundation) — sebagian selesai (tests pass, lint clean, alembic ok). Security fixes (default secrets, compose) masih butuh override prod.
M2 (Revenue MVP) — produk page, comparison, buying guide, search, collections: frontend pages sudah ada (produk, artikel, kategori, sitemap, robots); backend API lengkap. Vertical slice M2 siap, tapi belum diuji end-to-end (tidak ada backend server yang sedang jalan saat audit).
M3 (AI Operations) — disabled; hanya deterministik.
M4+ — belum.

Langkah berikut (user tunggu brief tambahan):
- User sudah berikan brief tambahan tapi belum paste isi lengkapnya; gw hold sesuai aturan (tunggu sinyal eksekusi).
- Begitu user konfirmasi lanjut, gw akan mulai Langkah 3-5 dari master command (Product Spec, Domain Model, Architecture, Security fixes) dan buat agent files di .hermes/agents/affiloom/.
