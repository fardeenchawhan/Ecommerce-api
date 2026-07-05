from datetime import datetime
from enum import Enum
from src.order.enums import OrderStatus

from sqlalchemy import (
    String,
    ForeignKey,
    Numeric,
    DateTime,
    Enum as SqlEnum,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.utils.db import Base





class OrderModel(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    total_amount: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    total_items: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    status: Mapped[OrderStatus] = mapped_column(
        SqlEnum(
            OrderStatus,
            name="order_status",
            create_type=False,   # <-- important
        ),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True,
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
        index=True,
    )

    user = relationship(
        "Usermodel",
        back_populates="orders",
    )

    order_items = relationship(
        "OrderItemModel",
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderItemModel(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    quantity: Mapped[int] = mapped_column(
        nullable=False,
    )

    unit_price: Mapped[float] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id"),
        nullable=False,
        index=True,
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True,
    )

    order = relationship(
        "OrderModel",
        back_populates="order_items",
    )

    product = relationship(
        "ProductModel",
        back_populates="order_items",
    )