import { Metadata } from "next";
import Link from "next/link";

import { AffiliateDisclosure } from "@/components/AffiliateDisclosure";
import { ProductCard } from "@/components/ProductCard";
import { SearchForm } from "@/components/SearchForm";
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
};

export default async function ProdukPage({
  searchParams,
}: {
  searchParams: SearchParams;
}) {
  const query = (searchParams.q ?? "").trim();

  let data;
  let errored = false;
  try {
    data = await listProducts({ q: query || undefined, limit: 24 });
  } catch {
    errored = true;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />

      <main className="mx-auto max-w-5xl px-4 py-10">
        <div className="flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
              Katalog Produk
            </h1>
            <p className="mt-2 max-w-2xl text-slate-600">
              Produk afiliasi kurasi dari mitra marketplace Indonesia. Setiap
              item mencantumkan komisi dan sumber secara terbuka.
            </p>
          </div>
          <SearchForm defaultValue={query} />
        </div>

        <div className="mt-6">
          <AffiliateDisclosure />
        </div>

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

function EmptyState({ query }: { query: string }) {
  return (
    <section className="mt-8 rounded-lg border border-dashed border-slate-300 bg-white p-10 text-center">
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
          className="mt-4 inline-block rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
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
      className="mt-8 rounded-lg border border-red-200 bg-red-50 p-6 text-red-900"
    >
      <h2 className="text-lg font-semibold">Gagal memuat katalog</h2>
      <p className="mt-2 text-sm">
        Layanan katalog sedang tidak dapat dihubungi. Coba muat ulang halaman
        beberapa saat lagi.
      </p>
    </section>
  );
}

function SiteFooter() {
  return (
    <footer className="mt-16 border-t bg-white">
      <div className="mx-auto flex max-w-5xl flex-col gap-2 px-4 py-6 text-sm text-slate-500 md:flex-row md:items-center md:justify-between">
        <p>© {new Date().getFullYear()} Affiloom. Semua hak dilindungi.</p>
        <p>
          Data katalog: adaptor demo deterministik. Tidak ada scraping
          marketplace.
        </p>
      </div>
    </footer>
  );
}
