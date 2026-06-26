from decimal import Decimal
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ProductCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    image_url: Optional[str] = None
    category_id: int


class ProductUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    stock: Optional[int] = None
    image_url: Optional[str] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponseSchema(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    stock: int
    image_url: Optional[str]
    is_active: bool
    category_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)