export type Product = {
  id: string;
  source: string;
  title: string;
  url: string;
  image_url: string | null;
  price: number | null;
  currency: string | null;
  commission_rate: number | null;
  category: string | null;
  description: string | null;
  last_seen_at: string;
};

export type ProductListResponse = {
  items: Product[];
  total: number;
  limit: number;
  offset: number;
  query: string | null;
};

export class NotFoundError extends Error {
  constructor(message = "Not found") {
    super(message);
    this.name = "NotFoundError";
  }
}
