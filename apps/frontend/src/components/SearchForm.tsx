/**
 * Uncontrolled server-friendly search form. Submits a GET to /produk?q=... so
 * the whole page (including search results) is a single server render.
 */
export function SearchForm({ defaultValue = "" }: { defaultValue?: string }) {
  return (
    <form
      action="/produk"
      method="get"
      className="flex w-full max-w-xl items-center gap-2"
      role="search"
    >
      <label htmlFor="product-search" className="sr-only">
        Cari produk
      </label>
      <input
        id="product-search"
        name="q"
        type="search"
        defaultValue={defaultValue}
        placeholder="Cari produk (mis. tas, kopi, sepatu)"
        className="flex-1 rounded-md border border-slate-300 bg-white px-3 py-2 text-sm shadow-sm placeholder:text-slate-400 focus:border-slate-900 focus:outline-none focus:ring-1 focus:ring-slate-900"
      />
      <button
        type="submit"
        className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-slate-700"
      >
        Cari
      </button>
    </form>
  );
}
