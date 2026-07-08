from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from fastapi import HTTPException, status

from src.review.models import ReviewModel
from src.user.models import Usermodel


def get_all_reviews(
    db: Session,
    current_user: Usermodel,
    skip: int = 0,
    limit: int = 20,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this resource.",
        )

    return (
        db.execute(
            select(ReviewModel)
            .options(
                joinedload(ReviewModel.user),
                joinedload(ReviewModel.product),
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


def get_review(
    review_id: int,
    db: Session,
    current_user: Usermodel,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this resource.",
        )

    review = (
        db.execute(
            select(ReviewModel)
            .options(
                joinedload(ReviewModel.user),
                joinedload(ReviewModel.product),
            )
            .where(
                ReviewModel.id == review_id,
            )
        )
        .unique()
        .scalar_one_or_none()
    )

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found.",
        )

    return review


def delete_review(
    review_id: int,
    db: Session,
    current_user: Usermodel,
):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can access this resource.",
        )

    review = db.get(ReviewModel, review_id)

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found.",
        )

    db.delete(review)
    db.commit()

    return {
        "message": "Review deleted successfully."
    }