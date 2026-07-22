from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from src.category.ditos import CategorySimpleResponseSchema


# -------------------------
# Create Product
# -------------------------

class ProductCreateSchema(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        examples=["Nike Air Max"],
        description="Product name",
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
        examples=["Premium running shoes with Air cushioning."],
        description="Detailed product description",
    )

    price: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
        examples=[999.99],
        description="Product price",
    )

    stock: int = Field(
        ...,
        ge=0,
        examples=[50],
        description="Available stock quantity",
    )

    image_url: str | None = Field(
    default=None,
    max_length=500,
    description="Product image URL",
    )


    brand: str | None = Field(
        default=None,
        max_length=100,
        examples=["Nike"],
        description="Product brand",
    )


# -------------------------
# Update Product
# -------------------------

class ProductUpdateSchema(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
        examples=["Nike Air Max"],
        description="Product name",
    )

    description: str | None = Field(
        default=None,
        max_length=2000,
        examples=["Premium running shoes with Air cushioning."],
        description="Detailed product description",
    )

    price: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=10,
        decimal_places=2,
        examples=[999.99],
        description="Product price",
    )

    stock: int | None = Field(
        default=None,
        ge=0,
        examples=[50],
        description="Available stock quantity",
    )

    image_url: str | None = Field(
    default=None,
    max_length=500,
    description="Product image URL",
)

    category_id: int | None = Field(
        default=None,
        gt=0,
        examples=[1],
        description="Category ID",
    )

    is_active: bool | None = Field(
        default=None,
        description="Whether the product is active",
    )

    brand: str | None = Field(
        default=None,
        max_length=100,
        examples=["Nike"],
        description="Product brand",
    )

    sku: str | None = Field(
        default=None,
        description="Product SKU",
    )


# -------------------------
# Product Response
# -------------------------

class ProductResponseSchema(BaseModel):
    id: int

    name: str = Field(
        ...,
        description="Product name",
        examples=["Nike Air Max"],
    )

    description: str | None = Field(
        default=None,
        description="Detailed product description",
    )

    price: Decimal = Field(
        ...,
        gt=0,
        max_digits=10,
        decimal_places=2,
        examples=[999.99],
        description="Product price",
    )

    stock: int = Field(
        ...,
        ge=0,
        description="Available stock",
    )

    image_url: str | None = Field(
        default=None,
        max_length=500,
        description="Product image URL",
    )

    is_active: bool = Field(
        ...,
        description="Whether the product is active",
    )

    category: CategorySimpleResponseSchema

    created_at: datetime
    updated_at: datetime

    brand: str | None = Field(
        default=None,
        description="Product brand",
    )


    sku: str = Field(
        ...,
        description="Product SKU",
    )

    average_rating: float = Field(
        default=0.0,
        ge=0,
        le=5,
        description="Average customer rating",
        examples=[4.8],
    )

    review_count: int = Field(
        default=0,
        ge=0,
        description="Total number of reviews",
        examples=[128],
    )

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Low Stock Response
# -------------------------

class LowStockProductSchema(BaseModel):
    id: int

    name: str = Field(
        ...,
        description="Product name",
    )

    sku: str = Field(
        ...,
        description="Product SKU",
    )

    stock: int = Field(
        ...,
        ge=0,
        description="Remaining stock",
    )

    brand: str | None = Field(
        default=None,
        description="Product brand",
    )

    model_config = ConfigDict(from_attributes=True)


# -------------------------
# Product Statistics
# -------------------------

class ProductStatisticsSchema(BaseModel):
    total_products: int = Field(
        ...,
        ge=0,
        description="Total number of products",
    )

    active_products: int = Field(
        ...,
        ge=0,
        description="Total active products",
    )

    inactive_products: int = Field(
        ...,
        ge=0,
        description="Total inactive products",
    )

    out_of_stock: int = Field(
        ...,
        ge=0,
        description="Products currently out of stock",
    )

    low_stock: int = Field(
        ...,
        ge=0,
        description="Products with low stock",
    )