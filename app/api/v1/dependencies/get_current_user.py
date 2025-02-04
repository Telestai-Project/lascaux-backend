from fastapi import Request, status, HTTPException
from app.domain.entities.user import User

# Dependency to get the current user 
async def get_current_user(request: Request) -> User:
    user: User = request.state.user
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user