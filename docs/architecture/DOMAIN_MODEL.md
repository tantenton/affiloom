# Domain Model (M7)

## Entities & Relationships

### Catalog
- **Product**: deduplicated catalog row (id, title, description, category, image_url, is_active)
  - FK: merchant_id → Merchant
  - Relationship: 1 Product → N Offer
- **Merchant**: affiliate provider partition (id, slug, display_name, is_active)
  - Relationship: 1 Merchant → N Product
  - Relationship: 1 Merchant → N SyncRun
- **Offer**: price/currency/deep-link observation (id, product_id, source, url, price, currency, commission_rate, is_active, last_seen_at)
  - FK: product_id → Product
  - Natural key: (product_id, source)
- **SyncRun**: ingest attempt tracking (id, merchant_id, status, products_seen, products_created, products_updated, started_at, finished_at)
  - FK: merchant_id → Merchant

### Content
- **Site**: domain surface (id, slug, domain, name, language, is_active)
  - Relationship: 1 Site → N ArticleCategory
  - Relationship: 1 Site → N Article
- **ArticleCategory**: editorial category (id, site_id, slug, name, description, is_active)
  - FK: site_id → Site
  - Relationship: 1 Category → N Article
- **Article**: SEO article (id, site_id, category_id, slug, title, excerpt, body_md, status, ai_provider, published_at)
  - FK: site_id → Site, category_id → ArticleCategory (nullable)
  - Relationship: 1 Article → N ArticleProduct
- **ArticleProduct**: internal link (id, article_id, product_id, position, score)
  - FK: article_id → Article, product_id → Product

### Collections (M7)
- **Collection**: curated product list (id, slug, title, description, is_active)
  - Relationship: 1 Collection → N CollectionProduct
- **CollectionProduct**: collection membership (id, collection_id, product_id, position)
  - FK: collection_id → Collection, product_id → Product

### Analytics (M4)
- **Pageview**: anonymous pageview event (id, path, referrer, user_agent, ip_hash, created_at)
- **CtaClick**: affiliate CTA click (id, product_id, article_id, url, ip_hash, created_at)
  - FK: product_id → Product (nullable), article_id → Article (nullable)

### Provenance (Future)
- **Source**: external data source (URL, API endpoint, feed)
- **Evidence**: claim supporting evidence (fact, source_id, retrieved_at, confidence)
- **Claim**: factual claim (product_id, claim_type, value, evidence_id)
