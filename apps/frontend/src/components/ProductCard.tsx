import Link from "next/link";
import { formatPrice } from "@/lib/format";
import { Product } from "@/lib/types";

export function ProductCard({ product }: { product: Product }) {
  return (
    <div className="group flex flex-col overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200/60 transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:ring-slate-300">
      {/* Image */}
      <Link
        href={`/produk/${product.id}`}
        className="relative block aspect-[4/3] w-full overflow-hidden bg-gradient-to-br from-slate-100 to-slate-200"
        tabIndex={-1}
        aria-hidden="true"
      >
        {product.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={product.image_url}
            alt={product.title}
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <svg className="h-12 w-12 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
        {/* Category badge overlay */}
        {product.category && (
          <span className="absolute left-3 top-3 rounded-full bg-white/90 px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-widest text-indigo-700 shadow-sm backdrop-blur-sm">
            {product.category}
          </span>
        )}
      </Link>

      {/* Content */}
      <div className="flex flex-1 flex-col p-4">
        <Link href={`/produk/${product.id}`}>
          <h3 className="line-clamp-2 text-sm font-semibold leading-snug text-slate-900 transition-colors group-hover:text-indigo-600">
            {product.title}
          </h3>
        </Link>

        {product.description && (
          <p className="mt-1.5 line-clamp-2 text-xs leading-relaxed text-slate-500">
            {product.description}
          </p>
        )}

        <div className="mt-auto flex items-end justify-between pt-4">
          <div>
            <p className="text-lg font-bold tracking-tight text-slate-900">
              {formatPrice(product.price, product.currency)}
            </p>
            {product.commission_rate != null && (
              <p className="mt-0.5 text-[10px] font-semibold uppercase tracking-wide text-emerald-600">
                {(product.commission_rate * 100).toFixed(0)}% komisi
              </p>
            )}
          </div>
          <Link
            href={`/produk/${product.id}`}
            className="rounded-xl bg-slate-900 px-3 py-1.5 text-[11px] font-bold text-white transition-colors hover:bg-indigo-600"
          >
            Detail
          </Link>
        </div>
      </div>
    </div>
  );
}
