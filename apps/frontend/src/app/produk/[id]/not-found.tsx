import Link from "next/link";

import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";

export default function ProductNotFound() {
  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />
      <main className="mx-auto max-w-2xl px-4 py-16 text-center">
        <h1 className="text-3xl font-bold text-slate-900">
          Produk tidak ditemukan
        </h1>
        <p className="mt-3 text-slate-600">
          Produk yang kamu cari mungkin sudah dihapus atau tidak pernah ada di
          katalog Affiloom.
        </p>
        <Link
          href="/produk"
          className="mt-6 inline-block rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
        >
          Kembali ke katalog
        </Link>
      </main>
      <SiteFooter />
    </div>
  );
}
