import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()

@pytest.mark.asyncio
async def test_create_moderation_log():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/moderation_logs/", json={"post_id": 1, "reason": "Inappropriate content"})
    assert response.status_code == 200
    assert response.json()["reason"] == "Inappropriate content"

@pytest.mark.asyncio
async def test_read_moderation_log():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/moderation_logs/1")
    assert response.status_code == 200
    assert response.json()["reason"] == "Inappropriate content"

@pytest.mark.asyncio
async def test_delete_moderation_log():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/moderation_logs/1")
    assert response.status_code == 200