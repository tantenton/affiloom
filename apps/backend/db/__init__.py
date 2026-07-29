"""Async SQLAlchemy engine, session factory, and ORM models for Affiloom.

The engine is created lazily so tests can override ``DATABASE_URL`` via env
before any connections are opened.
"""

from __future__ import annotations

from db.models import (
    Base,
    Merchant,
    Offer,
    Product,
    SyncRun,
    SyncRunStatus,
)
from db.session import (
    dispose_engine,
    get_engine,
    get_session,
    get_sessionmaker,
    reset_engine,
)

__all__ = [
    "Base",
    "Merchant",
    "Offer",
    "Product",
    "SyncRun",
    "SyncRunStatus",
    "dispose_engine",
    "get_engine",
    "get_session",
    "get_sessionmaker",
    "reset_engine",
]
