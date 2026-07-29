import Link from "next/link";

import { formatPrice } from "@/lib/format";
import { Product } from "@/lib/types";

export function ProductCard({ product }: { product: Product }) {
  return (
    <Link
      href={`/produk/${product.id}`}
      className="group flex h-full flex-col overflow-hidden rounded-lg border bg-white transition-shadow hover:shadow-md focus:outline-none focus:ring-2 focus:ring-slate-900"
      aria-label={`Lihat detail ${product.title}`}
    >
      <div className="aspect-square w-full overflow-hidden bg-slate-100">
        {product.image_url ? (
          // Deliberately a plain <img>: catalog images come from third-party
          // affiliate CDNs we don't control, so next/image optimisation is
          // wired in later once we harden allowed domains.
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={product.image_url}
            alt={product.title}
            loading="lazy"
            className="h-full w-full object-cover transition-transform group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-slate-400">
            Tanpa gambar
          </div>
        )}
      </div>
      <div className="flex flex-1 flex-col gap-2 p-4">
        {product.category ? (
          <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
            {product.category}
          </span>
        ) : null}
        <h3 className="line-clamp-2 text-sm font-semibold text-slate-900">
          {product.title}
        </h3>
        <p className="mt-auto text-base font-bold text-slate-900">
          {formatPrice(product.price, product.currency)}
        </p>
      </div>
    </Link>
  );
}
