# Merchant Adapter Specification (M5)

## 1. Overview
Affiloom requires all marketplace and merchant integrations to conform to strict partner compliance standards. Unofficial scraping, automated scraping browsers, or reverse-engineered private endpoints are strictly prohibited.

## 2. Mandatory Capabilities per Adapter
Every concrete merchant adapter MUST implement:
- Capability declaration (supported features, sync type, feed vs API)
- Configuration validation (API keys, partner IDs, affiliate tags)
- Timeouts and retry with exponential backoff
- Circuit breaker / rate limiter
- Price and stock freshness timestamps
- Idempotent upsert logic
- Safe handling of missing records (mark inactive, never delete history)
- No fabrication of data
- Structured logging without secrets
- Health check endpoint / status indicator

## 3. Supported Networks (Indonesia)
- Tokopedia Affiliate API (Official partner integration)
- Shopee Affiliate Partner API (Official partner integration)
- Blibli / Bukalapak / Lazada Affiliate Feeds (When partner access approved)
- Deterministic Sandbox Adapter (For development and testing)
