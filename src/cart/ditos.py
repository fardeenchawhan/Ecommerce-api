from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from src.product.ditos import ProductResponseSchema


# -------------------------
# Request Schemas
# -------------------------

class AddToCartSchema(BaseModel):
    product_id: int = Field(
        ...,
        gt=0,
        examples=[1],
        description="Product ID",
    )

    quantity: int = Field(
        ...,
        ge=1,
        examples=[2],
        description="Quantity to add",
    )


class UpdateCartSchema(BaseModel):
    quantity: int = Field(
        ...,
        ge=1,
        examples=[3],
        description="Updated quantity",
    )


# -------------------------
# Response Schemas
# -------------------------

class CartItemResponseSchema(BaseModel):
    id: int = Field(
        ...,
        description="Cart item ID",
    )

    quantity: int = Field(
        ...,
        ge=1,
        description="Quantity of this product",
    )

    product: ProductResponseSchema

    subtotal: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=2,
        examples=[1999.98],
        description="Subtotal for this cart item",
    )

    model_config = ConfigDict(from_attributes=True)


class CartResponseSchema(BaseModel):
    items: list[CartItemResponseSchema]

    total_items: int = Field(
        ...,
        ge=0,
        description="Total quantity of items in cart",
        examples=[4],
    )

    subtotal: Decimal = Field(
        ...,
        ge=0,
        max_digits=10,
        decimal_places=2,
        examples=[5499.97],
        description="Cart subtotal",
    )