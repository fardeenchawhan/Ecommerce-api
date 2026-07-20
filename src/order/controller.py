from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select,or_
from sqlalchemy.orm import Session, joinedload
from src.order.enums import OrderStatus, OrderSort
from datetime import datetime, timedelta
from src.cart.models import CartItemModel
from src.order.ditos import UpdateOrderStatusSchema
from src.order.models import OrderItemModel, OrderModel
from src.product.models import ProductModel
from src.user.models import Usermodel
from src.order.service import cancel_order
from fastapi import BackgroundTasks
from src.notification import service as notification_service


def checkout(db: Session, current_user: Usermodel, background_tasks: BackgroundTasks):
    cart_items = (
        db.execute(
            select(CartItemModel)
            .options(
                joinedload(CartItemModel.product)
            )
            .where(CartItemModel.user_id == current_user.id)
        )
        .unique()
        .scalars()
        .all()
    )

    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )

    total_amount = Decimal("0.00")
    total_items = 0

    order = OrderModel(
        user_id=current_user.id,
        total_amount=Decimal("0.00"),
        total_items=0,
        status=OrderStatus.PENDING,
    )

    db.add(order)
    db.flush()

    for cart_item in cart_items:

        product = (
            db.execute(
                select(ProductModel)
                .where(ProductModel.id == cart_item.product_id)
                .with_for_update()
            )
            .scalar_one()
        )

        if not product.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{product.name} is inactive"
            )

        if product.stock < cart_item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough stock for {product.name}"
            )

        product.stock -= cart_item.quantity

        unit_price = Decimal(product.price)

        order_item = OrderItemModel(
            order_id=order.id,
            product_id=product.id,
            quantity=cart_item.quantity,
            unit_price=unit_price,
        )

        db.add(order_item)

        total_items += cart_item.quantity

        total_amount += (
            unit_price * cart_item.quantity
        )

    order.total_amount = total_amount
    order.total_items = total_items

    for cart_item in cart_items:
        db.delete(cart_item)

    db.commit()
    db.refresh(order)

    notification_service.send_order_confirmation_email(
        background_tasks=background_tasks,
        email=current_user.email,
        name=current_user.name,
        order_id=order.id,
        total=order.total_amount,
    )

    return (
        db.execute(
            select(OrderModel)
            .options(
                joinedload(OrderModel.order_items)
                .joinedload(OrderItemModel.product)
            )
            .where(OrderModel.id == order.id)
        )
        .unique()
        .scalar_one()
    )


def get_my_orders(
    db: Session,
    current_user: Usermodel,
):
    return (
        db.execute(
            select(OrderModel)
            .options(
                joinedload(OrderModel.order_items)
                .joinedload(OrderItemModel.product)
            )
            .where(OrderModel.user_id == current_user.id)
            .order_by(OrderModel.created_at.desc())
        )
        .unique()
        .scalars()
        .all()
    )


def get_my_order(
    order_id: int,
    db: Session,
    current_user: Usermodel,
):
    order = (
        db.execute(
            select(OrderModel)
            .options(
                joinedload(OrderModel.order_items)
                .joinedload(OrderItemModel.product)
            )
            .where(
                OrderModel.id == order_id,
                OrderModel.user_id == current_user.id,
            )
        )
        .unique()
        .scalar_one_or_none()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )

    return order



def cancel_my_order(
    order_id: int,
    db: Session,
    current_user: Usermodel,
):
    order = (
        db.execute(
            select(OrderModel)
            .options(
                joinedload(OrderModel.order_items)
            )
            .where(
                OrderModel.id == order_id,
                OrderModel.user_id == current_user.id,
            )
        )
        .unique()
        .scalar_one_or_none()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )

    return cancel_order(order, db)
