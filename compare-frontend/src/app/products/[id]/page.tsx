import Link from "next/link";
import { CompareBar, isSelected, toggleSelected, MAX } from "@/lib/compare-store";
import { fetchProduct } from "@/lib/api";

export default async function ProductDetail(
  props: { params: Promise<{ id: string }>; searchParams: Promise<{ [key: string]: string | string[] | undefined }> }
) {
  const params = await props.params;
  const product = await fetchProduct(params.id);
  const selected = isSelected(product.id);

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <Link
        href="/"
        className="text-sm font-medium text-zinc-500 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-100"
      >
        ← Kembali
      </Link>

      <div className="mt-6 grid gap-6 md:grid-cols-2 md:gap-8">
        <div className="relative aspect-[4/3] overflow-hidden rounded-2xl bg-zinc-100 dark:bg-zinc-800">
          <img
            src={product.image || "/placeholder.svg"}
            alt={product.name}
            className="h-full w-full object-cover"
          />
        </div>
        <div className="flex flex-col gap-4">
          <h1 className="text-2xl font-extrabold tracking-tight text-zinc-900 dark:text-zinc-100 md:text-3xl">
            {product.name}
          </h1>
          <span className="inline-block w-fit rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-semibold text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
            {product.category}
          </span>
          <p className="text-sm leading-7 text-zinc-600 dark:text-zinc-300">
            {product.description}
          </p>
          <div>
            <span className="text-3xl font-extrabold text-zinc-900 dark:text-zinc-100">
              Rp{product.price.toLocaleString("id-ID")}
            </span>
          </div>

          <div className="mt-auto pt-4">
            <button
              onClick={() => {
                toggleSelected(product.id);
                // force refresh to show CompareBar
                window.location.reload();
              }}
              className={`inline-flex h-12 w-full items-center justify-center rounded-full text-sm font-bold shadow-lg transition-colors ${
                selected ? "bg-blue-700 text-white hover:bg-blue-800" : "bg-blue-600 text-white hover:bg-blue-700"
              }`}
            >
              {selected ? "Terpilih untuk Bandingkan" : "Bandingkan"}
            </button>
            <p className="mt-2 text-xs text-zinc-400 dark:text-zinc-500">
              {selected ? `Dipilih (${MAX} maksimal)` : "Pilih produk lain di halaman utama untuk dibandingkan"}
            </p>
          </div>
        </div>
      </div>

      <CompareBar />
    </div>
  );
}
