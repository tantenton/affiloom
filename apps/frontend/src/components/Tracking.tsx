"use client";

import { useEffect } from "react";

export function PageviewTracker() {
  useEffect(() => {
    if (typeof window === "undefined") return;
    const path = window.location.pathname;
    fetch(`${process.env.NEXT_PUBLIC_API_URL || "/api/track"}/pageview`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path, referrer: document.referrer }),
      keepalive: true,
    }).catch(() => {
      // analytics best-effort — never crash
    });
  }, []);
  return null;
}

export function CtaTracker({
  productId,
  articleId,
  url,
  children,
  className,
  "data-testid": testId,
}: {
  productId?: string;
  articleId?: string;
  url: string;
  children: React.ReactNode;
  className?: string;
  "data-testid"?: string;
}) {
  const handleClick = () => {
    if (typeof window === "undefined") return;
    fetch(
      `${process.env.NEXT_PUBLIC_API_URL || "/api/track"}/click`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ product_id: productId ?? null, article_id: articleId ?? null, url }),
        keepalive: true,
      }
    ).catch(() => {});
  };
  return (
    <a
      href={url}
      onClick={handleClick}
      target="_blank"
      rel="sponsored nofollow noopener noreferrer"
      className={className}
      data-testid={testId}
    >
      {children}
    </a>
  );
}
