from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, UniqueConstraint,DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.utils.db import Base


class CartItemModel(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "product_id",
            name="uq_cart_user_product"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    quantity: Mapped[int] = mapped_column(
        nullable=False,
        default=1
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    user = relationship(
        "Usermodel",
        back_populates="cart_items"
    )

    product = relationship(
        "ProductModel",
        back_populates="cart_items"
    )
















#     {
#   "items": [
#     {
#       "id": 7,
#       "name": "Hydro Flask Bottle",
#       "description": "insulated stainless steel water bottle",
#       "price": "500.00",
#       "stock": 20,
#       "image_url": "https://plus.unsplash.com/premium_photo-1678099940967-73fe30680949?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8d2lyZWxlc3MlMjBoZWFkcGhvbmVzfGVufDB8fDB8fHww",
#       "is_active": true,
#       "category": {
#         "id": 5,
#         "name": "Sports & Fitness"
#       },
#       "created_at": "2026-07-03T21:37:16.640677+05:30",
#       "updated_at": "2026-07-03T21:37:16.640677+05:30",
#       "brand": "Hydro",
#       "sku": "Hy-Bp"
#     },
#     {
#       "id": 1,
#       "name": "sony headphone",
#       "description": "sony headphone wireless WH-1000XM5",
#       "price": "700.00",
#       "stock": 10,
#       "image_url": "https://plus.unsplash.com/premium_photo-1678099940967-73fe30680949?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8d2lyZWxlc3MlMjBoZWFkcGhvbmVzfGVufDB8fDB8fHww",
#       "is_active": true,
#       "category": {
#         "id": 1,
#         "name": "Electronic & Gadgets"
#       },
#       "created_at": "2026-07-03T21:28:08.842748+05:30",
#       "updated_at": "2026-07-03T21:28:08.842748+05:30",
#       "brand": "SONY",
#       "sku": "SO-HP"
#     },
#     {
#       "id": 3,
#       "name": "Levi's 501",
#       "description": "classis straight",
#       "price": "800.00",
#       "stock": 15,
#       "image_url": "https://plus.unsplash.com/premium_photo-1678099940967-73fe30680949?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8d2lyZWxlc3MlMjBoZWFkcGhvbmVzfGVufDB8fDB8fHww",
#       "is_active": true,
#       "category": {
#         "id": 2,
#         "name": "Fashion & Apparel"
#       },
#       "created_at": "2026-07-03T21:31:10.853299+05:30",
#       "updated_at": "2026-07-03T21:31:10.853299+05:30",
#       "brand": "Levis",
#       "sku": "LV-PT"
#     },
#     {
#       "id": 6,
#       "name": "Ordinary Niacinamide",
#       "description": "high-strength vitamin and mineral",
#       "price": "999.00",
#       "stock": 15,
#       "image_url": "https://plus.unsplash.com/premium_photo-1678099940967-73fe30680949?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8d2lyZWxlc3MlMjBoZWFkcGhvbmVzfGVufDB8fDB8fHww",
#       "is_active": true,
#       "category": {
#         "id": 4,
#         "name": "Beauty & Personal Care"
#       },
#       "created_at": "2026-07-03T21:35:54.168770+05:30",
#       "updated_at": "2026-07-03T21:35:54.168770+05:30",
#       "brand": "Lodge",
#       "sku": "OR-Ni"
#     },
#     {
#       "id": 5,
#       "name": "Lodge Cast Iron",
#       "description": "Iron 10.25inch",
#       "price": "1400.00",
#       "stock": 15,
#       "image_url": "https://plus.unsplash.com/premium_photo-1678099940967-73fe30680949?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8d2lyZWxlc3MlMjBoZWFkcGhvbmVzfGVufDB8fDB8fHww",
#       "is_active": true,
#       "category": {
#         "id": 3,
#         "name": "Home & Kitchen"
#       },
#       "created_at": "2026-07-03T21:34:32.202621+05:30",
#       "updated_at": "2026-07-03T21:34:32.202621+05:30",
#       "brand": "Lodge",
#       "sku": "LD-IR"
#     },
#     {
#       "id": 2,
#       "name": "Apple Watch",
#       "description": "Smart Watch Health Tracking",
#       "price": "2700.00",
#       "stock": 10,
#       "image_url": "https://plus.unsplash.com/premium_photo-1678099940967-73fe30680949?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8d2lyZWxlc3MlMjBoZWFkcGhvbmVzfGVufDB8fDB8fHww",
#       "is_active": true,
#       "category": {
#         "id": 1,
#         "name": "Electronic & Gadgets"
#       },
#       "created_at": "2026-07-03T21:29:22.008570+05:30",
#       "updated_at": "2026-07-03T21:29:22.008570+05:30",
#       "brand": "Apple",
#       "sku": "AP-WA"
#     },
#     {
#       "id": 4,
#       "name": "Nike Air Max",
#       "description": "Sneaker with top Quality",
#       "price": "5000.00",
#       "stock": 15,
#       "image_url": "https://plus.unsplash.com/premium_photo-1678099940967-73fe30680949?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NXx8d2lyZWxlc3MlMjBoZWFkcGhvbmVzfGVufDB8fDB8fHww",
#       "is_active": true,
#       "category": {
#         "id": 2,
#         "name": "Fashion & Apparel"
#       },
#       "created_at": "2026-07-03T21:32:32.010565+05:30",
#       "updated_at": "2026-07-03T21:32:32.010565+05:30",
#       "brand": "NIKE",
#       "sku": "NK-90"
#     }
#   ],