"""Search indexer contract + fallback selection tests."""

from __future__ import annotations

import pytest

from config import settings
from services.search import (
    InMemoryIndexer,
    SearchIndexer,
    get_indexer,
    reset_indexer,
)


@pytest.mark.asyncio
async def test_in_memory_indexer_upsert_and_search() -> None:
    idx = InMemoryIndexer()
    await idx.upsert(
        [
            {"id": "1", "title": "Tas Jinjing Eco", "description": "", "category": "Fashion"},
            {"id": "2", "title": "Botol Minum", "description": "", "category": "Peralatan"},
        ]
    )

    hits = await idx.search("tas")
    assert [h["id"] for h in hits] == ["1"]
    hits = await idx.search("PERALATAN")
    assert [h["id"] for h in hits] == ["2"]

    await idx.delete(["1"])
    hits = await idx.search("tas")
    assert hits == []

    health = await idx.health()
    assert health["backend"] == "memory"


@pytest.mark.asyncio
async def test_get_indexer_falls_back_when_meilisearch_disabled(monkeypatch) -> None:
    monkeypatch.setattr(settings, "MEILI_ENABLED", False)
    reset_indexer()
    idx = await get_indexer()
    assert isinstance(idx, InMemoryIndexer)
    assert isinstance(idx, SearchIndexer)
    reset_indexer()


@pytest.mark.asyncio
async def test_get_indexer_falls_back_when_meilisearch_unreachable(monkeypatch) -> None:
    # Point at an unroutable host so probe_meilisearch returns False fast.
    monkeypatch.setattr(settings, "MEILI_ENABLED", True)
    monkeypatch.setattr(settings, "MEILI_HOST", "http://127.0.0.1:1")
    monkeypatch.setattr(settings, "MEILI_MASTER_KEY", "test")
    reset_indexer()
    idx = await get_indexer()
    assert isinstance(idx, InMemoryIndexer)
    reset_indexer()
