"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type Stored = string[];
const STORAGE_KEY = "compare_ids";
const MAX_COMPARE = 3;

function read(): Stored {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as Stored) : [];
  } catch {
    return [];
  }
}

function write(ids: Stored) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(ids));
  window.dispatchEvent(new Event("compare:update"));
}

export function getSelected(): Stored {
  return read();
}

export function isSelected(id: string): boolean {
  return read().includes(id);
}

export function toggleSelected(id: string) {
  const cur = read();
  const next = cur.includes(id)
    ? cur.filter((x) => x !== id)
    : cur.length < MAX_COMPARE
      ? [...cur, id]
      : cur; // ignore when full
  write(next);
}

export function useSelected(): [Stored, (id: string) => void] {
  const [selected, setSelected] = useState<Stored>(() => read());

  useEffect(() => {
    const handler = () => setSelected(read());
    window.addEventListener("compare:update", handler);
    window.addEventListener("storage", handler);
    return () => {
      window.removeEventListener("compare:update", handler);
      window.removeEventListener("storage", handler);
    };
  }, []);

  const toggle = (id: string) => toggleSelected(id);
  return [selected, toggle];
}

export function CompareBar() {
  const [selected] = useSelected();
  if (selected.length === 0) return null;

  const href = `/compare?ids=${encodeURIComponent(selected.join(","))}`;
  return (
    <div className="fixed inset-x-0 bottom-0 z-40 border-t border-zinc-200 bg-white/95 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/95">
      <div className="mx-auto flex max-w-3xl items-center justify-between gap-3 px-4 py-3">
        <p className="text-sm text-zinc-700 dark:text-zinc-300">
          <span className="font-semibold text-zinc-900 dark:text-zinc-100">
            {selected.length}
          </span>{" "}
          produk dipilih (maks. {MAX_COMPARE})
        </p>
        <Link
          href={href}
          aria-disabled={selected.length < 2}
          className="inline-flex h-10 items-center justify-center rounded-full bg-blue-600 px-5 text-sm font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-40 dark:bg-blue-500 dark:hover:bg-blue-400"
        >
          Bandingkan
        </Link>
      </div>
    </div>
  );
}

export const MAX = MAX_COMPARE;
