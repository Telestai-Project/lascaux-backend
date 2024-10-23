import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


import json
import requests
import time
import math
from dotenv import load_dotenv
from app.db.models import TLSAmount
from requests.exceptions import RequestException, Timeout
from datetime import datetime, timezone
from cassandra import InvalidRequest, OperationTimedOut, Unavailable
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

API_KEY = os.getenv("LIVECOINWATCH_API")
REQUIRED_AMOUNT = int(os.getenv("REQUIRED_AMOUNT", 2)) # pylint: disable=invalid-envvar-default


    
def fetch_price():
    url = "https://api.livecoinwatch.com/coins/single"
    payload = json.dumps({
        "currency": "USD",
        "code": "TLS",
        "meta": True
    })

    headers = {
        'content-type': 'application/json',
        'x-api-key': API_KEY,
    }

    try:
        response = requests.request("POST", url, headers=headers, data=payload, timeout=5)
        response.raise_for_status()  # Check for HTTP errors

        data = response.json()
        
        # Handle cases where data is None or doesn't contain 'rate'
        if data is None or 'rate' not in data:
            return None
        
        price = data.get('rate')
        return price
    
    except (RequestException, Timeout):
        return None


def calculate_tls_for_required_amount(price):
    if price is None:
        print("Price is None, skipping calculation.")
        return None
    
    try:
        tls_amount = REQUIRED_AMOUNT / price
        tls_amount_rounded = math.ceil(tls_amount)
        return tls_amount_rounded
    except ZeroDivisionError:
        print("Price cannot be zero.")
        return None


def update_price_every_10_mins():
    while True:
        price = fetch_price()
        tls_amount = calculate_tls_for_required_amount(price)

        if tls_amount is not None:
            store_required_amount_to_db(tls_amount)
        else:
            print("Failed to fetch or calculate TLS amount.")
        
        # Wait for 10 minutes (600 seconds) before the next update
        time.sleep(600)


def store_required_amount_to_db(tls_amount):
    try:
        # Create a new entry or update the existing one
        TLSAmount.create(tls_amount=tls_amount, updated_at=datetime.now(timezone.utc))
        print(f"Stored TLS amount: {tls_amount} in the database.")
    except (InvalidRequest, OperationTimedOut, Unavailable) as e:
        print(f"Database error occurred: {e}")
    except Exception as e: # pylint: disable=broad-exception-caught
        print(f"Error storing TLS amount to the database: {e}")


def fetch_user_balance(address):
    """
    Fetches the balance of a specified wallet address using the Blockbook explorer.

    This function uses the Blockbook explorer to fetch wallet balances since 
    Telestai doesn't have a method to fetch the wallet balance of another address 
    other than the address of the node.

    Args:
        address (str): The wallet address to fetch the balance for.

    Returns:
        float: The balance in TLS, or None if the balance could not be fetched.
    """
    
    base_url = "https://blockbook.telestai.io/" 
    url = f"{base_url}address/{address}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the balance element
        balance_element = soup.find('span', {'class': 'prim-amt'})

        if balance_element:
            # Extract the balance text
            balance_text = balance_element.text.strip()
            # Remove TLS and split into whole and decimal parts
            balance_text = balance_text.replace('TLS', '').replace(' ', '')
            whole_part, decimal_part = balance_text.split('.')
            # Combine the parts and convert to float
            balance_value = float(f"{whole_part}.{decimal_part}")
            return balance_value
        else:
            print("Balance element not found in the page.")
            return None
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")
        return None
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return None





