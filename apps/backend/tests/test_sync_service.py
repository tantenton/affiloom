"""Tests for the idempotent sync service.

We assemble the same components the admin endpoint uses (adapter, in-memory
indexer, per-test SQLite DB) and verify:

* First run creates the full catalog.
* Second run is a no-op (zero deltas, counts still reported).
* Missing items get deactivated.
* Search index reflects the current active set.
* Failures record a ``failed`` row without leaking half-written data.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Mapping

import pytest
from sqlalchemy import select

from adapters.provider import (
    DeterministicDemoAdapter,
    MarketplaceItem,
    demo_items,
)
from db.models import Merchant, Offer, Product, SyncRun, SyncRunStatus
from db.session import get_sessionmaker
from services.search import InMemoryIndexer
from services.sync import run_sync


def _seeded_adapter(
    items: Mapping[str, MarketplaceItem] | None = None,
) -> DeterministicDemoAdapter:
    seed = items if items is not None else {i.id: i for i in demo_items()}
    return DeterministicDemoAdapter(seed)


@pytest.mark.asyncio
async def test_first_sync_creates_full_catalog(initialized_db: str) -> None:
    adapter = _seeded_adapter()
    indexer = InMemoryIndexer()
    factory = get_sessionmaker()

    async with factory() as session:
        result = await run_sync(session, adapter=adapter, indexer=indexer)

    assert result.status is SyncRunStatus.SUCCESS
    assert result.seen == 10
    assert result.created == 10
    assert result.updated == 0
    assert result.deactivated == 0
    assert result.error is None

    async with factory() as session:
        merchants = (await session.execute(select(Merchant))).scalars().all()
        products = (await session.execute(select(Product))).scalars().all()
        offers = (await session.execute(select(Offer))).scalars().all()

    assert len(merchants) == 1
    assert merchants[0].slug == "demo"
    assert len(products) == 10
    assert {p.external_id for p in products} == {i.id for i in demo_items()}
    assert len(offers) == 10
    assert all(o.currency == "IDR" for o in offers)

    hits = await indexer.search("Tas")
    assert any("Tas" in h["title"] for h in hits)


@pytest.mark.asyncio
async def test_second_sync_is_idempotent(initialized_db: str) -> None:
    adapter = _seeded_adapter()
    indexer = InMemoryIndexer()
    factory = get_sessionmaker()

    async with factory() as session:
        await run_sync(session, adapter=adapter, indexer=indexer)
    async with factory() as session:
        result = await run_sync(session, adapter=adapter, indexer=indexer)

    assert result.status is SyncRunStatus.SUCCESS
    assert result.seen == 10
    assert result.created == 0
    assert result.updated == 0
    assert result.deactivated == 0

    async with factory() as session:
        products = (await session.execute(select(Product))).scalars().all()
        offers = (await session.execute(select(Offer))).scalars().all()
    assert len(products) == 10
    assert len(offers) == 10


@pytest.mark.asyncio
async def test_content_change_counts_as_update(initialized_db: str) -> None:
    original = _seeded_adapter()
    factory = get_sessionmaker()
    async with factory() as session:
        await run_sync(session, adapter=original, indexer=InMemoryIndexer())

    changed_items = list(demo_items())
    changed_items[0] = replace(changed_items[0], title="Tas Jinjing Baru Update")
    changed = _seeded_adapter({i.id: i for i in changed_items})

    async with factory() as session:
        result = await run_sync(session, adapter=changed, indexer=InMemoryIndexer())

    assert result.status is SyncRunStatus.SUCCESS
    assert result.updated == 1
    assert result.created == 0

    async with factory() as session:
        stmt = select(Product).where(Product.external_id == "demo-1")
        product = (await session.execute(stmt)).scalar_one()
    assert product.title == "Tas Jinjing Baru Update"


@pytest.mark.asyncio
async def test_missing_items_are_deactivated(initialized_db: str) -> None:
    factory = get_sessionmaker()
    full = _seeded_adapter()
    async with factory() as session:
        await run_sync(session, adapter=full, indexer=InMemoryIndexer())

    subset = {i.id: i for i in demo_items()[:5]}
    partial = _seeded_adapter(subset)
    async with factory() as session:
        result = await run_sync(session, adapter=partial, indexer=InMemoryIndexer())

    assert result.status is SyncRunStatus.SUCCESS
    assert result.deactivated == 5

    async with factory() as session:
        stmt = select(Product).where(Product.is_active.is_(False))
        deactivated = (await session.execute(stmt)).scalars().all()
    assert {p.external_id for p in deactivated} == {f"demo-{i}" for i in range(6, 11)}


class _FailingAdapter(DeterministicDemoAdapter):
    async def list(self, *, limit=20, offset=0, query=None):  # type: ignore[override]
        raise RuntimeError("adapter boom")


@pytest.mark.asyncio
async def test_failure_marks_run_failed(initialized_db: str) -> None:
    adapter = _FailingAdapter({})
    factory = get_sessionmaker()

    async with factory() as session:
        result = await run_sync(session, adapter=adapter, indexer=InMemoryIndexer())

    assert result.status is SyncRunStatus.FAILED
    assert result.error is not None
    assert "boom" in result.error

    async with factory() as session:
        runs = (await session.execute(select(SyncRun))).scalars().all()
    assert len(runs) == 1
    assert runs[0].status is SyncRunStatus.FAILED
    assert runs[0].finished_at is not None


@pytest.mark.asyncio
async def test_sync_stats_include_indexed_count(initialized_db: str) -> None:
    factory = get_sessionmaker()
    adapter = _seeded_adapter()
    indexer = InMemoryIndexer()

    async with factory() as session:
        result = await run_sync(session, adapter=adapter, indexer=indexer)
    async with factory() as session:
        run = await session.get(SyncRun, result.run_id)
    assert run is not None
    assert run.stats is not None
    assert run.stats["indexed"] == 10
    assert run.stats["adapter"] == "demo"
    assert isinstance(run.finished_at, datetime)
    assert run.started_at <= run.finished_at
