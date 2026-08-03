import { Metadata } from "next";
import Link from "next/link";

import { AffiliateDisclosure } from "@/components/AffiliateDisclosure";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { listProducts, listArticles } from "@/lib/api";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Affiloom — Rekomendasi Produk Afiliasi Indonesia",
  description:
    "Temukan rekomendasi produk terbaik, perbandingan, dan panduan belanja mindful untuk marketplace Indonesia.",
  openGraph: {
    title: "Affiloom — Rekomendasi Produk Afiliasi Indonesia",
    description:
      "Temukan rekomendasi produk terbaik, perbandingan, dan panduan belanja mindful.",
    locale: "id_ID",
    type: "website",
  },
};

function CategoryPill({
  name,
  href,
}: { name: string; href: string }) {
  return (
    <Link
      href={href}
      className="card px-5 py-4 text-center text-sm font-bold text-slate-700 no-underline"
    >
      {name}
    </Link>
  );
}

export default async function HomePage() {
  const products = await listProducts({ limit: 6 }).catch(() => null);
  const articles = await listArticles({ limit: 3 }).catch(() => null);

  const categories = [
    { name: "Fashion", href: "/produk?category=Fashion" },
    { name: "Elektronik", href: "/produk?category=Elektronik" },
    { name: "Kuliner", href: "/produk?category=Kuliner" },
    { name: "Kecantikan", href: "/produk?category=Kecantikan" },
    { name: "Olahraga", href: "/produk?category=Olahraga" },
    { name: "Rumah Tangga", href: "/produk?category=Rumah Tangga" },
    { name: "Peralatan", href: "/produk?category=Peralatan" },
    { name: "Alat Tulis", href: "/produk?category=Alat Tulis" },
  ];

  return (
    <div className="min-h-screen bg-white">
      <SiteHeader />

      {/* Hero */}
      <main>
        <section className="relative overflow-hidden bg-slate-950 text-white">
          <div className="absolute inset-0 opacity-30 bg-[radial-gradient(circle_at_30%_40%,rgba(99,102,241,0.35),transparent_50%),radial-gradient(circle_at_70%_60%,rgba(14,165,233,0.25),transparent_45%)]" />
          <div className="relative mx-auto max-w-5xl px-4 py-24">
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-indigo-300/90">
              Rekomendasi produk mindful
            </p>
            <h1 className="mt-6 text-3xl font-bold tracking-tight text-white sm:text-5xl lg:text-6xl">
              Belanja lebih <span className="text-indigo-400">cerdas</span>
            </h1>
            <p className="mt-5 max-w-2xl text-lg text-slate-300">
              Temukan produk terbaik dari marketplace Indonesia. Kami bandingkan,
              meringkas, dan menampilkan tautan afiliasi secara transparan.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/produk" className="btn-primary">
                Lihat katalog
              </Link>
              <Link href="/artikel" className="btn-secondary bg-white/10 text-white border-white/20 hover:bg-white/20 hover:text-white">
                Baca panduan
              </Link>
            </div>
          </div>
        </section>

        {/* Categories */}
        <section className="mx-auto max-w-6xl px-4 py-16">
          <div className="flex items-end justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">
                Jelajahi
              </p>
              <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
                Kategori populer
              </h2>
              <p className="mt-2 text-sm text-slate-600">
                Pilih kategori untuk melihat rekomendasi produk terkurasi.
              </p>
            </div>
            <Link href="/produk" className="text-sm font-bold text-slate-900 hover:text-indigo-600">
              Lihat semua →
            </Link>
          </div>
          <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {categories.map((c) => (
              <CategoryPill key={c.name} {...c} />
            ))}
          </div>
        </section>

        {/* Featured products */}
        {products && products.items.length > 0 ? (
          <section className="mx-auto max-w-6xl px-4 py-16">
            <div className="flex items-end justify-between gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">
                  Pilihan editor
                </p>
                <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
                  Produk rekomendasi
                </h2>
                <p className="mt-2 text-sm text-slate-600">
                  Produk dengan data harga terbaru dan ketersediaan terjangkau.
                </p>
              </div>
              <Link href="/produk" className="text-sm font-bold text-slate-900 hover:text-indigo-600">
                Lihat semua →
              </Link>
            </div>
            <div className="mt-8 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {products.items.slice(0, 6).map((product) => (
                <Link
                  key={product.id}
                  href={`/produk/${product.id}`}
                  className="card card-hover flex h-full flex-col overflow-hidden no-underline"
                >
                  <div className="aspect-[4/3] w-full overflow-hidden bg-slate-100">
                    {product.image_url ? (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img
                        src={product.image_url}
                        alt={product.title}
                        className="h-full w-full object-cover transition-transform duration-500 hover:scale-105"
                      />
                    ) : (
                      <div className="flex h-full w-full items-center justify-center text-slate-400">
                        Tanpa gambar
                      </div>
                    )}
                  </div>
                  <div className="flex flex-1 flex-col p-5">
                    {product.category ? (
                      <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-600">
                        {product.category}
                      </span>
                    ) : null}
                    <h3 className="mt-2 line-clamp-2 text-sm font-semibold leading-snug text-slate-900">
                      {product.title}
                    </h3>
                    <p className="mt-2 text-xs text-slate-500 line-clamp-2">
                      {product.description ?? "Produk afiliasi kurasi."}
                    </p>
                    <div className="mt-auto pt-4">
                      <span className="text-base font-bold text-slate-900">
                        {new Intl.NumberFormat("id-ID", {
                          style: "currency",
                          currency: product.currency ?? "IDR",
                          maximumFractionDigits: 0,
                        }).format(product.price ?? 0)}
                      </span>
                      <span className="ml-3 text-[11px] font-bold uppercase tracking-wide text-slate-400">
                        {product.commission_rate != null
                          ? `${(product.commission_rate * 100).toFixed(1)}% komisi`
                          : "Komisi tidak diketahui"}
                      </span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        ) : null}

        {/* Buying guide tease */}
        {articles && articles.items.length > 0 ? (
          <section className="mx-auto max-w-6xl px-4 py-16">
            <div className="flex items-end justify-between gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">
                  Panduan belanja
                </p>
                <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">
                  Buying guide terbaru
                </h2>
                <p className="mt-2 text-sm text-slate-600">
                  Rekomendasi berbasis metodologi, bukan review fiktif.
                </p>
              </div>
              <Link href="/artikel" className="text-sm font-bold text-slate-900 hover:text-indigo-600">
                Lihat semua →
              </Link>
            </div>
            <div className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {articles.items.slice(0, 3).map((article) => (
                <Link
                  key={article.id}
                  href={`/artikel/${article.slug}`}
                  className="card card-hover flex h-full flex-col justify-between p-6 no-underline"
                >
                  <div>
                    {article.category ? (
                      <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-600">
                        {article.category.name}
                      </span>
                    ) : null}
                    <h3 className="mt-2 text-lg font-semibold leading-snug text-slate-900">
                      {article.title}
                    </h3>
                    {article.excerpt ? (
                      <p className="mt-2 text-sm text-slate-600 line-clamp-2">
                        {article.excerpt}
                      </p>
                    ) : null}
                  </div>
                  <span className="mt-4 text-xs font-bold text-slate-500">
                    Baca panduan →
                  </span>
                </Link>
              ))}
            </div>
          </section>
        ) : null}

        {/* Disclosure + footer CTA */}
        <section className="mx-auto max-w-6xl px-4 pb-24">
          <div className="rounded-2xl border border-slate-200 bg-white p-8">
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div>
                <h2 className="text-xl font-bold text-slate-900">
                  Mengapa Affiloom berbeda?
                </h2>
                <p className="mt-2 text-sm text-slate-600">
                  Kami tidak menerbitkan review palsu, menjual data pribadi, atau
                  memaksa konten tipis. Setiap rekomendasi tercatat dan dapat
                  ditelusuri ke sumbernya.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">
                  Keadaan saat ini
                </h3>
                <ul className="mt-2 space-y-1 text-sm text-slate-700">
                  <li>• Data masih berasal dari adaptor demo deterministik</li>
                  <li>• Integrasi merchant sebenarnya akan ditambahkan bertahap</li>
                  <li>• AI-generated content aktif dengan fallback deterministik</li>
                </ul>
                <p className="mt-4 text-xs text-slate-500">
                  Milestone aman dan reversible. Produksi memerlukan approval Anda.
                </p>
              </div>
            </div>
            <div className="mt-6">
              <AffiliateDisclosure variant="inline" />
            </div>
          </div>
        </section>
      </main>
      <SiteFooter />
    </div>
  );
}
