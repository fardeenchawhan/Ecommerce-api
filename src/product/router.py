from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.product import controller
from src.product.ditos import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductResponseSchema
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
    response_model=List[ProductResponseSchema],
    summary="Get All Products"
)
async def get_all_products(
    db: Session = Depends(get_db)
):
    return controller.get_all_products(db)


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