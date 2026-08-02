"""Product catalog endpoints.

Read-only vertical slice backed by the deterministic demo adapter. Every
response is stable across runs so the frontend can be developed and tested
without live partner credentials.
"""

from __future__ import annotations

import re

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from adapters.provider import DeterministicDemoAdapter
from dependencies import get_catalog_adapter
from schemas.product import ProductListResponse, ProductOut

router = APIRouter(prefix="/api/products", tags=["products"])

# Adapter IDs must be URL-safe and length-bounded. This mirrors what a real
# affiliate provider would emit and keeps validation cheap without hitting the
# adapter for obviously invalid input.
_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,127}$")


@router.get("", response_model=ProductListResponse)
async def list_products(
    q: str | None = Query(
        default=None,
        max_length=100,
        description="Case-insensitive substring filter across title and category.",
    ),
    category: str | None = Query(
        default=None,
        max_length=64,
        description="Exact category filter (case-insensitive).",
    ),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    adapter: DeterministicDemoAdapter = Depends(get_catalog_adapter),
) -> ProductListResponse:
    items, total = await adapter.list(
        limit=limit, offset=offset, query=q, category=category
    )
    return ProductListResponse(
        items=[ProductOut.from_item(i) for i in items],
        total=total,
        limit=limit,
        offset=offset,
        query=q,
    )


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(
    product_id: str = Path(..., min_length=1, max_length=128),
    adapter: DeterministicDemoAdapter = Depends(get_catalog_adapter),
) -> ProductOut:
    if not _ID_PATTERN.match(product_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    item = await adapter.detail(product_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )
    return ProductOut.from_item(item)
