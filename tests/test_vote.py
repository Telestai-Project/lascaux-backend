import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db
from app.docker_utils import start_cassandra_container, stop_cassandra_container
from uuid import uuid4

@pytest.fixture(scope="session", autouse=True)
def setup_cassandra():
    start_cassandra_container()
    yield

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    init_db()

@pytest.mark.asyncio
async def test_create_vote():
    transport = ASGITransport(app=app)
    post_id = str(uuid4())
    user_id = str(uuid4())
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/votes/", json={"post_id": post_id, "user_id": user_id, "vote_value": 1})
    assert response.status_code == 200
    assert response.json()["vote_value"] == 1

@pytest.mark.asyncio
async def test_read_vote():
    transport = ASGITransport(app=app)
    vote_id = str(uuid4())
    post_id = str(uuid4())
    user_id = str(uuid4())
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create a vote first
        create_response = await ac.post("/votes/", json={"post_id": post_id, "user_id": user_id, "vote_value": 1})
        vote_id = create_response.json().get("id")
        response = await ac.get(f"/votes/{vote_id}")
    assert response.status_code == 200
    assert response.json()["vote_value"] == 1

@pytest.mark.asyncio
async def test_delete_vote():
    transport = ASGITransport(app=app)
    vote_id = str(uuid4())
    post_id = str(uuid4())
    user_id = str(uuid4())
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create a vote first
        create_response = await ac.post("/votes/", json={"post_id": post_id, "user_id": user_id, "vote_value": 1})
        vote_id = create_response.json().get("id")
        response = await ac.delete(f"/votes/{vote_id}")
    assert response.status_code == 200