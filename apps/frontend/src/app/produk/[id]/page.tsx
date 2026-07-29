import { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { AffiliateDisclosure } from "@/components/AffiliateDisclosure";
import { SiteHeader } from "@/components/SiteHeader";
import { getProduct } from "@/lib/api";
import { formatCommission, formatPrice } from "@/lib/format";
import { NotFoundError, Product } from "@/lib/types";

export const dynamic = "force-dynamic";

type Params = { id: string };

async function loadProduct(id: string): Promise<Product | null> {
  try {
    return await getProduct(id);
  } catch (error) {
    if (error instanceof NotFoundError) return null;
    throw error;
  }
}

export async function generateMetadata({
  params,
}: {
  params: Params;
}): Promise<Metadata> {
  const product = await loadProduct(params.id);
  if (!product) {
    return {
      title: "Produk tidak ditemukan — Affiloom",
      description: "Produk yang kamu cari tidak tersedia di katalog Affiloom.",
      robots: { index: false, follow: false },
    };
  }
  const price = formatPrice(product.price, product.currency);
  return {
    title: `${product.title} — Affiloom`,
    description:
      product.description ??
      `${product.title} dari ${product.source}. Harga ${price}.`,
    openGraph: {
      title: `${product.title} — Affiloom`,
      description:
        product.description ??
        `${product.title} dari ${product.source}. Harga ${price}.`,
      images: product.image_url ? [{ url: product.image_url }] : undefined,
      locale: "id_ID",
      type: "website",
    },
  };
}

export default async function ProductDetailPage({
  params,
}: {
  params: Params;
}) {
  const product = await loadProduct(params.id);
  if (!product) {
    notFound();
  }

  const priceLabel = formatPrice(product.price, product.currency);
  const commission = formatCommission(product.commission_rate);

  const jsonLd = {
    "@context": "https://schema.org/",
    "@type": "Product",
    name: product.title,
    description: product.description ?? product.title,
    image: product.image_url ? [product.image_url] : undefined,
    sku: product.id,
    category: product.category ?? undefined,
    brand: { "@type": "Brand", name: product.source },
    offers:
      product.price != null
        ? {
            "@type": "Offer",
            price: product.price,
            priceCurrency: product.currency ?? "IDR",
            availability: "https://schema.org/InStock",
            url: product.url,
          }
        : undefined,
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />

      <main className="mx-auto max-w-5xl px-4 py-10">
        <nav aria-label="Breadcrumb" className="mb-6 text-sm text-slate-500">
          <Link href="/produk" className="hover:text-slate-900">
            ← Kembali ke katalog
          </Link>
        </nav>

        <div className="grid gap-8 md:grid-cols-2">
          <div className="overflow-hidden rounded-lg border bg-white">
            {product.image_url ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={product.image_url}
                alt={product.title}
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="flex aspect-square items-center justify-center text-slate-400">
                Tanpa gambar
              </div>
            )}
          </div>

          <div className="flex flex-col gap-4">
            {product.category ? (
              <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
                {product.category}
              </span>
            ) : null}
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
              {product.title}
            </h1>
            <p className="text-2xl font-semibold text-slate-900">
              {priceLabel}
            </p>

            <dl className="mt-2 grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-slate-500">Sumber</dt>
                <dd className="font-medium text-slate-900">{product.source}</dd>
              </div>
              {commission ? (
                <div>
                  <dt className="text-slate-500">Komisi afiliasi</dt>
                  <dd className="font-medium text-slate-900">{commission}</dd>
                </div>
              ) : null}
              <div>
                <dt className="text-slate-500">ID produk</dt>
                <dd className="font-mono text-slate-900">{product.id}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Terakhir dilihat</dt>
                <dd className="text-slate-900">
                  {new Date(product.last_seen_at).toLocaleDateString("id-ID")}
                </dd>
              </div>
            </dl>

            {product.description ? (
              <p className="mt-4 leading-relaxed text-slate-700">
                {product.description}
              </p>
            ) : null}

            <a
              href={product.url}
              target="_blank"
              rel="sponsored nofollow noopener noreferrer"
              className="mt-6 inline-flex w-fit items-center justify-center rounded-md bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-sm hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:ring-offset-2"
              data-testid="affiliate-cta"
            >
              Beli via mitra afiliasi
            </a>

            <AffiliateDisclosure variant="inline" />
          </div>
        </div>
      </main>

      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(jsonLd),
        }}
      />
    </div>
  );
}
