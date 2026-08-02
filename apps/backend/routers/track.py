"""Public analytics tracking endpoints (M4-001).

Endpoints are deliberately write-only and unauthenticated: they store anonymous
events (hashed IP, user-agent) and never echo back any data. The admin layer
is the only place that can read aggregated stats.
"""

from __future__ import annotations

import hashlib

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import CtaClick, Pageview
from db.session import get_session

router = APIRouter(prefix="/api/track", tags=["tracking"])


def _hash(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:32]


class PageviewIn(BaseModel):
    path: str = Field(min_length=1, max_length=512)
    referrer: str | None = Field(default=None, max_length=1024)


class CtaClickIn(BaseModel):
    product_id: str | None = Field(default=None, max_length=64)
    article_id: str | None = Field(default=None, max_length=64)
    url: str = Field(min_length=1, max_length=2048)


@router.post("/pageview", status_code=204)
async def track_pageview(
    body: PageviewIn,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Record an anonymous pageview event."""
    ip = request.client.host if request.client else None
    session.add(
        Pageview(
            path=body.path,
            referrer=body.referrer,
            user_agent=request.headers.get("user-agent"),
            ip_hash=_hash(ip),
        )
    )
    await session.commit()


@router.post("/click", status_code=204)
async def track_cta_click(
    body: CtaClickIn,
    request: Request,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Record an affiliate CTA click event."""
    ip = request.client.host if request.client else None
    session.add(
        CtaClick(
            product_id=body.product_id,
            article_id=body.article_id,
            url=body.url,
            ip_hash=_hash(ip),
        )
    )
    await session.commit()
