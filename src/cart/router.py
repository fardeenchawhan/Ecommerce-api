from fastapi import APIRouter, Depends, status

from sqlalchemy.orm import Session

from src.cart import controller
from src.cart.ditos import (
    AddToCartSchema,
    UpdateCartSchema,
    CartResponseSchema,
    CartItemResponseSchema,
)
from src.user.models import Usermodel
from src.utils.db import get_db
from src.utils.helpers import get_current_user


cart_routes = APIRouter(
    prefix="/cart",
    tags=["Cart"]
)


@cart_routes.post(
    "",
    response_model=CartItemResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Add product to cart",
    description="Add a product to the logged-in user's cart."
)
async def add_to_cart(
    body: AddToCartSchema,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.add_to_cart(
        body=body,
        db=db,
        current_user=current_user,
    )


@cart_routes.get(
    "",
    response_model=CartResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get current user's cart",
    description="Returns all items in the logged-in user's cart."
)
async def get_cart(
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.get_cart(
        db=db,
        current_user=current_user,
    )


@cart_routes.patch(
    "/{cart_item_id}",
    response_model=CartItemResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update cart quantity",
    description="Update quantity of a cart item."
)
async def update_cart_item(
    cart_item_id: int,
    body: UpdateCartSchema,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.update_cart_item(
        cart_item_id=cart_item_id,
        body=body,
        db=db,
        current_user=current_user,
    )


@cart_routes.delete(
    "/{cart_item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove product from cart",
    description="Remove one product from the logged-in user's cart."
)
async def remove_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.remove_cart_item(
        cart_item_id=cart_item_id,
        db=db,
        current_user=current_user,
    )


@cart_routes.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Clear cart",
    description="Remove all products from the logged-in user's cart."
)
async def clear_cart(
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.clear_cart(
        db=db,
        current_user=current_user,
    )