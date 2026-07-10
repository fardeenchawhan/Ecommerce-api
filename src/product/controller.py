
from decimal import Decimal
from src.product.enums import ProductSortEnum

from fastapi import HTTPException, status
from sqlalchemy import select ,func
from sqlalchemy.orm import Session, selectinload

from src.product.models import ProductModel
from src.utils.pagination import paginate
from src.product.helper import generate_sku
from src.product.helper import generate_sku
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


from src.product.helper import generate_sku


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



