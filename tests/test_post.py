import pytest
from unittest.mock import patch
import random
import string
from datetime import datetime
from uuid import uuid4
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import init_db
from app.docker.docker_utils import start_cassandra_container, stop_cassandra_container
from app.db.models import User, TLSAmount


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
    
    # Random address from explorer for testing purposes
    wallet_address = "TsBAzkCpFwBURyyrG3voS8RKc8UbrwFA7r"
    
    required_balance = 10

    # Create a user with the specified wallet address
    User.create(wallet_address=wallet_address, display_name=generate_random_string(10))

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Set required TLS amount
        TLSAmount.create(tls_amount=required_balance, updated_at=datetime.now())

        # Test failed post creation due to insufficient balance
        user = User.objects(wallet_address=wallet_address).get()
        user.balance = required_balance - 1
        user.save()
        print(f"User balance set to {user.balance}")

        response = await ac.post("/posts/", json={"post_id": post_id, "user_id": user_id, "title": title, "content": content})
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")

        assert response.status_code == 403

        # Test successful post creation with sufficient balance
        user.balance = required_balance
        user.save()

        response = await ac.post("/posts/", json={"post_id": post_id, "user_id": user_id, "title": title, "content": content})
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")

        assert response.status_code == 200

        # Test successful post creation with balance above required
        user.balance = required_balance + 1
        user.save()

        response = await ac.post("/posts/", json={"post_id": post_id, "user_id": user_id, "title": title, "content": content})
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")

        assert response.status_code == 200
