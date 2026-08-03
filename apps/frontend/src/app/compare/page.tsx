import { Metadata } from "next";
import Link from "next/link";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { formatPrice } from "@/lib/format";
import { Product } from "@/lib/types";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Bandingkan Produk — Affiloom",
  description: "Bandingkan harga, spesifikasi, dan komisi produk afiliasi.",
};

async function getCompareData(ids: string[]): Promise<{ products: Product[]; missing: string[] }> {
  const baseUrl = process.env.INTERNAL_API_URL || "http://localhost:8000";
  const search = new URLSearchParams();
  ids.forEach(id => search.append("ids", id));
  
  const res = await fetch(`${baseUrl}/api/products/compare?${search.toString()}`, {
    next: { revalidate: 0 }
  });
  if (!res.ok) throw new Error("Gagal memuat data perbandingan");
  return res.json();
}

export default async function ComparePage({
  searchParams,
}: {
  searchParams: { ids?: string | string[] };
}) {
  const rawIds = typeof searchParams.ids === "string" ? [searchParams.ids] : searchParams.ids || [];
  const ids = rawIds.flatMap(id => id.split(",")).filter(Boolean);

  if (ids.length === 0) {
    return (
      <div className="min-h-screen bg-slate-50 pb-20 sm:pb-0">
        <SiteHeader />
        <main className="mx-auto max-w-5xl px-4 py-20 text-center">
          <h2 className="text-2xl font-bold text-slate-900">Pilih produk untuk dibandingkan</h2>
          <p className="mt-2 text-slate-600">Kamu belum memilih produk apa pun.</p>
          <Link href="/produk" className="mt-6 inline-block rounded-md bg-slate-900 px-6 py-2 text-sm font-medium text-white hover:bg-slate-700">
            Kembali ke katalog
          </Link>
        </main>
      </div>
    );
  }

  let data;
  try {
    data = await getCompareData(ids);
  } catch (err) {
    return (
      <div className="min-h-screen bg-slate-50 pb-20 sm:pb-0">
        <SiteHeader />
        <main className="mx-auto max-w-5xl px-4 py-20 text-center">
          <h2 className="text-2xl font-bold text-red-900">Gagal memuat perbandingan</h2>
          <p className="mt-2 text-slate-600">Pastikan ID produk valid dan coba lagi.</p>
        </main>
      </div>
    );
  }

  const rows = [
    { label: "Harga", key: "price", format: (v: any, p: Product) => formatPrice(v, p.currency) },
    { label: "Kategori", key: "category" },
    { label: "Sumber", key: "source" },
    { label: "Komisi", key: "commission_rate", format: (v: any) => v ? `${(v * 100).toFixed(1)}%` : "-" },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />
      <main className="mx-auto max-w-6xl px-4 py-10">
        <h1 className="text-3xl font-bold text-slate-900">Bandingkan Produk</h1>
        
        <div className="mt-8 overflow-x-auto rounded-lg border bg-white shadow-sm">
          <table className="w-full border-collapse text-left text-sm">
            <thead>
              <tr className="border-b bg-slate-50">
                <th className="w-48 border-r p-4 font-semibold text-slate-900">Fitur</th>
                {data.products.map(p => (
                  <th key={p.id} className="min-w-[200px] border-r p-4 text-center">
                    {p.image_url && (
                      // eslint-disable-next-line @next/next/no-img-element
                      <img src={p.image_url} alt={p.title} className="mx-auto mb-3 h-24 w-24 rounded object-cover" />
                    )}
                    <div className="font-bold text-slate-900">{p.title}</div>
                    <Link href={`/produk/${p.id}`} className="mt-2 block text-xs text-blue-600 hover:underline">Detail produk</Link>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map(row => (
                <tr key={row.label} className="border-t">
                  <td className="border-r bg-slate-50 p-4 font-medium text-slate-700">{row.label}</td>
                  {data.products.map(p => (
                    <td key={p.id} className="border-r p-4 text-center text-slate-900">
                      {row.format ? row.format((p as any)[row.key], p) : (p as any)[row.key] || "-"}
                    </td>
                  ))}
                </tr>
              ))}
              <tr className="border-t">
                <td className="border-r bg-slate-50 p-4 font-medium text-slate-700">Tindakan</td>
                {data.products.map(p => (
                  <td key={p.id} className="border-r p-4 text-center">
                    <a href={p.url} target="_blank" rel="sponsored nofollow noopener" className="inline-block rounded bg-slate-900 px-4 py-2 text-xs font-semibold text-white hover:bg-slate-700">Beli</a>
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </main>
      <SiteFooter />
    </div>
  );
}
