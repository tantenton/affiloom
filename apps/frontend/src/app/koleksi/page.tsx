import { Metadata } from "next";
import Link from "next/link";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { listCollections } from "@/lib/api";
import { CollectionSummary } from "@/lib/types";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Koleksi Kurasi — Affiloom",
  description:
    "Koleksi produk terkurasi berdasarkan budget, kebutuhan, dan kesempatan.",
};

export default async function CollectionsPage() {
  let collections: CollectionSummary[] = [];
  try {
    collections = await listCollections();
  } catch {
    collections = [];
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />
      <main className="mx-auto max-w-6xl px-4 py-12">
        <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">
          Kurasi
        </p>
        <h1 className="mt-2 text-4xl font-bold tracking-tight text-slate-900">
          Koleksi
        </h1>
        <p className="mt-3 max-w-2xl text-slate-600">
          Kumpulan produk pilihan berdasarkan budget, kebutuhan, dan kesempatan.
        </p>

        {collections.length === 0 ? (
          <section className="mt-10 rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center">
            <h2 className="text-lg font-semibold text-slate-900">
              Belum ada koleksi
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              Koleksi terkurasi akan segera hadir.
            </p>
          </section>
        ) : (
          <section className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {collections.map((c) => (
              <Link
                key={c.id}
                href={`/koleksi/${c.slug}`}
                className="card card-hover flex h-full flex-col justify-between p-6 no-underline"
              >
                <div>
                  <h2 className="text-xl font-bold text-slate-900">{c.title}</h2>
                  {c.description ? (
                    <p className="mt-2 text-sm text-slate-600 line-clamp-3">
                      {c.description}
                    </p>
                  ) : null}
                </div>
                <span className="mt-4 text-xs font-bold text-slate-400">
                  {c.product_count} produk →
                </span>
              </Link>
            ))}
          </section>
        )}
      </main>
      <SiteFooter />
    </div>
  );
}
