"""convert order status to enum

Revision ID: 17910fa83a1c
Revises: f5f7e9faabb3
Create Date: 2026-07-03 23:23:28.144865
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "17910fa83a1c"
down_revision: Union[str, Sequence[str], None] = "f5f7e9faabb3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


order_status = sa.Enum(
    "PENDING",
    "CONFIRMED",
    "SHIPPED",
    "DELIVERED",
    "CANCELLED",
    name="order_status",
)


def upgrade() -> None:
    # Create enum type
    order_status.create(op.get_bind(), checkfirst=True)

    # Convert existing values to uppercase
    op.execute("""
        UPDATE orders
        SET status = UPPER(status);
    """)

    # Convert column to enum
    op.execute("""
        ALTER TABLE orders
        ALTER COLUMN status
        TYPE order_status
        USING status::order_status;
    """)


def downgrade() -> None:
    # Convert ENUM -> VARCHAR
    op.execute(
        """
        ALTER TABLE orders
        ALTER COLUMN status
        TYPE VARCHAR(30)
        USING status::text;
        """
    )

    # Drop enum type
    order_status.drop(op.get_bind(), checkfirst=True)
