from sqlalchemy.orm import Session
from sqlalchemy import select
from fastapi import HTTPException, status

from src.product.models import ProductModel
from src.product.ditos import (
    ProductCreateSchema,
    ProductUpdateSchema
)
from src.category.models import CategoryModel


# -------------------------
# Create Product
# -------------------------

def create_product(
    body: ProductCreateSchema,
    db: Session,
):
    # check category exists
    category = db.execute(
        select(CategoryModel).where(
            CategoryModel.id == body.category_id
        )
    ).scalar_one_or_none()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    # check duplicate product name
    existing_product = db.execute(
        select(ProductModel).where(
            ProductModel.name == body.name
        )
    ).scalar_one_or_none()

    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product already exists"
        )

    new_product = ProductModel(
        name=body.name,
        description=body.description,
        price=body.price,
        stock=body.stock,
        image_url=body.image_url,
        category_id=body.category_id
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# -------------------------
# Get All Products
# -------------------------

def get_all_products(db: Session):

    products = db.execute(
        select(ProductModel).where(
            ProductModel.is_active == True
        )
    ).scalars().all()

    return products


# -------------------------
# Get One Product
# -------------------------

def get_one_product(
    product_id: int,
    db: Session
):

    product = db.get(ProductModel, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


def update_product(
    product_id: int,
    body: ProductUpdateSchema,
    db: Session
):

    product = db.get(ProductModel, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    data = body.model_dump(exclude_unset=True)

    # validate category
    if "category_id" in data:

        category = db.get(CategoryModel, data["category_id"])

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )

    # duplicate product name check
    if "name" in data:

        existing = db.execute(
            select(ProductModel).where(
                ProductModel.name == data["name"],
                ProductModel.id != product_id
            )
        ).scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product already exists"
            )

    for field, value in data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product



def delete_product(
    product_id: int,
    db: Session
):

    product = db.get(ProductModel, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product already deleted"
        )

    product.is_active = False

    db.commit()

    return None