import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db
import uuid

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    # Reset the database state before each test
    init_db()

def generate_unique_username():
    return f"testuser_{uuid.uuid4().hex[:8]}"

def generate_unique_wallet_address():
    return f"0x{uuid.uuid4().hex[:8]}"

@pytest.mark.asyncio
async def test_create_user():
    transport = ASGITransport(app=app)
    unique_username = generate_unique_username()
    unique_wallet_address = generate_unique_wallet_address()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/users/", json={"wallet_address": unique_wallet_address, "username": unique_username, "bio": "Test bio"})
    assert response.status_code == 200
    assert response.json()["username"] == unique_username

@pytest.mark.asyncio
async def test_read_user():
    transport = ASGITransport(app=app)
    unique_username = generate_unique_username()
    unique_wallet_address = generate_unique_wallet_address()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Ensure the user is created before reading
        create_response = await ac.post("/users/", json={"wallet_address": unique_wallet_address, "username": unique_username, "bio": "Test bio"})
        user_id = create_response.json().get("id")  # Assuming the response includes the user ID
        response = await ac.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == unique_username