import Link from "next/link";

export function SiteHeader() {
  return (
    <>
      {/* Top nav */}
      <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          {/* Logo - text only, no SVG */}
          <Link
            href="/"
            className="text-lg font-black tracking-tight text-slate-900"
          >
            Affi<span className="text-indigo-600">loom</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden items-center gap-1 sm:flex" aria-label="Navigasi desktop">
            <Link href="/" className="rounded-lg px-3 py-2 text-sm text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900">
              Beranda
            </Link>
            <Link href="/produk" className="rounded-lg px-3 py-2 text-sm text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900">
              Katalog
            </Link>
            <Link href="/koleksi" className="rounded-lg px-3 py-2 text-sm text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900">
              Koleksi
            </Link>
            <Link href="/artikel" className="rounded-lg px-3 py-2 text-sm text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900">
              Panduan
            </Link>
            <Link
              href="/produk"
              className="ml-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition-colors hover:bg-indigo-700"
            >
              Cari produk
            </Link>
          </nav>
        </div>
      </header>

      {/* Mobile bottom nav — text labels only, no SVG */}
      <nav
        aria-label="Navigasi utama"
        className="fixed bottom-0 left-0 right-0 z-50 flex items-center border-t border-slate-200 bg-white sm:hidden"
        style={{ paddingBottom: "env(safe-area-inset-bottom, 0px)" }}
      >
        {[
          { href: "/", label: "Beranda", icon: "🏠" },
          { href: "/produk", label: "Katalog", icon: "🛍️" },
          { href: "/koleksi", label: "Koleksi", icon: "📦" },
          { href: "/artikel", label: "Panduan", icon: "📖" },
        ].map(({ href, label, icon }) => (
          <Link
            key={href}
            href={href}
            className="flex flex-1 flex-col items-center gap-0.5 py-2 text-slate-500 transition-colors hover:text-indigo-600"
          >
            <span className="text-lg leading-none" aria-hidden="true">{icon}</span>
            <span className="text-[10px] font-medium">{label}</span>
          </Link>
        ))}
      </nav>

      {/* Spacer for mobile bottom nav */}
      <div className="h-14 sm:hidden" aria-hidden="true" />
    </>
  );
}
