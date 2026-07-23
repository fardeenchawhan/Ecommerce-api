from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.category import controller
from src.category.ditos import (
    CategoryCreateSchema,
    CategoryUpdateSchema,
    CategoryResponseSchema
)
from src.utils.db import get_db
from src.utils.helpers import get_current_user,get_current_admin
from src.user.models import Usermodel


category_routes = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@category_routes.post(
    "",
    response_model=CategoryResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create Category",
    description="Creates a new product category. Admin only."
)
async def create_category(
    body: CategoryCreateSchema,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
    current_admin: Usermodel = Depends(get_current_admin)
):
    return controller.create_category(body, db, current_user,current_admin)


@category_routes.get(
    "",
    response_model=List[CategoryResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Get Categories",
    description="Returns all available product categories."
)
async def get_all_categories(
    db: Session = Depends(get_db),
    search: str | None = None
):
    return controller.get_all_categories(db,search)


@category_routes.get(
    "/{category_id}",
    response_model=CategoryResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get Category",
    description="Returns details of a specific category."
)
async def get_one_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    return controller.get_one_category(category_id, db)


@category_routes.put(
    "/{category_id}",
    response_model=CategoryResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update Category",
    description="Updates an existing category. Admin only."
)
async def update_category(
    category_id: int,
    body: CategoryUpdateSchema,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
    current_admin: Usermodel = Depends(get_current_admin)
):
    return controller.update_category(category_id, body, db, current_user,current_admin)


@category_routes.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Category",
    description="Deletes a category. Admin only."
)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
    current_admin: Usermodel = Depends(get_current_admin)
):
    return controller.delete_category(category_id, db, current_user,current_admin)

