"""Admin dashboard API: aggregate stats for products, content, and sync health.

All endpoints require the admin bearer token.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    Article,
    ArticleStatus,
    Merchant,
    Product,
    SyncRun,
    SyncRunStatus,
)
from db.session import get_session
from routers.admin import _require_admin_token
from schemas.admin import (
    AdminDashboardResponse,
    ContentStats,
    ProductStats,
    SyncHealthStats,
)

router = APIRouter(
    prefix="/api/admin/dashboard",
    tags=["admin-dashboard"],
    dependencies=[Depends(_require_admin_token)],
)


@router.get("/summary", response_model=AdminDashboardResponse)
async def dashboard_summary(
    session: AsyncSession = Depends(get_session),
) -> AdminDashboardResponse:
    # ── Products ──────────────────────────────────────────────────────
    total_prod = (
        await session.execute(select(func.count()).select_from(Product))
    ).scalar_one()
    active_prod = (
        await session.execute(
            select(func.count()).select_from(Product).where(Product.is_active.is_(True))
        )
    ).scalar_one()
    inactive_prod = total_prod - active_prod

    merchant_count = (
        await session.execute(select(func.count()).select_from(Merchant))
    ).scalar_one()

    # ── Sync health ───────────────────────────────────────────────────
    total_syncs = (
        await session.execute(select(func.count()).select_from(SyncRun))
    ).scalar_one()
    success_syncs = (
        await session.execute(
            select(func.count())
            .select_from(SyncRun)
            .where(SyncRun.status == SyncRunStatus.SUCCESS)
        )
    ).scalar_one()
    failed_syncs = (
        await session.execute(
            select(func.count())
            .select_from(SyncRun)
            .where(SyncRun.status == SyncRunStatus.FAILED)
        )
    ).scalar_one()

    # Last successful sync per merchant
    merchant_syncs = (
        await session.execute(
            select(Merchant.slug, SyncRun)
            .join(SyncRun, SyncRun.merchant_id == Merchant.id)
            .where(SyncRun.status == SyncRunStatus.SUCCESS)
            .order_by(SyncRun.started_at.desc())
        )
    ).all()
    last_sync_map: dict[str, str] = {}
    for slug, run in merchant_syncs:
        if slug not in last_sync_map:
            last_sync_map[slug] = (
                run.finished_at.isoformat() if run.finished_at else run.started_at.isoformat()
            )

    # ── Content ───────────────────────────────────────────────────────
    total_articles = (
        await session.execute(select(func.count()).select_from(Article))
    ).scalar_one()
    published = (
        await session.execute(
            select(func.count())
            .select_from(Article)
            .where(Article.status == ArticleStatus.PUBLISHED)
        )
    ).scalar_one()
    draft = (
        await session.execute(
            select(func.count())
            .select_from(Article)
            .where(Article.status == ArticleStatus.DRAFT)
        )
    ).scalar_one()
    archived = total_articles - published - draft

    # Articles without excerpts (metadata completeness)
    missing_excerpt = (
        await session.execute(
            select(func.count())
            .select_from(Article)
            .where(Article.excerpt.is_(None), Article.status == ArticleStatus.PUBLISHED)
        )
    ).scalar_one()

    return AdminDashboardResponse(
        products=ProductStats(
            total=int(total_prod),
            active=int(active_prod),
            inactive=int(inactive_prod),
            merchants=int(merchant_count),
        ),
        sync=SyncHealthStats(
            total_runs=int(total_syncs),
            successful=int(success_syncs),
            failed=int(failed_syncs),
            healthy=failed_syncs == 0,
            last_success=last_sync_map,
        ),
        content=ContentStats(
            articles_total=int(total_articles),
            articles_published=int(published),
            articles_draft=int(draft),
            articles_archived=int(archived),
            missing_excerpt=int(missing_excerpt),
        ),
    )