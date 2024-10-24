import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import pytest
import math
import os
from unittest import mock
from app.get_amount.get_amount import fetch_price, calculate_tls_for_required_amount, store_required_amount_to_db
from requests.exceptions import Timeout, RequestException
from cassandra import InvalidRequest, OperationTimedOut
from app.docker.docker_utils import start_cassandra_container, stop_cassandra_container
from app.db.models import TLSAmount

# default to 2 if no value is set
REQUIRED_AMOUNT =  int(os.getenv("REQUIRED_AMOUNT", 2)) # pylint: disable=invalid-envvar-default

@pytest.fixture(scope="session", autouse=True)
def setup_cassandra():
    start_cassandra_container()
    yield
    
@pytest.fixture(scope="session", autouse=True)
def close_cassandra():
    yield
    stop_cassandra_container()
    
    
# Mock environment variables
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("LIVECOINWATCH_API", "fake_api_key")
    monkeypatch.setenv("REQUIRED_AMOUNT", "2")

# Mock requests globally for tests
@pytest.fixture(autouse=True)
def mock_requests():
    with mock.patch('requests.request') as mock_post:
        yield mock_post

# Tests for fetch_price function
def test_fetch_price_success(mock_requests):
    mock_requests.return_value.status_code = 200
    mock_requests.return_value.json.return_value = {'rate': 100}

    price = fetch_price()
    assert price == 100

def test_fetch_price_api_error(mock_requests):
    # Simulate a failed API call with status code 500
    mock_requests.return_value.status_code = 500
    mock_requests.return_value.json.return_value = None  # Simulate no valid JSON response

    price = fetch_price()
    assert price is None  # Expect price to be None due to the failed API call

def test_fetch_price_value_error(mock_requests):
    mock_requests.return_value.status_code = 200
    mock_requests.return_value.json.return_value = {}

    price = fetch_price()
    assert price is None

def test_fetch_price_timeout(mock_requests):
    mock_requests.side_effect = Timeout()
    price = fetch_price()
    assert price is None

def test_fetch_price_request_exception(mock_requests):
    mock_requests.side_effect = RequestException("API error")
    price = fetch_price()
    assert price is None

# Tests for calculate_tls_for_required_amount function
def test_calculate_tls_for_required_amount_success():
    price = 100
    tls_amount = calculate_tls_for_required_amount(price)
    expected_tls_amount = math.ceil(REQUIRED_AMOUNT / 100)  # REQUIRED_AMOUNT = $2
    assert tls_amount == expected_tls_amount

def test_calculate_tls_for_required_amount_with_fraction(mock_env_vars):
    price = 150  # Results in a fractional amount
    required_amount = REQUIRED_AMOUNT
    tls_amount = calculate_tls_for_required_amount(price)
    expected_tls_amount = math.ceil(required_amount / price)  # Expected rounding up
    assert tls_amount == expected_tls_amount
    

def test_calculate_tls_for_required_amount_price_none():
    tls_amount = calculate_tls_for_required_amount(None)
    assert tls_amount is None

def test_calculate_tls_for_required_amount_zero_division():
    tls_amount = calculate_tls_for_required_amount(0)
    assert tls_amount is None

# Tests for store_required_amount_to_db function
@mock.patch('app.db.models.TLSAmount.create')
def test_store_required_amount_to_db_success(mock_create):
    tls_amount = 20
    store_required_amount_to_db(tls_amount)
    mock_create.assert_called_once_with(tls_amount=tls_amount, updated_at=mock.ANY)

@mock.patch('app.db.models.TLSAmount.create', side_effect=InvalidRequest("Database error"))
def test_store_required_amount_to_db_invalid_request_error(mock_create):
    tls_amount = 20
    store_required_amount_to_db(tls_amount)
    mock_create.assert_called_once()
    
@mock.patch('app.db.models.TLSAmount.create', side_effect=OperationTimedOut("Timeout error"))
def test_store_required_amount_to_db_timeout_error(mock_create):
    tls_amount = 20
    store_required_amount_to_db(tls_amount)
    mock_create.assert_called_once()

@mock.patch('app.db.models.TLSAmount.create', side_effect=Exception("General error"))
def test_store_required_amount_to_db_general_error(mock_create):
    tls_amount = 20
    store_required_amount_to_db(tls_amount)
    mock_create.assert_called_once()

