"""Product API response models.

Keep this thin and DTO-shaped: it is the public contract consumed by the
frontend and any future partners. Domain objects (``MarketplaceItem``) stay
in ``adapters.provider`` and are never leaked directly.
"""

from __future__ import annotations

from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from adapters.provider import MarketplaceItem


class ProductOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    source: str
    title: str
    url: HttpUrl
    image_url: HttpUrl | None = None
    price: float | None = None
    currency: str | None = None
    commission_rate: float | None = None
    category: str | None = None
    description: str | None = None
    last_seen_at: datetime

    @classmethod
    def from_item(cls, item: MarketplaceItem) -> "ProductOut":
        return cls(
            id=item.id,
            source=item.source,
            title=item.title,
            url=item.url,  # type: ignore[arg-type]
            image_url=item.image_url,  # type: ignore[arg-type]
            price=item.price,
            currency=item.currency,
            commission_rate=item.commission_rate,
            category=item.category,
            description=item.description,
            last_seen_at=item.last_seen_at,
        )


class ProductListResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: List[ProductOut]
    total: int = Field(ge=0)
    limit: int = Field(ge=1, le=100)
    offset: int = Field(ge=0)
    query: str | None = None


class ProductCompareResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    products: List[ProductOut]
    missing: List[str]


__all__ = ["ProductOut", "ProductListResponse", "ProductCompareResponse"]
