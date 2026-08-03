import { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";

import { AffiliateDisclosure } from "@/components/AffiliateDisclosure";
import { SiteFooter } from "@/components/SiteFooter";
import { SiteHeader } from "@/components/SiteHeader";
import { CtaTracker } from "@/components/Tracking";
import { getProduct, listProducts } from "@/lib/api";
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
      <div className="min-h-screen bg-slate-50 pb-20 sm:pb-0">
        <SiteHeader />

        <main className="mx-auto max-w-5xl px-4 py-10">
          <nav aria-label="Breadcrumb" className="mb-6 text-sm text-slate-500">
            <Link href="/produk" className="hover:text-slate-900">
              ← Kembali ke katalog
            </Link>
          </nav>

          <div className="grid gap-8 md:grid-cols-2">
            {/* Image */}
            <div className="overflow-hidden rounded-2xl bg-gradient-to-br from-slate-100 to-slate-200 shadow-lg ring-1 ring-slate-200">
              {product.image_url ? (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  src={product.image_url}
                  alt={product.title}
                  className="aspect-square w-full object-cover"
                  fetchPriority="high"
                  decoding="async"
                />
              ) : (
                <div className="flex aspect-square items-center justify-center">
                  <svg
                    className="h-16 w-16 text-slate-300"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    width="64"
                    height="64"
                    style={{ width: 64, height: 64, flexShrink: 0 }}
                    aria-hidden="true"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              )}
            </div>

            {/* Info */}
            <div className="flex flex-col gap-4">
              {product.category && (
                <span className="inline-block w-fit rounded-full bg-indigo-100 px-3 py-1 text-xs font-bold uppercase tracking-widest text-indigo-700">
                  {product.category}
                </span>
              )}
              <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
                {product.title}
              </h1>
              <p className="text-3xl font-bold text-slate-900">
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
                    <FreshnessBadge date={product.last_seen_at} />
                  </dd>
                </div>
              </dl>

              {product.description ? (
                <p className="mt-4 leading-relaxed text-slate-700">
                  {product.description}
                </p>
              ) : null}

              <div className="mt-6 flex flex-wrap gap-3">
                <CtaTracker
                  url={product.url}
                  productId={product.id}
                  className="btn-primary"
                  data-testid="affiliate-cta"
                >
                  Beli via mitra afiliasi
                </CtaTracker>
                <Link
                  href={`/compare?ids=${product.id}`}
                  className="btn-secondary"
                >
                  Bandingkan
                </Link>
              </div>

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
        <SiteFooter />
      </div>
    );
  }


  function FreshnessBadge({ date }: { date: string }) {
    const parsed = new Date(date);
    const now = new Date();
    const diffDays = Math.floor(
      (now.getTime() - parsed.getTime()) / (1000 * 60 * 60 * 24)
    );
    let label: string;
    let color: string;
    if (diffDays <= 1) {
      label = "Hari ini";
      color = "bg-green-100 text-green-800";
    } else if (diffDays <= 7) {
      label = `${diffDays} hari lalu`;
      color = "bg-green-100 text-green-800";
    } else if (diffDays <= 30) {
      label = `${diffDays} hari lalu`;
      color = "bg-yellow-100 text-yellow-800";
    } else {
      label = `${diffDays} hari lalu`;
      color = "bg-red-100 text-red-800";
    }
    return (
      <span
        className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${color}`}
        title={`Data diperbarui: ${parsed.toLocaleDateString("id-ID")}`}
      >
        {label}
      </span>
    );
  }
