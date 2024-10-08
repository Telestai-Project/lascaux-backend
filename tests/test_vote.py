import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()

@pytest.mark.asyncio
async def test_create_vote():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/votes/", json={"post_id": 1, "user_id": 1, "vote_value": 1})
    assert response.status_code == 200
    assert response.json()["vote_value"] == 1

@pytest.mark.asyncio
async def test_read_vote():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/votes/1")
    assert response.status_code == 200
    assert response.json()["vote_value"] == 1

@pytest.mark.asyncio
async def test_delete_vote():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/votes/1")
    assert response.status_code == 200