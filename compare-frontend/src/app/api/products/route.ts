import { NextResponse } from "next/server";
import { mockProducts } from "@/lib/mock";

export async function GET() {
  return NextResponse.json(mockProducts);
}
