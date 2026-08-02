"""Meilisearch indexing abstraction with deterministic in-memory fallback.

Selection priority
------------------
1. If ``settings.MEILI_ENABLED`` is ``True`` **and** Meilisearch is reachable,
   use ``MeilisearchIndexer`` over HTTP.
2. Otherwise fall back to ``InMemoryIndexer`` — a thin dict that supports the
   same interface and makes tests/CI hermetic without a running Meilisearch.

The ``get_indexer()`` factory returns the live or fallback indexer based on
the env setting. Code that needs an indexer should call it and not hard-wire
either implementation.

Protocol
--------
Both implementations share the ``SearchIndexer`` protocol so they're
type-checkable and swappable without base-class overhead.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Protocol, runtime_checkable

import httpx

from config import settings

log = logging.getLogger(__name__)


@runtime_checkable
class SearchIndexer(Protocol):
    async def upsert(self, documents: list[dict]) -> None: ...
    async def delete(self, ids: list[str]) -> None: ...
    async def search(self, query: str, *, limit: int = 20) -> list[dict]: ...
    async def health(self) -> dict: ...


class InMemoryIndexer:
    """Deterministic in-memory search backend (dev / test / CI)."""

    def __init__(self) -> None:
        self._docs: dict[str, dict] = {}

    async def upsert(self, documents: list[dict]) -> None:
        for doc in documents:
            self._docs[str(doc["id"])] = doc

    async def delete(self, ids: list[str]) -> None:
        for i in ids:
            self._docs.pop(str(i), None)

    async def search(self, query: str, *, limit: int = 20) -> list[dict]:
        q = query.lower()
        hits = [
            d
            for d in self._docs.values()
            if q in d.get("title", "").lower()
            or q in d.get("description", "").lower()
            or q in d.get("category", "").lower()
        ]
        return hits[:limit]

    async def health(self) -> dict:
        return {"backend": "memory", "docs": len(self._docs)}


class MeilisearchIndexer:
    """Thin async wrapper around the Meilisearch REST API.

    All network calls are best-effort: failures are logged and raised so the
    caller can decide whether to surface them or swallow.
    """

    def __init__(
        self,
        host: str,
        master_key: str,
        index: str,
    ) -> None:
        self._base = host.rstrip("/")
        self._headers = {"Authorization": f"Bearer {master_key}"}
        self._index = index
        self._client = httpx.AsyncClient(headers=self._headers, timeout=10)

    async def _ensure_index(self) -> None:
        """Create the index if it doesn't exist. Idempotent.

        Explicitly handles 409 (already exists) as a no-op, while letting
        other errors propagate so unreachable hosts are visible.
        """
        try:
            resp = await self._client.post(
                f"{self._base}/indexes",
                json={"uid": self._index, "primaryKey": "id"},
            )
            # 201 = created, 409 = already exists (Meilisearch behavior); either is OK.
            if resp.status_code == 409:
                pass  # index already exists — safe no-op
            elif resp.status_code not in (201, 204):
                resp.raise_for_status()
        except Exception:
            # Only suppress connection/reachability errors silently; anything else
            # should be visible for debugging (per design doc / KNOWN_ISSUES).
            raise

    async def upsert(self, documents: list[dict]) -> None:
        await self._ensure_index()
        resp = await self._client.put(
            f"{self._base}/indexes/{self._index}/documents", json=documents
        )
        resp.raise_for_status()

    async def delete(self, ids: list[str]) -> None:
        if not ids:
            return
        # Use ``request`` because httpx's ``delete`` helper doesn't accept a
        # JSON body and Meilisearch requires the id list in the payload.
        resp = await self._client.request(
            "POST",
            f"{self._base}/indexes/{self._index}/documents/delete-batch",
            json=ids,
        )
        resp.raise_for_status()

    async def search(self, query: str, *, limit: int = 20) -> list[dict]:
        resp = await self._client.post(
            f"{self._base}/indexes/{self._index}/search",
            json={"q": query, "limit": limit},
        )
        resp.raise_for_status()
        return resp.json().get("hits", [])

    async def health(self) -> dict:
        resp = await self._client.get(f"{self._base}/health")
        return {"backend": "meilisearch", "http_status": resp.status_code}


async def probe_meilisearch(host: str, master_key: str) -> bool:
    """Return True if Meilisearch answers to a health ping within 2 s."""
    headers = {"Authorization": f"Bearer {master_key}"}
    try:
        async with httpx.AsyncClient(headers=headers, timeout=2) as c:
            r = await c.get(f"{host.rstrip('/')}/health")
            return r.status_code == 200
    except Exception:  # noqa: BLE001
        return False


_indexer: SearchIndexer | None = None
_indexer_lock = asyncio.Lock()


async def get_indexer() -> SearchIndexer:
    """Return the process-level indexer (cached after first call).

    * ``settings.MEILI_ENABLED=True`` and reachable Meilisearch → live indexer.
    * Otherwise → InMemoryIndexer.
    """
    global _indexer  # noqa: PLW0603
    async with _indexer_lock:
        if _indexer is None:
            if settings.MEILI_ENABLED and await probe_meilisearch(
                settings.MEILI_HOST, settings.MEILI_MASTER_KEY
            ):
                log.info("search: using Meilisearch at %s", settings.MEILI_HOST)
                _indexer = MeilisearchIndexer(
                    settings.MEILI_HOST,
                    settings.MEILI_MASTER_KEY,
                    settings.MEILI_INDEX,
                )
            else:
                log.info(
                    "search: using InMemoryIndexer (Meilisearch disabled/unreachable)"
                )
                _indexer = InMemoryIndexer()
    return _indexer


def reset_indexer() -> None:
    """Reset the cached indexer (test helper)."""
    global _indexer  # noqa: PLW0603
    _indexer = None


__all__ = [
    "InMemoryIndexer",
    "MeilisearchIndexer",
    "SearchIndexer",
    "get_indexer",
    "probe_meilisearch",
    "reset_indexer",
]
