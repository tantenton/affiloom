import Link from "next/link";
import { formatPrice } from "@/lib/format";
import { Product } from "@/lib/types";

export function ProductCard({ product }: { product: Product }) {
  return (
    <article className="group flex flex-col overflow-hidden rounded-2xl border border-gray-100 bg-white shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md">
      {/* Image — constrained, never overflow */}
      <Link
        href={`/produk/${product.id}`}
        className="relative block w-full overflow-hidden bg-gray-100"
        style={{ aspectRatio: "4/3" }}
        tabIndex={-1}
        aria-hidden="true"
      >
        {product.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={product.image_url}
            alt={product.title}
            loading="lazy"
            style={{
              width: "100%",
              height: "100%",
              objectFit: "cover",
              display: "block",
              maxWidth: "100%",
              maxHeight: "100%",
            }}
            className="transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="40"
              height="40"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              className="text-gray-300"
              style={{ width: 40, height: 40, flexShrink: 0 }}
            >
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
          </div>
        )}

        {/* Category overlay badge */}
        {product.category && (
          <span
            className="absolute left-2 top-2 rounded-full bg-white/90 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider text-indigo-700 shadow-sm"
            style={{ backdropFilter: "blur(4px)" }}
          >
            {product.category}
          </span>
        )}
      </Link>

      {/* Content */}
      <div className="flex flex-1 flex-col p-3 sm:p-4">
        <Link href={`/produk/${product.id}`} className="block" style={{ minHeight: 44 }}>
          <h3 className="line-clamp-2 text-sm font-semibold leading-snug text-gray-900 transition-colors group-hover:text-indigo-600">
            {product.title}
          </h3>
        </Link>

        {product.description && (
          <p className="mt-1 line-clamp-2 text-xs leading-relaxed text-gray-500">
            {product.description}
          </p>
        )}

        <div className="mt-auto flex items-end justify-between gap-2 pt-3">
          <div className="min-w-0">
            <p className="text-base font-bold text-gray-900 sm:text-lg">
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
            className="flex-shrink-0 rounded-lg bg-indigo-600 px-3 py-2 text-[11px] font-bold text-white transition-colors hover:bg-indigo-700"
            style={{ minHeight: 36, minWidth: 44, display: "inline-flex", alignItems: "center" }}
          >
            Detail
          </Link>
        </div>
      </div>
    </article>
  );
}
