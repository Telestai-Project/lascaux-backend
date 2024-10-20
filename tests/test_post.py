import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import init_db
from app.docker_utils import start_cassandra_container, stop_cassandra_container
from uuid import uuid4
import random
import string

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

def generate_random_string(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@pytest.mark.asyncio
async def test_create_post():
    transport = ASGITransport(app=app)
    post_id = str(uuid4())
    user_id = str(uuid4())
    title = generate_random_string(15)
    content = generate_random_string(50)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post("/posts/", json={"post_id": post_id, "user_id": user_id, "title": title, "content": content})
    assert response.status_code == 200
    assert response.json()["title"] == title
    assert response.json()["content"] == content