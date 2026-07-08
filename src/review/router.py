from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.review import controller, admin_service
from src.review.ditos import (
    CreateReviewSchema,
    UpdateReviewSchema,
    ReviewResponseSchema,
)
from src.user.models import Usermodel
from src.utils.db import get_db
from src.utils.helpers import (
    get_current_user,
    get_current_admin,
)

review_routes = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
)


# ============================================================
# User Routes
# ============================================================

@review_routes.post(
    "/product/{product_id}",
    response_model=ReviewResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create review",
    description="Create a review for a purchased product.",
)
async def create_review(
    product_id: int,
    body: CreateReviewSchema,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.create_review(
        product_id,
        body,
        db,
        current_user,
    )


@review_routes.patch(
    "/{review_id}",
    response_model=ReviewResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Update review",
    description="Update your own review.",
)
async def update_review(
    review_id: int,
    body: UpdateReviewSchema,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.update_review(
        review_id,
        body,
        db,
        current_user,
    )


@review_routes.delete(
    "/{review_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete review",
    description="Delete your own review.",
)
async def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.delete_review(
        review_id,
        db,
        current_user,
    )


@review_routes.get(
    "/me",
    response_model=List[ReviewResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="My reviews",
    description="Get all reviews created by the current user.",
)
async def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_user),
):
    return controller.get_my_reviews(
        db,
        current_user,
    )


@review_routes.get(
    "/product/{product_id}",
    response_model=List[ReviewResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="Product reviews",
    description="Get reviews of a product.",
)
async def get_product_reviews(
    product_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    return controller.get_product_reviews(
        product_id,
        db,
        skip,
        limit,
    )


@review_routes.get(
    "/product/{product_id}/rating",
    status_code=status.HTTP_200_OK,
    summary="Product rating",
    description="Get average rating and review count of a product.",
)
async def get_product_rating(
    product_id: int,
    db: Session = Depends(get_db),
):
    return controller.get_product_rating(
        product_id,
        db,
    )


# ============================================================
# Admin Routes
# ============================================================

@review_routes.get(
    "/admin/all",
    response_model=List[ReviewResponseSchema],
    status_code=status.HTTP_200_OK,
    summary="All reviews",
    description="Admin: Get all reviews.",
)
async def get_all_reviews(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_admin),
):
    return admin_service.get_all_reviews(
        db,
        current_user,
        skip,
        limit,
    )


@review_routes.get(
    "/admin/{review_id}",
    response_model=ReviewResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Get review",
    description="Admin: Get a single review.",
)
async def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_admin),
):
    return admin_service.get_review(
        review_id,
        db,
        current_user,
    )


@review_routes.delete(
    "/admin/{review_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete review",
    description="Admin: Delete any review.",
)
async def delete_review_admin(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: Usermodel = Depends(get_current_admin),
):
    return admin_service.delete_review(
        review_id,
        db,
        current_user,
    )