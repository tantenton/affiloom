import Link from "next/link";

// Desktop: top nav. Mobile: logo only on top + sticky bottom nav bar.
export function SiteHeader() {
  return (
    <>
      <header className="sticky top-0 z-40 border-b bg-white/90 backdrop-blur-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <Link
            href="/"
            className="text-lg font-black tracking-tight text-slate-900"
          >
            Affi<span className="text-indigo-600">loom</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden items-center gap-1 text-sm sm:flex">
            {[
              { href: "/", label: "Beranda" },
              { href: "/produk", label: "Katalog" },
              { href: "/koleksi", label: "Koleksi" },
              { href: "/artikel", label: "Panduan" },
            ].map(({ href, label }) => (
              <Link
                key={href}
                href={href}
                className="rounded-lg px-3 py-1.5 text-slate-600 transition-colors hover:bg-slate-100 hover:text-slate-900"
              >
                {label}
              </Link>
            ))}
            <Link
              href="/produk"
              className="ml-2 rounded-lg bg-slate-900 px-4 py-1.5 text-sm font-semibold text-white transition-colors hover:bg-slate-700"
            >
              Cari produk
            </Link>
          </nav>
        </div>
      </header>

      {/* Mobile bottom nav */}
      <nav
        aria-label="Navigasi utama"
        className="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-around border-t bg-white/95 pb-safe px-2 py-2 backdrop-blur-sm sm:hidden"
        style={{ paddingBottom: "max(0.5rem, env(safe-area-inset-bottom))" }}
      >
        {[
          {
            href: "/",
            label: "Beranda",
            icon: (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-5 w-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
            ),
          },
          {
            href: "/produk",
            label: "Katalog",
            icon: (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-5 w-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 10h16M4 14h16M4 18h16" />
              </svg>
            ),
          },
          {
            href: "/koleksi",
            label: "Koleksi",
            icon: (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-5 w-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            ),
          },
          {
            href: "/artikel",
            label: "Panduan",
            icon: (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} className="h-5 w-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            ),
          },
        ].map(({ href, label, icon }) => (
          <Link
            key={href}
            href={href}
            className="flex flex-col items-center gap-0.5 px-3 py-1 text-slate-500 transition-colors hover:text-indigo-600"
          >
            {icon}
            <span className="text-[10px] font-medium">{label}</span>
          </Link>
        ))}
      </nav>

      {/* Spacer so content isn't hidden behind bottom nav on mobile */}
      <div className="h-16 sm:hidden" />
    </>
  );
}
