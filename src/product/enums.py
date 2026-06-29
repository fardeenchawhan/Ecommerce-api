from enum import Enum


class ProductSortEnum(str, Enum):
    newest = "newest"
    oldest = "oldest"
    price_low = "price_low"
    price_high = "price_high"
    name_asc = "name_asc"
    name_desc = "name_desc"