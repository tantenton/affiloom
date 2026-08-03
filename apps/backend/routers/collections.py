"""Public collections endpoints (M7).

Curated product collections — list, detail with products.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Collection, CollectionProduct
from db.session import get_session

router = APIRouter(prefix="/api/collections", tags=["collections"])


class CollectionSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    slug: str
    title: str
    description: str | None
    product_count: int


class CollectionProductItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    title: str
    image_url: str | None
    price: float | None
    currency: str | None
    category: str | None


class CollectionDetail(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    slug: str
    title: str
    description: str | None
    products: list[CollectionProductItem]


@router.get("", response_model=list[CollectionSummary])
async def list_collections(
    session: AsyncSession = Depends(get_session),
) -> list[CollectionSummary]:
    rows = (
        await session.execute(
            select(Collection)
            .where(Collection.is_active.is_(True))
            .order_by(Collection.title)
        )
    ).scalars().all()
    result = []
    for c in rows:
        count = (
            await session.execute(
                select(CollectionProduct)
                .where(CollectionProduct.collection_id == c.id)
            )
        ).scalars().all()
        result.append(
            CollectionSummary(
                id=c.id,
                slug=c.slug,
                title=c.title,
                description=c.description,
                product_count=len(count),
            )
        )
    return result


@router.get("/{slug}", response_model=CollectionDetail)
async def get_collection(
    slug: str,
    session: AsyncSession = Depends(get_session),
) -> CollectionDetail:
    col = (
        await session.execute(
            select(Collection)
            .where(Collection.slug == slug, Collection.is_active.is_(True))
            .options(selectinload(Collection.products).selectinload(CollectionProduct.product))
        )
    ).scalar_one_or_none()
    if not col:
        raise HTTPException(status_code=404, detail="Collection not found")
    items = sorted(col.products, key=lambda cp: cp.position)
    return CollectionDetail(
        id=col.id,
        slug=col.slug,
        title=col.title,
        description=col.description,
        products=[
            CollectionProductItem(
                id=cp.product.id,
                title=cp.product.title,
                image_url=cp.product.image_url,
                price=None,
                currency=None,
                category=cp.product.category,
            )
            for cp in items
            if cp.product
        ],
    )
