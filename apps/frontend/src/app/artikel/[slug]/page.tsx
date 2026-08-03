import { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { AffiliateDisclosure } from "@/components/AffiliateDisclosure";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { getArticle } from "@/lib/api";
import { Article, NotFoundError } from "@/lib/types";

export const dynamic = "force-dynamic";

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
      robots: { index: false, follow: false },
    };
  }
  return {
    title: article.meta_title ?? `${article.title} — Affiloom`,
    description: article.meta_description ?? article.excerpt ?? article.title,
    alternates: { canonical: article.canonical_path },
    openGraph: {
      title: article.meta_title ?? article.title,
      description: article.meta_description ?? article.excerpt ?? article.title,
      type: "article",
      locale: "id_ID",
      publishedTime: article.published_at ?? undefined,
      modifiedTime: article.updated_at,
    },
  };
}

function renderMarkdown(markdown: string): string[] {
  return markdown
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);
}

export default async function ArtikelDetailPage({
  params,
}: {
  params: Params;
}) {
  const article = await loadArticle(params.slug);
  if (!article) notFound();

  const paragraphs = renderMarkdown(article.body_md);
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: article.title,
    description: article.meta_description ?? article.excerpt ?? article.title,
    datePublished: article.published_at ?? undefined,
    dateModified: article.updated_at,
    inLanguage: article.language,
    mainEntityOfPage: article.canonical_path,
  };

  return (
    <div className="min-h-screen bg-slate-50 pb-20 sm:pb-0">
      <SiteHeader />
      <main className="mx-auto max-w-4xl px-4 py-10">
        <nav aria-label="Breadcrumb" className="mb-8 text-sm text-slate-500">
          <Link href="/artikel" className="hover:text-slate-900">
            ← Kembali ke artikel
          </Link>
        </nav>

        <article className="rounded-lg border bg-white p-6 shadow-sm md:p-10">
          {article.category ? (
            <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
              {article.category.name}
            </span>
          ) : null}
          <h1 className="mt-3 text-3xl font-bold tracking-tight text-slate-900 md:text-4xl">
            {article.title}
          </h1>
          {article.excerpt ? (
            <p className="mt-4 text-lg leading-relaxed text-slate-600">
              {article.excerpt}
            </p>
          ) : null}
          <div className="mt-5 flex flex-wrap gap-3 text-xs text-slate-400">
            {article.published_at ? (
              <span>
                Terbit {new Date(article.published_at).toLocaleDateString("id-ID")}
              </span>
            ) : null}
            <span>
              Diperbarui {new Date(article.updated_at).toLocaleDateString("id-ID")}
            </span>
          </div>

          <div className="mt-8 space-y-4 leading-7 text-slate-700">
            {paragraphs.map((paragraph, index) => {
              if (paragraph.startsWith("# ")) {
                return (
                  <h2 key={index} className="pt-4 text-2xl font-bold text-slate-900">
                    {paragraph.slice(2)}
                  </h2>
                );
              }
              if (paragraph.startsWith("## ")) {
                return (
                  <h3 key={index} className="pt-3 text-xl font-semibold text-slate-900">
                    {paragraph.slice(3)}
                  </h3>
                );
              }
              return <p key={index}>{paragraph}</p>;
            })}
          </div>

          {article.products.length > 0 ? (
            <section className="mt-10 border-t pt-8" aria-labelledby="produk-terkait">
              <h2 id="produk-terkait" className="text-2xl font-bold text-slate-900">
                Produk terkait
              </h2>
              <p className="mt-2 text-sm text-slate-600">
                Produk di bawah berasal dari data katalog. Komisi tidak memengaruhi urutan editorial.
              </p>
              <ul className="mt-4 grid gap-4 sm:grid-cols-2">
                {article.products.map((product) => (
                  <li key={product.id} className="rounded-lg border p-4">
                    {product.image_url ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={product.image_url}
                        alt={product.title}
                        className="aspect-video w-full rounded object-cover"
                      />
                    ) : null}
                    <h3 className="mt-3 font-semibold text-slate-900">{product.title}</h3>
                    {product.category ? (
                      <p className="mt-1 text-xs text-slate-500">{product.category}</p>
                    ) : null}
                    <a
                      href={product.url}
                      target="_blank"
                      rel="sponsored nofollow noopener noreferrer"
                      className="mt-3 inline-block rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
                    >
                      Lihat di mitra
                    </a>
                  </li>
                ))}
              </ul>
            </section>
          ) : null}

          <div className="mt-8">
            <AffiliateDisclosure variant="inline" />
          </div>
        </article>
      </main>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <SiteFooter />
    </div>
  );
}
