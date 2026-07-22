from decimal import Decimal

from pydantic import BaseModel


class ProductSearchFilterSchema(BaseModel):
    brand: str | None = None

    category: str | None = None

    keywords: str | None = None

    min_price: Decimal | None = None

    max_price: Decimal | None = None



class ProductMetadataSchema(BaseModel):
    category: str
    category_id: int
    tags: list[str]