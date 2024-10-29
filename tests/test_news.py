import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from httpx import AsyncClient
from app.db.models import User
from app.db.database import init_db
from app.docker.docker_utils import start_cassandra_container, stop_cassandra_container
from uuid import uuid4
from datetime import datetime, timezone
from app.main import app
from app.auth.auth import create_access_token

@pytest.fixture(scope="session", autouse=True)
def setup_cassandra():
    start_cassandra_container()
    yield

@pytest.fixture(scope="session", autouse=True)
def close_cassandra():
    yield
    stop_cassandra_container()
    
    
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    init_db()
    
# Fixture to create an admin user
@pytest.fixture
def admin_user():
    user = User.create(
        id=uuid4(),
        wallet_address="admin_wallet_address",
        display_name="admin_user",
        tags=["admin"],
        created_at=datetime.now(timezone.utc)
    )
    return user

# Fixture to create a regular user
@pytest.fixture
def regular_user():
    user = User.create(
        id=uuid4(),
        wallet_address="TcsCu4yjc2GFZCXPVkxQ6E54MWCHkdT9z2", #Zach's wallet addy lmao
        display_name="regular_user",
        tags=[],
        created_at=datetime.now(timezone.utc)
    )
    return user

# Fixture to create a token for a given user
def get_auth_token(user):
    return create_access_token({"sub": user.wallet_address})

# Test creating news as an admin
@pytest.mark.asyncio
async def test_create_news_as_admin(admin_user):
    # Create access token for admin user
    token = get_auth_token(admin_user)
    
    # Set up request data
    news_data = {
        "title": "Admin News",
        "content": "This is a news article by an admin.",
        "admin_id": str(admin_user.id)
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/news/",
            json=news_data,
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Assert successful news creation
    assert response.status_code == 200
    assert response.json()["title"] == "Admin News"
    assert response.json()["content"] == "This is a news article by an admin."

# Test creating news as a non-admin user
@pytest.mark.asyncio
async def test_create_news_as_non_admin(regular_user):
    # Create access token for regular user
    token = get_auth_token(regular_user)
    
    # Set up request data
    news_data = {
        "title": "User News",
        "content": "This should not be allowed.",
        "admin_id": str(regular_user.id)
    }
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/news/",
            json=news_data,
            headers={"Authorization": f"Bearer {token}"}
        )
    
    # Assert forbidden error for non-admin user
    assert response.status_code == 403
    assert response.json()["detail"] == "Admin permissions required"