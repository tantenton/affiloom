"""Idempotent catalog sync service.

Given an adapter (currently the deterministic demo, later a partner-API
adapter) this pulls the current catalog, upserts merchants/products/offers,
deactivates rows that disappeared, and records a ``SyncRun`` with counters.

Compliance
----------
The service does NOT perform marketplace scraping or live-API impersonation.
It reads from the provider adapter passed in; the demo adapter is fed by
``adapters.provider.demo_items`` fixtures, and future partner adapters must
call official affiliate APIs.

Idempotency
-----------
The natural key is ``(merchant.slug, item.id)`` mapped to Product via
``(merchant_id, external_id)``. Re-running against the same fixture is a
no-op: it updates ``last_seen_at`` and returns zero created/updated deltas
(barring content changes) — verified by tests.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.provider import DeterministicDemoAdapter, MarketplaceItem
from config import settings
from db.models import Merchant, Offer, Product, SyncRun, SyncRunStatus
from services.events import publish_sync_event, sync_lock
from services.search import SearchIndexer, get_indexer

log = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class SyncResult:
    run_id: str
    merchant_slug: str
    status: SyncRunStatus
    seen: int
    created: int
    updated: int
    deactivated: int
    error: Optional[str] = None
    skipped: bool = False


async def _upsert_merchant(
    session: AsyncSession, slug: str, display_name: str
) -> Merchant:
    stmt = select(Merchant).where(Merchant.slug == slug)
    merchant = (await session.execute(stmt)).scalar_one_or_none()
    if merchant is None:
        merchant = Merchant(slug=slug, display_name=display_name, is_active=True)
        session.add(merchant)
        await session.flush()
    else:
        if merchant.display_name != display_name or not merchant.is_active:
            merchant.display_name = display_name
            merchant.is_active = True
    return merchant


async def _apply_item(
    session: AsyncSession,
    merchant: Merchant,
    item: MarketplaceItem,
    now: datetime,
) -> tuple[str, str]:
    """Upsert one ``MarketplaceItem`` → ``Product`` + primary ``Offer``.

    Returns a tuple ``(product_status, offer_status)`` where each is one of
    ``created``/``updated``/``noop``.
    """
    stmt = select(Product).where(
        Product.merchant_id == merchant.id,
        Product.external_id == item.id,
    )
    product = (await session.execute(stmt)).scalar_one_or_none()

    product_status = "noop"
    if product is None:
        product = Product(
            merchant_id=merchant.id,
            external_id=item.id,
            title=item.title,
            description=item.description,
            category=item.category,
            image_url=item.image_url,
            is_active=True,
            last_seen_at=now,
        )
        session.add(product)
        await session.flush()
        product_status = "created"
    else:
        content_changed = (
            product.title != item.title
            or product.description != item.description
            or product.category != item.category
            or product.image_url != item.image_url
            or not product.is_active
        )
        if content_changed:
            product.title = item.title
            product.description = item.description
            product.category = item.category
            product.image_url = item.image_url
            product.is_active = True
            product_status = "updated"
        product.last_seen_at = now

    offer_stmt = select(Offer).where(
        Offer.product_id == product.id,
        Offer.source == item.source,
    )
    offer = (await session.execute(offer_stmt)).scalar_one_or_none()
    offer_status = "noop"
    if offer is None:
        offer = Offer(
            product_id=product.id,
            source=item.source,
            url=item.url,
            price=item.price,
            currency=item.currency,
            commission_rate=item.commission_rate,
            is_active=True,
            last_seen_at=now,
        )
        session.add(offer)
        offer_status = "created"
    else:
        offer_changed = (
            offer.url != item.url
            or offer.price != item.price
            or offer.currency != item.currency
            or offer.commission_rate != item.commission_rate
            or not offer.is_active
        )
        if offer_changed:
            offer.url = item.url
            offer.price = item.price
            offer.currency = item.currency
            offer.commission_rate = item.commission_rate
            offer.is_active = True
            offer_status = "updated"
        offer.last_seen_at = now

    return product_status, offer_status


async def _deactivate_missing(
    session: AsyncSession,
    merchant: Merchant,
    seen_external_ids: set[str],
) -> int:
    """Mark products missing from the current pull inactive.

    Their offers are cascaded to ``is_active=False`` too so the read layer
    can just filter on ``Product.is_active``.
    """
    stmt = select(Product).where(
        Product.merchant_id == merchant.id,
        Product.is_active.is_(True),
    )
    active = (await session.execute(stmt)).scalars().all()
    deactivated = 0
    for prod in active:
        if prod.external_id in seen_external_ids:
            continue
        prod.is_active = False
        deactivated += 1
        await session.execute(
            update(Offer)
            .where(Offer.product_id == prod.id)
            .values(is_active=False)
        )
    return deactivated


async def _index_products(
    indexer: SearchIndexer,
    session: AsyncSession,
    merchant: Merchant,
) -> int:
    """Push the merchant's active catalog into the search index.

    Returns the number of documents pushed.
    """
    stmt = select(Product, Offer).join(Offer, Offer.product_id == Product.id).where(
        Product.merchant_id == merchant.id,
        Product.is_active.is_(True),
        Offer.is_active.is_(True),
    )
    rows = (await session.execute(stmt)).all()
    docs: list[dict] = []
    for product, offer in rows:
        docs.append(
            {
                "id": product.id,
                "external_id": product.external_id,
                "merchant": merchant.slug,
                "title": product.title,
                "description": product.description or "",
                "category": product.category or "",
                "image_url": product.image_url,
                "url": offer.url,
                "price": offer.price,
                "currency": offer.currency,
                "last_seen_at": product.last_seen_at.isoformat(),
            }
        )
    if docs:
        await indexer.upsert(docs)
    return len(docs)


async def run_sync(
    session: AsyncSession,
    *,
    adapter: DeterministicDemoAdapter,
    trigger: str = "admin",
    display_name: Optional[str] = None,
    indexer: Optional[SearchIndexer] = None,
) -> SyncResult:
    """Execute one idempotent sync cycle for ``adapter``.

    Blocks if another sync for the same merchant already holds the Redis lock
    (when Redis is enabled). Otherwise runs to completion, commits, publishes
    a best-effort ``sync.completed`` event, and returns counters.
    """
    slug = adapter.name
    display = display_name or slug.capitalize()

    async with sync_lock(slug) as owned:
        if not owned:
            log.info("sync: %s skipped — another worker holds the lock", slug)
            return SyncResult(
                run_id="",
                merchant_slug=slug,
                status=SyncRunStatus.PENDING,
                seen=0,
                created=0,
                updated=0,
                deactivated=0,
                skipped=True,
            )

        merchant = await _upsert_merchant(session, slug, display)
        run = SyncRun(
            merchant_id=merchant.id,
            status=SyncRunStatus.RUNNING,
            trigger=trigger,
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)
        # Capture the id explicitly so the failure path can requery on a
        # fresh session without triggering lazy loads on a rolled-back one.
        run_id = run.id

        seen = created = updated_count = deactivated = 0
        try:
            items, total = await adapter.list(
                limit=settings.SYNC_MAX_ITEMS, offset=0
            )
            now = datetime.now(timezone.utc)
            seen_ids: set[str] = set()
            for item in items:
                p_status, o_status = await _apply_item(session, merchant, item, now)
                seen += 1
                seen_ids.add(item.id)
                if p_status == "created":
                    created += 1
                elif p_status == "updated":
                    updated_count += 1
                # Offer-only changes still count as an update.
                if p_status == "noop" and o_status in {"created", "updated"}:
                    updated_count += 1

            deactivated = await _deactivate_missing(session, merchant, seen_ids)

            # Search indexing runs after DB mutations but before commit so a
            # failure rolls the whole run back into the ``failed`` bucket.
            active_indexer = indexer or await get_indexer()
            indexed = await _index_products(active_indexer, session, merchant)

            run.status = SyncRunStatus.SUCCESS
            run.products_seen = seen
            run.products_created = created
            run.products_updated = updated_count
            run.products_deactivated = deactivated
            run.finished_at = datetime.now(timezone.utc)
            run.stats = {
                "total_available": total,
                "indexed": indexed,
                "adapter": adapter.name,
            }
            await session.commit()

            await publish_sync_event(
                {
                    "run_id": run.id,
                    "merchant": slug,
                    "status": run.status.value,
                    "seen": seen,
                    "created": created,
                    "updated": updated_count,
                    "deactivated": deactivated,
                }
            )

            return SyncResult(
                run_id=run.id,
                merchant_slug=slug,
                status=run.status,
                seen=seen,
                created=created,
                updated=updated_count,
                deactivated=deactivated,
            )
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            # Expunge in-flight ORM state before requerying so no lazy loads
            # fire against the rolled-back transaction.
            session.expunge_all()
            failure = await session.get(SyncRun, run_id)
            if failure is not None:
                failure.status = SyncRunStatus.FAILED
                failure.error = str(exc)[:2000]
                failure.finished_at = datetime.now(timezone.utc)
                await session.commit()
            log.exception("sync: %s failed", slug)
            return SyncResult(
                run_id=run_id,
                merchant_slug=slug,
                status=SyncRunStatus.FAILED,
                seen=seen,
                created=created,
                updated=updated_count,
                deactivated=deactivated,
                error=str(exc),
            )


__all__ = ["SyncResult", "run_sync"]
