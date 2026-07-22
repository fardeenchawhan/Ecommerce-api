from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from src.category.models import CategoryModel
from src.product.ditos import ProductCreateSchema, ProductUpdateSchema
from src.product.helper import generate_sku
from src.product.models import ProductModel
from src.user.models import Usermodel
from src.utils.logger import logger
from src.cache.service import delete_pattern
from src.ai.product_ai import generate_product_metadata
from sqlalchemy.exc import SQLAlchemyError

def create_product(
    body: ProductCreateSchema,
    db: Session,
    current_user: Usermodel,
):
    
    # -----------------------------
    # Duplication check
    # -----------------------------
    
    normalized_name = body.name.strip().lower()
    normalized_brand = (body.brand or "").strip().lower()


    existing = (
    db.execute(
        select(ProductModel.id).where(
            func.lower(ProductModel.name) == normalized_name,
            func.lower(ProductModel.brand) == normalized_brand,
        ).limit(1)
    )
    .scalar()
)

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product already exists."
        )
    # -----------------------------
    # Generate AI Metadata
    # -----------------------------
    metadata = generate_product_metadata(
        db=db,
        name=body.name,
        description=body.description or "",
        brand=body.brand,
    )

    # -----------------------------
    # Generate Unique SKU
    # -----------------------------
    while True:
        sku = generate_sku(
            category_name=metadata.category,
            brand=body.brand or "GENERIC",
        )

        existing_sku = (
            db.execute(
                select(ProductModel).where(
                    ProductModel.sku == sku
                )
            )
            .scalar_one_or_none()
        )

        if existing_sku is None:
            break

    # -----------------------------
    # Prepare Product Data
    # -----------------------------
    data = body.model_dump()

    data["category_id"] = metadata.category_id
    data["tags"] = ",".join(metadata.tags)

    # -----------------------------
    # Create Product
    # -----------------------------
    product = ProductModel(
        **data,
        sku=sku,
    )


    db.add(product)
    db.commit()
    db.refresh(product)

    # -----------------------------
    # Clear Product Cache
    # -----------------------------
    delete_pattern("products:*")

    logger.info(
        f"Admin {current_user.id} created product {product.id}"
    )

    return product


def update_product(
    product_id: int,
    body: ProductUpdateSchema,
    db: Session,
    current_user: Usermodel,
):
    product = db.get(ProductModel, product_id)

    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    update_data = body.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        category = db.get(
            CategoryModel,
            update_data["category_id"],
        )

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found.",
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    delete_pattern("products:*")

    return product


def delete_product(
    product_id: int,
    db: Session,
    current_user: Usermodel,
):
    product = db.get(ProductModel, product_id)

    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found.",
        )

    product.is_active = False

    db.commit()

    delete_pattern("products:*")

    return None


def get_low_stock_products(
    db: Session,
    current_user: Usermodel,
    threshold: int = 5,
):
    return (
        db.execute(
            select(ProductModel)
            .where(
                ProductModel.is_active == True,
                ProductModel.stock <= threshold,
            )
            .order_by(ProductModel.stock.asc())
        )
        .scalars()
        .all()
    )


def get_product_statistics(
    db: Session,
    current_user: Usermodel,
    threshold: int = 5,
):
    total_products = db.scalar(
        select(func.count()).select_from(ProductModel)
    )

    active_products = db.scalar(
        select(func.count())
        .select_from(ProductModel)
        .where(ProductModel.is_active == True)
    )

    inactive_products = db.scalar(
        select(func.count())
        .select_from(ProductModel)
        .where(ProductModel.is_active == False)
    )

    out_of_stock = db.scalar(
        select(func.count())
        .select_from(ProductModel)
        .where(
            ProductModel.is_active == True,
            ProductModel.stock == 0,
        )
    )

    low_stock = db.scalar(
        select(func.count())
        .select_from(ProductModel)
        .where(
            ProductModel.is_active == True,
            ProductModel.stock <= threshold
        )
    )

    return {
        "total_products": total_products,
        "active_products": active_products,
        "inactive_products": inactive_products,
        "out_of_stock": out_of_stock,
        "low_stock": low_stock,
    }
