import { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { AffiliateDisclosure } from "@/components/AffiliateDisclosure";
import { SiteHeader } from "@/components/SiteHeader";
import { getArticle } from "@/lib/api";
import { renderMarkdown } from "@/lib/markdown";
import { Article, NotFoundError } from "@/lib/types";

export const dynamic = "force-dynamic";

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

type Params = { slug: string };

async function loadArticle(slug: string): Promise<Article | null> {
  try {
    return await getArticle(slug);
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
  const article = await loadArticle(params.slug);
  if (!article) {
    return {
      title: "Artikel tidak ditemukan — Affiloom",
      description: "Artikel yang kamu cari tidak tersedia.",
      robots: { index: false, follow: false },
    };
  }
  const canonicalUrl = `${siteUrl}${article.canonical_path || `/artikel/${article.slug}`}`;
  return {
    title: article.meta_title ?? `${article.title} — Affiloom`,
    description:
      article.meta_description ??
      article.excerpt ??
      article.title,
    alternates: { canonical: canonicalUrl },
    openGraph: {
      title: article.meta_title ?? article.title,
      description:
        article.meta_description ??
        article.excerpt ??
        article.title,
      locale: "id_ID",
      type: "article",
      url: canonicalUrl,
    },
  };
}

export default async function ArticlePage({
  params,
}: {
  params: Params;
}) {
  const article = await loadArticle(params.slug);
  if (!article || article.status !== "published") {
    notFound();
  }

  const canonicalUrl = `${siteUrl}${article.canonical_path || `/artikel/${article.slug}`}`;
  const html = renderMarkdown(article.body_md);

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: article.title,
    description: article.meta_description ?? article.excerpt ?? undefined,
    inLanguage: article.language,
    datePublished: article.published_at ?? undefined,
    dateModified: article.updated_at,
    mainEntityOfPage: canonicalUrl,
    author: { "@type": "Organization", name: "Affiloom" },
    publisher: { "@type": "Organization", name: "Affiloom" },
    articleSection: article.category?.name,
    about: article.products.map((p) => ({
      "@type": "Product",
      name: p.title,
      sku: p.external_id,
      category: p.category ?? undefined,
      image: p.image_url ?? undefined,
      offers: {
        "@type": "Offer",
        url: p.url,
      },
    })),
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />

      <main className="mx-auto max-w-3xl px-4 py-10">
        <nav aria-label="Breadcrumb" className="mb-6 text-sm text-slate-500">
          <Link href="/artikel" className="hover:text-slate-900">
            ← Kembali ke artikel
          </Link>
          {article.category ? (
            <>
              <span className="mx-2">/</span>
              <Link
                href={`/kategori/${article.category.slug}`}
                className="hover:text-slate-900"
              >
                {article.category.name}
              </Link>
            </>
          ) : null}
        </nav>

        <header>
          {article.category ? (
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
              {article.category.name}
            </span>
          ) : null}
          <h1 className="mt-1 text-3xl font-bold tracking-tight text-slate-900">
            {article.title}
          </h1>
          {article.excerpt ? (
            <p className="mt-3 text-lg text-slate-600">{article.excerpt}</p>
          ) : null}
          {article.published_at ? (
            <p className="mt-3 text-sm text-slate-400">
              Terbit{" "}
              {new Date(article.published_at).toLocaleDateString("id-ID", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </p>
          ) : null}
        </header>

        <div className="mt-6">
          <AffiliateDisclosure />
        </div>

        <article
          className="prose prose-slate mt-8 max-w-none text-slate-800 [&_h1]:text-2xl [&_h1]:font-semibold [&_h2]:mt-8 [&_h2]:text-xl [&_h2]:font-semibold [&_p]:mt-4 [&_p]:leading-relaxed [&_ul]:mt-4 [&_ul]:list-disc [&_ul]:pl-6 [&_code]:rounded [&_code]:bg-slate-100 [&_code]:px-1"
          dangerouslySetInnerHTML={{ __html: html }}
        />

        {article.products.length > 0 ? (
          <section className="mt-10" aria-label="Produk terkait">
            <h2 className="text-xl font-semibold text-slate-900">
              Produk terkait
            </h2>
            <ul className="mt-4 grid gap-4 sm:grid-cols-2">
              {article.products.map((p) => (
                <li key={p.id} className="rounded-lg border bg-white p-4">
                  <div className="flex flex-col gap-2">
                    {p.category ? (
                      <span className="text-xs uppercase tracking-wide text-slate-500">
                        {p.category}
                      </span>
                    ) : null}
                    <p className="font-medium text-slate-900">{p.title}</p>
                    <div className="mt-2 flex gap-3">
                      <Link
                        href={`/produk/${p.external_id}`}
                        className="rounded-md border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-900 hover:bg-slate-100"
                      >
                        Lihat detail
                      </Link>
                      <a
                        href={p.url}
                        target="_blank"
                        rel="sponsored nofollow noopener noreferrer"
                        className="rounded-md bg-slate-900 px-3 py-2 text-xs font-medium text-white hover:bg-slate-700"
                      >
                        Beli via mitra
                      </a>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        ) : null}
      </main>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
    </div>
  );
}
