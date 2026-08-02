import Link from "next/link";
import { formatPrice } from "@/lib/format";
import { Product } from "@/lib/types";

export function ProductCard({ product }: { product: Product }) {
  return (
    <div className="card card-hover group flex h-full flex-col overflow-hidden">
      <Link href={`/produk/${product.id}`} className="block aspect-[4/3] w-full overflow-hidden bg-slate-100">
        {product.image_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={product.image_url}
            alt={product.title}
            loading="lazy"
            className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-slate-400 font-medium">
            No image
          </div>
        )}
      </Link>
      <div className="flex flex-1 flex-col p-5">
        <div className="flex items-start justify-between gap-4">
          <div className="flex flex-col gap-1.5">
            {product.category ? (
              <span className="text-[10px] font-bold uppercase tracking-widest text-indigo-600">
                {product.category}
              </span>
            ) : null}
            <Link href={`/produk/${product.id}`}>
              <h3 className="line-clamp-2 text-sm font-semibold leading-snug text-slate-900 group-hover:text-indigo-600 transition-colors">
                {product.title}
              </h3>
            </Link>
          </div>
        </div>
        <div className="mt-auto pt-4 flex items-center justify-between">
          <p className="text-base font-bold text-slate-900 tracking-tight">
            {formatPrice(product.price, product.currency)}
          </p>
          <Link 
            href={`/produk/${product.id}`}
            className="text-[11px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-slate-900 transition-colors"
          >
            Details →
          </Link>
        </div>
      </div>
    </div>
  );
}
