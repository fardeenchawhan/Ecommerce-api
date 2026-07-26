import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
os.environ["TESTING"] = "1"
os.environ["DB_CONNECTION"] = "postgresql://postgres:postgres123@localhost:5432/ecommerce_test_db"


from main import app
from src.utils.db import Base, engine

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


@pytest.fixture
def test_client():
    return client