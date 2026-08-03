"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const CATEGORIES = [
  "Fashion",
  "Elektronik",
  "Kuliner",
  "Kecantikan",
  "Olahraga",
  "Rumah Tangga",
  "Peralatan",
  "Alat Tulis",
];

const SORT_OPTIONS = [
  { label: "Relevansi", value: "" },
  { label: "Harga: Rendah ke Tinggi", value: "price_asc" },
  { label: "Harga: Tinggi ke Rendah", value: "price_desc" },
  { label: "Komisi Tertinggi", value: "commission_desc" },
];

function buildHref(category: string | null, q: string | null, sort: string) {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (category) params.set("category", category);
  if (sort) params.set("sort", sort);
  const s = params.toString();
  return `/produk${s ? `?${s}` : ""}`;
}

interface Props {
  currentCategory: string | null;
  currentQuery: string | null;
  currentSort: string | null;
}

function FilterContent({ currentCategory, currentQuery, currentSort, onClose }: Props & { onClose?: () => void }) {
  return (
    <div className="flex flex-col gap-6">
      {/* Categories */}
      <div>
        <p className="mb-3 text-xs font-bold uppercase tracking-widest" style={{ color: "rgb(var(--color-text-muted))" }}>
          Kategori
        </p>
        <ul className="space-y-0.5">
          <li>
            <Link
              href={buildHref(null, currentQuery, currentSort || "")}
              onClick={onClose}
              className="flex w-full items-center rounded-lg px-3 py-2 text-sm font-medium transition-all"
              style={{
                background: !currentCategory ? "rgb(var(--color-primary-light))" : "transparent",
                color: !currentCategory ? "rgb(var(--color-primary))" : "rgb(var(--color-text-muted))",
              }}
            >
              Semua produk
            </Link>
          </li>
          {CATEGORIES.map((cat) => {
            const active = currentCategory === cat;
            return (
              <li key={cat}>
                <Link
                  href={buildHref(cat, currentQuery, currentSort || "")}
                  onClick={onClose}
                  className="flex w-full items-center rounded-lg px-3 py-2 text-sm font-medium transition-all"
                  style={{
                    background: active ? "rgb(var(--color-primary-light))" : "transparent",
                    color: active ? "rgb(var(--color-primary))" : "rgb(var(--color-text-muted))",
                  }}
                >
                  {cat}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>

      {/* Sort */}
      <div>
        <p className="mb-3 text-xs font-bold uppercase tracking-widest" style={{ color: "rgb(var(--color-text-muted))" }}>
          Urutkan
        </p>
        <ul className="space-y-0.5">
          {SORT_OPTIONS.map(({ label, value }) => {
            const active = (currentSort || "") === value;
            return (
              <li key={value}>
                <Link
                  href={buildHref(currentCategory, currentQuery, value)}
                  onClick={onClose}
                  className="flex w-full items-center rounded-lg px-3 py-2 text-sm font-medium transition-all"
                  style={{
                    background: active ? "rgb(var(--color-primary-light))" : "transparent",
                    color: active ? "rgb(var(--color-primary))" : "rgb(var(--color-text-muted))",
                  }}
                >
                  {label}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}

export function ProductFilters({ currentCategory, currentQuery, currentSort }: Props) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  // Close on Escape
  useEffect(() => {
    if (!drawerOpen) return;
    const handler = (e: KeyboardEvent) => { if (e.key === "Escape") setDrawerOpen(false); };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [drawerOpen]);

  // Lock body scroll when drawer open
  useEffect(() => {
    if (drawerOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => { document.body.style.overflow = ""; };
  }, [drawerOpen]);

  const activeCount = [currentCategory, currentSort].filter(Boolean).length;

  return (
    <>
      {/* Desktop sidebar */}
      <aside
        className="hidden lg:block w-52 flex-shrink-0"
        aria-label="Filter produk"
      >
        <div
          className="sticky top-20 rounded-2xl p-4"
          style={{
            background: "rgb(var(--color-surface))",
            border: "1px solid rgb(var(--color-border))",
            boxShadow: "var(--shadow-sm)",
          }}
        >
          <p className="mb-4 text-sm font-bold" style={{ color: "rgb(var(--color-text))" }}>
            Filter
          </p>
          <FilterContent
            currentCategory={currentCategory}
            currentQuery={currentQuery}
            currentSort={currentSort}
          />
        </div>
      </aside>

      {/* Mobile: sticky filter button */}
      <div className="lg:hidden">
        <button
          onClick={() => setDrawerOpen(true)}
          className="btn btn-secondary flex items-center gap-2 text-sm"
          style={{ height: 40, minHeight: 40 }}
          aria-expanded={drawerOpen}
          aria-controls="filter-drawer"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: 16, height: 16, flexShrink: 0 }}>
            <line x1="4" y1="6" x2="20" y2="6" />
            <line x1="8" y1="12" x2="20" y2="12" />
            <line x1="12" y1="18" x2="20" y2="18" />
          </svg>
          Filter &amp; Urutkan
          {activeCount > 0 && (
            <span
              className="ml-1 rounded-full px-1.5 py-0.5 text-[10px] font-bold text-white"
              style={{ background: "rgb(var(--color-primary))" }}
            >
              {activeCount}
            </span>
          )}
        </button>

        {/* Backdrop */}
        {drawerOpen && (
          <div
            className="fixed inset-0 z-40"
            style={{ background: "rgba(0,0,0,0.4)", backdropFilter: "blur(2px)" }}
            onClick={() => setDrawerOpen(false)}
            aria-hidden="true"
          />
        )}

        {/* Bottom drawer */}
        <div
          id="filter-drawer"
          role="dialog"
          aria-modal="true"
          aria-label="Filter produk"
          className="fixed bottom-0 left-0 right-0 z-50 rounded-t-2xl p-6 transition-transform duration-300"
          style={{
            background: "rgb(var(--color-surface))",
            boxShadow: "0 -4px 24px rgb(0 0 0 / 0.12)",
            transform: drawerOpen ? "translateY(0)" : "translateY(100%)",
            maxHeight: "80vh",
            overflowY: "auto",
          }}
        >
          <div className="mb-5 flex items-center justify-between">
            <p className="text-base font-bold" style={{ color: "rgb(var(--color-text))" }}>
              Filter &amp; Urutkan
            </p>
            <button
              onClick={() => setDrawerOpen(false)}
              className="flex items-center justify-center rounded-lg p-2 transition-colors"
              style={{ minHeight: 44, minWidth: 44, color: "rgb(var(--color-text-muted))" }}
              aria-label="Tutup filter"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: 20, height: 20, flexShrink: 0 }}>
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <FilterContent
            currentCategory={currentCategory}
            currentQuery={currentQuery}
            currentSort={currentSort}
            onClose={() => setDrawerOpen(false)}
          />
          <div className="mt-6 pb-safe">
            <button
              onClick={() => setDrawerOpen(false)}
              className="btn btn-primary w-full justify-center"
            >
              Terapkan Filter
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
