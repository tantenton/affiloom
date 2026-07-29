from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable, List, Mapping


@dataclass(frozen=True, slots=True)
class MarketplaceItem:
    id: str
    source: str
    title: str
    url: str
    image_url: str | None = None
    price: float | None = None
    currency: str | None = None
    commission_rate: float | None = None
    last_seen_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class MarketplaceProviderAdapter(ABC):
    """Contract for compliant affiliate provider integrations.

    Concrete adapters must be deterministic and must not perform automated
    browsing or scraping beyond what a partner API explicitly allows.
    """

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def health(self) -> dict:
        """Return provider health / connectivity status."""
        ...

    @abstractmethod
    async def search(self, query: str, *, limit: int = 20) -> Iterable[MarketplaceItem]:
        ...

    @abstractmethod
    async def detail(self, item_id: str) -> MarketplaceItem | None:
        ...


class DeterministicDemoAdapter(MarketplaceProviderAdapter):
    """Deterministic sandbox adapter for local development and tests."""

    @property
    def name(self) -> str:
        return "demo"

    def __init__(self, seed: Mapping[str, MarketplaceItem]) -> None:
        self._items: List[MarketplaceItem] = list(seed.values())

    async def health(self) -> dict:
        return {"provider": self.name, "ready": True}

    async def search(self, query: str, *, limit: int = 20) -> Iterable[MarketplaceItem]:
        q = query.lower()
        return [item for item in self._items if q in item.title.lower()][:limit]

    async def detail(self, item_id: str) -> MarketplaceItem | None:
        for item in self._items:
            if item.id == item_id:
                return item
        return None


def demo_items() -> List[MarketplaceItem]:
    """Deterministic fixed seed for tests and local demos."""
    now = datetime.now(timezone.utc)
    return [
        MarketplaceItem(
            id="demo-1",
            source="demo",
            title="Tas Jinjing Kanvas Eco",
            url="https://example.com/demo-1",
            price=125000.0,
            currency="IDR",
            commission_rate=0.08,
            last_seen_at=now,
        ),
        MarketplaceItem(
            id="demo-2",
            source="demo",
            title="Botol Minum Isulang 1L",
            url="https://example.com/demo-2",
            price=89000.0,
            currency="IDR",
            commission_rate=0.06,
            last_seen_at=now,
        ),
    ]


__all__ = [
    "MarketplaceItem",
    "MarketplaceProviderAdapter",
    "DeterministicDemoAdapter",
    "demo_items",
]

