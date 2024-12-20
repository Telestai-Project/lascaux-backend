from fastapi import Depends, HTTPException, status, Request

async def auth_required(request: Request):
    if request.state.user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return request.state.user
