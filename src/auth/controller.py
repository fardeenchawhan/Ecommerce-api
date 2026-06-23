from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
import jwt
from pwdlib import PasswordHash

from src.auth.ditos import RegisterSchema, LoginSchema
from src.user.models import Usermodel
from src.utils.settings import settings


password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.EXPIRY_TIME)
    payload = {
        "id": user_id,
        "exp": expire
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token


def register_user(body: RegisterSchema, db: Session):
    existing_user = db.execute(
        select(Usermodel).where(Usermodel.username == body.username)
    ).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    existing_email = db.execute(
        select(Usermodel).where(Usermodel.email == body.email)
    ).scalar_one_or_none()

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    new_user = Usermodel(
        name=body.name,
        username=body.username,
        email=body.email,
        hash_password=get_password_hash(body.password),
        is_admin=False
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(body: LoginSchema, db: Session):
    user = db.execute(
        select(Usermodel).where(Usermodel.username == body.username)
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not verify_password(body.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer"
    }