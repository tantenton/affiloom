import { SiteHeader } from "@/components/SiteHeader";

export default function Loading() {
  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />
      <main className="mx-auto max-w-5xl px-4 py-10" aria-busy="true">
        <div className="h-8 w-64 animate-pulse rounded bg-slate-200" />
        <div className="mt-3 h-4 w-96 animate-pulse rounded bg-slate-200" />
        <ul className="mt-8 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, index) => (
            <li
              key={index}
              className="h-72 animate-pulse rounded-lg border bg-white"
            />
          ))}
        </ul>
      </main>
    </div>
  );
}
