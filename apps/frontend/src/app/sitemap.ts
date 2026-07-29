import type { MetadataRoute } from "next";

import { getSitemap } from "@/lib/api";

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

/**
 * The backend owns the canonical URL list. This route proxies its `/api/sitemap`
 * response into the Next.js metadata sitemap format so every URL surfaced in
 * `/sitemap.xml` is the same set the backend advertises — no drift between
 * dev/staging/prod and no static list to hand-maintain.
 */
export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  try {
    const { entries } = await getSitemap();
    return entries.map((e) => ({
      url: new URL(e.loc, siteUrl).toString(),
      lastModified: new Date(e.lastmod),
      changeFrequency:
        (e.changefreq as MetadataRoute.Sitemap[number]["changeFrequency"]) ??
        "weekly",
      priority: e.priority,
    }));
  } catch {
    // Never blow up on build: return a minimal static map so the sitemap
    // endpoint still resolves during CI or offline builds.
    return [
      { url: `${siteUrl}/`, changeFrequency: "weekly", priority: 1.0 },
      { url: `${siteUrl}/produk`, changeFrequency: "daily", priority: 0.9 },
      { url: `${siteUrl}/artikel`, changeFrequency: "daily", priority: 0.8 },
    ];
  }
}
