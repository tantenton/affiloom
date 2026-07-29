"""Test smoke adapter."""

import pytest

from adapters.provider import (
    DeterministicDemoAdapter,
    MarketplaceProviderAdapter,
    demo_items,
)


def test_interface_impl() -> None:
    """Verify DeterministicDemoAdapter implements the abstract interface."""
    assert issubclass(DeterministicDemoAdapter, MarketplaceProviderAdapter)
    assert hasattr(DeterministicDemoAdapter, "name")
    assert hasattr(DeterministicDemoAdapter, "health")
    assert hasattr(DeterministicDemoAdapter, "search")
    assert hasattr(DeterministicDemoAdapter, "detail")


def test_demo_items_count() -> None:
    """Smoke: demo_items returns the deterministic catalog of 10 items."""
    items = demo_items()
    assert len(items) == 10
    ids = [item.id for item in items]
    assert ids == sorted(ids, key=lambda s: int(s.split("-")[1]))
    assert len(set(ids)) == len(ids)


@pytest.mark.anyio
async def test_demo_adapter_search_basic() -> None:
    """Smoke: search returns matching items deterministically."""
    seed = {item.id: item for item in demo_items()}
    adapter = DeterministicDemoAdapter(seed)

    results = await adapter.search("Tas Jinjing", limit=10)
    results_list = list(results)
    assert len(results_list) >= 1
    for item in results_list:
        assert "Tas" in item.title or "Jinjing" in item.title

    item = await adapter.detail("demo-1")
    assert item is not None
    assert item.id == "demo-1"
    assert item.price == 125000.0
    assert item.currency == "IDR"

    unknown = await adapter.detail("nonexistent")
    assert unknown is None

    results_upper = await adapter.search("tas jinjing", limit=10)
    assert len(list(results_upper)) > 0

    limited = await adapter.search("Tas", limit=1)
    assert len(list(limited)) == 1

    assert adapter.name == "demo"


@pytest.mark.anyio
async def test_demo_adapter_health() -> None:
    """Smoke: health endpoint reports ready."""
    seed = {item.id: item for item in demo_items()}
    adapter = DeterministicDemoAdapter(seed)
    status = await adapter.health()
    assert status["ready"] is True
    assert status["provider"] == "demo"


@pytest.mark.anyio
async def test_demo_adapter_determinism() -> None:
    """Determinism: same seed + same query == same results (order included)."""
    seed1 = {item.id: item for item in demo_items()}
    seed2 = {item.id: item for item in demo_items()}
    adapter1 = DeterministicDemoAdapter(seed1)
    adapter2 = DeterministicDemoAdapter(seed2)

    res1 = sorted(await adapter1.search("tas"), key=lambda i: i.id)
    res2 = sorted(await adapter2.search("tas"), key=lambda i: i.id)
    assert len(res1) == len(res2)
    for a, b in zip(res1, res2):
        assert a.id == b.id
        assert a.title == b.title
        assert a.price == b.price
