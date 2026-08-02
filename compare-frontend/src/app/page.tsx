"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import type { Product } from "@/lib/types";
import { CompareBar, useSelected, MAX } from "@/lib/compare-store";

const PLACEHOLDER =
  "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400' viewBox='0 0 400 400'%3E%3Crect width='400' height='400' fill='%23e4e4e7'/%3E%3Ctext x='50%25' y='50%25' fill='%2371717a' font-size='18' font-family='sans-serif' text-anchor='middle' dy='.3em'%3ENo Image%3C/text%3E%3C/svg%3E";

export default function HomePage() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, toggle] = useSelected();

  useEffect(() => {
    fetch("/api/products")
      .then((r) => r.json())
      .then((data: Product[]) => setProducts(data))
      .catch(() => setProducts([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="mb-6 text-2xl font-bold tracking-tight text-zinc-900 dark:text-zinc-100">
        Produk
      </h1>

      {loading ? (
        <div className="grid gap-4 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <div
              key={i}
              className="h-52 animate-pulse rounded-xl bg-zinc-100 dark:bg-zinc-800"
            />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {products.map((product) => {
            const isIn = selected.includes(product.id);
            return (
              <div
                key={product.id}
                className="relative flex flex-col overflow-hidden rounded-xl border border-zinc-200 bg-white transition-shadow hover:shadow-md dark:border-zinc-800 dark:bg-zinc-950"
              >
                <div className="relative aspect-[4/3] w-full bg-zinc-100 dark:bg-zinc-800">
                  {product.image ? (
                    <Image
                      src={product.image}
                      alt={product.name}
                      fill
                      className="object-cover"
                      sizes="(max-width: 640px) 100vw, 50vw"
                    />
                  ) : (
                    <img
                      src={PLACEHOLDER}
                      alt=""
                      className="h-full w-full object-cover"
                    />
                  )}
                </div>
                <div className="flex flex-1 flex-col gap-1.5 p-4">
                  <span className="text-xs font-medium text-blue-600 dark:text-blue-400">
                    {product.category}
                  </span>
                  <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-100">
                    {product.name}
                  </h2>
                  <p className="line-clamp-1 text-sm text-zinc-500 dark:text-zinc-400">
                    {product.description}
                  </p>
                  <div className="mt-auto flex items-center justify-between pt-2">
                    <span className="text-lg font-bold text-zinc-900 dark:text-zinc-100">
                      Rp{product.price.toLocaleString("id-ID")}
                    </span>
                    <button
                      onClick={() => toggle(product.id)}
                      className={`inline-flex h-9 items-center rounded-full px-4 text-sm font-semibold transition-colors ${
                        isIn
                          ? "bg-blue-600 text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-400"
                          : selected.length >= MAX && !isIn
                            ? "cursor-not-allowed border border-zinc-300 text-zinc-400 dark:border-zinc-700 dark:text-zinc-600"
                            : "border border-zinc-300 text-zinc-700 hover:bg-zinc-100 dark:border-zinc-700 dark:text-zinc-300 dark:hover:bg-zinc-800"
                      }`}
                      disabled={selected.length >= MAX && !isIn}
                    >
                      {isIn ? "Terpilih" : "Pilih"}
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      <CompareBar />
    </div>
  );
}