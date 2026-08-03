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
    <div className="min-h-screen bg-slate-50 pb-20 sm:pb-0">
      <SiteHeader />

      <main className="mx-auto max-w-6xl px-4 py-12">
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">
              Katalog
            </p>
            <h1 className="mt-2 text-4xl font-bold tracking-tight text-slate-900">
              Produk Kurasi
            </h1>
            <p className="mt-3 max-w-2xl text-slate-600">
              Produk afiliasi kurasi dari mitra marketplace Indonesia. Setiap
              item mencantumkan komisi dan sumber secara terbuka.
            </p>
          </div>
          <SearchForm defaultValue={query} />
        </div>

        <div className="mt-8">
          <AffiliateDisclosure />
        </div>

        <nav aria-label="Filter kategori" className="mt-8 flex flex-wrap gap-2">
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

        {errored ? (
          <ErrorState />
        ) : !data || data.items.length === 0 ? (
          <EmptyState query={query} />
        ) : (
          <ResultsGrid
            items={data.items}
            total={data.total}
            query={data.query}
          />
        )}
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
    <section className="mt-8" aria-label="Hasil produk">
      <p className="text-sm text-slate-500">
        Menampilkan {items.length} dari {total} produk
        {query ? (
          <>
            {" "}untuk pencarian <span className="font-medium">&ldquo;{query}&rdquo;</span>
          </>
        ) : null}
        .
      </p>
      <ul className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((item) => (
          <li key={item.id} className="h-full">
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
  const base = "rounded-full border px-4 py-1.5 text-sm font-medium transition-all duration-200";
  const className = active
    ? `${base} border-slate-900 bg-slate-900 text-white shadow-sm`
    : `${base} border-slate-200 bg-white text-slate-600 hover:border-slate-400 hover:text-slate-900 hover:shadow-sm`;
  return (
    <Link href={href} className={className}>
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

