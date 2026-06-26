from typing import Optional
from sqlalchemy import String, Text, Float, ForeignKey,Numeric,Boolean,DateTime,func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.utils.db import Base
from decimal import Decimal
from datetime import datetime


class ProductModel(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2),nullable=False)
    stock: Mapped[int] = mapped_column(default=0)
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True ,nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(), onupdate=func.now(),nullable=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)

    category = relationship("CategoryModel", back_populates="products")
    cart_items = relationship("CartItemModel", back_populates="product", cascade="all, delete")
    order_items = relationship("OrderItemModel", back_populates="product")