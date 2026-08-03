"use client";

import { useRouter } from "next/navigation";

interface Props {
  currentSort: string | null;
  currentCategory: string | null;
  currentQuery: string | null;
}

export function SortSelect({ currentSort, currentCategory, currentQuery }: Props) {
  const router = useRouter();

  function handleChange(e: React.ChangeEvent<HTMLSelectElement>) {
    const params = new URLSearchParams();
    if (currentQuery) params.set("q", currentQuery);
    if (currentCategory) params.set("category", currentCategory);
    if (e.target.value) params.set("sort", e.target.value);
    router.push(`/produk${params.toString() ? `?${params.toString()}` : ""}`);
  }

  return (
    <select
      value={currentSort || ""}
      onChange={handleChange}
      className="input w-auto px-3 text-sm"
      style={{ height: 40, minHeight: 40, minWidth: 130, flex: "1 1 130px", maxWidth: 220 }}
      aria-label="Urutkan produk"
    >
      <option value="">Relevansi</option>
      <option value="price_asc">Harga: Rendah → Tinggi</option>
      <option value="price_desc">Harga: Tinggi → Rendah</option>
      <option value="commission_desc">Komisi Tertinggi</option>
    </select>
  );
}
