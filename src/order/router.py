from typing import List

from fastapi import APIRouter, Depends, status,Query
from sqlalchemy.orm import Session
from src.order.enums import OrderStatus, OrderSort
from datetime import datetime

from src.order import controller
from src.order.ditos import (
    OrderResponseSchema,
    UpdateOrderStatusSchema,
)
from src.utils.helpers import get_current_admin
from src.user.models import Usermodel
from src.utils.db import get_db
from src.utils.helpers import get_current_user
from src.order import admin_service


order_routes = APIRouter(
    prefix="/orders",
    tags=["Orders"],
)


@order_routes.post(
    "/checkout",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Checkout cart",
    description="Create an order from the current user's cart.",
)
async def checkout(
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.checkout(db, current_user)



@order_routes.get(
    "",
    response_model=List[OrderResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="My orders",
    description="Get all orders of the current user.",
)
async def get_my_orders(
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.get_my_orders(db, current_user)


@order_routes.get(
    "/{order_id}",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get order",
    description="Get a single order of the current user.",
)
async def get_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.get_my_order(
        order_id,
        db,
        current_user,
    )


@order_routes.get(
    "/admin/all",
    response_model=List[OrderResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Admin - Get all orders",
    description="""
Search, filter and paginate all orders.

Supports:

- Pagination
- Search by username
- Search by name
- Search by email
- Filter by status
- Filter by start date
- Filter by end date
""",
)
async def get_all_orders(
    skip: int = Query(
        default=0,
        ge=0,
        description="Number of records to skip",
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of records to return",
    ),
    status_filter: OrderStatus | None = Query(
        default=None,
        description="Filter by order status",
    ),

    sort_by: OrderSort = Query(
    default=OrderSort.NEWEST,
    description="Sorting option",
    ),

    search: str | None = Query(
        default=None,
        description="Search by username, name or email",
    ),
    start_date: datetime | None = Query(
        default=None,
        description="Orders created on or after this date",
    ),
    end_date: datetime | None = Query(
        default=None,
        description="Orders created on or before this date",
    ),
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_admin),
):
    return admin_service.get_all_orders(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        search=search,
        start_date=start_date,
        end_date=end_date,
        sort_by=sort_by,
    )


@order_routes.patch(
    "/{order_id}/status",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update order status",
    description="Admin: Update order status.",
)
async def update_order_status(
    order_id: int,
    body: UpdateOrderStatusSchema,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_admin),
):
    return admin_service.update_order_status(
        order_id,
        body,
        db,
        current_user,
    )



@order_routes.patch(
    "/{order_id}/cancel",
    response_model=OrderResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Cancel my order",
    description="""
Cancel the current user's order.

Rules:
- Only the owner can cancel.
- Only PENDING or CONFIRMED orders can be cancelled.
- Stock is automatically restored.
""",
)
async def cancel_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.cancel_my_order(
        order_id,
        db,
        current_user,
    )