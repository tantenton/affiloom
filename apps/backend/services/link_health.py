"""Link health and merchant fallback utilities (M5-003).

Performs shallow link validity checks for outbound affiliate URLs.
"""

from __future__ import annotations

import asyncio
from urllib.parse import urlparse

import httpx

DEFAULT_TIMEOUT_SECONDS = 5.0


def validate_url_format(url: str) -> tuple[bool, str | None]:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False, "Only http(s) URLs allowed"
    if not parsed.netloc:
        return False, "Missing host"
    return True, None


async def check_link_health(
    url: str,
    client: httpx.AsyncClient | None = None,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict:
    """Shallow health probe (HEAD then GET fallback).

    Returns a dict with `url`, `ok`, `status_code`, `error`.
    """
    valid, error = validate_url_format(url)
    if not valid:
        return {"url": url, "ok": False, "status_code": None, "error": error}

    own_client = client is None
    client = client or httpx.AsyncClient(timeout=timeout)
    try:
        for method in ("HEAD", "GET"):
            try:
                response = await client.request(method, url, follow_redirects=True)
                if response.status_code < 500:
                    return {
                        "url": url,
                        "ok": response.status_code < 400,
                        "status_code": response.status_code,
                        "error": (
                            None
                            if response.status_code < 400
                            else f"HTTP {response.status_code}"
                        ),
                    }
            except httpx.RequestError as exc:
                if method == "GET":
                    return {
                        "url": url,
                        "ok": False,
                        "status_code": None,
                        "error": str(exc),
                    }
        return {"url": url, "ok": False, "status_code": None, "error": "Unreachable"}
    finally:
        if own_client:
            await client.aclose()


async def batch_check_links(urls: list[str], concurrency: int = 5) -> list[dict]:
    sem = asyncio.Semaphore(concurrency)

    async def _run(url: str) -> dict:
        async with sem:
            return await check_link_health(url)

    return await asyncio.gather(*(_run(u) for u in urls))


__all__ = ["check_link_health", "batch_check_links", "validate_url_format"]
