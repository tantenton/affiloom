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


class Site(Base):
    """SEO site / domain surface.

    Kept as a first-class row so a future multi-brand setup can attach articles
    and canonical URLs to a specific domain without leaking the value into
    every request.
    """

    __tablename__ = "sites"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    slug: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    tagline: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(16), nullable=False, default="id-ID")
    default_locale: Mapped[str] = mapped_column(
        String(16), nullable=False, default="id_ID"
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    categories: Mapped[list["ArticleCategory"]] = relationship(
        back_populates="site", cascade="all, delete-orphan"
    )
    articles: Mapped[list["Article"]] = relationship(
        back_populates="site", cascade="all, delete-orphan"
    )


class ArticleCategory(Base):
    """Editorial category grouping articles (topic vertical)."""

    __tablename__ = "article_categories"
    __table_args__ = (
        UniqueConstraint("site_id", "slug", name="uq_article_categories_site_slug"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    site_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False
    )
    slug: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    site: Mapped[Site] = relationship(back_populates="categories")
    articles: Mapped[list["Article"]] = relationship(back_populates="category")


class ArticleStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Article(Base):
    """SEO article with canonical slug + status lifecycle.

    Deterministic drafts persist under ``DRAFT`` until an admin publishes them.
    ``body_md`` is Markdown and never contains raw HTML from AI providers so
    the render layer stays predictable. AI-provider generation is opt-in and
    disabled when credentials are absent.
    """

    __tablename__ = "articles"
    __table_args__ = (
        UniqueConstraint("site_id", "slug", name="uq_articles_site_slug"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    site_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("sites.id", ondelete="CASCADE"), nullable=False
    )
    category_id: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("article_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    slug: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    excerpt: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    body_md: Mapped[str] = mapped_column(Text, nullable=False, default="")
    meta_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    canonical_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    language: Mapped[str] = mapped_column(String(16), nullable=False, default="id-ID")
    status: Mapped[ArticleStatus] = mapped_column(
        Enum(ArticleStatus, name="article_status", native_enum=False, length=16),
        nullable=False,
        default=ArticleStatus.DRAFT,
        index=True,
    )
    ai_provider: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    ai_model: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    site: Mapped[Site] = relationship(back_populates="articles")
    category: Mapped[Optional[ArticleCategory]] = relationship(
        back_populates="articles"
    )
    product_links: Mapped[list["ArticleProduct"]] = relationship(
        back_populates="article", cascade="all, delete-orphan"
    )


class ArticleProduct(Base):
    """Internal link between article and product (with ordering + suggestion score)."""

    __tablename__ = "article_products"
    __table_args__ = (
        UniqueConstraint(
            "article_id", "product_id", name="uq_article_products_article_product"
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    article_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    article: Mapped[Article] = relationship(back_populates="product_links")
class Collection(Base):
    __tablename__ = "collections"
    __table_args__ = (UniqueConstraint("slug", name="uq_collections_slug"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    slug: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    products: Mapped[list["CollectionProduct"]] = relationship(
        back_populates="collection", cascade="all, delete-orphan"
    )


class CollectionProduct(Base):
    __tablename__ = "collection_products"
    __table_args__ = (
        UniqueConstraint(
            "collection_id", "product_id", name="uq_collection_products_col_prod"
        ),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    collection_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("collections.id", ondelete="CASCADE"), nullable=False
    )
    product_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    collection: Mapped[Collection] = relationship(back_populates="products")
    product: Mapped[Product] = relationship()


class Pageview(Base):
    """Anonymous pageview event for the analytics surface (M4-001)."""

    __tablename__ = "pageviews"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    path: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    referrer: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    ip_hash: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False, index=True
    )


class CtaClick(Base):
    """Affiliate CTA click event (M4-001).

    Stores the product the user clicked and a hash of the visitor IP so we can
    de-duplicate without storing PII.
    """

    __tablename__ = "cta_clicks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_uuid)
    product_id: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True
    )
    article_id: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True
    )
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    ip_hash: Mapped[Optional[str]] = mapped_column(
        String(64), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False, index=True
    )


__all__ = [
    "Article",
    "ArticleCategory",
    "ArticleProduct",
    "ArticleStatus",
    "Base",
    "Collection",
    "CollectionProduct",
    "CtaClick",
    "Merchant",
    "Offer",
    "Pageview",
    "Product",
    "Site",
    "SyncRun",
    "SyncRunStatus",
]
