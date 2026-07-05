from fastapi import HTTPException, status
from sqlalchemy import select,or_
from sqlalchemy.orm import Session, joinedload
from src.order.enums import OrderStatus, OrderSort
from datetime import datetime, timedelta
from src.order.ditos import UpdateOrderStatusSchema
from src.order.models import OrderItemModel, OrderModel
from src.user.models import Usermodel




def get_all_orders(
    db: Session,
    current_user: Usermodel,
    skip: int = 0,
    limit: int = 10,
    status_filter: OrderStatus | None = None,
    search: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
    sort_by: OrderSort = OrderSort.NEWEST,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this resource",
        )

    query = (
        select(OrderModel)
        .join(OrderModel.user)
        .options(
            joinedload(OrderModel.user),
            joinedload(OrderModel.order_items)
            .joinedload(OrderItemModel.product),
        )
    )

    # -------------------------
    # Status Filter
    # -------------------------

    if status_filter:
        query = query.where(
            OrderModel.status == status_filter
        )

    # -------------------------
    # Search
    # -------------------------

    if search:
        keyword = f"%{search.strip()}%"

        query = query.where(
            or_(
                Usermodel.username.ilike(keyword),
                Usermodel.name.ilike(keyword),
                Usermodel.email.ilike(keyword),
            )
        )

    # -------------------------
    # Date Filters
    # -------------------------

    if start_date:
        query = query.where(
            OrderModel.created_at >= start_date
        )

    if end_date:
        query = query.where(
            OrderModel.created_at <= end_date + timedelta(days=1)
        )

    # -------------------------
    # Sorting
    # -------------------------

# -------------------------
# Sorting
# -------------------------

    if sort_by == OrderSort.NEWEST:
        query = query.order_by(
            OrderModel.created_at.desc()
        )

    elif sort_by == OrderSort.OLDEST:
        query = query.order_by(
            OrderModel.created_at.asc()
        )

    elif sort_by == OrderSort.HIGHEST:
        query = query.order_by(
            OrderModel.total_amount.desc()
        )

    elif sort_by == OrderSort.LOWEST:
        query = query.order_by(
            OrderModel.total_amount.asc()
        )

    # -------------------------
    # Pagination
    # -------------------------

    query = query.offset(skip).limit(limit)

    return (
        db.execute(query)
        .unique()
        .scalars()
        .all()
    )


def update_order_status(
    order_id: int,
    body: UpdateOrderStatusSchema,
    db: Session,
    current_user: Usermodel,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can update order status"
        )

    order = db.get(OrderModel, order_id)

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    order.status = body.status

    db.commit()

    db.refresh(order)

    return order