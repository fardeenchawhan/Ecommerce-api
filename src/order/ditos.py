from decimal import Decimal
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

from src.product.ditos import ProductResponseSchema


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItemResponseSchema(BaseModel):
    id: int
    quantity: int
    unit_price: Decimal
    product: ProductResponseSchema

    model_config = ConfigDict(from_attributes=True)


class OrderResponseSchema(BaseModel):
    id: int
    total_amount: Decimal
    total_items: int
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    order_items: list[OrderItemResponseSchema]

    model_config = ConfigDict(from_attributes=True)


class UpdateOrderStatusSchema(BaseModel):
    status: OrderStatus