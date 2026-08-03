"""M7 collections and collection_products

Revision ID: 20260803_0001_m7_collections
Revises: 20260801_0001_m4_analytics
Create Date: 2026-08-03 02:57:00

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "20260803_0001_m7_collections"
down_revision = "20260801_0001_m4_analytics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "collections",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_collections_slug"),
    )
    op.create_index(op.f("ix_collections_slug"), "collections", ["slug"])
    op.create_index(op.f("ix_collections_is_active"), "collections", ["is_active"])

    op.create_table(
        "collection_products",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("collection_id", sa.String(length=64), nullable=False),
        sa.Column("product_id", sa.String(length=64), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["collection_id"], ["collections.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "collection_id", "product_id", name="uq_collection_products_col_prod"
        ),
    )


def downgrade() -> None:
    op.drop_table("collection_products")
    op.drop_index(op.f("ix_collections_is_active"), table_name="collections")
    op.drop_index(op.f("ix_collections_slug"), table_name="collections")
    op.drop_table("collections")
