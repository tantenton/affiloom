import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Affiloom — Marketplace Afiliasi Indonesia",
  description:
    "Jelajahi produk afiliasi mindful dari marketplace Indonesia. Transparansi total, etika, dan kesiapan skala.",
};

export default function Home() {
  return (
    <main className="min-h-screen">
      <header className="border-b">
        <div className="mx-auto max-w-5xl px-4 py-6">
          <h1 className="text-2xl font-bold tracking-tight">Affiloom</h1>
          <p className="mt-2 text-gray-600">
            Marketplace afiliasi mindful — Indonesia.
          </p>
        </div>
      </header>

      <section className="mx-auto max-w-5xl px-4 py-12">
        <h2 className="text-xl font-semibold">Tujuan</h2>
        <p className="mt-2 max-w-2xl text-gray-700">
          Menghubungkan creator, publisher, dan affiliator dengan etika dan transparansi
          maksimal. Vertikal awal: integrasi read-only dengan Shopee dan Tokopedia
          tanpa scraping otomatis, lewat adapter resmi partner.
        </p>
      </section>

      <section className="mx-auto max-w-5xl px-4 pb-16">
        <div className="rounded-lg border bg-white p-6">
          <h3 className="text-lg font-medium">Kode Etik Afiliasi</h3>
          <ul className="mt-3 list-disc space-y-2 pl-6 text-gray-700">
            <li>Pengungkapan afiliasi ditampilkan secara eksplisit.</li>
            <li>Tidak ada jualan palsu atau review fiktif.</li>
            <li>
              Integrasi hanya melalui jalur API resmi partner atau read-only publik
              yang diizinkan.
            </li>
          </ul>
        </div>
      </section>
    </main>
  );
}
