import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()

@pytest.mark.asyncio
async def test_create_comment():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/comments/", json={"post_id": 1, "user_id": 1, "comment_text": "Great post!"})
    assert response.status_code == 200
    assert response.json()["comment_text"] == "Great post!"

@pytest.mark.asyncio
async def test_read_comment():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/comments/1")
    assert response.status_code == 200
    assert response.json()["comment_text"] == "Great post!"

@pytest.mark.asyncio
async def test_delete_comment():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.delete("/comments/1")
    assert response.status_code == 200