"""add payment fields

Revision ID: 3de0c0dd28ec
Revises: fd1f225dfc95
Create Date: 2026-07-23 00:33:23.734166
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "3de0c0dd28ec"
down_revision: Union[str, Sequence[str], None] = "fd1f225dfc95"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


payment_status_enum = postgresql.ENUM(
    "PENDING",
    "PAID",
    "FAILED",
    "REFUNDED",
    name="paymentstatus",
)


def upgrade() -> None:
    """Upgrade schema."""

    # Create enum type first
    payment_status_enum.create(op.get_bind(), checkfirst=True)

    # Add columns
    op.add_column(
        "orders",
        sa.Column(
            "payment_status",
            payment_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "razorpay_order_id",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "orders",
        sa.Column(
            "razorpay_payment_id",
            sa.String(length=100),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("orders", "razorpay_payment_id")
    op.drop_column("orders", "razorpay_order_id")
    op.drop_column("orders", "payment_status")

    # Drop enum type
    payment_status_enum.drop(op.get_bind(), checkfirst=True)
