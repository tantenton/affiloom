"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

export function SiteHeader() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [q, setQ] = useState("");
  const pathname = usePathname();
  const router = useRouter();
  const searchRef = useRef<HTMLInputElement>(null);

  // Close menu on route change
  useEffect(() => {
    setMenuOpen(false);
    setSearchOpen(false);
  }, [pathname]);

  // Focus search input when opened
  useEffect(() => {
    if (searchOpen) searchRef.current?.focus();
  }, [searchOpen]);

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (q.trim()) router.push(`/produk?q=${encodeURIComponent(q.trim())}`);
    setSearchOpen(false);
  }

  const navLinks = [
    { href: "/", label: "Beranda" },
    { href: "/produk", label: "Katalog" },
    { href: "/koleksi", label: "Koleksi" },
    { href: "/artikel", label: "Panduan" },
    { href: "/compare", label: "Perbandingan" },
  ];

  return (
    <>
      <header
        className="sticky top-0 z-40"
        style={{
          background: "rgb(var(--color-surface))",
          borderBottom: "1px solid rgb(var(--color-border))",
          boxShadow: "var(--shadow-sm)",
        }}
      >
        <div className="mx-auto flex h-14 max-w-7xl items-center gap-3 px-4 sm:h-16">
          {/* Logo */}
          <Link
            href="/"
            className="flex-shrink-0 text-lg font-black tracking-tight"
            style={{ color: "rgb(var(--color-text))", minHeight: 44, display: "inline-flex", alignItems: "center" }}
          >
            Affi<span style={{ color: "rgb(var(--color-primary))" }}>loom</span>
          </Link>

          {/* Desktop search bar */}
          <form
            onSubmit={handleSearch}
            className="mx-4 hidden flex-1 max-w-xl sm:flex"
          >
            <div className="relative flex w-full items-center">
              <svg
                style={{ position: "absolute", left: 14, width: 16, height: 16, flexShrink: 0, color: "rgb(var(--color-text-muted))" }}
                viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
              >
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
              <input
                type="search"
                placeholder="Cari produk, koleksi, atau kategori…"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                className="input w-full pl-10 pr-4 text-sm"
                style={{ height: 40, minHeight: 40 }}
              />
            </div>
          </form>

          {/* Desktop nav */}
          <nav className="hidden items-center gap-0.5 sm:flex">
            {navLinks.map(({ href, label }) => {
              const active = pathname === href || (href !== "/" && pathname.startsWith(href));
              return (
                <Link
                  key={href}
                  href={href}
                  className="rounded-lg px-3 py-2 text-sm font-medium transition-all"
                  style={{
                    color: active ? "rgb(var(--color-primary))" : "rgb(var(--color-text-muted))",
                    background: active ? "rgb(var(--color-primary-light))" : "transparent",
                    minHeight: 44,
                    display: "inline-flex",
                    alignItems: "center",
                  }}
                >
                  {label}
                </Link>
              );
            })}
          </nav>

          {/* Mobile: search icon + hamburger */}
          <div className="ml-auto flex items-center gap-1 sm:hidden">
            <button
              aria-label="Cari"
              onClick={() => setSearchOpen((v) => !v)}
              className="flex items-center justify-center rounded-lg p-2 transition-colors"
              style={{ minHeight: 44, minWidth: 44, color: "rgb(var(--color-text-muted))" }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: 20, height: 20, flexShrink: 0 }}>
                <circle cx="11" cy="11" r="8" />
                <line x1="21" y1="21" x2="16.65" y2="16.65" />
              </svg>
            </button>
            <button
              aria-label={menuOpen ? "Tutup menu" : "Buka menu"}
              aria-expanded={menuOpen}
              onClick={() => setMenuOpen((v) => !v)}
              className="flex items-center justify-center rounded-lg p-2 transition-colors"
              style={{ minHeight: 44, minWidth: 44, color: "rgb(var(--color-text-muted))" }}
            >
              {menuOpen ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: 20, height: 20, flexShrink: 0 }}>
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ width: 20, height: 20, flexShrink: 0 }}>
                  <line x1="3" y1="6" x2="21" y2="6" />
                  <line x1="3" y1="12" x2="21" y2="12" />
                  <line x1="3" y1="18" x2="21" y2="18" />
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Mobile search bar — expands below header */}
        {searchOpen && (
          <div className="border-t px-4 py-3 sm:hidden" style={{ borderColor: "rgb(var(--color-border))", background: "rgb(var(--color-surface))" }}>
            <form onSubmit={handleSearch} className="flex gap-2">
              <input
                ref={searchRef}
                type="search"
                placeholder="Cari produk…"
                value={q}
                onChange={(e) => setQ(e.target.value)}
                className="input flex-1 text-sm"
                style={{ height: 44 }}
              />
              <button type="submit" className="btn btn-primary px-4 text-sm" style={{ height: 44, minHeight: 44 }}>
                Cari
              </button>
            </form>
          </div>
        )}

        {/* Mobile hamburger menu */}
        {menuOpen && (
          <nav
            aria-label="Menu mobile"
            className="border-t sm:hidden"
            style={{ borderColor: "rgb(var(--color-border))", background: "rgb(var(--color-surface))" }}
          >
            {navLinks.map(({ href, label }) => {
              const active = pathname === href || (href !== "/" && pathname.startsWith(href));
              return (
                <Link
                  key={href}
                  href={href}
                  className="flex items-center px-5 py-3 text-sm font-medium transition-colors"
                  style={{
                    color: active ? "rgb(var(--color-primary))" : "rgb(var(--color-text))",
                    borderLeft: active ? "3px solid rgb(var(--color-primary))" : "3px solid transparent",
                    minHeight: 44,
                  }}
                >
                  {label}
                </Link>
              );
            })}
            <div className="px-5 py-4">
              <Link href="/produk" className="btn btn-primary w-full justify-center text-sm">
                Lihat Katalog
              </Link>
            </div>
          </nav>
        )}
      </header>
    </>
  );
}
