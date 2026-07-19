from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.dashboard.ditos import DashboardResponseSchema
from src.order.models import OrderModel
from src.order.enums import OrderStatus
from src.product.models import ProductModel
from src.user.models import Usermodel
from src.cache.service import get_cache, set_cache
from src.cache.constants import DASHBOARD_CACHE
from src.utils.logger import logger


def get_dashboard(
    db: Session,
    current_user: Usermodel,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this resource",
        )
    
    cache_key = "dashboard"

    cached = get_cache(cache_key)

    if cached:
        return DashboardResponseSchema(**cached)
    total_users = db.scalar(
        select(func.count()).select_from(Usermodel)
    )

    total_products = db.scalar(
        select(func.count()).select_from(ProductModel)
    )

    total_orders = db.scalar(
        select(func.count()).select_from(OrderModel)
    )

    pending_orders = db.scalar(
        select(func.count())
        .select_from(OrderModel)
        .where(OrderModel.status == OrderStatus.PENDING)
    )

    confirmed_orders = db.scalar(
        select(func.count())
        .select_from(OrderModel)
        .where(OrderModel.status == OrderStatus.CONFIRMED)
    )

    shipped_orders = db.scalar(
        select(func.count())
        .select_from(OrderModel)
        .where(OrderModel.status == OrderStatus.SHIPPED)
    )

    delivered_orders = db.scalar(
        select(func.count())
        .select_from(OrderModel)
        .where(OrderModel.status == OrderStatus.DELIVERED)
    )

    cancelled_orders = db.scalar(
        select(func.count())
        .select_from(OrderModel)
        .where(OrderModel.status == OrderStatus.CANCELLED)
    )

    total_sales = (
        db.scalar(
            select(
                func.coalesce(
                    func.sum(OrderModel.total_amount),
                    0,
                )
            ).where(
                OrderModel.status == OrderStatus.DELIVERED
            )
        )
        or Decimal("0.00")
    )

    # -----------------------------
    # Today's Orders
    # -----------------------------
    today_orders = db.scalar(
        select(func.count())
        .select_from(OrderModel)
        .where(
            func.date(OrderModel.created_at) == func.current_date()
        )
    )

    # -----------------------------
    # Today's Sales
    # -----------------------------
    today_sales = (
        db.scalar(
            select(
                func.coalesce(
                    func.sum(OrderModel.total_amount),
                    0,
                )
            ).where(
                OrderModel.status == OrderStatus.DELIVERED,
                func.date(OrderModel.created_at) == func.current_date(),
            )
        )
        or Decimal("0.00")
    )

    # -----------------------------
    # Average Order Value
    # -----------------------------
    average_order_value = (
        db.scalar(
            select(
                func.coalesce(
                    func.avg(OrderModel.total_amount),
                    0,
                )
            ).where(
                OrderModel.status == OrderStatus.DELIVERED
            )
        )
        or Decimal("0.00")
    )

    dashboard = DashboardResponseSchema(
    total_users=total_users,
    total_products=total_products,

    total_orders=total_orders,

    pending_orders=pending_orders,
    confirmed_orders=confirmed_orders,
    shipped_orders=shipped_orders,
    delivered_orders=delivered_orders,
    cancelled_orders=cancelled_orders,

    total_sales=total_sales,

    today_orders=today_orders,
    today_sales=today_sales,
    average_order_value=average_order_value,
    )

    set_cache(
        cache_key,
        dashboard,
        DASHBOARD_CACHE,
    )

    return dashboard