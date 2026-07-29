import { Metadata } from "next";
import Link from "next/link";

import { AffiliateDisclosure } from "@/components/AffiliateDisclosure";
import { SiteHeader } from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "Affiloom — Marketplace Afiliasi Indonesia",
  description:
    "Jelajahi produk afiliasi mindful dari marketplace Indonesia. Transparansi total, etika, dan kesiapan skala.",
  openGraph: {
    title: "Affiloom — Marketplace Afiliasi Indonesia",
    description:
      "Platform afiliasi mindful untuk marketplace Indonesia. Transparan, beretika, dan siap menskalakan.",
    locale: "id_ID",
    type: "website",
  },
};

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />

      <main>
        <section className="mx-auto max-w-5xl px-4 py-16">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
            Marketplace afiliasi mindful — Indonesia
          </h1>
          <p className="mt-4 max-w-2xl text-lg text-slate-600">
            Menghubungkan creator, publisher, dan affiliator dengan etika dan
            transparansi maksimal. Vertikal awal: integrasi read-only dengan
            Shopee dan Tokopedia lewat jalur API resmi partner — tanpa
            scraping.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link
              href="/produk"
              className="rounded-md bg-slate-900 px-5 py-3 text-sm font-semibold text-white hover:bg-slate-700"
            >
              Jelajahi katalog
            </Link>
            <a
              href="#etika"
              className="rounded-md border border-slate-300 bg-white px-5 py-3 text-sm font-semibold text-slate-900 hover:bg-slate-100"
            >
              Kode etik afiliasi
            </a>
          </div>
        </section>

        <section id="etika" className="mx-auto max-w-5xl px-4 pb-16">
          <div className="rounded-lg border bg-white p-6">
            <h2 className="text-lg font-semibold text-slate-900">
              Kode Etik Afiliasi
            </h2>
            <ul className="mt-3 list-disc space-y-2 pl-6 text-slate-700">
              <li>Pengungkapan afiliasi ditampilkan secara eksplisit.</li>
              <li>Tidak ada jualan palsu atau review fiktif.</li>
              <li>
                Integrasi hanya melalui jalur API resmi partner atau read-only
                publik yang diizinkan.
              </li>
              <li>
                Data yang tampil dalam milestone ini berasal dari adaptor demo
                deterministik.
              </li>
            </ul>
            <div className="mt-6">
              <AffiliateDisclosure variant="inline" />
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
