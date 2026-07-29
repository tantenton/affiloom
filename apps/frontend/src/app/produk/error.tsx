"use client";

import { SiteHeader } from "@/components/SiteHeader";

export default function CatalogError({
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />
      <main
        className="mx-auto max-w-2xl px-4 py-16 text-center"
        role="alert"
      >
        <h1 className="text-2xl font-bold text-slate-900">
          Katalog gagal dimuat
        </h1>
        <p className="mt-2 text-slate-600">
          Terjadi kesalahan saat menghubungi layanan katalog. Silakan coba
          lagi.
        </p>
        <button
          onClick={() => reset()}
          className="mt-6 rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
        >
          Coba lagi
        </button>
      </main>
    </div>
  );
}
