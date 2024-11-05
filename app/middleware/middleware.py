import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import Request, HTTPException, status
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from app.db.models import User
from app.auth.auth import SECRET_KEY, ALGORITHM

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        authorization: str = request.headers.get("Authorization")
        if authorization:
            try:
                scheme, token = authorization.split()
                if scheme.lower() != "bearer":
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme")
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                wallet_address: str = payload.get("sub")
                if wallet_address is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
                user = User.objects(wallet_address=wallet_address).first()
                if user is None:
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
                # Attach user to request state
                request.state.user = user
            except (JWTError, ValueError) as exc:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
        else:
            request.state.user = None
        response = await call_next(request)
        return response
