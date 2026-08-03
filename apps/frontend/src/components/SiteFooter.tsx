import Link from "next/link";

export function SiteFooter() {
  const year = new Date().getFullYear();

  const links = {
    Jelajahi: [
      { href: "/produk", label: "Katalog produk" },
      { href: "/koleksi", label: "Koleksi kurasi" },
      { href: "/artikel", label: "Panduan belanja" },
      { href: "/compare", label: "Perbandingan" },
    ],
    Tentang: [
      { href: "/metodologi", label: "Metodologi" },
      { href: "/pengungkapan-afiliasi", label: "Pengungkapan afiliasi" },
      { href: "/privasi", label: "Privasi" },
      { href: "/syarat-ketentuan", label: "Syarat & ketentuan" },
    ],
    Kontak: [
      { href: "/kontak", label: "Hubungi kami" },
      { href: "https://github.com/tantenton/affiloom", label: "GitHub", external: true },
    ],
  };

  return (
    <footer
      style={{
        background: "rgb(var(--color-surface))",
        borderTop: "1px solid rgb(var(--color-border))",
      }}
    >
      <div className="mx-auto max-w-7xl px-4 py-12">
        <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
          {/* Brand */}
          <div className="col-span-2 sm:col-span-1">
            <Link
              href="/"
              className="text-xl font-black tracking-tight"
              style={{ color: "rgb(var(--color-text))" }}
            >
              Affi<span style={{ color: "rgb(var(--color-primary))" }}>loom</span>
            </Link>
            <p className="mt-3 text-sm leading-relaxed" style={{ color: "rgb(var(--color-text-muted))" }}>
              Rekomendasi produk afiliasi transparan untuk marketplace Indonesia.
            </p>
            <p className="mt-2 text-xs font-medium" style={{ color: "rgb(var(--color-text-light))" }}>
              Komisi tercantum terbuka. Tanpa dark pattern.
            </p>
          </div>

          {/* Nav columns */}
          {Object.entries(links).map(([title, items]) => (
            <div key={title}>
              <h3
                className="text-xs font-bold uppercase tracking-wider"
                style={{ color: "rgb(var(--color-text))" }}
              >
                {title}
              </h3>
              <ul className="mt-4 space-y-2">
                {items.map((item) => (
                  <li key={item.href}>
                    {"external" in item && item.external ? (
                      <a
                        href={item.href}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm transition-colors hover:underline"
                        style={{ color: "rgb(var(--color-text-muted))" }}
                      >
                        {item.label}
                      </a>
                    ) : (
                      <Link
                        href={item.href}
                        className="text-sm transition-colors hover:underline"
                        style={{ color: "rgb(var(--color-text-muted))" }}
                      >
                        {item.label}
                      </Link>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div
          className="mt-12 flex flex-col items-center justify-between gap-2 border-t pt-6 text-xs sm:flex-row"
          style={{
            borderColor: "rgb(var(--color-border))",
            color: "rgb(var(--color-text-light))",
          }}
        >
          <p>© {year} Affiloom. Semua hak dilindungi.</p>
          <p>Data katalog: adaptor demo deterministik. Tidak ada scraping marketplace.</p>
        </div>
      </div>
    </footer>
  );
}
