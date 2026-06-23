from fastapi import FastAPI
from src.utils.db import Base, engine

# import models so tables are registered
from src.user.models import Usermodel
from src.category.models import CategoryModel
from src.product.models import ProductModel
from src.cart.models import CartItemModel
from src.order.models import OrderModel, OrderItemModel

# routers
from src.auth.router import auth_routes
from src.user.router import user_routes
from src.category.router import category_routes
from src.product.router import product_routes
from src.cart.router import cart_routes
from src.order.router import order_routes


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce API",
    description="""
    A FastAPI-based E-Commerce backend with:

    - JWT Authentication
    - User Management
    - Category Management
    - Product Management
    - Cart Management
    - Order Management
    """,
    version="1.0.0"
)

app.include_router(auth_routes)
app.include_router(user_routes)
app.include_router(category_routes)
app.include_router(product_routes)
app.include_router(cart_routes)
app.include_router(order_routes)


@app.get("/", tags=["System"], summary="API Information")
async def root():
    return {
        "message": "E-Commerce API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["System"], summary="Health check")
async def health():
    return {"status": "healthy"}