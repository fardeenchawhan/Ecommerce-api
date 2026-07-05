from decimal import Decimal
from pydantic import BaseModel


class DashboardResponseSchema(BaseModel):
    total_users: int
    total_products: int

    total_orders: int

    pending_orders: int
    confirmed_orders: int
    shipped_orders: int
    delivered_orders: int
    cancelled_orders: int

    total_sales: Decimal

    # NEW
    today_orders: int
    today_sales: Decimal
    average_order_value: Decimal