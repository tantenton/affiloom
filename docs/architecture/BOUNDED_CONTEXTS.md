# Bounded Contexts (M7)

## 1. Catalog Context
**Purpose**: Product discovery, merchant offers, sync, freshness tracking.
**Owner**: Backend Worker
**Entities**: Product, Merchant, Offer, SyncRun
**API boundary**: `/api/products`, `/api/categories`
**Rules**: Never fabricate products. Mark inactive instead of deleting. Freshness label required on stale data (>24h).

## 2. Content Context
**Purpose**: Editorial articles, buying guides, product linking.
**Owner**: Content / Editorial Agent
**Entities**: Site, ArticleCategory, Article, ArticleProduct
**API boundary**: `/api/articles`, `/api/content`
**Rules**: AI-generated body must have `ai_provider` recorded. No thin content. Disclosure required near affiliate links.

## 3. Collections Context
**Purpose**: Curated product lists, shareable collections.
**Owner**: Frontend Worker
**Entities**: Collection, CollectionProduct
**API boundary**: `/api/collections`
**Rules**: Collections are editorial — cannot be auto-published without review.

## 4. Analytics Context
**Purpose**: Anonymous event tracking, funnel analytics, affiliate attribution.
**Owner**: Analytics / Growth Agent
**Entities**: Pageview, CtaClick
**API boundary**: `/api/track`, `/api/admin/dashboard`
**Rules**: No PII stored. IP is hashed. Click fraud detection is future work.

## 5. Affiliate Context
**Purpose**: Affiliate link routing, redirect tracking, link health, disclosure.
**Owner**: Affiliate Integration Agent
**Entities**: AffiliateLink (future), CtaClick
**API boundary**: `/api/outbound`
**Rules**: All affiliate links go through centralized redirect. rel=sponsored enforced. Destination changes require admin approval.

## 6. Admin Context
**Purpose**: Content approval, sync control, feature flags, audit.
**Owner**: Program Manager
**Entities**: SyncRun, Article (draft), AdminAuditLog
**API boundary**: `/api/admin/*`
**Rules**: RBAC enforced. All mutations logged. Mass publish requires explicit approval.
