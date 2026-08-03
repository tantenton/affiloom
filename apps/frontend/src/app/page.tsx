import { Metadata } from "next";
import Link from "next/link";

import { AffiliateDisclosure } from "@/components/AffiliateDisclosure";
import { ProductCard } from "@/components/ProductCard";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { listArticles, listProducts } from "@/lib/api";

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

const CATEGORIES = [
  { name: "Fashion", href: "/produk?category=Fashion" },
  { name: "Elektronik", href: "/produk?category=Elektronik" },
  { name: "Kuliner", href: "/produk?category=Kuliner" },
  { name: "Kecantikan", href: "/produk?category=Kecantikan" },
  { name: "Olahraga", href: "/produk?category=Olahraga" },
  { name: "Rumah Tangga", href: "/produk?category=Rumah%20Tangga" },
  { name: "Peralatan", href: "/produk?category=Peralatan" },
  { name: "Alat Tulis", href: "/produk?category=Alat%20Tulis" },
];

export default async function HomePage() {
  const products = await listProducts({ limit: 8 }).catch(() => null);
  const articles = await listArticles({ limit: 3 }).catch(() => null);

  return (
    <div className="min-h-screen" style={{ background: "rgb(var(--color-bg))" }}>
      <SiteHeader />

      <main>
        {/* Hero — warm editorial, NOT dark */}
        <section
          className="relative overflow-hidden"
          style={{
            background: "linear-gradient(135deg, rgb(245 243 255) 0%, rgb(254 252 249) 60%, rgb(255 247 237) 100%)",
            borderBottom: "1px solid rgb(var(--color-border))",
          }}
        >
          <div className="mx-auto max-w-5xl px-4 py-16 sm:py-24">
            <p className="section-label">Rekomendasi produk mindful</p>
            <h1
              className="mt-4 text-3xl font-bold tracking-tight sm:text-5xl lg:text-6xl"
              style={{ color: "rgb(var(--color-text))", lineHeight: 1.15 }}
            >
              Belanja lebih{" "}
              <span style={{ color: "rgb(var(--color-primary))" }}>cerdas</span>
            </h1>
            <p
              className="mt-5 max-w-xl text-base leading-relaxed sm:text-lg"
              style={{ color: "rgb(var(--color-text-muted))" }}
            >
              Produk terbaik dari marketplace Indonesia — dibandingkan,
              diringkas, dan disajikan secara transparan. Komisi tercantum terbuka.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/produk" className="btn btn-primary">
                Lihat katalog
              </Link>
              <Link href="/artikel" className="btn btn-secondary">
                Baca panduan
              </Link>
            </div>
            {/* Trust signals */}
            <div className="mt-10 flex flex-wrap gap-4">
              {["Komisi transparan", "Tanpa dark pattern", "Data deterministik"].map((t) => (
                <span
                  key={t}
                  className="flex items-center gap-1.5 text-xs font-medium"
                  style={{ color: "rgb(var(--color-text-muted))" }}
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" style={{ width: 14, height: 14, flexShrink: 0, color: "rgb(var(--color-success))" }}>
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                  {t}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* Categories */}
        <section className="mx-auto max-w-7xl px-4 py-12">
          <div className="mb-6 flex items-end justify-between gap-4">
            <div>
              <p className="section-label">Jelajahi</p>
              <h2 className="mt-2 text-xl font-bold sm:text-2xl" style={{ color: "rgb(var(--color-text))" }}>
                Kategori populer
              </h2>
            </div>
            <Link
              href="/produk"
              className="text-sm font-semibold transition-colors"
              style={{ color: "rgb(var(--color-primary))" }}
            >
              Lihat semua →
            </Link>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-4 sm:gap-3">
            {CATEGORIES.map((c) => (
              <Link
                key={c.name}
                href={c.href}
                className="card rounded-xl px-4 py-3 text-center text-sm font-semibold transition-all hover:-translate-y-0.5"
                style={{ color: "rgb(var(--color-text))" }}
              >
                {c.name}
              </Link>
            ))}
          </div>
        </section>

        {/* Featured products */}
        {products && products.items.length > 0 && (
          <section className="mx-auto max-w-7xl px-4 py-4 pb-12">
            <div className="mb-6 flex items-end justify-between gap-4">
              <div>
                <p className="section-label">Pilihan editor</p>
                <h2 className="mt-2 text-xl font-bold sm:text-2xl" style={{ color: "rgb(var(--color-text))" }}>
                  Produk rekomendasi
                </h2>
              </div>
              <Link
                href="/produk"
                className="text-sm font-semibold transition-colors"
                style={{ color: "rgb(var(--color-primary))" }}
              >
                Lihat semua →
              </Link>
            </div>
            {/* 2 col mobile, 3 tablet, 4 desktop */}
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4 lg:gap-5">
              {products.items.slice(0, 8).map((product) => (
                <ProductCard key={product.id} product={product} />
              ))}
            </div>
          </section>
        )}

        {/* Articles */}
        {articles && articles.items.length > 0 && (
          <section
            className="py-12"
            style={{ background: "rgb(var(--color-surface))", borderTop: "1px solid rgb(var(--color-border))", borderBottom: "1px solid rgb(var(--color-border))" }}
          >
            <div className="mx-auto max-w-7xl px-4">
              <div className="mb-6 flex items-end justify-between gap-4">
                <div>
                  <p className="section-label">Panduan belanja</p>
                  <h2 className="mt-2 text-xl font-bold sm:text-2xl" style={{ color: "rgb(var(--color-text))" }}>
                    Buying guide terbaru
                  </h2>
                </div>
                <Link
                  href="/artikel"
                  className="text-sm font-semibold"
                  style={{ color: "rgb(var(--color-primary))" }}
                >
                  Lihat semua →
                </Link>
              </div>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                {articles.items.slice(0, 3).map((article) => (
                  <Link
                    key={article.id}
                    href={`/artikel/${article.slug}`}
                    className="card card-hover flex flex-col justify-between p-5 no-underline"
                  >
                    {article.category && (
                      <span className="section-label">{article.category.name}</span>
                    )}
                    <h3
                      className="mt-2 text-base font-semibold leading-snug line-clamp-2"
                      style={{ color: "rgb(var(--color-text))" }}
                    >
                      {article.title}
                    </h3>
                    {article.excerpt && (
                      <p
                        className="mt-2 text-sm line-clamp-2"
                        style={{ color: "rgb(var(--color-text-muted))" }}
                      >
                        {article.excerpt}
                      </p>
                    )}
                    <span
                      className="mt-4 text-xs font-bold"
                      style={{ color: "rgb(var(--color-primary))" }}
                    >
                      Baca panduan →
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          </section>
        )}

        {/* Why Affiloom */}
        <section className="mx-auto max-w-7xl px-4 py-12">
          <div
            className="rounded-2xl p-6 sm:p-8"
            style={{ background: "rgb(var(--color-surface))", border: "1px solid rgb(var(--color-border))" }}
          >
            <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <div>
                <p className="section-label">Tentang kami</p>
                <h2 className="mt-2 text-lg font-bold sm:text-xl" style={{ color: "rgb(var(--color-text))" }}>
                  Mengapa Affiloom berbeda?
                </h2>
                <p className="mt-2 text-sm leading-relaxed" style={{ color: "rgb(var(--color-text-muted))" }}>
                  Tidak ada review palsu, tidak menjual data pribadi, tidak memaksa konten tipis.
                  Setiap rekomendasi tercatat dan dapat ditelusuri ke sumbernya.
                </p>
              </div>
              <div>
                <h3 className="text-sm font-bold" style={{ color: "rgb(var(--color-text))" }}>
                  Status saat ini
                </h3>
                <ul className="mt-2 space-y-1.5 text-sm" style={{ color: "rgb(var(--color-text-muted))" }}>
                  {[
                    "Data berasal dari adaptor demo deterministik",
                    "Integrasi merchant ditambahkan bertahap",
                    "AI-generated content aktif dengan fallback deterministik",
                  ].map((item) => (
                    <li key={item} className="flex items-start gap-2">
                      <span style={{ color: "rgb(var(--color-text-light))" }}>•</span>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="mt-6 border-t pt-6" style={{ borderColor: "rgb(var(--color-border))" }}>
              <AffiliateDisclosure variant="inline" />
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
