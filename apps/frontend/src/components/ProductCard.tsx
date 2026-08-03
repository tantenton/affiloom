import Link from "next/link";
import { formatPrice } from "@/lib/format";
import { Product } from "@/lib/types";

interface ProductCardProps {
  product: Product;
  loading?: boolean;
  showCompare?: boolean;
  onCompareToggle?: (id: string) => void;
  compareChecked?: boolean;
}

export function ProductCard({ 
  product, 
  loading = false,
  showCompare = false,
  onCompareToggle,
  compareChecked = false,
}: ProductCardProps) {
  // Calculate freshness
  const lastSeenDate = new Date(product.last_seen_at);
  const hoursSinceUpdate = (Date.now() - lastSeenDate.getTime()) / (1000 * 60 * 60);
  const isStale = hoursSinceUpdate > 24;
  const isFresh = hoursSinceUpdate < 1;

  // Extract brand from source (demo: "tokopedia" -> "Tokopedia")
  const brand = product.source.charAt(0).toUpperCase() + product.source.slice(1);

  if (loading) {
    return <ProductCardSkeleton />;
  }

  return (
    <article 
      className="group relative flex flex-col overflow-hidden card card-hover"
      style={{ minHeight: 320 }}
    >
      {/* Compare checkbox (top-left, overlays image) */}
      {showCompare && (
        <label
          className="absolute left-2 top-2 z-10 flex items-center gap-1.5 rounded-lg px-2 py-1 text-xs font-medium backdrop-blur-sm"
          style={{ 
            background: "rgba(255,255,255,0.9)",
            cursor: "pointer",
            minHeight: 32,
          }}
          onClick={(e) => e.stopPropagation()}
        >
          <input
            type="checkbox"
            checked={compareChecked}
            onChange={() => onCompareToggle?.(product.id)}
            className="h-4 w-4 rounded border-gray-300"
            style={{ accentColor: "rgb(var(--color-primary))" }}
          />
          <span style={{ color: "rgb(var(--color-text))" }}>Bandingkan</span>
        </label>
      )}

      {/* Image */}
      <Link
        href={`/produk/${product.id}`}
        className="relative block w-full overflow-hidden"
        style={{ 
          aspectRatio: "4/3",
          background: "rgb(var(--color-bg))",
        }}
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
            }}
            className="transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center">
            <svg
              width="32"
              height="32"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              style={{ width: 32, height: 32, flexShrink: 0, color: "rgb(var(--color-border))" }}
            >
              <rect x="3" y="3" width="18" height="18" rx="2" />
              <circle cx="8.5" cy="8.5" r="1.5" />
              <polyline points="21 15 16 10 5 21" />
            </svg>
          </div>
        )}

        {/* Category badge (only if factual from backend) */}
        {product.category && (
          <span
            className="badge badge-category absolute right-2 top-2 shadow-sm"
            style={{ backdropFilter: "blur(4px)" }}
          >
            {product.category}
          </span>
        )}
      </Link>

      {/* Content */}
      <div className="flex flex-1 flex-col p-3 sm:p-4">
        {/* Brand + Freshness */}
        <div className="mb-2 flex items-center justify-between gap-2">
          <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: "rgb(var(--color-text-muted))" }}>
            {brand}
          </span>
          {isFresh && (
            <span className="badge text-[9px]" style={{ background: "rgb(var(--color-success-light))", color: "rgb(var(--color-success))" }}>
              Baru
            </span>
          )}
          {isStale && (
            <span className="badge text-[9px]" style={{ background: "rgb(var(--color-warning-light))", color: "rgb(var(--color-warning))" }}>
              Harga lama
            </span>
          )}
        </div>

        {/* Title */}
        <Link href={`/produk/${product.id}`} className="block">
          <h3 
            className="line-clamp-2 text-sm font-semibold leading-snug transition-colors group-hover:underline"
            style={{ color: "rgb(var(--color-text))", minHeight: 40 }}
          >
            {product.title}
          </h3>
        </Link>

        {/* Description / Best for (optional, factual only) */}
        {product.description && (
          <p className="mt-1 line-clamp-2 text-xs leading-relaxed" style={{ color: "rgb(var(--color-text-muted))" }}>
            {product.description}
          </p>
        )}

        {/* Price + Commission */}
        <div className="mt-auto flex items-end justify-between gap-2 pt-3">
          <div className="min-w-0">
            {product.price != null && product.currency ? (
              <p className="text-base font-bold sm:text-lg" style={{ color: "rgb(var(--color-text))" }}>
                {formatPrice(product.price, product.currency)}
              </p>
            ) : (
              <p className="text-sm font-medium" style={{ color: "rgb(var(--color-text-muted))" }}>
                Harga tidak tersedia
              </p>
            )}
            {product.commission_rate != null && (
              <p className="badge badge-commission mt-1 text-[9px]">
                {(product.commission_rate * 100).toFixed(0)}% komisi
              </p>
            )}
          </div>
          <Link
            href={`/produk/${product.id}`}
            className="btn btn-primary flex-shrink-0 px-3 py-2 text-xs"
            style={{ minHeight: 36, fontSize: "11px" }}
          >
            Detail
          </Link>
        </div>
      </div>
    </article>
  );
}

// Skeleton state
export function ProductCardSkeleton() {
  return (
    <div className="card animate-pulse" style={{ minHeight: 320 }}>
      <div className="aspect-[4/3] w-full" style={{ background: "rgb(var(--color-border))" }} />
      <div className="flex flex-1 flex-col p-3 sm:p-4">
        <div className="mb-2 h-3 w-16 rounded" style={{ background: "rgb(var(--color-border))" }} />
        <div className="h-4 w-full rounded" style={{ background: "rgb(var(--color-border))" }} />
        <div className="mt-1 h-4 w-3/4 rounded" style={{ background: "rgb(var(--color-border))" }} />
        <div className="mt-2 h-3 w-full rounded" style={{ background: "rgb(var(--color-border))" }} />
        <div className="mt-auto flex items-end justify-between gap-2 pt-3">
          <div className="h-5 w-20 rounded" style={{ background: "rgb(var(--color-border))" }} />
          <div className="h-9 w-16 rounded" style={{ background: "rgb(var(--color-border))" }} />
        </div>
      </div>
    </div>
  );
}
