import type { Metadata } from "next";
import { PageviewTracker } from "@/components/Tracking";
import "./globals.css";

const siteUrl =
  process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Affiloom",
    template: "%s — Affiloom",
  },
  description:
    "Platform afiliasi mindful untuk marketplace Indonesia. Transparan, beretika, dan siap menskalakan.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="id">
      <body>
        <PageviewTracker />
        {children}
      </body>
    </html>
  );
}
