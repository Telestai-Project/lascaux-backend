from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.models import User
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_current_user(token: str = Depends(oauth2_scheme)):
    logging.info("Decoding JWT token")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        wallet_address: str = payload.get("sub")
        if wallet_address is None:
            logging.error("Wallet address not found in token")
            raise credentials_exception
    except JWTError as e:
        logging.error(f"JWT decoding error: {e}")
        raise credentials_exception
    user = User.objects(wallet_address=wallet_address).first()
    if user is None:
        logging.error("User not found for wallet address")
        raise credentials_exception
    logging.info(f"User {user.wallet_address} authenticated successfully")
    return user