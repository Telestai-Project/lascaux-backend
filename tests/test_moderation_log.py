import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import init_db
from app.docker.docker_utils import start_cassandra_container, stop_cassandra_container
from uuid import uuid4

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

@pytest.mark.asyncio
async def test_create_moderation_log():
    transport = ASGITransport(app=app)
    post_id = str(uuid4())
    user_id = str(uuid4())  # Generate a user_id
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/moderation_logs/", json={"post_id": post_id, "user_id": user_id, "reason": "Inappropriate content"})
    assert response.status_code == 200
    assert response.json()["reason"] == "Inappropriate content"

@pytest.mark.asyncio
async def test_read_moderation_log():
    transport = ASGITransport(app=app)
    log_id = str(uuid4())
    post_id = str(uuid4())
    user_id = str(uuid4())  # Generate a user_id
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create a moderation log first
        create_response = await ac.post("/moderation_logs/", json={"post_id": post_id, "user_id": user_id, "reason": "Inappropriate content"})
        log_id = create_response.json().get("id")
        response = await ac.get(f"/moderation_logs/{log_id}")
    assert response.status_code == 200
    assert response.json()["reason"] == "Inappropriate content"

@pytest.mark.asyncio
async def test_delete_moderation_log():
    transport = ASGITransport(app=app)
    log_id = str(uuid4())
    post_id = str(uuid4())
    user_id = str(uuid4())  # Generate a user_id
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create a moderation log first
        create_response = await ac.post("/moderation_logs/", json={"post_id": post_id, "user_id": user_id, "reason": "Inappropriate content"})
        log_id = create_response.json().get("id")
        response = await ac.delete(f"/moderation_logs/{log_id}")
    assert response.status_code == 200