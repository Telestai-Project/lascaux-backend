import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
from app.db.database import init_db
from app.docker.docker_utils import start_cassandra_container, stop_cassandra_container
import uuid
from app.db.models import User
from uuid import uuid4
from datetime import timezone, datetime
from httpx import AsyncClient
from app.main import app


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

def generate_unique_display_name():
    return f"testuser_{uuid.uuid4().hex[:8]}"

def generate_unique_wallet_address():
    return f"0x{uuid.uuid4().hex[:8]}"

# @pytest.mark.asyncio
# async def test_create_user():
#     transport = ASGITransport(app=app)
#     unique_display_name = generate_unique_display_name()
#     unique_wallet_address = generate_unique_wallet_address()
#     async with AsyncClient(transport=transport, base_url="http://test") as ac:
#         response = await ac.post("/users/", json={"wallet_address": unique_wallet_address, "display_name": unique_display_name, "bio": "Test bio"})
#     assert response.status_code == 200
#     assert response.json()["display_name"] == unique_display_name

# @pytest.mark.asyncio
# async def test_read_user():
#     transport = ASGITransport(app=app)
#     unique_display_name = generate_unique_display_name()
#     unique_wallet_address = generate_unique_wallet_address()
#     async with AsyncClient(transport=transport, base_url="http://test") as ac:
#         # Ensure the user is created before reading
#         create_response = await ac.post("/users/", json={"wallet_address": unique_wallet_address, "display_name": unique_display_name, "bio": "Test bio"})
#         user_id = create_response.json().get("id")  # Assuming the response includes the user ID
#         response = await ac.get(f"/users/{user_id}")
#     assert response.status_code == 200
#     assert response.json()["display_name"] == unique_display_name

@pytest.mark.asyncio
async def test_get_admin_users(setup_admin_users):
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/admins")
    
    # Check response status
    assert response.status_code == 200, f"Unexpected status code {response.status_code}, Response: {response.json()}"

    # Parse response JSON data
    data = response.json()
    
    # Check the number of returned admins matches the setup
    assert len(data) == 2, f"Expected 2 admins, got {len(data)}. Response: {data}"

    # Validate data structure for each admin user
    for user_data in data:
        assert "id" in user_data, f"Missing 'id' in user_data: {user_data}"
        assert "wallet_address" in user_data, f"Missing 'wallet_address' in user_data: {user_data}"
        assert "display_name" in user_data, f"Missing 'display_name' in user_data: {user_data}"
        assert "bio" in user_data, f"Missing 'bio' in user_data: {user_data}"
        assert "profile_photo_url" in user_data, f"Missing 'profile_photo_url' in user_data: {user_data}"
        assert "created_at" in user_data, f"Missing 'created_at' in user_data: {user_data}"
        assert "tags" in user_data, f"Missing 'tags' in user_data: {user_data}"
        assert "admin" in user_data["tags"], f"Expected 'admin' tag in 'tags': {user_data['tags']}"


@pytest.fixture(scope="function")
def setup_admin_users():
    # Retrieve all users with the "admin" tag for cleanup
    admin_users = User.objects.filter(tags__contains=["admin"]).all()
    for admin_user in admin_users:
        admin_user.delete()

    # Create valid admin users for testing
    admin_user_1 = User.create(
        id=uuid4(),
        wallet_address="TcsCu4yjc2GFZCXPVkxQ6E54MWCHkdT9z2",  # random wallet addy for testing
        display_name="admin_user_1",
        bio="Admin User 1 Bio",
        profile_photo_url="/lascaux-backend/img/coolguy.jpg",
        created_at=datetime.now(timezone.utc),
        tags=["admin"]
    )
    admin_user_2 = User.create(
        id=uuid4(),
        wallet_address="TvdqDw3ZzLrYwr3qukMj86rf3dtMQwL5PU",  # random wallet addy for testing
        display_name="admin_user_2",
        bio="Admin User 2 Bio",
        profile_photo_url="/lascaux-backend/img/angrycat.jpg",
        created_at=datetime.now(timezone.utc),
        tags=["admin"]
    )

    yield [admin_user_1, admin_user_2]

    # Clean up after the test by deleting the specific users created
    admin_user_1.delete()
    admin_user_2.delete()

    

