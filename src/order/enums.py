from enum import Enum

import enum
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

class PaymentStatus(str,enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    FAILED = "FAILED"
    REFUNDED = "REFUNDED"