from typing import List

from fastapi import APIRouter, Depends, status,Query
from sqlalchemy.orm import Session
from src.utils.schemas import PaginatedResponse
from src.product.enums import ProductSortEnum
from decimal import Decimal
from src.product import controller
from src.product import admin_service

from src.product import controller
from src.product.ditos import ( ProductCreateSchema,ProductUpdateSchema,ProductResponseSchema,ProductStatisticsSchema,LowStockProductSchema)
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
    return admin_service.create_product(body, db,current_user)


# -------------------------
# Get All Products
# -------------------------

@product_routes.get(
    "",
    response_model=PaginatedResponse[ProductResponseSchema],
    summary="Get all products"
)
async def get_all_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    category_id: int | None = None,
    search: str | None = None,
    min_price: Decimal | None = Query(None, ge=0),
    max_price: Decimal | None = Query(None, ge=0),
    in_stock: bool | None = None,
    sort: ProductSortEnum = ProductSortEnum.newest,
    db: Session = Depends(get_db),
):
    return controller.get_all_products(
        db=db,
        page=page,
        limit=limit,
        category_id=category_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        sort=sort,
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
    return admin_service.update_product(
        product_id,
        body,
        db,
        current_user
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
    return admin_service.delete_product(
        product_id,
        db,
        current_user
    )



@product_routes.get(
    "/admin/low-stock",
    response_model=List[LowStockProductSchema],
    summary="Low Stock Products",
)
async def get_low_stock_products(
    threshold: int = Query(
        default=5,
        ge=1,
    ),
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_admin),
):
    return admin_service.get_low_stock_products(
        db=db,
        current_user=current_user,
        threshold=threshold,
    )


@product_routes.get(
    "/admin/statistics",
    response_model=ProductStatisticsSchema,
    summary="Product Statistics",
)
async def get_product_statistics(
    threshold: int = Query(
        default=5,
        ge=1,
    ),
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_admin),
):
    return admin_service.get_product_statistics(
        db=db,
        current_user=current_user,
        threshold=threshold,
    )