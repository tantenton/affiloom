import type { CompareResponse, Product } from "@/lib/types";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export async function fetchProducts() {
  const res = await fetch(`${BASE}/api/products`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) throw new Error("Gagal memuat produk");
  return res.json() as Promise<Product[]>;
}

export async function fetchProduct(id: string) {
  const res = await fetch(`${BASE}/api/products/${id}`, {
    next: { revalidate: 60 },
  });
  if (!res.ok) throw new Error("Gagal memuat detail produk");
  return res.json() as Promise<Product>;
}

export async function fetchCompare(ids: string[]) {
  const params = new URLSearchParams({ ids: ids.join(",") });
  const res = await fetch(`${BASE}/api/products/compare?${params.toString()}`);
  if (!res.ok) throw new Error("Gagal memuat perbandingan");
  return res.json() as Promise<CompareResponse>;
}
