import type { Product } from "@/lib/types";

export const mockProducts: Product[] = [
  {
    id: "p1",
    name: "Headphone Aurora X1",
    price: 1299000,
    image: "",
    category: "Audio",
    description:
      "Headphone wireless dengan noise cancelling aktif dan baterai 40 jam.",
    rating: 4.6,
    specs: {
      Bluetooth: "5.3",
      "Baterai": "40 jam",
      "Noise Cancelling": "Ya",
      "Berat": "250 g",
      "Garansi": "1 tahun",
    },
  },
  {
    id: "p2",
    name: "Headphone Nimbus Pro",
    price: 1799000,
    image: "",
    category: "Audio",
    description:
      "Suara audiophile-grade dengan driver 50mm dan dukungan Hi-Res Audio.",
    rating: 4.8,
    specs: {
      Bluetooth: "5.2",
      "Baterai": "60 jam",
      "Noise Cancelling": "Ya",
      "Berat": "280 g",
      "Garansi": "2 tahun",
    },
  },
  {
    id: "p3",
    name: "Earbuds Lumen Mini",
    price: 549000,
    image: "",
    category: "Audio",
    description: "Earbubs ringan dengan charging case dan IPX5 tahan keringat.",
    rating: 4.3,
    specs: {
      Bluetooth: "5.3",
      "Baterai": "24 jam",
      "Noise Cancelling": "Tidak",
      "Berat": "45 g",
      "Garansi": "6 bulan",
    },
  },
  {
    id: "p4",
    name: "Speaker Vortex 360",
    price: 899000,
    image: "",
    category: "Audio",
    description: "Speaker portabel 360 derajat, bass boost, dan 20 jam pemutaran.",
    rating: 4.5,
    specs: {
      Bluetooth: "5.1",
      "Baterai": "20 jam",
      "Noise Cancelling": "Tidak",
      "Berat": "550 g",
      "Garansi": "1 tahun",
    },
  },
];
