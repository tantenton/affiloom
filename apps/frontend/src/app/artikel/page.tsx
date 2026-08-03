import { Metadata } from "next";
import Link from "next/link";

import { AffiliateDisclosure } from "@/components/AffiliateDisclosure";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { listArticles, listCategories } from "@/lib/api";
import { ArticleListItem } from "@/lib/types";

export const dynamic = "force-dynamic";

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const metadata: Metadata = {
  title: "Artikel & Panduan Belanja — Affiloom",
  description:
    "Panduan belanja afiliasi berbahasa Indonesia. Rekomendasi produk transparan dari mitra marketplace resmi.",
  alternates: { canonical: `${siteUrl}/artikel` },
  openGraph: {
    title: "Artikel & Panduan Belanja — Affiloom",
    description:
      "Panduan belanja afiliasi berbahasa Indonesia. Transparan, beretika, dan siap menskalakan.",
    locale: "id_ID",
    type: "website",
    url: `${siteUrl}/artikel`,
  },
};

type SearchParams = {
  kategori?: string;
};

export default async function ArtikelPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const kategori = (searchParams.kategori ?? "").trim() || undefined;

  let articles;
  let categories;
  let errored = false;
  try {
    [articles, categories] = await Promise.all([
      listArticles({ category: kategori, limit: 30 }),
      listCategories(),
    ]);
  } catch {
    errored = true;
  }

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    name: "Artikel Affiloom",
    inLanguage: "id-ID",
    url: `${siteUrl}/artikel`,
    hasPart: (articles?.items ?? []).map((a) => ({
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
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
              Artikel & Panduan Belanja
            </h1>
            <p className="mt-2 max-w-2xl text-slate-600">
              Kurasi konten SEO berbahasa Indonesia. Setiap artikel merujuk
              pada produk afiliasi dari mitra resmi.
            </p>
          </div>
        </div>

        <div className="mt-6">
          <AffiliateDisclosure />
        </div>

        {categories && categories.items.length > 0 ? (
          <nav
            aria-label="Kategori artikel"
            className="mt-6 flex flex-wrap gap-2"
          >
            <CategoryChip href="/artikel" active={!kategori}>
              Semua
            </CategoryChip>
            {categories.items.map((cat) => (
              <CategoryChip
                key={cat.id}
                href={`/artikel?kategori=${encodeURIComponent(cat.slug)}`}
                active={kategori === cat.slug}
              >
                {cat.name}
              </CategoryChip>
            ))}
          </nav>
        ) : null}

        {errored ? (
          <ErrorState />
        ) : !articles || articles.items.length === 0 ? (
          <EmptyState kategori={kategori} />
        ) : (
          <ArticleGrid items={articles.items} total={articles.total} />
        )}
      </main>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <SiteFooter />
    </div>
  );
}

function CategoryChip({
  href,
  active,
  children,
}: {
  href: string;
  active: boolean;
  children: React.ReactNode;
}) {
  const base = "rounded-full border px-3 py-1 text-sm";
  const cls = active
    ? `${base} border-slate-900 bg-slate-900 text-white`
    : `${base} border-slate-300 bg-white text-slate-700 hover:bg-slate-100`;
  return (
    <Link href={href} className={cls}>
      {children}
    </Link>
  );
}

function ArticleGrid({
  items,
  total,
}: {
  items: ArticleListItem[];
  total: number;
}) {
  return (
    <section className="mt-8" aria-label="Daftar artikel">
      <p className="text-sm text-slate-500">
        Menampilkan {items.length} dari {total} artikel.
      </p>
      <ul className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
        {items.map((article) => (
          <li key={article.id} className="h-full">
            <Link
              href={`/artikel/${article.slug}`}
              className="flex h-full flex-col gap-2 rounded-lg border bg-white p-5 transition-shadow hover:shadow-md focus:outline-none focus:ring-2 focus:ring-slate-900"
            >
              {article.category ? (
                <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  {article.category.name}
                </span>
              ) : null}
              <h2 className="text-lg font-semibold text-slate-900">
                {article.title}
              </h2>
              {article.excerpt ? (
                <p className="text-sm text-slate-600">{article.excerpt}</p>
              ) : null}
              {article.published_at ? (
                <p className="mt-auto text-xs text-slate-400">
                  Terbit{" "}
                  {new Date(article.published_at).toLocaleDateString("id-ID")}
                </p>
              ) : null}
            </Link>
          </li>
        ))}
      </ul>
    </section>
  );
}

function EmptyState({ kategori }: { kategori?: string }) {
  return (
    <section className="mt-8 rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center">
      <h2 className="text-lg font-semibold text-slate-900">
        Belum ada artikel
      </h2>
      <p className="mt-2 text-slate-600">
        {kategori
          ? `Belum ada artikel pada kategori "${kategori}".`
          : "Belum ada artikel yang dipublikasikan. Cek kembali sebentar lagi."}
      </p>
      {kategori ? (
        <Link
          href="/artikel"
          className="mt-4 inline-block rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
        >
          Reset filter
        </Link>
      ) : null}
    </section>
  );
}

function ErrorState() {
  return (
    <section
      role="alert"
      className="mt-8 rounded-lg border border-red-200 bg-red-50 p-6 text-red-900"
    >
      <h2 className="text-lg font-semibold">Gagal memuat artikel</h2>
      <p className="mt-2 text-sm">
        Layanan konten sedang tidak dapat dihubungi. Coba muat ulang halaman
        beberapa saat lagi.
      </p>
    </section>
  );
}
