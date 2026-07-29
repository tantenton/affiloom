import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="border-b bg-white">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4">
        <Link href="/" className="text-xl font-bold tracking-tight text-slate-900">
          Affiloom
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link href="/" className="text-slate-600 hover:text-slate-900">
            Beranda
          </Link>
          <Link
            href="/produk"
            className="text-slate-600 hover:text-slate-900"
          >
            Katalog
          </Link>
        </nav>
      </div>
    </header>
  );
}
