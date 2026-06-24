from pydantic import BaseModel
from typing import Optional


class CategoryCreateSchema(BaseModel):
    name: str


class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = None


class CategoryResponseSchema(BaseModel):
    id: int
    name: str

    model_config = {
        "from_attributes": True
    }