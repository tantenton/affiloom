"""Marketplace provider adapter contract + deterministic demo implementation.

Compliance: concrete adapters MUST call official partner APIs only.
No scraping, no browser automation, no reverse-engineered private endpoints.
The demo adapter serves fixed in-memory data and is safe for local dev/tests.
"""

from __future__ import annotations

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
    category: str | None = None
    description: str | None = None
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
    async def search(
        self, query: str, *, limit: int = 20
    ) -> Iterable[MarketplaceItem]: ...

    @abstractmethod
    async def detail(self, item_id: str) -> MarketplaceItem | None: ...


class DeterministicDemoAdapter(MarketplaceProviderAdapter):
    """Deterministic sandbox adapter for local development and tests."""

    @property
    def name(self) -> str:
        return "demo"

    def __init__(self, seed: Mapping[str, MarketplaceItem]) -> None:
        # Preserve insertion order so listings are stable and deterministic.
        self._items: List[MarketplaceItem] = list(seed.values())

    async def health(self) -> dict:
        return {"provider": self.name, "ready": True}

    async def list(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        query: str | None = None,
        category: str | None = None,
    ) -> tuple[List[MarketplaceItem], int]:
        """Return a page after optional text and exact category filters."""
        pool = list(self._items)
        if category:
            wanted_category = category.strip().casefold()
            pool = [
                item
                for item in pool
                if item.category and item.category.casefold() == wanted_category
            ]
        if query:
            q = query.lower().strip()
            pool = [
                item
                for item in pool
                if q in item.title.lower()
                or (item.category is not None and q in item.category.lower())
            ]
        total = len(pool)
        return pool[offset : offset + limit], total

    async def search(self, query: str, *, limit: int = 20) -> Iterable[MarketplaceItem]:
        page, _ = await self.list(limit=limit, query=query)
        return page

    async def detail(self, item_id: str) -> MarketplaceItem | None:
        for item in self._items:
            if item.id == item_id:
                return item
        return None


# Deterministic fixed timestamp so responses are byte-identical across runs and
# JSON-LD schema rendering is stable for tests. Kept in the past on purpose.
_DEMO_TIMESTAMP = datetime(2026, 7, 1, 0, 0, 0, tzinfo=timezone.utc)


def demo_items() -> List[MarketplaceItem]:
    """Deterministic fixed seed for tests and local demos."""
    return [
        MarketplaceItem(
            id="demo-1",
            source="demo",
            title="Tas Jinjing Kanvas Eco",
            url="https://example.com/demo-1",
            image_url="https://picsum.photos/seed/demo-1/600/600",
            price=125000.0,
            currency="IDR",
            commission_rate=0.08,
            category="Fashion",
            description=(
                "Tas jinjing kanvas ramah lingkungan, kapasitas 12L, cocok untuk "
                "belanja harian dan aktivitas kampus."
            ),
            last_seen_at=_DEMO_TIMESTAMP,
        ),
        MarketplaceItem(
            id="demo-2",
            source="demo",
            title="Botol Minum Insulasi 1L",
            url="https://example.com/demo-2",
            image_url="https://picsum.photos/seed/demo-2/600/600",
            price=89000.0,
            currency="IDR",
            commission_rate=0.06,
            category="Peralatan",
            description=(
                "Botol minum stainless dinding ganda, mempertahankan suhu 12 jam "
                "panas dan 24 jam dingin."
            ),
            last_seen_at=_DEMO_TIMESTAMP,
        ),
        MarketplaceItem(
            id="demo-3",
            source="demo",
            title="Kaos Katun Combed 30s",
            url="https://example.com/demo-3",
            image_url="https://picsum.photos/seed/demo-3/600/600",
            price=79000.0,
            currency="IDR",
            commission_rate=0.10,
            category="Fashion",
            description=(
                "Kaos oversize katun combed 30s, jahitan rantai, tersedia enam "
                "warna dasar netral."
            ),
            last_seen_at=_DEMO_TIMESTAMP,
        ),
        MarketplaceItem(
            id="demo-4",
            source="demo",
            title="Kopi Arabika Gayo 200g",
            url="https://example.com/demo-4",
            image_url="https://picsum.photos/seed/demo-4/600/600",
            price=95000.0,
            currency="IDR",
            commission_rate=0.05,
            category="Kuliner",
            description=(
                "Biji kopi arabika Gayo single origin, roast medium, dikemas dalam "
                "kantong valve satu arah."
            ),
            last_seen_at=_DEMO_TIMESTAMP,
        ),
        MarketplaceItem(
            id="demo-5",
            source="demo",
            title="Lampu Meja LED Sentuh",
            url="https://example.com/demo-5",
            image_url="https://picsum.photos/seed/demo-5/600/600",
            price=189000.0,
            currency="IDR",
            commission_rate=0.07,
            category="Rumah Tangga",
            description=(
                "Lampu meja LED dengan kontrol sentuh tiga tingkat kecerahan, "
                "isi ulang USB-C, cocok untuk meja kerja."
            ),
            last_seen_at=_DEMO_TIMESTAMP,
        ),
        MarketplaceItem(
            id="demo-6",
            source="demo",
            title="Buku Catatan A5 Dotted",
            url="https://example.com/demo-6",
            image_url="https://picsum.photos/seed/demo-6/600/600",
            price=65000.0,
            currency="IDR",
            commission_rate=0.09,
            category="Alat Tulis",
            description=(
                "Buku catatan A5 sampul kain linen, 160 halaman kertas 100 gsm "
                "dotted, jahit benang."
            ),
            last_seen_at=_DEMO_TIMESTAMP,
        ),
        MarketplaceItem(
            id="demo-7",
            source="demo",
            title="Headphone Bluetooth Over-Ear",
            url="https://example.com/demo-7",
            image_url="https://picsum.photos/seed/demo-7/600/600",
            price=499000.0,
            currency="IDR",
            commission_rate=0.04,
            category="Elektronik",
            description=(
                "Headphone bluetooth over-ear dengan peredam bising pasif dan "
                "daya tahan baterai 30 jam."
            ),
            last_seen_at=_DEMO_TIMESTAMP,
        ),
        MarketplaceItem(
            id="demo-8",
            source="demo",
            title="Sepatu Lari Ringan Trail",
            url="https://example.com/demo-8",
            image_url="https://picsum.photos/seed/demo-8/600/600",
            price=649000.0,
            currency="IDR",
            commission_rate=0.06,
            category="Olahraga",
            description=(
                "Sepatu lari trail dengan sol karet agresif, upper mesh breathable, "
                "bobot 260 gram."
            ),
            last_seen_at=_DEMO_TIMESTAMP,
        ),
        MarketplaceItem(
            id="demo-9",
            source="demo",
            title="Serum Vitamin C 20ml",
            url="https://example.com/demo-9",
            image_url="https://picsum.photos/seed/demo-9/600/600",
            price=145000.0,
            currency="IDR",
            commission_rate=0.12,
            category="Kecantikan",
            description=(
                "Serum wajah dengan 10% asam askorbat stabil, tekstur ringan, "
                "cocok untuk kulit sensitif."
            ),
            last_seen_at=_DEMO_TIMESTAMP,
        ),
        MarketplaceItem(
            id="demo-10",
            source="demo",
            title="Tikar Yoga Anti Slip 6mm",
            url="https://example.com/demo-10",
            image_url="https://picsum.photos/seed/demo-10/600/600",
            price=219000.0,
            currency="IDR",
            commission_rate=0.08,
            category="Olahraga",
            description=(
                "Matras yoga TPE bebas PVC, ketebalan 6mm, permukaan bertekstur "
                "dua sisi anti selip."
            ),
            last_seen_at=_DEMO_TIMESTAMP,
        ),
    ]


__all__ = [
    "MarketplaceItem",
    "MarketplaceProviderAdapter",
    "DeterministicDemoAdapter",
    "demo_items",
]
