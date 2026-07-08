from pydantic import BaseModel
from typing import Optional


class CategoryCreateSchema(BaseModel):
    name: str


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = None


class CategorySimpleResponseSchema(BaseModel):
    id: int
    name: str


class CategoryResponseSchema(BaseModel):
    id: int
    name: str
    product_count: int

    model_config = {
        "from_attributes": True
    }