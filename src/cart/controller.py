from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from src.cart.ditos import AddToCartSchema, UpdateCartSchema
from src.cart.models import CartItemModel
from src.product.models import ProductModel
from src.user.models import Usermodel


def add_to_cart(
    body: AddToCartSchema,
    db: Session,
    current_user: Usermodel,
):
    product = db.get(ProductModel, body.product_id)

    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    if product.stock < body.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested quantity exceeds available stock."
        )

    cart_item = db.execute(
        select(CartItemModel).where(
            CartItemModel.user_id == current_user.id,
            CartItemModel.product_id == body.product_id
        )
    ).scalar_one_or_none()

    if cart_item:
        new_quantity = cart_item.quantity + body.quantity

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock."
            )

        cart_item.quantity = new_quantity

    else:
        cart_item = CartItemModel(
            user_id=current_user.id,
            product_id=body.product_id,
            quantity=body.quantity
        )

        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)

    return {
    "id": cart_item.id,
    "quantity": cart_item.quantity,
    "subtotal": Decimal(str(cart_item.product.price)) * cart_item.quantity,
    "product": cart_item.product,
}




def get_cart(
    db: Session,
    current_user: Usermodel,
):
    cart_items = (
        db.execute(
            select(CartItemModel)
            .options(
                joinedload(CartItemModel.product)
                .joinedload(ProductModel.category)
            )
            .where(CartItemModel.user_id == current_user.id)
        )
        .unique()
        .scalars()
        .all()
    )

    total_items = sum(item.quantity for item in cart_items)

    subtotal = sum(
        Decimal(str(item.product.price)) * item.quantity
        for item in cart_items
    )

    return {
        "items": [
            {
                **item.__dict__,
                "subtotal": Decimal(str(item.product.price)) * item.quantity,
            }
            for item in cart_items
        ],
        "total_items": total_items,
        "subtotal": subtotal,
    }


def update_cart_item(
    cart_item_id: int,
    body: UpdateCartSchema,
    db: Session,
    current_user: Usermodel,
):
    cart_item = db.execute(
        select(CartItemModel)
        .options(joinedload(CartItemModel.product))
        .where(
            CartItemModel.id == cart_item_id,
            CartItemModel.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found."
        )

    if body.quantity > cart_item.product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested quantity exceeds available stock."
        )

    cart_item.quantity = body.quantity

    db.commit()
    db.refresh(cart_item)

    return {
    "id": cart_item.id,
    "quantity": cart_item.quantity,
    "subtotal": Decimal(str(cart_item.product.price)) * cart_item.quantity,
    "product": cart_item.product,
}


def remove_cart_item(
    cart_item_id: int,
    db: Session,
    current_user: Usermodel,
):
    cart_item = db.execute(
        select(CartItemModel).where(
            CartItemModel.id == cart_item_id,
            CartItemModel.user_id == current_user.id
        )
    ).scalar_one_or_none()

    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found."
        )

    db.delete(cart_item)
    db.commit()

    return None


def clear_cart(
    db: Session,
    current_user: Usermodel,
):
    cart_items = db.execute(
        select(CartItemModel).where(
            CartItemModel.user_id == current_user.id
        )
    ).scalars().all()

    for item in cart_items:
        db.delete(item)

    db.commit()

    return None