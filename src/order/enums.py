from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class OrderSort(str, Enum):
    NEWEST = "newest"
    OLDEST = "oldest"
    HIGHEST = "highest"
    LOWEST = "lowest"