from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, List, Mapping


@dataclass(frozen=True)
class MarketplaceItem:
    id: str
    source: str
    title: str
    url: str
    image_url: str | None
    price: float | None
    currency: str | None
    commission_rate: float | None
    last_seen_at: datetime


class MarketplaceProviderAdapter(ABC):
    """Contract for read-only provider integrations.

    Concrete adapters must be deterministic and must not perform automated
    browsing or scraping beyond what a partner API allows.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    async def search(self, query: str, *, limit: int = 20) -> Iterable[MarketplaceItem]:
        ...

    @abstractmethod
    async def detail(self, item_id: str) -> MarketplaceItem | None:
        ...


class DeterministicDemoAdapter(MarketplaceProviderAdapter):
    @property
    def name(self) -> str:
        return "demo"

    def __init__(self, seed: Mapping[str, MarketplaceItem]) -> None:
        self._items = list(seed)

    async def search(self, query: str, *, limit: int = 20) -> Iterable[MarketplaceItem]:
        q = query.lower()
        return [item for item in self._items if q in item.title.lower()][:limit]

    async def detail(self, item_id: str) -> MarketplaceItem | None:
        for item in self._items:
            if item.id == item_id:
                return item
        return None


def demo_items() -> List[MarketplaceItem]:
    now = datetime.utcnow()
    return [
        MarketplaceItem(
            id="demo-1",
            source="demo",
            title="Tas Jinjing Kanvas Eco",
            url="https://example.com/demo-1",
            image_url=None,
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
            image_url=None,
            price=89000.0,
            currency="IDR",
            commission_rate=0.06,
            last_seen_at=now,
        ),
    ]
