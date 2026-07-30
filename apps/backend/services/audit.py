"""Daily audit job: actionable findings for operators.

The audit is designed as a pure function that reads the DB and returns a
list of findings, each with a severity, category, and an actionable message.
The CLI wrapper (``workers.audit_worker``) calls this and emits JSON.

Findings cover:
* sync health — stale syncs, repeated failures, merchants with zero runs
* data quality — products without categories, offers with null prices
* content gaps — published articles missing excerpts or meta descriptions
* dead-letter review — sync runs stuck in PENDING/RUNNING too long

Each finding maps to a remediation hint so the operator knows the next step.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    Article,
    ArticleStatus,
    Merchant,
    Offer,
    Product,
    SyncRun,
    SyncRunStatus,
)


class Severity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True, slots=True)
class Finding:
    severity: Severity
    category: str
    message: str
    remediation: str
    context: dict = field(default_factory=dict)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def _audit_sync_health(session: AsyncSession, now: datetime) -> list[Finding]:
    findings: list[Finding] = []

    # 1. Failed syncs in last 24h
    cutoff = now - timedelta(hours=24)
    failed = (
        (
            await session.execute(
                select(SyncRun)
                .where(
                    SyncRun.status == SyncRunStatus.FAILED, SyncRun.started_at >= cutoff
                )
                .order_by(SyncRun.started_at.desc())
            )
        )
        .scalars()
        .all()
    )

    for run in failed:
        findings.append(
            Finding(
                severity=Severity.CRITICAL,
                category="sync.health",
                message=f"Sync run {run.id} failed (last 24h)",
                remediation=(  # noqa: E501
                    "Check worker logs; verify API credentials and retry."
                ),
                context={
                    "run_id": run.id,
                    "merchant_id": run.merchant_id,
                    "error": (run.error or "")[:300],
                    "started_at": run.started_at.isoformat(),
                },
            )
        )

    # 2. Merchants with no successful sync ever
    merchants_with_success = (
        (
            await session.execute(
                select(Merchant.id)
                .distinct()
                .join(SyncRun, SyncRun.merchant_id == Merchant.id)
                .where(SyncRun.status == SyncRunStatus.SUCCESS)
            )
        )
        .scalars()
        .all()
    )
    success_merchants = set(merchants_with_success)

    all_merchants = (
        (await session.execute(select(Merchant).where(Merchant.is_active.is_(True))))
        .scalars()
        .all()
    )

    for merchant in all_merchants:
        if merchant.id not in success_merchants:
            findings.append(
                Finding(
                    severity=Severity.WARNING,
                    category="sync.health",
                    message=f"Merchant '{merchant.slug}' has no successful sync",
                    remediation=(  # noqa: E501
                        "Trigger sync manually or verify scheduled worker is running."
                    ),
                    context={
                        "merchant_slug": merchant.slug,
                        "merchant_id": merchant.id,
                    },
                )
            )

    # 3. Stale successful sync (last success older than 7 days)
    stale_cutoff = now - timedelta(days=7)
    stale = (
        await session.execute(
            select(Merchant.slug, func.max(SyncRun.started_at))
            .join(SyncRun, SyncRun.merchant_id == Merchant.id)
            .where(SyncRun.status == SyncRunStatus.SUCCESS)
            .group_by(Merchant.slug)
        )
    ).all()

    for slug, last_run in stale:
        if last_run is None:
            continue
        # Normalize: SQLite returns naive datetimes; Postgres returns aware ones.
        last_run_aware = (
            last_run.replace(tzinfo=timezone.utc)
            if last_run.tzinfo is None
            else last_run
        )
        if last_run_aware < stale_cutoff:
            findings.append(
                Finding(
                    severity=Severity.WARNING,
                    category="sync.stale",
                    message=f"Merchant '{slug}' last synced >7 days ago",
                    remediation="Verify sync-worker scheduling; check adapter connectivity.",  # noqa: E501
                    context={"merchant_slug": slug, "last_sync": last_run.isoformat()},
                )
            )

    # 4. Dead-letter: runs stuck in PENDING or RUNNING for >1h
    stuck_cutoff = now - timedelta(hours=1)
    stuck = (
        (
            await session.execute(
                select(SyncRun)
                .where(
                    SyncRun.status.in_([SyncRunStatus.PENDING, SyncRunStatus.RUNNING]),
                    SyncRun.started_at < stuck_cutoff,
                )
                .order_by(SyncRun.started_at.desc())
            )
        )
        .scalars()
        .all()
    )

    for run in stuck:
        findings.append(
            Finding(
                severity=Severity.CRITICAL,
                category="sync.dead_letter",
                message=f"Sync run {run.id} stuck in {run.status.value} for >1h",
                remediation=(  # noqa: E501
                    "Inspect worker; check Redis lock; restart worker if needed."
                ),
                context={
                    "run_id": run.id,
                    "merchant_id": run.merchant_id,
                    "status": run.status.value,
                    "started_at": run.started_at.isoformat(),
                },
            )
        )

    return findings


async def _audit_data_quality(session: AsyncSession) -> list[Finding]:
    findings: list[Finding] = []

    # Products missing category
    missing_cat = (
        await session.execute(
            select(func.count())
            .select_from(Product)
            .where(Product.category.is_(None), Product.is_active.is_(True))
        )
    ).scalar_one()

    if missing_cat > 0:
        findings.append(
            Finding(
                severity=Severity.WARNING,
                category="data.products",
                message=f"{missing_cat} active products missing category",
                remediation="Review catalog adapter output; add category mapping in adapter config.",  # noqa: E501
                context={"missing_category_count": int(missing_cat)},
            )
        )

    # Products missing description
    missing_desc = (
        await session.execute(
            select(func.count())
            .select_from(Product)
            .where(Product.description.is_(None), Product.is_active.is_(True))
        )
    ).scalar_one()

    if missing_desc > 0:
        findings.append(
            Finding(
                severity=Severity.INFO,
                category="data.products",
                message=f"{missing_desc} active products missing description",
                remediation="Enrich product descriptions via adapter or manual admin input.",  # noqa: E501
                context={"missing_description_count": int(missing_desc)},
            )
        )

    # Active offers with null price
    null_price = (
        await session.execute(
            select(func.count())
            .select_from(Offer)
            .where(Offer.price.is_(None), Offer.is_active.is_(True))
        )
    ).scalar_one()

    if null_price > 0:
        findings.append(
            Finding(
                severity=Severity.WARNING,
                category="data.offers",
                message=f"{null_price} active offers missing price",
                remediation="Verify adapter is returning prices; check partner API price field.",  # noqa: E501
                context={"null_price_count": int(null_price)},
            )
        )

    # Products with no active offers (orphaned)
    orphaned_prod = (
        await session.execute(
            select(func.count())
            .select_from(Product)
            .where(
                Product.is_active.is_(True),
                ~Product.id.in_(
                    select(Offer.product_id).where(Offer.is_active.is_(True))
                ),
            )
        )
    ).scalar_one()

    if orphaned_prod > 0:
        findings.append(
            Finding(
                severity=Severity.WARNING,
                category="data.products",
                message=f"{orphaned_prod} active products with no active offers",
                remediation="Re-sync merchant or deactivate orphaned products.",
                context={"orphaned_count": int(orphaned_prod)},
            )
        )

    return findings


async def _audit_content(session: AsyncSession) -> list[Finding]:
    findings: list[Finding] = []

    # Published articles missing excerpt
    missing_excerpt = (
        await session.execute(
            select(func.count())
            .select_from(Article)
            .where(
                Article.excerpt.is_(None),
                Article.status == ArticleStatus.PUBLISHED,
            )
        )
    ).scalar_one()

    if missing_excerpt > 0:
        findings.append(
            Finding(
                severity=Severity.INFO,
                category="content.metadata",
                message=f"{missing_excerpt} published articles missing excerpt",
                remediation="Review editorial workflow; add excerpts before publication.",  # noqa: E501
                context={"missing_excerpt_count": int(missing_excerpt)},
            )
        )

    # Published articles missing meta_description
    missing_meta = (
        await session.execute(
            select(func.count())
            .select_from(Article)
            .where(
                Article.meta_description.is_(None),
                Article.status == ArticleStatus.PUBLISHED,
            )
        )
    ).scalar_one()

    if missing_meta > 0:
        findings.append(
            Finding(
                severity=Severity.WARNING,
                category="content.seo",
                message=f"{missing_meta} published articles missing meta_description",
                remediation="Generate meta descriptions via admin content API or manual review.",  # noqa: E501
                context={"missing_meta_count": int(missing_meta)},
            )
        )

    # Published articles with no product links
    from db.models import ArticleProduct

    articles_without_links = (
        await session.execute(
            select(func.count())
            .select_from(Article)
            .where(
                Article.status == ArticleStatus.PUBLISHED,
                ~Article.id.in_(select(ArticleProduct.article_id).distinct()),
            )
        )
    ).scalar_one()

    if articles_without_links > 0:
        findings.append(
            Finding(
                severity=Severity.INFO,
                category="content.links",
                message=f"{articles_without_links} published articles no product links",  # noqa: E501
                remediation="Run link suggestion generation for existing articles.",  # noqa: E501
                context={"unlinked_article_count": int(articles_without_links)},
            )
        )

    return findings


async def run_audit(
    session: AsyncSession, *, now: Optional[datetime] = None
) -> list[Finding]:
    """Execute all audit checks and return actionable findings."""
    audit_time = now or _utcnow()
    findings: list[Finding] = []

    findings.extend(await _audit_sync_health(session, audit_time))
    findings.extend(await _audit_data_quality(session))
    findings.extend(await _audit_content(session))

    return findings


def finding_to_dict(f: Finding) -> dict:
    return {
        "severity": f.severity.value,
        "category": f.category,
        "message": f.message,
        "remediation": f.remediation,
        "context": f.context,
    }


__all__ = [
    "Finding",
    "Severity",
    "finding_to_dict",
    "run_audit",
]
