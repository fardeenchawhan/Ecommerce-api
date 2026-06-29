from decimal import Decimal
from pydantic import BaseModel, Field

from src.product.ditos import ProductResponseSchema


# ---------- Request Schemas ----------

class AddToCartSchema(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1)


class UpdateCartSchema(BaseModel):
    quantity: int = Field(..., ge=1)


# ---------- Response Schemas ----------

class CartItemResponseSchema(BaseModel):
    id: int
    quantity: int
    product: ProductResponseSchema
    subtotal: Decimal

    model_config = {
        "from_attributes": True
    }


class CartResponseSchema(BaseModel):
    items: list[CartItemResponseSchema]
    total_items: int
    subtotal: Decimal