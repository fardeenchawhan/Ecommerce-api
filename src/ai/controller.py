from src.ai.service import parse_search_query,rewrite_search
from src.category.models import CategoryModel
from sqlalchemy import select

from src.category.models import CategoryModel
from src.product import controller as product_controller
from src.product.enums import ProductSortEnum
from sqlalchemy import select
from sqlalchemy.orm import Session





def _search_products(
    db: Session,
    query: str,
):
    filters = parse_search_query(
        db,
        query,
    )

    category_id = None

    if filters.category:

        category = (
            db.execute(
                select(CategoryModel).where(
                    CategoryModel.name.ilike(filters.category)
                )
            )
            .scalar_one_or_none()
        )

        if category:
            category_id = category.id

    results = product_controller.get_all_products(
        db=db,
        page=1,
        limit=10,
        category_id=category_id,
        brand=filters.brand,
        search=filters.keywords,
        min_price=filters.min_price,
        max_price=filters.max_price,
        in_stock=True,
        sort=ProductSortEnum.newest,
    )

    return results


def ai_search(
    query: str,
    db: Session,
):

    results = _search_products(
        db,
        query,
    )

    if results["total"] == 0:

        rewritten = rewrite_search(query)


        results = _search_products(
            db,
            rewritten,
        )

    return results