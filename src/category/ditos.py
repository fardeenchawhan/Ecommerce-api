from typing import Optional

from pydantic import BaseModel, Field


class CategoryCreateSchema(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Electronics"],
        description="Category name",
    )


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        examples=["Fashion"],
        description="Updated category name",
    )


class CategorySimpleResponseSchema(BaseModel):
    id: int

    name: str = Field(
        ...,
        examples=["Electronics"],
        description="Category name",
    )

    model_config = {
        "from_attributes": True
    }


class CategoryResponseSchema(BaseModel):
    id: int

    name: str = Field(
        ...,
        examples=["Electronics"],
        description="Category name",
    )

    product_count: int = Field(
        default=None,
        ge=0,
        description="Total active products in this category",
        examples=[12],
    )

    model_config = {
        "from_attributes": True
    }