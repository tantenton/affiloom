"""Sitemap + robots endpoints (backend-served).

Frontend `sitemap.ts` and `robots.ts` proxy against this so they only need to
hit the backend once. Response is deterministic and cacheable.
"""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.provider import DeterministicDemoAdapter
from db.models import Article, ArticleCategory, ArticleStatus, Site
from db.session import get_session
from dependencies import get_catalog_adapter

router = APIRouter(prefix="/api", tags=["seo"])


@router.get("/sitemap")
async def sitemap(
    session: AsyncSession = Depends(get_session),
    adapter: DeterministicDemoAdapter = Depends(get_catalog_adapter),
) -> dict:
    """Return the flat list of canonical URLs to include in the sitemap.

    Static entries + product detail URLs + published articles + categories.
    Frontend renders them into XML via next-app-router `sitemap.ts`.
    """
    items, _ = await adapter.list(limit=1000, offset=0)
    now_iso = datetime.now(timezone.utc).isoformat()

    entries: list[dict] = [
        {"loc": "/", "changefreq": "weekly", "priority": 1.0, "lastmod": now_iso},
        {"loc": "/produk", "changefreq": "daily", "priority": 0.9, "lastmod": now_iso},
        {"loc": "/artikel", "changefreq": "daily", "priority": 0.8, "lastmod": now_iso},
    ]

    for item in items:
        entries.append(
            {
                "loc": f"/produk/{item.id}",
                "changefreq": "weekly",
                "priority": 0.7,
                "lastmod": item.last_seen_at.isoformat(),
            }
        )

    # Include published articles + categories from the active site.
    site = (
        await session.execute(
            select(Site).where(Site.is_active.is_(True)).limit(1)
        )
    ).scalar_one_or_none()
    if site is not None:
        cat_stmt = select(ArticleCategory).where(
            ArticleCategory.site_id == site.id,
            ArticleCategory.is_active.is_(True),
        )
        for cat in (await session.execute(cat_stmt)).scalars().all():
            entries.append(
                {
                    "loc": f"/kategori/{cat.slug}",
                    "changefreq": "weekly",
                    "priority": 0.6,
                    "lastmod": cat.updated_at.isoformat(),
                }
            )
        art_stmt = select(Article).where(
            Article.site_id == site.id,
            Article.status == ArticleStatus.PUBLISHED,
        )
        for art in (await session.execute(art_stmt)).scalars().all():
            entries.append(
                {
                    "loc": art.canonical_path or f"/artikel/{art.slug}",
                    "changefreq": "weekly",
                    "priority": 0.7,
                    "lastmod": (art.published_at or art.updated_at).isoformat(),
                }
            )

    return {"entries": entries}


@router.get("/robots")
async def robots() -> dict:
    """Return machine-readable robots directives.

    Frontend `robots.ts` renders these into the final `/robots.txt`.
    """
    return {
        "rules": [
            {"user_agent": "*", "allow": "/", "disallow": ["/api/admin/"]},
        ],
        "sitemaps": ["/sitemap.xml"],
    }


__all__ = ["router"]
