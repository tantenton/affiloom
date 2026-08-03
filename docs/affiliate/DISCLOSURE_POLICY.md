# Disclosure Policy (M5)

## 1. Principle
User utility > affiliate commission. Editorial integrity is never sold.

## 2. Rules
- Every page with outbound affiliate links must render an `AffiliateDisclosure` component near the content.
- Each CTA button that links to a merchant must be visibly marked (e.g., "Lihat di merchant") and routed via `/api/outbound/go`.
- Affiliate links must be `rel="sponsored nofollow noopener noreferrer"` for SEO hygiene.
- No dark patterns: no hidden links, no auto-redirects, no deceptive button labels.

## 3. Enforcement
- Frontend components enforce disclosure at render time (Server component default).
- Backend redirect service logs outbound clicks for analytics (CtaClick).
