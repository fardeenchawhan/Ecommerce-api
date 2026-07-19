from decimal import Decimal

from pydantic import BaseModel, Field


class DashboardResponseSchema(BaseModel):
    total_users: int = Field(
        ...,
        ge=0,
        description="Total registered users",
    )

    total_products: int = Field(
        ...,
        ge=0,
        description="Total products in the catalog",
    )

    total_orders: int = Field(
        ...,
        ge=0,
        description="Total orders placed",
    )

    pending_orders: int = Field(
        ...,
        ge=0,
        description="Orders waiting for confirmation",
    )

    confirmed_orders: int = Field(
        ...,
        ge=0,
        description="Confirmed orders",
    )

    shipped_orders: int = Field(
        ...,
        ge=0,
        description="Orders currently shipped",
    )

    delivered_orders: int = Field(
        ...,
        ge=0,
        description="Successfully delivered orders",
    )

    cancelled_orders: int = Field(
        ...,
        ge=0,
        description="Cancelled orders",
    )

    total_sales: Decimal = Field(
        ...,
        ge=0,
        max_digits=12,
        decimal_places=2,
        description="Total lifetime sales",
        examples=[125499.50],
    )

    today_orders: int = Field(
        ...,
        ge=0,
        description="Orders created today",
    )

    today_sales: Decimal = Field(
        ...,
        ge=0,
        max_digits=12,
        decimal_places=2,
        description="Sales generated today",
        examples=[2450.75],
    )

    average_order_value: Decimal = Field(
        ...,
        ge=0,
        max_digits=12,
        decimal_places=2,
        description="Average value of each order",
        examples=[899.99],
    )