import type { MetadataRoute } from "next";

import { getRobots } from "@/lib/api";

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

/**
 * Same idea as sitemap.ts: backend owns the source-of-truth for robots
 * directives so we can update the policy without redeploying the frontend.
 */
export default async function robots(): Promise<MetadataRoute.Robots> {
  try {
    const { rules, sitemaps } = await getRobots();
    return {
      rules: rules.map((r) => ({
        userAgent: r.user_agent,
        allow: r.allow,
        disallow: r.disallow,
      })),
      sitemap: sitemaps.map((s) => new URL(s, siteUrl).toString()),
    };
  } catch {
    return {
      rules: [{ userAgent: "*", allow: "/", disallow: ["/api/admin/"] }],
      sitemap: `${siteUrl}/sitemap.xml`,
    };
  }
}
