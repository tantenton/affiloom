"""Admin API response models.

Everything is a thin Pydantic DTO — the SQL layer stays in ``db.models``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict


class SyncRunOut(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    merchant_slug: str
    status: str
    trigger: str
    products_seen: int
    products_created: int
    products_updated: int
    products_deactivated: int
    started_at: datetime
    finished_at: Optional[datetime] = None
    error: Optional[str] = None
    stats: Optional[dict[str, Any]] = None


class SyncRunListResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[SyncRunOut]
    total: int


class SyncTriggerResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    run_id: str
    merchant: str
    status: str
    seen: int
    created: int
    updated: int
    deactivated: int
    skipped: bool = False
    error: Optional[str] = None


# ── M6 Admin Dashboard ────────────────────────────────────────────────────


class ProductStats(BaseModel):
    model_config = ConfigDict(frozen=True)

    total: int
    active: int
    inactive: int
    merchants: int


class SyncHealthStats(BaseModel):
    model_config = ConfigDict(frozen=True)

    total_runs: int
    successful: int
    failed: int
    healthy: bool
    last_success: dict[str, str] = {}


class ContentStats(BaseModel):
    model_config = ConfigDict(frozen=True)

    articles_total: int
    articles_published: int
    articles_draft: int
    articles_archived: int
    missing_excerpt: int


class AnalyticsStats(BaseModel):
    model_config = ConfigDict(frozen=True)

    pageviews_total: int
    cta_clicks_total: int
    clicks_today: int


class AdminDashboardResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    products: ProductStats
    sync: SyncHealthStats
    content: ContentStats
    analytics: AnalyticsStats


__all__ = [
    "AdminDashboardResponse",
    "AnalyticsStats",
    "ContentStats",
    "ProductStats",
    "SyncHealthStats",
    "SyncRunListResponse",
    "SyncRunOut",
    "SyncTriggerResponse",
]
