from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.cart.models import CartItemModel
from src.order.ditos import UpdateOrderStatusSchema
from src.order.models import OrderItemModel, OrderModel
from src.product.models import ProductModel
from src.user.models import Usermodel


def checkout(db: Session, current_user: Usermodel):
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
        status="pending",
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


def get_all_orders(
    db: Session,
    current_user: Usermodel,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this resource"
        )

    return (
        db.execute(
            select(OrderModel)
            .options(
                joinedload(OrderModel.user),
                joinedload(OrderModel.order_items)
                .joinedload(OrderItemModel.product),
            )
            .order_by(OrderModel.created_at.desc())
        )
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

    order.status = body.status.value

    db.commit()

    db.refresh(order)

    return order