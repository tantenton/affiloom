import { Metadata } from "next";
import Link from "next/link";

import { AffiliateDisclosure } from "@/components/AffiliateDisclosure";
import { EmptyState, ErrorState, ProductGrid } from "@/components/ProductGrid";
import { ProductFilters } from "@/components/ProductFilters";
import { SearchForm } from "@/components/SearchForm";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { SortSelect } from "@/components/SortSelect";
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
  sort?: string;
};

export default async function ProductListingPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const query = searchParams.q || null;
  const category = searchParams.category || null;
  const sort = searchParams.sort || null;

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

      <main className="mx-auto flex w-full max-w-7xl gap-6 px-4 py-6 sm:py-10">
        {/* Left sidebar (desktop only) */}
        <ProductFilters currentCategory={category} currentQuery={query} currentSort={sort} />

        {/* Main content */}
        <div className="min-w-0 flex-1">
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

          {/* Search + sort + mobile filter */}
          <div className="mb-6 flex flex-col gap-3">
            <SearchForm defaultValue={query || undefined} />
            <div className="flex flex-wrap gap-2">
              <SortSelect currentSort={sort} currentCategory={category} currentQuery={query} />
              <div className="lg:hidden">
                <ProductFilters currentCategory={category} currentQuery={query} currentSort={sort} />
              </div>
            </div>
          </div>

          {/* Results */}
          {errored ? (
            <ErrorState />
          ) : !data || data.items.length === 0 ? (
            <EmptyState query={query} />
          ) : (
            <>
              {/* Result count */}
              <div className="mb-4">
                <p className="text-sm" style={{ color: "rgb(var(--color-text-muted))" }}>
                  <span className="font-semibold" style={{ color: "rgb(var(--color-text))" }}>{data.items.length}</span> dari{" "}
                  <span className="font-semibold" style={{ color: "rgb(var(--color-text))" }}>{data.total}</span> produk
                  {data.query && (
                    <> untuk <span className="font-medium" style={{ color: "rgb(var(--color-text))" }}>&ldquo;{data.query}&rdquo;</span></>
                  )}
                </p>
              </div>
              {/* Grid */}
              <ProductGrid items={data.items} />
              {/* Pagination hint */}
              {data.items.length < data.total && (
                <div className="mt-8 text-center">
                  <p className="text-sm" style={{ color: "rgb(var(--color-text-muted))" }}>
                    Menampilkan {data.items.length} dari {data.total} produk. Pagination akan ditambahkan segera.
                  </p>
                </div>
              )}
            </>
          )}

          {/* Affiliate disclosure */}
          <div className="mt-12">
            <AffiliateDisclosure />
          </div>
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}


