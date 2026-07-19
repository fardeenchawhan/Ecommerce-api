from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.product.ditos import ProductResponseSchema
from src.user.ditos import PublicUserResponseSchema


# -------------------------
# Create Review
# -------------------------

class CreateReviewSchema(BaseModel):
    rating: int = Field(
        ...,
        ge=1,
        le=5,
        examples=[5],
        description="Rating between 1 and 5",
    )

    comment: str | None = Field(
        default=None,
        max_length=1000,
        examples=["Excellent product. Highly recommended."],
        description="Review comment",
    )


# -------------------------
# Update Review
# -------------------------

class UpdateReviewSchema(BaseModel):
    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
        examples=[4],
        description="Updated rating",
    )

    comment: str | None = Field(
        default=None,
        max_length=1000,
        examples=["Still good after one month of use."],
        description="Updated review comment",
    )


# -------------------------
# Review Response
# -------------------------

class ReviewResponseSchema(BaseModel):
    id: int = Field(
        ...,
        description="Review ID",
    )

    rating: int = Field(
        ...,
        ge=1,
        le=5,
        description="Review rating",
    )

    comment: str | None = Field(
        default=None,
        description="Review comment",
    )

    created_at: datetime

    updated_at: datetime

    user: PublicUserResponseSchema

    product: ProductResponseSchema

    model_config = ConfigDict(from_attributes=True)