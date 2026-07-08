from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.product.ditos import ProductResponseSchema
from src.user.ditos import UserResponseSchema


class CreateReviewSchema(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str | None = Field(
        default=None,
        max_length=1000,
    )


class UpdateReviewSchema(BaseModel):
    rating: int | None = Field(
        default=None,
        ge=1,
        le=5,
    )

    comment: str | None = Field(
        default=None,
        max_length=1000,
    )


class ReviewResponseSchema(BaseModel):
    id: int
    rating: int
    comment: str | None

    created_at: datetime
    updated_at: datetime

    user: UserResponseSchema
    product: ProductResponseSchema

    model_config = ConfigDict(from_attributes=True)