# Threat Model (M7)

## 1. Scope
Affiloom web platform: FastAPI backend, Next.js frontend, SQLite/PostgreSQL, affiliate redirect service, AI content pipeline.

## 2. Threats

| # | Threat | Vector | Impact |
|---|--------|--------|--------|
| T1 | Account Takeover | Brute force admin token, credential stuffing | Full admin access, affiliate destination change |
| T2 | Broken Access Control | Missing auth check on admin endpoints | Data exposure, unauthorized mutations |
| T3 | XSS | Reflected/stored in product titles, article body | Session hijack, click fraud injection |
| T4 | SQL Injection | Unsanitized query params | Data exfiltration, data destruction |
| T5 | CSRF | State-changing GET/POST without CSRF token | Unauthorized admin actions |
| T6 | SSRF | Unvalidated outbound URLs (link health, AI fetch) | Internal network access, metadata exfiltration |
| T7 | Prompt Injection | Malicious content in product/article fields passed to LLM | Hallucinated claims, data exfiltration via model |
| T8 | Click Fraud | Automated outbound clicks on affiliate links | Commission fraud, merchant ban |
| T9 | Affiliate Link Replacement | MITM or backend compromise replacing target URLs | Revenue theft, phishing |
| T10 | Data Poisoning | Malicious merchant feed injecting fake prices/specs | User harm, false claims, legal liability |
| T11 | DoS | Rate limit bypass, large payload, slow request | Service unavailability |
| T12 | Secret Leakage | API keys in logs, git history, error responses | Credential compromise |

## 3. Trust Boundaries
- Public internet → FastAPI backend (rate-limited, validated)
- FastAPI backend → AI provider (API key, cost limit)
- FastAPI backend → Merchant adapter (partner API only, no scraping)
- Admin token → Admin endpoints (RBAC enforced in code)
