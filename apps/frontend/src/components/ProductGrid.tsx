import Link from "next/link";
import { ProductCardSkeleton } from "@/components/ProductCard";
import { Product } from "@/lib/types";
import { ProductCard } from "@/components/ProductCard";

// ---- ProductGrid ----
interface ProductGridProps {
  items?: Product[];
  loading?: boolean;
  skeletonCount?: number;
}

export function ProductGrid({ items, loading = false, skeletonCount = 8 }: ProductGridProps) {
  return (
    <ul
      className="grid grid-cols-2 gap-3 sm:grid-cols-3 sm:gap-4 lg:grid-cols-4 lg:gap-5"
      aria-busy={loading}
      aria-label="Daftar produk"
    >
      {loading
        ? Array.from({ length: skeletonCount }).map((_, i) => (
            <li key={i} aria-hidden="true">
              <ProductCardSkeleton />
            </li>
          ))
        : items?.map((item) => (
            <li key={item.id}>
              <ProductCard product={item} />
            </li>
          ))}
    </ul>
  );
}

// ---- EmptyState ----
interface EmptyStateProps {
  query?: string | null;
  title?: string;
  description?: string;
}

export function EmptyState({ query, title, description }: EmptyStateProps) {
  const heading = title ?? (query ? "Tidak ada produk yang cocok" : "Belum ada produk");
  const body = description ?? (
    query
      ? `Tidak ada produk untuk "${query}". Coba kata kunci lain.`
      : "Katalog kosong. Silakan cek kembali nanti."
  );

  return (
    <section
      className="flex flex-col items-center rounded-2xl border border-dashed px-6 py-16 text-center"
      style={{
        borderColor: "rgb(var(--color-border))",
        background: "rgb(var(--color-surface))",
      }}
      aria-label="Tidak ada hasil"
    >
      <svg
        width="48"
        height="48"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        style={{ width: 48, height: 48, flexShrink: 0, color: "rgb(var(--color-border))" }}
        aria-hidden="true"
      >
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
      </svg>

      <h2
        className="mt-4 text-lg font-semibold"
        style={{ color: "rgb(var(--color-text))" }}
      >
        {heading}
      </h2>
      <p className="mt-2 max-w-sm text-sm leading-relaxed" style={{ color: "rgb(var(--color-text-muted))" }}>
        {body}
      </p>
      {query && (
        <Link
          href="/produk"
          className="btn btn-secondary mt-6"
        >
          Reset pencarian
        </Link>
      )}
    </section>
  );
}

// ---- ErrorState ----
interface ErrorStateProps {
  message?: string;
  onRetry?: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <section
      role="alert"
      aria-live="polite"
      className="flex flex-col items-center rounded-2xl border px-6 py-12 text-center"
      style={{
        borderColor: "rgb(var(--color-danger) / 0.3)",
        background: "rgb(var(--color-danger-light))",
      }}
    >
      <svg
        width="40"
        height="40"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        style={{ width: 40, height: 40, flexShrink: 0, color: "rgb(var(--color-danger))" }}
        aria-hidden="true"
      >
        <circle cx="12" cy="12" r="10" />
        <line x1="12" y1="8" x2="12" y2="12" />
        <line x1="12" y1="16" x2="12.01" y2="16" />
      </svg>
      <h2
        className="mt-3 text-base font-semibold"
        style={{ color: "rgb(var(--color-danger))" }}
      >
        Gagal memuat produk
      </h2>
      <p className="mt-1 text-sm" style={{ color: "rgb(var(--color-danger))" }}>
        {message ?? "Terjadi kesalahan. Silakan coba lagi."}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="btn btn-secondary mt-4 text-sm"
        >
          Coba lagi
        </button>
      )}
    </section>
  );
}
