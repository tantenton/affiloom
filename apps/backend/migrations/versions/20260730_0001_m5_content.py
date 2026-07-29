"""m5: SEO content (sites, article_categories, articles, article_products)

Revision ID: 20260730_0001
Revises: 20260729_0001
Create Date: 2026-07-30 00:00:00
"""
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260730_0001"
down_revision: Union[str, None] = "20260729_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_ARTICLE_STATUS = sa.Enum(
    "draft",
    "published",
    "archived",
    name="article_status",
    native_enum=False,
    length=16,
)


def upgrade() -> None:
    op.create_table(
        "sites",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("slug", sa.String(length=64), nullable=False, unique=True),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("tagline", sa.String(length=255), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=False, server_default="id-ID"),
        sa.Column(
            "default_locale", sa.String(length=16), nullable=False, server_default="id_ID"
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "article_categories",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "site_id",
            sa.String(length=64),
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "site_id", "slug", name="uq_article_categories_site_slug"
        ),
    )
    op.create_index(
        "ix_article_categories_slug", "article_categories", ["slug"]
    )
    op.create_index(
        "ix_article_categories_is_active", "article_categories", ["is_active"]
    )

    op.create_table(
        "articles",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "site_id",
            sa.String(length=64),
            sa.ForeignKey("sites.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "category_id",
            sa.String(length=64),
            sa.ForeignKey("article_categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("slug", sa.String(length=200), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("excerpt", sa.String(length=500), nullable=True),
        sa.Column("body_md", sa.Text(), nullable=False, server_default=""),
        sa.Column("meta_title", sa.String(length=255), nullable=True),
        sa.Column("meta_description", sa.String(length=500), nullable=True),
        sa.Column("canonical_path", sa.String(length=512), nullable=True),
        sa.Column("language", sa.String(length=16), nullable=False, server_default="id-ID"),
        sa.Column("status", _ARTICLE_STATUS, nullable=False, server_default="draft"),
        sa.Column("ai_provider", sa.String(length=64), nullable=True),
        sa.Column("ai_model", sa.String(length=128), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("site_id", "slug", name="uq_articles_site_slug"),
    )
    op.create_index("ix_articles_slug", "articles", ["slug"])
    op.create_index("ix_articles_status", "articles", ["status"])
    op.create_index("ix_articles_category_id", "articles", ["category_id"])
    op.create_index("ix_articles_published_at", "articles", ["published_at"])

    op.create_table(
        "article_products",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "article_id",
            sa.String(length=64),
            sa.ForeignKey("articles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.String(length=64),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "article_id", "product_id", name="uq_article_products_article_product"
        ),
    )


def downgrade() -> None:
    op.drop_table("article_products")
    op.drop_index("ix_articles_published_at", table_name="articles")
    op.drop_index("ix_articles_category_id", table_name="articles")
    op.drop_index("ix_articles_status", table_name="articles")
    op.drop_index("ix_articles_slug", table_name="articles")
    op.drop_table("articles")
    op.drop_index(
        "ix_article_categories_is_active", table_name="article_categories"
    )
    op.drop_index("ix_article_categories_slug", table_name="article_categories")
    op.drop_table("article_categories")
    op.drop_table("sites")
