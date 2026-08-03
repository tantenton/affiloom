# Affiliate Policy Registry (M5)

## 1. Compliance Rules
- **Disclosure**: Every affiliate link or call-to-action must be accompanied by a clear affiliate disclosure (`AffiliateDisclosure` component).
- **No Fake Claims**: Editorial ratings and summaries are independent of affiliate commission rates. Commission rates must never influence product score or rank.
- **Link Hygiene**: All outbound affiliate links must use the centralized redirect service (`/api/outbound/go`) which enforces `rel="sponsored nofollow noopener noreferrer"` equivalent attributes and tracks clicks.
- **Timestamp Freshness**: Prices and stock data must display freshness timestamps. Stale data (>24h without sync) is explicitly labeled.
