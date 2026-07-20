from fastapi import APIRouter
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.auth.ditos import RegisterSchema, LoginSchema, TokenResponseSchema
from src.user.ditos import UserResponseSchema
from src.auth import controller
from src.utils.db import get_db
from fastapi import BackgroundTasks
from src.notification import service as notification_service 
from src.email.templates import welcome_email_template



auth_routes = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@auth_routes.post(
    "/register",
    response_model=UserResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
async def register(body: RegisterSchema,background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user= controller.register_user(body, db ,background_tasks)
    return user


@auth_routes.post(
    "/login",
    response_model=TokenResponseSchema,
    status_code=status.HTTP_200_OK,
    summary="Login user"
)
async def login(body: LoginSchema, db: Session = Depends(get_db)):
    return controller.login_user(body, db)