from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.product.ditos import ProductResponseSchema
from src.order.enums import OrderStatus


# -------------------------
# Order Item Response
# -------------------------

class OrderItemResponseSchema(BaseModel):
    id: int = Field(
        ...,
        description="Order item ID",
    )

    quantity: int = Field(
        ...,
        ge=1,
        description="Quantity ordered",
        examples=[2],
    )

    unit_price: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=2,
        examples=[999.99],
        description="Price of a single unit at purchase time",
    )

    product: ProductResponseSchema

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Order Response
# -------------------------

class OrderResponseSchema(BaseModel):
    id: int = Field(
        ...,
        description="Order ID",
    )

    total_amount: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=2,
        examples=[2999.97],
        description="Total amount of the order",
    )

    total_items: int = Field(
        ...,
        ge=0,
        examples=[3],
        description="Total quantity of items in the order",
    )

    status: OrderStatus = Field(
        ...,
        description="Current order status",
    )

    created_at: datetime

    updated_at: datetime

    order_items: list[OrderItemResponseSchema]

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Update Order Status
# -------------------------

class UpdateOrderStatusSchema(BaseModel):
    status: OrderStatus = Field(
        ...,
        description="New order status",
        examples=["SHIPPED"],
    )