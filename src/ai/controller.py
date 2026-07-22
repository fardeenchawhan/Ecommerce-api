from src.ai.service import parse_search_query
from src.category.models import CategoryModel
from sqlalchemy import select

from src.category.models import CategoryModel
from src.product import controller as product_controller
from src.product.enums import ProductSortEnum


def ai_search(query: str,db):

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

    return product_controller.get_all_products(
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