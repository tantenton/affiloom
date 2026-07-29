import { SiteHeader } from "@/components/SiteHeader";

export default function Loading() {
  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />
      <main
        className="mx-auto max-w-5xl px-4 py-10"
        aria-busy="true"
      >
        <div className="grid gap-8 md:grid-cols-2">
          <div className="aspect-square animate-pulse rounded-lg border bg-white" />
          <div className="flex flex-col gap-4">
            <div className="h-8 w-2/3 animate-pulse rounded bg-slate-200" />
            <div className="h-6 w-1/3 animate-pulse rounded bg-slate-200" />
            <div className="h-4 w-1/2 animate-pulse rounded bg-slate-200" />
            <div className="mt-6 h-12 w-48 animate-pulse rounded bg-slate-200" />
          </div>
        </div>
      </main>
    </div>
  );
}
