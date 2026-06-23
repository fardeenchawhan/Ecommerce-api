from fastapi import APIRouter

product_routes = APIRouter(
    prefix="/products",
    tags=["Products"]
)