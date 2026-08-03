# Security Controls (M7)

## 1. Implemented Controls

### SecureHeadersMiddleware (M1-002)
**Location**: `apps/backend/main.py`
**Protection**:
- `X-Content-Type-Options: nosniff` — MIME-type sniffing prevention
- `X-Frame-Options: DENY` — clickjacking defense
- `X-XSS-Protection: 0` — disable legacy XSS filter (CSP preferred)
- `Content-Security-Policy` — script, style, img, font, connect restrictions
- `Referrer-Policy: strict-origin-when-cross-origin`

### Rate Limiting (SlowAPI)
**Location**: `apps/backend/main.py`
**Protection**: 100 requests/minute per IP (default), extensible per-route

### Input Validation (Pydantic)
**Location**: All routers (`routers/*.py`)
**Protection**: Type-safe schema validation on all request bodies, query params

### RBAC (Admin Token)
**Location**: `routers/admin.py` (`_require_admin_token` dependency)
**Protection**: Bearer token validation on `/api/admin/*` endpoints

### Admin Audit Log (M1-005)
**Location**: `middlewares/admin_audit.py`
**Protection**: Logs all admin actions (method, path, user-agent, timestamp) to audit table

### Affiliate Disclosure
**Location**: `components/AffiliateDisclosure.tsx`
**Protection**: Visible disclosure on all pages with affiliate links

### URL Validation (Link Health)
**Location**: `services/link_health.py`
**Protection**: Rejects non-http(s) schemes (SSRF defense), validates URL format before redirect

### Env Schema Validation (M1-004)
**Location**: `config.py` (`validate_security()`)
**Protection**: Startup checks for production secrets (warns if defaults detected)

### CORS Scoping
**Location**: `main.py`
**Protection**: Scoped to configured frontend origin, no wildcard

### Output Encoding
**Protection**: React auto-escapes JSX, Pydantic serializes safely

## 2. Remaining Gaps (Future Work)
- CSRF token enforcement (currently none)
- Webhook signature validation (not implemented)
- Prompt injection: user content not yet delimited in AI calls
- Click fraud detection: no behavioral analysis yet
- Cost ceiling enforcement: circuit breaker code stub exists but not active
