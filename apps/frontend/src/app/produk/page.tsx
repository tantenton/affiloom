import { Metadata } from "next";
import Link from "next/link";

import { AffiliateDisclosure } from "@/components/AffiliateDisclosure";
import { ProductCard } from "@/components/ProductCard";
import { SearchForm } from "@/components/SearchForm";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { listProducts } from "@/lib/api";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Katalog Produk Afiliasi — Affiloom",
  description:
    "Jelajahi katalog produk afiliasi dari marketplace Indonesia. Data disajikan lewat adaptor demo deterministik, tanpa scraping.",
  openGraph: {
    title: "Katalog Produk Afiliasi — Affiloom",
    description:
      "Katalog produk afiliasi Indonesia. Transparan, beretika, dan siap menskalakan.",
    locale: "id_ID",
    type: "website",
  },
};

type SearchParams = {
  q?: string;
  category?: string;
};

const PRODUCT_CATEGORIES = [
  "Fashion",
  "Peralatan",
  "Kuliner",
  "Rumah Tangga",
  "Alat Tulis",
  "Elektronik",
  "Olahraga",
  "Kecantikan",
];

function categoryHref(q: string, category?: string) {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (category) params.set("category", category);
  const query = params.toString();
  return `/produk${query ? `?${query}` : ""}`;
}

export default async function ProdukPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const query = (searchParams.q ?? "").trim();
  const category = (searchParams.category ?? "").trim();

  let data;
  let errored = false;
  try {
    data = await listProducts({ q: query || undefined, category: category || undefined, limit: 24 });
  } catch {
    errored = true;
  }

  return (
    <div className="min-h-screen pb-16 sm:pb-0" style={{ background: "rgb(var(--color-bg))" }}>
      <SiteHeader />

      <main className="mx-auto w-full max-w-7xl px-4 py-6 sm:py-10">
        {/* Breadcrumb */}
        <nav aria-label="Breadcrumb" className="mb-4 text-xs text-stone-500">
          <Link href="/" className="hover:underline">Beranda</Link>
          <span className="mx-1.5">/</span>
          <span className="font-medium text-stone-900">
            {category || "Katalog"}
          </span>
        </nav>

        {/* Hero + Category description */}
        <header className="mb-6 sm:mb-8">
          <p className="section-label">{category ? "Kategori" : "Katalog"}</p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl lg:text-4xl" style={{ color: "rgb(var(--color-text))" }}>
            {category || "Semua Produk"}
          </h1>
          <p className="mx-auto mt-2 max-w-2xl text-sm leading-relaxed" style={{ color: "rgb(var(--color-text-muted))" }}>
            {category
              ? `Produk pilihan kategori ${category} dari marketplace Indonesia. Komisi tercantum transparan.`
              : "Jelajahi produk afiliasi kurasi dari berbagai kategori. Komisi tercantum transparan."}
          </p>
        </header>

        {/* Search */}
        <div className="mb-4">
          <SearchForm defaultValue={query} />
        </div>

        {/* Category chips — horizontal scroll on mobile */}
        <div className="mb-6 flex items-center gap-3">
          <span className="hidden text-xs font-semibold uppercase tracking-wider sm:block" style={{ color: "rgb(var(--color-text-muted))", flexShrink: 0 }}>
            Kategori
          </span>
          <nav
            aria-label="Filter kategori"
            className="flex gap-2 overflow-x-auto pb-1"
            style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
          >
            <CategoryChip href={categoryHref(query)} active={!category}>
              Semua
            </CategoryChip>
            {PRODUCT_CATEGORIES.map((cat) => (
              <CategoryChip
                key={cat}
                href={categoryHref(query, cat)}
                active={category === cat}
              >
                {cat}
              </CategoryChip>
            ))}
          </nav>
        </div>

        {/* Results */}
        {errored ? (
          <ErrorState />
        ) : !data || data.items.length === 0 ? (
          <EmptyState query={query} />
        ) : (
          <ResultsGrid items={data.items} total={data.total} query={data.query} />
        )}

        {/* Affiliate disclosure */}
        <div className="mt-12">
          <AffiliateDisclosure />
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}

function ResultsGrid({
  items,
  total,
  query,
}: {
  items: Awaited<ReturnType<typeof listProducts>>["items"];
  total: number;
  query: string | null;
}) {
  return (
    <section aria-label="Hasil produk">
      <p className="mb-4 text-sm text-gray-500">
        <span className="font-semibold text-gray-900">{items.length}</span> dari{" "}
        <span className="font-semibold text-gray-900">{total}</span> produk
        {query ? (
          <> untuk &ldquo;<span className="font-medium text-gray-900">{query}</span>&rdquo;</>
        ) : null}
      </p>
      {/* Mobile: 2 col, tablet: 3 col, desktop: 4 col */}
      <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4 lg:gap-5">
        {items.map((item) => (
          <li key={item.id}>
            <ProductCard product={item} />
          </li>
        ))}
      </ul>
    </section>
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
  return (
    <Link
      href={href}
      className={`chip flex-shrink-0${active ? " chip-active" : ""}`}
    >
      {children}
    </Link>
  );
}

function EmptyState({ query }: { query: string }) {
  return (
    <section className="mt-8 rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center">
      <h2 className="text-lg font-semibold text-slate-900">
        Tidak ada produk yang cocok
      </h2>
      <p className="mt-2 text-slate-600">
        {query
          ? `Kami belum menemukan produk untuk "${query}". Coba kata kunci lain.`
          : "Katalog kosong. Silakan cek kembali nanti."}
      </p>
      {query ? (
        <Link
          href="/produk"
          className="btn-primary mt-6"
        >
          Reset pencarian
        </Link>
      ) : null}
    </section>
  );
}

function ErrorState() {
  return (
    <section
      role="alert"
      className="mt-8 rounded-2xl border border-red-200 bg-red-50 p-6 text-red-900"
    >
      <h2 className="text-lg font-semibold">Gagal memuat katalog</h2>
      <p className="mt-2 text-sm">
        Layanan katalog sedang tidak dapat dihubungi. Coba muat ulang halaman
        beberapa saat lagi.
      </p>
    </section>
  );
}

