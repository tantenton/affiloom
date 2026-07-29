import { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { AffiliateDisclosure } from "@/components/AffiliateDisclosure";
import { SiteHeader } from "@/components/SiteHeader";
import { getCategory, listArticles } from "@/lib/api";
import { Category, NotFoundError } from "@/lib/types";

export const dynamic = "force-dynamic";

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

type Params = { slug: string };

async function loadCategory(slug: string): Promise<Category | null> {
  try {
    return await getCategory(slug);
  } catch (error) {
    if (error instanceof NotFoundError) return null;
    throw error;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const cat = await loadCategory(params.slug);
  if (!cat) {
    return {
      title: "Kategori tidak ditemukan — Affiloom",
      description: "Kategori yang kamu cari tidak tersedia di Affiloom.",
      robots: { index: false, follow: false },
    };
  }
  const canonicalUrl = `${siteUrl}/kategori/${cat.slug}`;
  return {
    title: `${cat.name} — Affiloom`,
    description:
      cat.description ?? `Artikel dan panduan pada kategori ${cat.name}.`,
    alternates: { canonical: canonicalUrl },
    openGraph: {
      title: `${cat.name} — Affiloom`,
      description:
        cat.description ?? `Artikel dan panduan pada kategori ${cat.name}.`,
      locale: "id_ID",
      type: "website",
      url: canonicalUrl,
    },
  };
}

export default async function KategoriPage({
  params,
}: {
  params: Params;
}) {
  const cat = await loadCategory(params.slug);
  if (!cat) {
    notFound();
  }

  const canonicalUrl = `${siteUrl}/kategori/${cat.slug}`;
  const articles = await listArticles({ category: cat.slug, limit: 30 });

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: cat.name,
    description: cat.description ?? undefined,
    inLanguage: "id-ID",
    url: canonicalUrl,
    hasPart: articles.items.map((a) => ({
      "@type": "Article",
      headline: a.title,
      inLanguage: a.language,
      url: `${siteUrl}${a.canonical_path || `/artikel/${a.slug}`}`,
      datePublished: a.published_at ?? undefined,
      dateModified: a.updated_at,
    })),
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />

      <main className="mx-auto max-w-5xl px-4 py-10">
        <nav aria-label="Breadcrumb" className="mb-6 text-sm text-slate-500">
          <Link href="/artikel" className="hover:text-slate-900">
            ← Semua artikel
          </Link>
        </nav>

        <header>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">
            {cat.name}
          </h1>
          {cat.description ? (
            <p className="mt-2 max-w-2xl text-slate-600">{cat.description}</p>
          ) : null}
          <p className="mt-2 text-sm text-slate-500">
            {cat.article_count} artikel dipublikasikan pada kategori ini.
          </p>
        </header>

        <div className="mt-6">
          <AffiliateDisclosure />
        </div>

        {articles.items.length === 0 ? (
          <section className="mt-8 rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center">
            <h2 className="text-lg font-semibold text-slate-900">
              Belum ada artikel pada kategori ini
            </h2>
            <p className="mt-2 text-slate-600">
              Silakan kembali sebentar lagi atau jelajahi{" "}
              <Link href="/artikel" className="underline">
                semua artikel
              </Link>
              .
            </p>
          </section>
        ) : (
          <ul className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2">
            {articles.items.map((article) => (
              <li key={article.id} className="h-full">
                <Link
                  href={`/artikel/${article.slug}`}
                  className="flex h-full flex-col gap-2 rounded-lg border bg-white p-5 transition-shadow hover:shadow-md focus:outline-none focus:ring-2 focus:ring-slate-900"
                >
                  <h2 className="text-lg font-semibold text-slate-900">
                    {article.title}
                  </h2>
                  {article.excerpt ? (
                    <p className="text-sm text-slate-600">{article.excerpt}</p>
                  ) : null}
                  {article.published_at ? (
                    <p className="mt-auto text-xs text-slate-400">
                      Terbit{" "}
                      {new Date(article.published_at).toLocaleDateString(
                        "id-ID",
                      )}
                    </p>
                  ) : null}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </main>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </div>
  );
}
