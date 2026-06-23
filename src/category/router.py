from fastapi import APIRouter

category_routes = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)

