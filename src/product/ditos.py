from decimal import Decimal
from datetime import datetime
from typing import Optional
from typing import List
from src.category.ditos import CategorySimpleResponseSchema

from pydantic import BaseModel, ConfigDict,Field


class ProductCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal = Field(
    ...,
    gt=0,
    max_digits=10,
    decimal_places=2,
    examples=[999.99],
    description="Product price"
)
    stock: int
    image_url: Optional[str] = None
    category_id: int
    brand: str | None = None


class ProductUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None
    brand: str | None = None
    sku: str | None = None


class ProductResponseSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal = Field(
    ...,
    gt=0,
    max_digits=10,
    decimal_places=2,
    examples=[999.99],
    description="Product price"
)
    stock: int
    image_url: Optional[str]
    is_active: bool
    category: CategorySimpleResponseSchema
    created_at: datetime
    updated_at: datetime
    brand:str | None
    sku: str
    average_rating: float = 0.0
    review_count: int = 0

    model_config = ConfigDict(from_attributes=True)



class ProductListResponseSchema(BaseModel):
    items: List[ProductResponseSchema]
    page: int
    limit: int
    total: int
    total_pages: int





class LowStockProductSchema(BaseModel):
    id: int
    name: str
    sku: str
    stock: int
    brand: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ProductStatisticsSchema(BaseModel):
    total_products: int
    active_products: int
    inactive_products: int
    out_of_stock: int
    low_stock: int