export interface Product {
  id: string;
  name: string;
  price: number;
  image: string;
  category: string;
  description: string;
  rating: number;
  specs?: Record<string, string | number>;
}

export interface CompareResponse {
  products: Product[];
  differences: {
    field: string;
    values: [string | null, string | null];
  }[];
}
