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
    status_code=status.HTTP_201_CREATED,
    summary="Create Product",
description="Creates a new product. Admin only."
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
     response_model_exclude={
        "items": {
            "__all__": {
                "stock",
                "sku",
                "is_active",
            }
        }
    },
    summary="Browse Products",
description="Returns paginated products with filtering, searching, and sorting."
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
    response_model_exclude={
        "stock",
        "is_active",
    },
    summary="Get Product",
description="Returns detailed information about a specific product."
)
async def get_one_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    return controller.get_one_product(product_id, db)



@product_routes.put(
    "/{product_id}",
    response_model=ProductResponseSchema,
    summary="Update Product",
description="Updates an existing product. Admin only."
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
    summary="Delete Product",
description="Deletes a product. Admin only."
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
description="Returns products with low inventory. Admin only."
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
description="Returns product inventory statistics. Admin only."
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