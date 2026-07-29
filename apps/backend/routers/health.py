"""Health and readiness endpoints with dependency probes.

* ``/health``  — liveness probe, always 200 while the process is up.
* ``/ready``   — readiness probe; 200 only when all *required* dependencies
                  healthy, 503 otherwise. Optional deps degrade but do not fail
                  readiness.
* ``/deps``    — per-dependency detail: name, healthy, latency, error, required.
"""

from __future__ import annotations

import time
from typing import Any

from fastapi import APIRouter, Response

from config import settings
from db.session import get_engine

router = APIRouter(tags=["health"])


def _latency(start: float) -> float:
    return round(time.monotonic() - start, 4)


async def _probe_db() -> dict[str, Any]:
    ok, latency, err = False, 0.0, None
    try:
        engine = get_engine()
        t0 = time.monotonic()
        async with engine.connect() as conn:
            await conn.execute(__import__("sqlalchemy").text("SELECT 1"))
        latency = _latency(t0)
        ok = True
    except Exception as exc:  # noqa: BLE001
        err = str(exc)[:512]
    return {
        "name": "database",
        "healthy": ok,
        "latency_s": latency,
        "error": err,
        "required": True,
    }


async def _probe_redis() -> dict[str, Any]:
    if not settings.REDIS_ENABLED:
        return {
            "name": "redis",
            "healthy": True,
            "latency_s": 0.0,
            "error": None,
            "required": False,
            "note": "disabled",
        }
    ok, latency, err = False, 0.0, None
    try:
        import redis.asyncio as aioredis

        client = aioredis.from_url(settings.REDIS_URL)
        t0 = time.monotonic()
        await client.ping()
        latency = _latency(t0)
        await client.aclose()
        ok = True
    except Exception as exc:  # noqa: BLE001
        err = str(exc)[:200]
    return {
        "name": "redis",
        "healthy": ok,
        "latency_s": latency,
        "error": err,
        "required": False,
    }


async def _probe_search() -> dict[str, Any]:
    if not settings.MEILI_ENABLED:
        return {
            "name": "search",
            "healthy": True,
            "latency_s": 0.0,
            "error": None,
            "required": False,
            "note": "disabled",
        }
    ok, latency, err = False, 0.0, None
    try:
        from services.search import probe_meilisearch

        t0 = time.monotonic()
        ok = await probe_meilisearch(settings.MEILI_HOST, settings.MEILI_MASTER_KEY)
        latency = _latency(t0)
    except Exception as exc:  # noqa: BLE001
        err = str(exc)[:200]
    return {
        "name": "search",
        "healthy": ok,
        "latency_s": latency,
        "error": err,
        "required": False,
    }


async def _get_all_deps() -> list[dict[str, Any]]:
    return [
        await _probe_db(),
        await _probe_redis(),
        await _probe_search(),
    ]


@router.get("/health")
async def health() -> dict[str, str]:
    """Liveness: process is up."""
    return {"status": "ok"}


@router.get("/ready")
async def ready(response: Response) -> dict[str, Any]:
    """Startup readiness: all *required* deps must be healthy."""
    deps = await _get_all_deps()
    required_healthy = all(d["healthy"] for d in deps if d.get("required"))
    response.status_code = 200 if required_healthy else 503
    return {
        "status": "ready" if required_healthy else "not_ready",
        "deps": deps,
    }


@router.get("/deps")
async def deps_detail() -> dict[str, Any]:
    """Return per-dependency status for monitoring dashboards."""
    deps = await _get_all_deps()
    all_healthy = all(d["healthy"] for d in deps)
    return {
        "status": "healthy" if all_healthy else "degraded",
        "deps": deps,
    }


@router.get("/metrics")
async def metrics() -> dict[str, Any]:
    """Lightweight application metrics for monitoring.

    Returns counts of products, merchants, sync runs, and articles so
    operators and dashboards have a one-stop health summary in one call.
    """
    from sqlalchemy import func, select

    from db.models import Article, ArticleStatus, Merchant, Product, SyncRun, SyncRunStatus
    from db.session import get_sessionmaker

    session_factory = get_sessionmaker()
    result: dict[str, Any] = {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }

    async with session_factory() as session:
        total_prod = (
            await session.execute(select(func.count()).select_from(Product))
        ).scalar_one()
        active_prod = (
            await session.execute(
                select(func.count())
                .select_from(Product)
                .where(Product.is_active.is_(True))
            )
        ).scalar_one()
        merchant_count = (
            await session.execute(select(func.count()).select_from(Merchant))
        ).scalar_one()
        total_syncs = (
            await session.execute(select(func.count()).select_from(SyncRun))
        ).scalar_one()
        failed_syncs = (
            await session.execute(
                select(func.count())
                .select_from(SyncRun)
                .where(SyncRun.status == SyncRunStatus.FAILED)
            )
        ).scalar_one()
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

        result.update(
            {
                "products": {"total": int(total_prod), "active": int(active_prod)},
                "merchants": int(merchant_count),
                "sync": {
                    "total_runs": int(total_syncs),
                    "failed": int(failed_syncs),
                    "healthy": failed_syncs == 0,
                },
                "content": {
                    "articles_total": int(total_articles),
                    "articles_published": int(published),
                    "articles_draft": int(draft),
                },
            }
        )

    return result