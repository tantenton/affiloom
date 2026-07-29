/**
 * Affiliate disclosure banner.
 *
 * Every page that surfaces affiliate deep-links must render this so visitors
 * understand the commercial relationship before they click. The wording
 * follows what Indonesian consumer-protection guidance and major partner
 * programs (Shopee Affiliate, Tokopedia Affiliate) require: transparent, in
 * the same viewport, and phrased plainly.
 */
export function AffiliateDisclosure({
  variant = "banner",
}: {
  variant?: "banner" | "inline";
}) {
  const base =
    "rounded-md border border-amber-200 bg-amber-50 text-amber-900 text-sm";
  const className =
    variant === "banner" ? `${base} px-4 py-3` : `${base} px-3 py-2`;

  return (
    <aside
      role="note"
      aria-label="Pengungkapan afiliasi"
      className={className}
      data-testid="affiliate-disclosure"
    >
      <strong className="font-semibold">Pengungkapan afiliasi.</strong>{" "}
      Halaman ini memuat tautan afiliasi. Jika kamu melakukan pembelian melalui
      tautan tersebut, Affiloom dapat menerima komisi dari mitra marketplace
      tanpa biaya tambahan untukmu. Data produk berasal dari adaptor demo
      deterministik dan hanya digunakan untuk pengembangan.
    </aside>
  );
}
