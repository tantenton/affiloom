"use client";

import { Suspense } from "react";
import CompareContent from "./content";

function LoadingFallback() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <div className="h-8 w-64 animate-pulse rounded bg-zinc-100 dark:bg-zinc-800" />
      <div className="mt-6 h-72 animate-pulse rounded-2xl bg-zinc-100 dark:bg-zinc-800" />
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <CompareContent />
    </Suspense>
  );
}