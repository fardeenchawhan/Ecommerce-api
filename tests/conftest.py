import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
os.environ["TESTING"] = "1"
os.environ["DB_CONNECTION"] = "postgresql://postgres:postgres123@localhost:5432/ecommerce_test_db"


from main import app
from src.utils.db import Base, engine
from sqlalchemy import select

from src.utils.db import SessionLocal
from src.user.models import Usermodel
from src.auth.controller import get_password_hash

# Create tables once
Base.metadata.create_all(bind=engine)

client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def disable_email():
    """
    Disable sending emails during tests.
    """
    with patch("src.notification.service.send_welcome_email"):
        yield

@pytest.fixture(scope="session", autouse=True)
def create_test_admin():
    db = SessionLocal()

    admin = db.execute(
        select(Usermodel).where(Usermodel.username == "admin")
    ).scalar_one_or_none()

    if admin is None:
        admin = Usermodel(
            name="Admin",
            username="admin",
            email="admin@example.com",
            hash_password=get_password_hash("Admin@123"),
            is_admin=True,
        )

        db.add(admin)
        db.commit()

    db.close()

@pytest.fixture
def test_client():
    return client