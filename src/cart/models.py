from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint,DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.utils.db import Base


class CartItemModel(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_cart_user_product"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    quantity: Mapped[int] = mapped_column(
        nullable=False,
        default=1
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    user = relationship(
        "Usermodel",
        back_populates="cart_items"
    )

    product = relationship(
        "ProductModel",
        back_populates="cart_items"
    )


