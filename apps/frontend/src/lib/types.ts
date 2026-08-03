export type Product = {
  id: string;
  source: string;
  title: string;
  url: string;
  image_url: string | null;
  price: number | null;
  currency: string | null;
  commission_rate: number | null;
  category: string | null;
  description: string | null;
  last_seen_at: string;
};

export type ProductListResponse = {
  items: Product[];
  total: number;
  limit: number;
  offset: number;
  query: string | null;
};

export class NotFoundError extends Error {
  constructor(message = "Not found") {
    super(message);
    this.name = "NotFoundError";
  }
}

export type Category = {
  id: string;
  slug: string;
  name: string;
  description: string | null;
  article_count: number;
};

export type CategoryListResponse = {
  items: Category[];
  total: number;
};

export type ArticleProduct = {
  id: string;
  product_id: string;
  external_id: string;
  title: string;
  url: string;
  image_url: string | null;
  category: string | null;
  score: number;
  position: number;
};

export type Article = {
  id: string;
  slug: string;
  title: string;
  excerpt: string | null;
  body_md: string;
  meta_title: string | null;
  meta_description: string | null;
  canonical_path: string;
  language: string;
  status: "draft" | "published" | "archived";
  category: Category | null;
  products: ArticleProduct[];
  published_at: string | null;
  updated_at: string;
};

export type ArticleListItem = {
  id: string;
  slug: string;
  title: string;
  excerpt: string | null;
  meta_title: string | null;
  meta_description: string | null;
  canonical_path: string;
  language: string;
  status: "draft" | "published" | "archived";
  category: Category | null;
  published_at: string | null;
  updated_at: string;
};

export type ArticleListResponse = {
  items: ArticleListItem[];
  total: number;
  limit: number;
  offset: number;
  category: string | null;
};

export type Site = {
  id: string;
  slug: string;
  domain: string;
  name: string;
  tagline: string | null;
  language: string;
  default_locale: string;
};

export type SitemapEntry = {
  loc: string;
  changefreq: string;
  priority: number;
  lastmod: string;
};

export type SitemapResponse = { entries: SitemapEntry[] };

export type RobotsRule = {
  user_agent: string;
  allow: string;
  disallow: string[];
};

export type RobotsResponse = {
  rules: RobotsRule[];
  sitemaps: string[];
};

export type CollectionSummary = { id: string; slug: string; title: string; description: string | null; product_count: number; };
export type CollectionProductItem = { id: string; title: string; image_url: string | null; price: number | null; currency: string | null; category: string | null; };
export type CollectionDetail = { id: string; slug: string; title: string; description: string | null; products: CollectionProductItem[]; };
