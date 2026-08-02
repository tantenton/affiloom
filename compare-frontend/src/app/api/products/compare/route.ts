import { NextResponse } from "next/server";
import { mockProducts } from "@/lib/mock";
import type { CompareResponse } from "@/lib/types";

export async function GET(req: Request) {
  const { searchParams } = new URL(req.url);
  const ids = (searchParams.get("ids") ?? "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  if (ids.length < 2) {
    return NextResponse.json(
      { error: "Minimal 2 produk untuk dibandingkan" },
      { status: 400 }
    );
  }

  const products = ids
    .map((id) => mockProducts.find((p) => p.id === id))
    .filter((p): p is NonNullable<typeof p> => Boolean(p));

  if (products.length < 2) {
    return NextResponse.json(
      { error: "Produk tidak ditemukan" },
      { status: 404 }
    );
  }

  // Compute key-wise differences for the first two products to match
  // the backend's CompareResponse shape.
  const [a, b] = products;
  const keys = Array.from(
    new Set([...Object.keys(a.specs ?? {}), ...Object.keys(b.specs ?? {})])
  );
  const differences = keys.map((field) => ({
    field,
    values: [
      a.specs?.[field] != null ? String(a.specs[field]) : null,
      b.specs?.[field] != null ? String(b.specs[field]) : null,
    ] as [string | null, string | null],
  }));

  const payload: CompareResponse = { products, differences };
  return NextResponse.json(payload);
}
