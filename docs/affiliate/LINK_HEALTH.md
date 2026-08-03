# Link Health (M5-003)

## Policy
- All outbound affiliate URLs must be validated before being rendered.
- Only `http` and `https` schemes are allowed.
- `javascript:`, `data:`, and other schemes are rejected (link-injection defense).
- Broken or inactive links must be flagged and hidden from public pages.

## Implementation
- `apps/backend/services/link_health.py` — HEAD-then-GET probe with bounded timeout, batch checker with concurrency limit.
- URL validation rejects non-http(s) schemes.

## Fallback
- If a merchant link is unhealthy, the product card shows "Tidak tersedia" and hides the CTA instead of linking to a dead URL.
