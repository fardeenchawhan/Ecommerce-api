
from decimal import Decimal
from src.product.enums import ProductSortEnum

from fastapi import HTTPException, status
from sqlalchemy import select ,func
from sqlalchemy.orm import Session, selectinload

from src.category.models import CategoryModel
from src.product.ditos import ProductCreateSchema, ProductUpdateSchema
from src.product.models import ProductModel
from src.user.models import Usermodel
from src.utils.pagination import paginate

from src.review.models import ReviewModel

def attach_review_stats(
    db: Session,
    products: list[ProductModel],
):
    if not products:
        return products

    product_ids = [product.id for product in products]

    review_stats = (
        db.execute(
            select(
                ReviewModel.product_id,
                func.avg(ReviewModel.rating),
                func.count(ReviewModel.id),
            )
            .where(
                ReviewModel.product_id.in_(product_ids)
            )
            .group_by(
                ReviewModel.product_id
            )
        )
        .all()
    )

    stats = {
        product_id: (
            round(float(avg_rating), 2),
            review_count,
        )
        for product_id, avg_rating, review_count in review_stats
    }

    for product in products:
        average_rating, review_count = stats.get(
            product.id,
            (0.0, 0),
        )

        product.average_rating = average_rating
        product.review_count = review_count

    return products


def create_product(
    body: ProductCreateSchema,
    db: Session,
    current_user: Usermodel,
):
    existing_sku = db.execute(
            select(ProductModel).where(
                ProductModel.sku == body.sku
            )
        ).scalar_one_or_none()

    if existing_sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists."
        )

    category = db.get(CategoryModel, body.category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    product = ProductModel(**body.model_dump())

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def get_all_products(
    db: Session,
    page: int = 1,
    limit: int = 10,
    category_id: int | None = None,
    search: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    in_stock: bool | None = None,
    sort: ProductSortEnum = ProductSortEnum.newest,
):
    query = (
        select(ProductModel)
        .options(
            selectinload(ProductModel.category)
        )
        .where(ProductModel.is_active == True)
    )

    if category_id is not None:
        query = query.where(
            ProductModel.category_id == category_id
        )

    if search:
        query = query.where(
            ProductModel.name.ilike(f"%{search}%")
        )

    if min_price is not None:
        query = query.where(
            ProductModel.price >= min_price
        )

    if max_price is not None:
        query = query.where(
            ProductModel.price <= max_price
        )

    if in_stock:
        query = query.where(
            ProductModel.stock > 0
        )

    if sort == ProductSortEnum.price_low:
        query = query.order_by(ProductModel.price.asc())

    elif sort == ProductSortEnum.price_high:
        query = query.order_by(ProductModel.price.desc())

    elif sort == ProductSortEnum.name_asc:
        query = query.order_by(ProductModel.name.asc())

    elif sort == ProductSortEnum.name_desc:
        query = query.order_by(ProductModel.name.desc())

    elif sort == ProductSortEnum.oldest:
        query = query.order_by(ProductModel.created_at.asc())

    else:
        query = query.order_by(ProductModel.created_at.desc())

    result= paginate(
        db=db,
        query=query,
        page=page,
        limit=limit,
    )

    result["items"]= attach_review_stats(
        db,
        result["items"],
    )

    return result




def get_one_product(
    product_id: int,
    db: Session,
):
    product = db.execute(
        select(ProductModel)
        .options(
            selectinload(ProductModel.category)
        )
        .where(
            ProductModel.id == product_id,
            ProductModel.is_active == True
        )
    ).scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    
    attach_review_stats(
        db,
        [product]
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
            detail="Product not found."
        )
    existing_sku=None
    update_data = body.model_dump(exclude_unset=True)
    if "sku" in update_data:
        existing_sku = db.execute(
            select(ProductModel).where(
                ProductModel.sku == update_data["sku"],
                ProductModel.id != product.id
            )
        ).scalar_one_or_none()

    if existing_sku:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SKU already exists."
        )

    if "category_id" in update_data:
        category = db.get(CategoryModel, update_data["category_id"])

        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found."
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


def delete_product(
    product_id: int,
    db: Session,
    current_user: Usermodel,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete products."
        )

    product = db.get(ProductModel, product_id)

    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    product.is_active = False

    db.commit()

    return None