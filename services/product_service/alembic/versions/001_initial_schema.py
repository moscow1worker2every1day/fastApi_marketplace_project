"""Initial categories and products tables.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-26 16:20:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "categories",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["categories.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=False)

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=1024), nullable=True),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False),
        sa.Column(
            "available",
            sa.Boolean(),
            server_default="true",
            nullable=False,
        ),
        sa.Column("seller_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.CheckConstraint("price >= 0", name="check_product_price_positive"),
        sa.CheckConstraint("stock >= 0", name="check_product_stock_positive"),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")
