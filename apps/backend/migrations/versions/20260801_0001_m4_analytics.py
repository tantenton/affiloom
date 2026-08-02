"""add analytics tables for M4-001."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260801_0001_m4_analytics"
down_revision = "20260730_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pageviews",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("path", sa.String(length=512), nullable=False),
        sa.Column("referrer", sa.String(length=1024), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("ip_hash", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pageviews_path", "pageviews", ["path"], unique=False)
    op.create_index("ix_pageviews_ip_hash", "pageviews", ["ip_hash"], unique=False)
    op.create_index(
        "ix_pageviews_created_at", "pageviews", ["created_at"], unique=False
    )

    op.create_table(
        "cta_clicks",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("product_id", sa.String(length=64), nullable=True),
        sa.Column("article_id", sa.String(length=64), nullable=True),
        sa.Column("url", sa.String(length=2048), nullable=False),
        sa.Column("ip_hash", sa.String(length=64), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_cta_clicks_product_id", "cta_clicks", ["product_id"], unique=False)
    op.create_index("ix_cta_clicks_article_id", "cta_clicks", ["article_id"], unique=False)
    op.create_index("ix_cta_clicks_ip_hash", "cta_clicks", ["ip_hash"], unique=False)
    op.create_index(
        "ix_cta_clicks_created_at", "cta_clicks", ["created_at"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_cta_clicks_created_at", table_name="cta_clicks")
    op.drop_index("ix_cta_clicks_ip_hash", table_name="cta_clicks")
    op.drop_index("ix_cta_clicks_article_id", table_name="cta_clicks")
    op.drop_index("ix_cta_clicks_product_id", table_name="cta_clicks")
    op.drop_table("cta_clicks")
    op.drop_index("ix_pageviews_created_at", table_name="pageviews")
    op.drop_index("ix_pageviews_ip_hash", table_name="pageviews")
    op.drop_index("ix_pageviews_path", table_name="pageviews")
    op.drop_table("pageviews")
