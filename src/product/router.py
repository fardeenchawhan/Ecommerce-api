from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from src.utils.schemas import PaginatedResponse

from src.product import controller
from src.product.ditos import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductResponseSchema,
)
from src.utils.db import get_db
from src.utils.helpers import get_current_admin
from src.user.models import Usermodel


product_routes = APIRouter(
    prefix="/products",
    tags=["Products"]
)


# -------------------------
# Create Product
# -------------------------

@product_routes.post(
    "",
    response_model=ProductResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create Product"
)
async def create_product(

    body: ProductCreateSchema,

    db: Session = Depends(get_db),

    current_user: Usermodel = Depends(get_current_admin)

):
    return controller.create_product(body, db)


# -------------------------
# Get All Products
# -------------------------

@product_routes.get(
    "",
    response_model=PaginatedResponse[ProductResponseSchema],
    summary="Get All Products"
)
async def get_all_products(

    page: int = 1,
    limit: int = 10,

    search: str | None = None,

    category_id: int | None = None,

    min_price: float | None = None,

    max_price: float | None = None,

    in_stock: bool | None = None,

    sort: str | None = None,

    db: Session = Depends(get_db)

):

    return controller.get_all_products(
        db=db,
        page=page,
        limit=limit,
        search=search,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        sort=sort
    )


# -------------------------
# Get One Product
# -------------------------

@product_routes.get(
    "/{product_id}",
    response_model=ProductResponseSchema,
    summary="Get One Product"
)
async def get_one_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    return controller.get_one_product(product_id, db)



@product_routes.put(
    "/{product_id}",
    response_model=ProductResponseSchema,
    summary="Update Product"
)
async def update_product(

    product_id: int,

    body: ProductUpdateSchema,

    db: Session = Depends(get_db),

    current_user: Usermodel = Depends(get_current_admin)

):
    return controller.update_product(
        product_id,
        body,
        db
    )



@product_routes.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Product"
)
async def delete_product(

    product_id: int,

    db: Session = Depends(get_db),

    current_user: Usermodel = Depends(get_current_admin)

):
    return controller.delete_product(
        product_id,
        db
    )