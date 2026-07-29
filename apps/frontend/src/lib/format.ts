/**
 * Format a price as Indonesian rupiah. Falls back to a plain number when the
 * currency is unknown so we never guess.
 */
export function formatPrice(
  price: number | null,
  currency: string | null,
): string {
  if (price == null) return "Harga tidak tersedia";
  if (currency === "IDR") {
    return new Intl.NumberFormat("id-ID", {
      style: "currency",
      currency: "IDR",
      maximumFractionDigits: 0,
    }).format(price);
  }
  if (currency) {
    return `${currency} ${price.toLocaleString("id-ID")}`;
  }
  return price.toLocaleString("id-ID");
}

export function formatCommission(rate: number | null): string | null {
  if (rate == null) return null;
  return `${(rate * 100).toFixed(1)}%`;
}
