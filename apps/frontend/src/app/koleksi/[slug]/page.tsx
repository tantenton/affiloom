import { Metadata } from "next";
import Link from "next/link";
import Image from "next/image";

import { SiteHeader } from "@/components/SiteHeader";
import { getCollection } from "@/lib/api";
import { NotFoundError } from "@/lib/types";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

type Props = {
  params: { slug: string };
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  try {
    const collection = await getCollection(params.slug);
    return {
      title: `${collection.title} — Affiloom`,
      description: collection.description || `Koleksi ${collection.title}`,
    };
  } catch (err) {
    if (err instanceof NotFoundError) {
      return { title: "Koleksi tidak ditemukan" };
    }
    return { title: "Koleksi" };
  }
}

export default async function CollectionDetailPage({ params }: Props) {
  let collection;
  try {
    collection = await getCollection(params.slug);
  } catch (err) {
    if (err instanceof NotFoundError) {
      notFound();
    }
    throw err;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />
      <main className="mx-auto max-w-6xl px-4 py-12">
        <p className="text-xs font-bold uppercase tracking-widest text-indigo-600">
          Koleksi
        </p>
        <h1 className="mt-2 text-4xl font-bold tracking-tight text-slate-900">
          {collection.title}
        </h1>
        {collection.description ? (
          <p className="mt-3 max-w-2xl text-slate-600">{collection.description}</p>
        ) : null}

        {collection.products.length === 0 ? (
          <section className="mt-10 rounded-2xl border border-dashed border-slate-300 bg-white p-12 text-center">
            <h2 className="text-lg font-semibold text-slate-900">
              Belum ada produk
            </h2>
            <p className="mt-2 text-sm text-slate-600">
              Produk dalam koleksi ini akan segera hadir.
            </p>
          </section>
        ) : (
          <section className="mt-10 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {collection.products.map((product) => (
              <Link
                key={product.id}
                href={`/produk/${product.id}`}
                className="card card-hover flex h-full flex-col overflow-hidden no-underline"
              >
                {product.image_url ? (
                  <div className="relative aspect-square w-full overflow-hidden bg-slate-100">
                    <Image
                      src={product.image_url}
                      alt={product.title}
                      fill
                      className="object-cover"
                      sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
                    />
                  </div>
                ) : (
                  <div className="flex aspect-square w-full items-center justify-center bg-slate-100">
                    <span className="text-sm text-slate-400">No image</span>
                  </div>
                )}
                <div className="flex flex-1 flex-col justify-between p-4">
                  <div>
                    <h2 className="text-base font-semibold text-slate-900 line-clamp-2">
                      {product.title}
                    </h2>
                    {product.category ? (
                      <p className="mt-1 text-xs text-slate-500">{product.category}</p>
                    ) : null}
                  </div>
                  {product.price != null && product.currency ? (
                    <p className="mt-3 text-lg font-bold text-indigo-600">
                      {product.currency} {product.price.toLocaleString("id-ID")}
                    </p>
                  ) : null}
                </div>
              </Link>
            ))}
          </section>
        )}
      </main>
    </div>
  );
}
