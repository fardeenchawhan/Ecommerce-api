from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.order.order_status import OrderStatus

from src.order import controller
from src.order.ditos import (
    OrderResponseSchema,
    UpdateOrderStatusSchema,
)
from src.utils.helpers import get_current_admin
from src.user.models import Usermodel
from src.utils.db import get_db
from src.utils.helpers import get_current_user


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
    summary="Get all orders",
)
async def get_all_orders(
    skip: int = 0,
    limit: int = 10,
    status: OrderStatus | None = None,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_admin),
):
    return controller.get_all_orders(
        db=db,
        current_user=current_user,
        skip=skip,
        limit=limit,
        status_filter=status,
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
    return controller.update_order_status(
        order_id,
        body,
        db,
        current_user,
    )