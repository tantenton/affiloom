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


__all__ = ["SyncRunListResponse", "SyncRunOut", "SyncTriggerResponse"]
