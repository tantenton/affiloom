"""Admin sync endpoints.

Guarded by a shared bearer token (``settings.ADMIN_API_TOKEN``). When the
token is unset the router refuses every request with 503 so a misconfigured
production deploy fails closed instead of exposing the trigger endpoint.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.provider import DeterministicDemoAdapter
from config import settings
from db.models import Merchant, SyncRun
from db.session import get_session
from dependencies import get_catalog_adapter
from schemas.admin import SyncRunListResponse, SyncRunOut, SyncTriggerResponse
from services.sync import run_sync

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _require_admin_token(
    authorization: str | None = Header(default=None),
) -> None:
    token = settings.ADMIN_API_TOKEN
    if not token:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin API disabled: ADMIN_API_TOKEN is not configured.",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    provided = authorization[len("Bearer ") :].strip()
    # Constant-time-ish comparison; the tokens are short and the exposure
    # is admin-only, but avoid short-circuit compare regardless.
    if len(provided) != len(token) or not all(
        a == b for a, b in zip(provided, token)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin token",
        )


def _serialize(run: SyncRun, merchant_slug: str) -> SyncRunOut:
    return SyncRunOut(
        id=run.id,
        merchant_slug=merchant_slug,
        status=run.status.value,
        trigger=run.trigger,
        products_seen=run.products_seen,
        products_created=run.products_created,
        products_updated=run.products_updated,
        products_deactivated=run.products_deactivated,
        started_at=run.started_at,
        finished_at=run.finished_at,
        error=run.error,
        stats=run.stats,
    )


@router.post(
    "/sync/{merchant}",
    response_model=SyncTriggerResponse,
    dependencies=[Depends(_require_admin_token)],
)
async def trigger_sync(
    merchant: str,
    session: AsyncSession = Depends(get_session),
    adapter: DeterministicDemoAdapter = Depends(get_catalog_adapter),
) -> SyncTriggerResponse:
    if merchant != adapter.name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No adapter registered for merchant '{merchant}'",
        )
    result = await run_sync(session, adapter=adapter, trigger="admin")
    return SyncTriggerResponse(
        run_id=result.run_id,
        merchant=result.merchant_slug,
        status=result.status.value,
        seen=result.seen,
        created=result.created,
        updated=result.updated,
        deactivated=result.deactivated,
        skipped=result.skipped,
        error=result.error,
    )


@router.get(
    "/sync/runs",
    response_model=SyncRunListResponse,
    dependencies=[Depends(_require_admin_token)],
)
async def list_sync_runs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
) -> SyncRunListResponse:
    total = (
        await session.execute(select(func.count()).select_from(SyncRun))
    ).scalar_one()
    stmt = (
        select(SyncRun, Merchant.slug)
        .join(Merchant, Merchant.id == SyncRun.merchant_id)
        .order_by(SyncRun.started_at.desc())
        .limit(limit)
        .offset(offset)
    )
    rows = (await session.execute(stmt)).all()
    return SyncRunListResponse(
        items=[_serialize(run, slug) for run, slug in rows],
        total=int(total),
    )


@router.get(
    "/sync/runs/{run_id}",
    response_model=SyncRunOut,
    dependencies=[Depends(_require_admin_token)],
)
async def get_sync_run(
    run_id: str,
    session: AsyncSession = Depends(get_session),
) -> SyncRunOut:
    stmt = (
        select(SyncRun, Merchant.slug)
        .join(Merchant, Merchant.id == SyncRun.merchant_id)
        .where(SyncRun.id == run_id)
    )
    row = (await session.execute(stmt)).one_or_none()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sync run not found",
        )
    run, slug = row
    return _serialize(run, slug)


__all__ = ["router"]
