from fastapi import APIRouter

user_routes = APIRouter(
    prefix="/users",
    tags=["Users"]
)