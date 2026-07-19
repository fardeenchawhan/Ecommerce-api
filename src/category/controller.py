from fastapi import HTTPException, status
from sqlalchemy import select,func
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder
from src.product.models import ProductModel
from src.cache.service import get_cache,set_cache,delete_pattern
from src.cache.constants import CATEGORY_CACHE
from src.category.models import CategoryModel
from src.category.ditos import CategoryCreateSchema, CategoryUpdateSchema
from src.user.models import Usermodel


def create_category(
    body: CategoryCreateSchema,
    db: Session,
    current_user: Usermodel,
    current_admin:Usermodel
):

    existing_category = db.execute(
        select(CategoryModel).where(CategoryModel.name == body.name)
    ).scalar_one_or_none()

    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )

    new_category = CategoryModel(name=body.name)

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    delete_pattern("products:*")
    delete_pattern("categories*")

    return new_category



def get_all_categories(
    db: Session,
    search: str | None = None,
):
    
    cache_key = "categories"

    cached = get_cache(cache_key)

    if cached:
        print("✅ Categories served from Redis")
        return cached
    
    query = (
        select(
            CategoryModel,
            func.count(ProductModel.id).label("product_count")
        )
        .outerjoin(
            ProductModel,
            ProductModel.category_id == CategoryModel.id
        )
        .group_by(CategoryModel.id)
        .order_by(CategoryModel.name.asc())
    )

    if search:
        query = query.where(
            CategoryModel.name.ilike(f"%{search}%")
        )

    result = db.execute(query).all()

    categories = []

    for category, product_count in result:
        category.product_count = product_count
        categories.append(category)

    set_cache(
    cache_key,
    categories,
    CATEGORY_CACHE,
    )
    return categories


def get_one_category(
    category_id: int,
    db: Session,
):
    result = db.execute(
        select(
            CategoryModel,
            func.count(ProductModel.id).label("product_count")
        )
        .outerjoin(
            ProductModel,
            ProductModel.category_id == CategoryModel.id
        )
        .where(
            CategoryModel.id == category_id
        )
        .group_by(CategoryModel.id)
    ).first()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    category, product_count = result

    category.product_count = product_count

    return category

def update_category(
    category_id: int,
    body: CategoryUpdateSchema,
    db: Session,
    current_user: Usermodel,
    current_admin:Usermodel
):


    category = db.get(CategoryModel, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    update_data = body.model_dump(exclude_unset=True)

    if "name" in update_data:
        existing_category = db.execute(
            select(CategoryModel).where(
                CategoryModel.name == update_data["name"],
                CategoryModel.id != category_id
            )
        ).scalar_one_or_none()

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )

    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)

    delete_pattern("products:*")
    delete_pattern("categories*")

    return category


def delete_category(
    category_id: int,
    db: Session,
    current_user: Usermodel,
    current_admin:Usermodel
):

    category = db.get(CategoryModel, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    db.delete(category)
    db.commit()

    delete_pattern("products:*")
    delete_pattern("categories*")

    return None