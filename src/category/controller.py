from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.category.models import CategoryModel
from src.category.ditos import CategoryCreateSchema, CategoryUpdateSchema
from src.user.models import Usermodel


def create_category(
    body: CategoryCreateSchema,
    db: Session,
    current_user: Usermodel
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create categories"
        )

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

    return new_category


def get_all_categories(db: Session):
    result = db.execute(select(CategoryModel))
    categories = result.scalars().all()
    return categories


def get_one_category(category_id: int, db: Session):
    category = db.get(CategoryModel, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


def update_category(
    category_id: int,
    body: CategoryUpdateSchema,
    db: Session,
    current_user: Usermodel
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can update categories"
        )

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

    return category


def delete_category(
    category_id: int,
    db: Session,
    current_user: Usermodel
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete categories"
        )

    category = db.get(CategoryModel, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    db.delete(category)
    db.commit()

    return None