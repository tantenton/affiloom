import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="border-t bg-slate-50">
      <div className="mx-auto max-w-6xl px-4 py-12">
        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
          {/* Brand */}
          <div>
            <Link href="/" className="text-xl font-black tracking-tight text-slate-900">
              Affi<span className="text-indigo-600">loom</span>
            </Link>
            <p className="mt-3 text-sm text-slate-600">
              Rekomendasi produk afiliasi transparan untuk marketplace Indonesia.
            </p>
          </div>

          {/* Jelajahi */}
          <div>
            <h3 className="text-sm font-bold text-slate-900">Jelajahi</h3>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <Link href="/produk" className="text-slate-600 hover:text-slate-900">
                  Katalog produk
                </Link>
              </li>
              <li>
                <Link href="/koleksi" className="text-slate-600 hover:text-slate-900">
                  Koleksi kurasi
                </Link>
              </li>
              <li>
                <Link href="/artikel" className="text-slate-600 hover:text-slate-900">
                  Panduan belanja
                </Link>
              </li>
            </ul>
          </div>

          {/* Tentang */}
          <div>
            <h3 className="text-sm font-bold text-slate-900">Tentang</h3>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <Link href="/metodologi" className="text-slate-600 hover:text-slate-900">
                  Metodologi
                </Link>
              </li>
              <li>
                <Link href="/pengungkapan-afiliasi" className="text-slate-600 hover:text-slate-900">
                  Pengungkapan afiliasi
                </Link>
              </li>
              <li>
                <Link href="/privasi" className="text-slate-600 hover:text-slate-900">
                  Privasi
                </Link>
              </li>
              <li>
                <Link href="/syarat-ketentuan" className="text-slate-600 hover:text-slate-900">
                  Syarat & ketentuan
                </Link>
              </li>
            </ul>
          </div>

          {/* Kontak */}
          <div>
            <h3 className="text-sm font-bold text-slate-900">Kontak</h3>
            <ul className="mt-3 space-y-2 text-sm">
              <li>
                <Link href="/kontak" className="text-slate-600 hover:text-slate-900">
                  Hubungi kami
                </Link>
              </li>
              <li>
                <a
                  href="https://github.com/tantenton/affiloom"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-600 hover:text-slate-900"
                >
                  GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 border-t border-slate-200 pt-8 text-center text-sm text-slate-500">
          <p>© {new Date().getFullYear()} Affiloom. Semua hak dilindungi.</p>
          <p className="mt-2">
            Data katalog: adaptor demo deterministik. Tidak ada scraping marketplace.
          </p>
        </div>
      </div>
    </footer>
  );
}
