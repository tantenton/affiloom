# Affiloom Product Spec (M7)

## 1. Target User
- **Geography**: Indonesia
- **Device**: Mobile-first (60% mobile traffic expected)
- **Need**: Product discovery, comparison, buying guidance before purchase decision
- **Pain**: Information overload, fake reviews, thin affiliate content, stale prices
- **Gain**: Trusted recommendations, transparent affiliate disclosure, freshness labels

## 2. Core User Journeys (MVP)
1. **Search by need**: "laptop untuk pelajar" → relevant products + buying guide
2. **Browse category**: Fashion → product grid with freshness badges
3. **Open product detail**: see price, merchant, commission, freshness, compare link
4. **Compare products**: side-by-side comparison of 2-4 items
5. **Read buying guide**: top pick, budget pick, upgrade pick with methodology
6. **Explore collection**: curated list (e.g., "Setup Kerja Minimalis")
7. **Ask recommendation assistant**: (future) chat-based product Q&A
8. **Click merchant CTA**: outbound redirect with click logging
9. **Report stale/wrong data**: (future) user correction form
10. **Return and save shortlist**: (future) wishlist / bookmarks

## 3. MVP Public Pages
- Homepage: dark hero, category pills, featured products, buying guide tease
- Search: `/produk?q=...`
- Category: `/produk?category=Fashion`
- Product detail: `/produk/[id]`
- Comparison: `/compare?ids=...`
- Buying guide: `/artikel/[slug]`
- Collections: `/koleksi`, `/koleksi/[slug]`
- Disclosure: `/pengungkapan-afiliasi`
- Methodology: `/metodologi`
- Privacy: `/privasi`
- Terms: `/syarat-ketentuan`
- Contact/Report: `/kontak`
- Sitemap: `/sitemap`
- Robots: `/robots.txt`

## 4. Admin Pages
- Products: list, edit, activate/deactivate
- Offers: manage merchant offers
- Sync: trigger sync, view history
- Drafts: review AI-generated articles
- Collections: create/edit curated lists
- Analytics: dashboard with pageview, CTA click stats
- Audit log: admin action history
- Feature flags: toggle AI features, merchant adapters

## 5. Non-Functional Requirements
- Mobile-first responsive design
- < 3s Time to Interactive (TTI)
- WCAG 2.1 AA compliance (manual testing required)
- SEO-friendly (structured data, canonical URLs, sitemap)
- Transparent affiliate disclosure on all pages with links
- No fake reviews, no fabricated test results
- Prices display freshness timestamp
