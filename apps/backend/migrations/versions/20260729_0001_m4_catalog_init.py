"""m4: catalog persistence init (merchants, products, offers, sync_runs).

Revision ID: 20260729_0001
Revises:
Create Date: 2026-07-29 00:00:00
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260729_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_SYNC_STATUS = sa.Enum(
    "pending",
    "running",
    "success",
    "failed",
    name="sync_run_status",
    native_enum=False,
    length=16,
)


def upgrade() -> None:
    op.create_table(
        "merchants",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column("slug", sa.String(length=64), nullable=False, unique=True),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "merchant_id",
            sa.String(length=64),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("external_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=128), nullable=True),
        sa.Column("image_url", sa.String(length=1024), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint(
            "merchant_id", "external_id", name="uq_products_merchant_ext"
        ),
    )
    op.create_index("ix_products_category", "products", ["category"])
    op.create_index("ix_products_is_active", "products", ["is_active"])

    op.create_table(
        "offers",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "product_id",
            sa.String(length=64),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("source", sa.String(length=64), nullable=False),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("price", sa.Float(), nullable=True),
        sa.Column("currency", sa.String(length=8), nullable=True),
        sa.Column("commission_rate", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("product_id", "source", name="uq_offers_product_source"),
    )

    op.create_table(
        "sync_runs",
        sa.Column("id", sa.String(length=64), primary_key=True),
        sa.Column(
            "merchant_id",
            sa.String(length=64),
            sa.ForeignKey("merchants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", _SYNC_STATUS, nullable=False),
        sa.Column("trigger", sa.String(length=32), nullable=False),
        sa.Column("products_seen", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("products_created", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("products_updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "products_deactivated", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("stats", sa.JSON(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_sync_runs_started_at", "sync_runs", ["started_at"])
    op.create_index("ix_sync_runs_status", "sync_runs", ["status"])


def downgrade() -> None:
    op.drop_index("ix_sync_runs_status", table_name="sync_runs")
    op.drop_index("ix_sync_runs_started_at", table_name="sync_runs")
    op.drop_table("sync_runs")
    op.drop_table("offers")
    op.drop_index("ix_products_is_active", table_name="products")
    op.drop_index("ix_products_category", table_name="products")
    op.drop_table("products")
    op.drop_table("merchants")
