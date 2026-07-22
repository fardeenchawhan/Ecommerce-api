
from decimal import Decimal
from src.product.enums import ProductSortEnum

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select ,func
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import or_ , and_
from src.product.models import ProductModel
from src.utils.pagination import paginate
from src.product.helper import generate_sku
from src.product.helper import generate_sku
from src.review.models import ReviewModel
import json
from src.cache.service import get_cache, set_cache
from src.cache.constants import PRODUCT_CACHE

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
    brand: str | None = None,
    search: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
    in_stock: bool | None = None,
    sort: ProductSortEnum = ProductSortEnum.newest,
):
    
    cache_key = (
    f"products:"
    f"{page}:"
    f"{limit}:"
    f"{category_id}:"
    f"{brand}:"
    f"{search}:"
    f"{min_price}:"
    f"{max_price}:"
    f"{in_stock}:"
    f"{sort.value}"
    )

    cached = get_cache(cache_key)

    if cached:
        return cached
    
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

    if brand:
        query = query.where(
            ProductModel.brand.ilike(f"%{brand}%")
        )

    if search:

        words = search.split()

        conditions = []

        for word in words:

            conditions.append(
                or_(
                    ProductModel.name.ilike(f"%{word}%"),
                    ProductModel.description.ilike(f"%{word}%"),
                    ProductModel.brand.ilike(f"%{word}%"),
                    ProductModel.tags.ilike(f"%{word}%"),
                )
            )

        query = query.where(and_(*conditions))

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

    encoded = jsonable_encoder(result)

    set_cache(
        cache_key,
        encoded,
        PRODUCT_CACHE,
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



