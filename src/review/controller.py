from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from fastapi import HTTPException, status

from src.order.enums import OrderStatus
from src.order.models import OrderItemModel, OrderModel
from src.product.models import ProductModel
from src.review.ditos import (
    CreateReviewSchema,
    UpdateReviewSchema,
)
from src.review.models import ReviewModel
from src.user.models import Usermodel


def create_review(
    product_id: int,
    body: CreateReviewSchema,
    db: Session,
    current_user: Usermodel,
):
    product = db.get(ProductModel, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    purchased = (
        db.execute(
            select(OrderItemModel)
            .join(OrderModel)
            .where(
                OrderModel.user_id == current_user.id,
                (OrderModel.status == OrderStatus.DELIVERED) | (OrderModel.status == OrderStatus.CANCELLED),
                OrderItemModel.product_id == product_id
            )
        )
        .scalars()
        .first()
    )

    if not purchased:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only review products you have purchased.",
        )

    existing_review = (
        db.execute(
            select(ReviewModel).where(
                ReviewModel.user_id == current_user.id,
                ReviewModel.product_id == product_id,
            )
        )
        .scalars()
        .first()
    )

    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product.",
        )

    review = ReviewModel(
        rating=body.rating,
        comment=body.comment,
        user_id=current_user.id,
        product_id=product_id,
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return (
        db.execute(
            select(ReviewModel)
            .options(
                joinedload(ReviewModel.user),
                joinedload(ReviewModel.product),
            )
            .where(ReviewModel.id == review.id)
        )
        .unique()
        .scalar_one()
    )


def update_review(
    review_id: int,
    body: UpdateReviewSchema,
    db: Session,
    current_user: Usermodel,
):
    review = db.get(ReviewModel, review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found.",
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own review.",
        )

    data = body.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(review, key, value)

    db.commit()
    db.refresh(review)

    return (
        db.execute(
            select(ReviewModel)
            .options(
                joinedload(ReviewModel.user),
                joinedload(ReviewModel.product),
            )
            .where(ReviewModel.id == review.id)
        )
        .unique()
        .scalar_one()
    )


def delete_review(
    review_id: int,
    db: Session,
    current_user: Usermodel,
):
    review = db.get(ReviewModel, review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found.",
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own review.",
        )

    db.delete(review)
    db.commit()

    return {
        "message": "Review deleted successfully."
    }


def get_my_reviews(
    db: Session,
    current_user: Usermodel,
):
    return (
        db.execute(
            select(ReviewModel)
            .options(
                joinedload(ReviewModel.product),
                joinedload(ReviewModel.user),
            )
            .where(
                ReviewModel.user_id == current_user.id,
            )
            .order_by(
                ReviewModel.created_at.desc()
            )
        )
        .unique()
        .scalars()
        .all()
    )


def get_product_reviews(
    product_id: int,
    db: Session,
    skip: int = 0,
    limit: int = 10,
):
    return (
        db.execute(
            select(ReviewModel)
            .options(
                joinedload(ReviewModel.user),
            )
            .where(
                ReviewModel.product_id == product_id,
            )
            .order_by(
                ReviewModel.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )
        .unique()
        .scalars()
        .all()
    )


def get_product_rating(
    product_id: int,
    db: Session,
):
    average_rating, total_reviews = db.execute(
        select(
            func.coalesce(
                func.avg(ReviewModel.rating),
                0,
            ),
            func.count(ReviewModel.id),
        )
        .where(
            ReviewModel.product_id == product_id,
        )
    ).one()

    return {
        "average_rating": round(float(average_rating), 2),
        "total_reviews": total_reviews,
    }