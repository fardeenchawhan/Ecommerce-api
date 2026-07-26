import os
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

os.environ["TESTING"] = "1"
os.environ["DB_CONNECTION"] = (
    "postgresql://postgres:postgres123@localhost:5432/ecommerce_test_db"
)

from main import app
from src.auth.controller import get_password_hash
from src.category.models import CategoryModel
from src.user.models import Usermodel
from src.utils.db import Base, SessionLocal, engine

# -------------------------
# Database
# -------------------------

Base.metadata.create_all(bind=engine)

client = TestClient(app)


# -------------------------
# Disable Emails
# -------------------------

@pytest.fixture(scope="session", autouse=True)
def disable_email():
    with patch("src.notification.service.send_welcome_email"),\
         patch("src.notification.service.send_order_confirmation_email"), \
         patch("src.notification.service.send_order_status_email"):
        yield


# -------------------------
# Admin User
# -------------------------

@pytest.fixture(scope="session", autouse=True)
def create_test_admin():
    db = SessionLocal()

    admin = db.execute(
        select(Usermodel).where(
            Usermodel.username == "admin"
        )
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


# -------------------------
# Default Category
# -------------------------

@pytest.fixture(scope="session", autouse=True)
def create_default_category():
    db = SessionLocal()

    category = db.execute(
        select(CategoryModel).where(
            CategoryModel.name == "Electronics"
        )
    ).scalar_one_or_none()

    if category is None:
        category = CategoryModel(
            name="Electronics",
        )

        db.add(category)
        db.commit()

    db.close()


# -------------------------
# Client
# -------------------------

@pytest.fixture
def test_client():
    return client


# -------------------------
# Login Helpers
# -------------------------

@pytest.fixture
def admin_headers(test_client):

    response = test_client.post(
        "/auth/login",
        json={
            "username": "admin",
            "password": "Admin@123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


@pytest.fixture
def user_headers(test_client):

    username = f"user_{uuid4().hex[:8]}"

    register = test_client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "username": username,
            "email": f"{username}@gmail.com",
            "password": "Password@123",
        },
    )

    assert register.status_code == 201

    login = test_client.post(
        "/auth/login",
        json={
            "username": username,
            "password": "Password@123",
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }