"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import type { CompareResponse } from "@/lib/types";

export default function CompareContent() {
  const params = useSearchParams();
  const idsParam = params.get("ids") ?? "";
  const ids = idsParam.split(",").map((s) => s.trim()).filter(Boolean);

  const [data, setData] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (ids.length < 2) return; 
    fetch(`/api/products/compare?ids=${encodeURIComponent(ids.join(","))}`)
      .then(async (r) => {
        if (!r.ok) {
          const err = await r.json().catch(() => ({}));
          throw new Error(err.error ?? "Gagal membandingkan");
        }
        return r.json();
      })
      .then((payload: CompareResponse) => {
        setData(payload);
        setError(null);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [idsParam]);

  if (ids.length < 2) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-16 text-center">
        <h1 className="text-xl font-bold text-zinc-900 dark:text-zinc-100">
          Perlu 2 produk
        </h1>
        <p className="mt-3 text-sm text-zinc-500 dark:text-zinc-400">
          Pilih minimal dua produk dari halaman utama untuk mulai membandingkan.
        </p>
        <Link
          href="/"
          className="mt-6 inline-flex h-10 items-center justify-center rounded-full bg-blue-600 px-6 text-sm font-bold text-white hover:bg-blue-700"
        >
          Kembali ke produk
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-extrabold tracking-tight text-zinc-900 dark:text-zinc-100">
        Perbandingan Produk
      </h1>

      {loading ? (
        <div className="mt-6 space-y-4">
          <div className="h-72 animate-pulse rounded-2xl bg-zinc-100 dark:bg-zinc-800" />
        </div>
      ) : error ? (
        <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900/40 dark:bg-red-900/20 dark:text-red-300">
          {error}
        </div>
      ) : data ? (
        <>
          {/* Card comparison */}
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            {data.products.map((p) => (
              <Link
                key={p.id}
                href={`/products/${p.id}`}
                className="rounded-2xl border border-zinc-200 bg-white p-4 transition hover:shadow-md dark:border-zinc-800 dark:bg-zinc-950"
              >
                <h2 className="font-bold text-zinc-900 dark:text-zinc-100">
                  {p.name}
                </h2>
                <p className="text-xs text-zinc-500 dark:text-zinc-400">{p.category}</p>
                <p className="mt-2 text-2xl font-extrabold text-blue-700 dark:text-blue-400">
                  Rp{p.price.toLocaleString("id-ID")}
                </p>
                <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-300">
                  {p.description}
                </p>
                <p className="mt-2 text-xs text-zinc-400 dark:text-zinc-500">
                  Rating: {p.rating}
                </p>
              </Link>
            ))}
          </div>

          {/* Specs comparison table */}
          <div className="mt-8 overflow-x-auto rounded-2xl border border-zinc-200 dark:border-zinc-800">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-zinc-200 dark:border-zinc-800">
                  <th className="text-left px-4 py-3 font-semibold text-zinc-900 dark:text-zinc-100">
                    Fitur
                  </th>
                  {data.products.map((p) => (
                    <th key={p.id} className="text-left px-4 py-3 font-semibold text-zinc-900 dark:text-zinc-100">
                      {p.name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {data.differences.map((d) => (
                  <tr
                    key={d.field}
                    className="border-b border-zinc-100 last:border-0 dark:border-zinc-800/60"
                  >
                    <td className="px-4 py-3 text-zinc-700 dark:text-zinc-300">{d.field}</td>
                    {d.values.map((v, i) => (
                      <td key={i} className="px-4 py-3 text-zinc-900 dark:text-zinc-100">
                        {v == null ? "—" : v}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      ) : null}
    </div>
  );
}