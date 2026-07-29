"""ORM models for the M4 catalog persistence layer.

Design notes
------------
* ``Merchant`` is the affiliate provider partition (``demo``, ``shopee``, ...).
* ``Product`` is the deduplicated catalog row; ``(merchant_id, external_id)`` is
  the natural key that maps back to whichever partner-issued id we saw. That
  lets us keep ``id`` as a stable internal UUID we can safely expose in URLs.
* ``Offer`` is one price/currency/deep-link observation for a product; a
  product can carry multiple offers if the same catalog item shows up on
  different partner storefronts.
* ``SyncRun`` tracks every ingest attempt (idempotent adapter pulls) so the
  admin surface can show the last N runs, their status, and counters.

Everything is timezone-aware UTC. String IDs are UUIDs so the wire contract
stays stable across DBs (Postgres in prod, SQLite in tests).
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def _uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class SyncRunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class Merchant(Base):
    __tablename__ = "merchants"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    # Stable slug the adapter reports as ``adapter.name``.
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="merchant", cascade="all, delete-orphan"
    )
    sync_runs: Mapped[list["SyncRun"]] = relationship(
        back_populates="merchant", cascade="all, delete-orphan"
    )


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("merchant_id", "external_id", name="uq_products_merchant_ext"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    merchant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False
    )
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(
        String(128), nullable=True, index=True
    )
    image_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    merchant: Mapped[Merchant] = relationship(back_populates="products")
    offers: Mapped[list["Offer"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class Offer(Base):
    __tablename__ = "offers"
    __table_args__ = (
        UniqueConstraint("product_id", "source", name="uq_offers_product_source"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    product_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    # Provider slug that observed the offer. Matches ``Merchant.slug`` today
    # but is stored on the offer so future multi-source merges keep the trail.
    source: Mapped[str] = mapped_column(String(64), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    commission_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    product: Mapped[Product] = relationship(back_populates="offers")


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    merchant_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("merchants.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[SyncRunStatus] = mapped_column(
        Enum(SyncRunStatus, name="sync_run_status", native_enum=False, length=16),
        nullable=False,
        default=SyncRunStatus.PENDING,
        index=True,
    )
    # Discriminator so operators can tell scheduled/CLI runs from admin trigger.
    trigger: Mapped[str] = mapped_column(String(32), nullable=False, default="admin")
    products_seen: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    products_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    products_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    products_deactivated: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stats: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False, index=True
    )
    finished_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    merchant: Mapped[Merchant] = relationship(back_populates="sync_runs")


__all__ = [
    "Base",
    "Merchant",
    "Offer",
    "Product",
    "SyncRun",
    "SyncRunStatus",
]
