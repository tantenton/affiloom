import {
  Article,
  ArticleListResponse,
  Category,
  CategoryListResponse,
  NotFoundError,
  Product,
  ProductListResponse,
  RobotsResponse,
  Site,
  SitemapResponse,
} from "./types";

/**
 * Backend base URL used on the server. Falls back to the compose service name
 * when the app is running inside Docker, and to localhost during local dev.
 */
function apiBaseUrl(): string {
  return (
    process.env.INTERNAL_API_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    "http://localhost:8000"
  );
}

type FetchOptions = {
  signal?: AbortSignal;
  /**
   * Revalidation window in seconds. The catalog is static demo data, so a
   * short window is plenty and keeps the pages snappy in production.
   */
  revalidate?: number;
};

async function apiFetch<T>(path: string, opts: FetchOptions = {}): Promise<T> {
  const url = `${apiBaseUrl().replace(/\/$/, "")}${path}`;
  const response = await fetch(url, {
    signal: opts.signal,
    next: { revalidate: opts.revalidate ?? 60 },
    headers: { Accept: "application/json" },
  });

  if (response.status === 404) {
    throw new NotFoundError();
  }
  if (!response.ok) {
    throw new Error(`API ${response.status} for ${path}`);
  }
  return (await response.json()) as T;
}

export type ListProductsParams = {
  q?: string;
  category?: string;
  limit?: number;
  offset?: number;
};

export async function listProducts(
  params: ListProductsParams = {},
  opts: FetchOptions = {},
): Promise<ProductListResponse> {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (params.category) search.set("category", params.category);
  if (params.limit != null) search.set("limit", String(params.limit));
  if (params.offset != null) search.set("offset", String(params.offset));
  const query = search.toString();
  return apiFetch<ProductListResponse>(
    `/api/products${query ? `?${query}` : ""}`,
    opts,
  );
}

export async function getProduct(
  id: string,
  opts: FetchOptions = {},
): Promise<Product> {
  return apiFetch<Product>(`/api/products/${encodeURIComponent(id)}`, opts);
}

export async function getCurrentSite(opts: FetchOptions = {}): Promise<Site> {
  return apiFetch<Site>("/api/sites/current", opts);
}

export async function listCategories(
  opts: FetchOptions = {},
): Promise<CategoryListResponse> {
  return apiFetch<CategoryListResponse>("/api/categories", opts);
}

export async function getCategory(
  slug: string,
  opts: FetchOptions = {},
): Promise<Category> {
  return apiFetch<Category>(
    `/api/categories/${encodeURIComponent(slug)}`,
    opts,
  );
}

export type ListArticlesParams = {
  category?: string;
  limit?: number;
  offset?: number;
};

export async function listArticles(
  params: ListArticlesParams = {},
  opts: FetchOptions = {},
): Promise<ArticleListResponse> {
  const search = new URLSearchParams();
  if (params.category) search.set("category", params.category);
  if (params.limit != null) search.set("limit", String(params.limit));
  if (params.offset != null) search.set("offset", String(params.offset));
  const query = search.toString();
  return apiFetch<ArticleListResponse>(
    `/api/articles${query ? `?${query}` : ""}`,
    opts,
  );
}

export async function getArticle(
  slug: string,
  opts: FetchOptions = {},
): Promise<Article> {
  return apiFetch<Article>(
    `/api/articles/${encodeURIComponent(slug)}`,
    opts,
  );
}

export async function getSitemap(
  opts: FetchOptions = {},
): Promise<SitemapResponse> {
  return apiFetch<SitemapResponse>("/api/sitemap", opts);
}

export async function getRobots(
  opts: FetchOptions = {},
): Promise<RobotsResponse> {
  return apiFetch<RobotsResponse>("/api/robots", opts);
}
