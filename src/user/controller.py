from sqlalchemy import select

from src.user.models import Usermodel
from src.utils.db import SessionLocal
from src.utils.settings import settings
from src.auth.controller import get_password_hash


def create_admin_if_not_exists():
    db = SessionLocal()
    try:
        existing_admin = db.execute(
            select(Usermodel).where(Usermodel.email == settings.ADMIN_EMAIL)
        ).scalar_one_or_none()

        if existing_admin:
            return

        admin_user = Usermodel(
            name=settings.ADMIN_NAME,
            username=settings.ADMIN_USERNAME,
            email=settings.ADMIN_EMAIL,
            hash_password=get_password_hash(settings.ADMIN_PASSWORD),
            is_admin=True
        )

        db.add(admin_user)
        db.commit()

    finally:
        db.close()